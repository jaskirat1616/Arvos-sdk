# macOS OpenCV Threading Fix

## Problem

When running with threading, got this error:
```
❌ Display loop error: Unknown C++ exception from OpenCV code
cv2.error: Unknown C++ exception from OpenCV code
```

## Root Cause

**macOS requires all GUI operations to run on the main thread.**

This is a fundamental macOS/Cocoa limitation:
- OpenCV GUI functions (`cv2.imshow`, `cv2.waitKey`, `cv2.namedWindow`) use Cocoa
- Cocoa requires all UI operations on the main application thread
- Python threading creates new threads that are NOT the main thread
- This works on Linux/Windows but FAILS on macOS

## Solution

**Keep display on main thread, integrate with asyncio event loop:**

```python
async def main():
    # Start async server
    server_task = asyncio.create_task(server.start())

    # Main loop runs on main thread
    while running:
        # Display (sync, on main thread)
        viewer.show()  # cv2.imshow, cv2.waitKey

        # Yield to async tasks
        await asyncio.sleep(0.001)
```

### How It Works

1. **Main thread:** Runs asyncio event loop + OpenCV display
2. **Async tasks:** WebSocket server runs as async task
3. **Integration:** `await asyncio.sleep(0.001)` lets async tasks process between frames
4. **Fast JPEG decode:** `cv2.imdecode` still used (3x faster than PIL)

### Performance

- **Display:** Runs on main thread (required by macOS)
- **Network:** Runs in async task (non-blocking)
- **JPEG decode:** Happens in async callbacks (fast cv2.imdecode)
- **Loop speed:** 1ms sleep = up to 1000 FPS theoretical, limited by cv2.waitKey(1)

## Architecture

```
Main Thread (asyncio event loop):
├── Async Task: WebSocket Server
│   ├── Receive data
│   ├── cv2.imdecode (fast)
│   └── Update viewer.latest_frame
│
├── Display Loop (sync)
│   ├── cv2.imshow(viewer.latest_frame)
│   ├── cv2.waitKey(1)
│   └── await asyncio.sleep(0.001)
│
└── Loop continues...
```

## Changes Made

### 1. Removed Threading
- Deleted `threading.Thread` approach
- Removed `self.lock` (not needed - single thread)
- Removed `start_display()` and `stop_display()` methods

### 2. Simplified Display
- `show()` method runs on main thread
- Called directly in async main loop
- No threading complexity

### 3. Integrated with Asyncio
```python
# Main loop
while running:
    viewer.show()  # Sync display
    await asyncio.sleep(0.001)  # Let async tasks run
```

## Expected Performance

- **FPS:** 20-30 FPS (limited by iPhone, not Python)
- **Latency:** ~1-2ms per frame processing
- **CPU:** Efficient - sleeps when idle
- **Compatibility:** Works on macOS, Linux, Windows

## Why This is Better Than Threading

1. ✅ **macOS Compatible** - GUI on main thread
2. ✅ **Simple** - No locks, no race conditions
3. ✅ **Fast** - cv2.imdecode still used
4. ✅ **Async** - Server runs concurrently
5. ✅ **Clean** - One event loop, one thread

## Testing

```bash
python examples/live_camera_view.py
```

Should now work without OpenCV C++ errors on macOS!

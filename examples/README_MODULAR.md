# Arvos Modular Viewers - ROS-like Architecture

## Overview

Separate viewer processes for maximum performance and stability.
Each viewer runs independently, avoiding asyncio+OpenCV conflicts.

## Architecture

```
iPhone (Arvos App)
       ↓ WebSocket (port 9090)
       ↓
   ┌───┴───┬───────┬───────┐
   │       │       │       │
Camera   Depth    GPS   (IMU/Pose)
Viewer   Viewer  Viewer  Viewers
```

Each viewer:
- ✅ Separate process
- ✅ Independent event loop
- ✅ Maximum FPS (no interference)
- ✅ Can be launched/stopped individually

## Quick Start

### Launch All Viewers

```bash
python launch_all.py
```

This opens 3 windows:
- **Camera** - Live video feed (25-30 FPS)
- **Depth** - LiDAR depth map
- **GPS** - OpenStreetMap location

### Launch Individual Viewers

**Camera only (maximum FPS):**
```bash
python camera_viewer.py
```

**Depth only:**
```bash
python depth_viewer.py
```

**GPS only:**
```bash
python gps_viewer.py
```

### Launch Combinations

**Camera + Depth (no GPS):**
```bash
python launch_all.py --no-gps
```

**Camera only:**
```bash
python launch_all.py --camera-only
```

## Performance

### Single Viewer (Maximum FPS)
- Camera: **28-30 FPS** ✅
- Depth: Updates at sensor rate (~5 FPS)
- GPS: Updates when moved

### All Viewers (ROS-like)
- Camera: **25-30 FPS** ✅
- Depth: **Real-time** ✅
- GPS: **Real-time** ✅

**No interference between viewers!**

## How It Works

### Problem with Monolithic Approach
```python
# BAD: Everything in one process
async def main():
    show_camera()  # Blocks
    show_depth()   # Blocks
    show_gps()     # Blocks
    # AsyncIO scheduling chaos!
```

### Solution: Separate Processes
```python
# GOOD: Each viewer is independent
Process 1: camera_viewer.py (own event loop)
Process 2: depth_viewer.py  (own event loop)
Process 3: gps_viewer.py    (own event loop)
```

### Benefits

1. **No asyncio conflicts** - Each process has own event loop
2. **Maximum FPS** - Camera gets full CPU when needed
3. **Fault isolation** - GPS crash doesn't affect camera
4. **Easy to extend** - Add new viewers without touching existing ones
5. **ROS-like** - Familiar architecture for robotics developers

## Stopping Viewers

**Stop all:**
- Press `Ctrl+C` in launcher terminal
- Or close any window and press `q`

**Stop individual:**
- Press `q` in the window
- Or close the window

## Advanced Usage

### Custom Port

```bash
python launch_all.py --port 8080
```

### Launch in Background

```bash
nohup python launch_all.py &
```

### Monitor Logs

```bash
python launch_all.py 2>&1 | tee arvos.log
```

## Comparison to Alternatives

### vs Foxglove
- ✅ Simpler (no web stack)
- ✅ Native performance
- ❌ Less interactive (no 3D rotation)

### vs Single Process
- ✅ Much better FPS
- ✅ No asyncio conflicts
- ✅ More stable
- ❌ Slightly more memory

### vs Zenoh/DDS
- ✅ Simpler setup
- ✅ No external dependencies
- ❌ Only works with Arvos

## Files

```
examples/
├── launch_all.py        # ROS-like launcher
├── camera_viewer.py     # Camera-only viewer
├── depth_viewer.py      # Depth-only viewer
├── gps_viewer.py        # GPS-only viewer
└── README_MODULAR.md    # This file
```

## Troubleshooting

### "Connection refused"
Make sure iPhone app is running and connected to same network.

### Low FPS
Try camera-only mode:
```bash
python camera_viewer.py
```

If still slow, check network/iPhone.

### Windows overlap
Drag windows to separate monitors or arrange on screen.

### Multiple connections
Each viewer connects independently. iPhone sends data to all.

## Future Enhancements

Potential additions:
- IMU viewer (real-time orientation)
- Pose viewer (6DOF trajectory)
- Recording viewer (save streams)
- Web viewer (browser-based)

## Summary

This modular architecture:
- ✅ Solves asyncio+OpenCV conflicts
- ✅ Achieves 25-30 FPS camera
- ✅ Runs depth and GPS simultaneously
- ✅ Familiar to ROS developers
- ✅ Easy to extend and maintain

**Perfect for production use!** 🚀

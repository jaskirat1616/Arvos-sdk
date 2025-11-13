# Apple Watch Quick Start Guide

Get Apple Watch sensor data streaming to your Python code in 5 minutes.

## Step 1: Hardware Setup (1 minute)

- ✅ iPhone 12 Pro or newer with Arvos app
- ✅ Apple Watch Series 6+ paired with iPhone
- ✅ Computer on same WiFi network

## Step 2: Install Watch Companion (2 minutes)

The watch companion app is built into the Arvos iOS app and installs automatically.

1. Open **Arvos** app on iPhone
2. The watch app installs automatically to paired watch
3. Wait for installation to complete (check Watch home screen)

## Step 3: Enable Watch Sensors (30 seconds)

In Arvos app on iPhone:

1. Tap **"Sensor Test"** or **"Settings"**
2. Toggle **"Apple Watch"** to ON
3. Verify status shows **"Connected"**

## Step 4: Run Example (1 minute)

```bash
cd arvos-sdk
python examples/simple_watch_receiver.py
```

Scan the QR code with iPhone → Tap "START" → Done! 🎉

## What You'll Receive

### Watch IMU Data (50-100 Hz)
```python
async def on_watch_imu(data: WatchIMUData):
    print(f"Accel: {data.linear_acceleration} m/s²")
    print(f"Gyro: {data.angular_velocity} rad/s")
    print(f"Gravity: {data.gravity} m/s²")
```

### Watch Attitude (~50 Hz)
```python
async def on_watch_attitude(data: WatchAttitudeData):
    print(f"Pitch: {data.pitch} rad")
    print(f"Roll: {data.roll} rad")
    print(f"Yaw: {data.yaw} rad")
    print(f"Quaternion: {data.quaternion}")
```

### Motion Activity (on change)
```python
async def on_watch_activity(data: WatchMotionActivityData):
    print(f"Activity: {data.state}")  # walking, running, cycling, etc.
    print(f"Confidence: {data.confidence}")  # 0.0 - 1.0
```

## Complete Example

```python
import asyncio
from arvos import ArvosServer

server = ArvosServer(port=9090)

# Define callbacks
async def on_watch_imu(data):
    print(f"⌚ Watch IMU: {data.linear_acceleration}")

async def on_watch_attitude(data):
    print(f"🧭 Attitude: pitch={data.pitch:.2f}, roll={data.roll:.2f}")

async def on_watch_activity(data):
    print(f"🏃 Activity: {data.state} ({data.confidence:.1%})")

# Register callbacks
server.on_watch_imu = on_watch_imu
server.on_watch_attitude = on_watch_attitude
server.on_watch_activity = on_watch_activity

# Start server
asyncio.run(server.start())
```

## Troubleshooting

**No data arriving?**
1. Check "Apple Watch" is enabled in Arvos app
2. Verify watch shows in Settings → Bluetooth on iPhone
3. Make sure watch is not in Low Power Mode
4. Try restarting both devices

**Low sample rate?**
- Close other apps on watch
- Disable Theater Mode on watch
- Check Bluetooth connection quality

## Next Steps

- 📖 Full examples: `examples/README_WATCH.md`
- 🔧 API reference: `README.md` → "Apple Watch Sensors" section
- 📱 iOS app integration: `/arvos/WATCH_INTEGRATION.md`

## Use Cases

- **Gait analysis** - Track walking patterns
- **Fall detection** - Monitor sudden movements
- **Activity recognition** - ML training data
- **Gesture control** - Control robots with watch gestures
- **Sports analytics** - Form analysis, cadence tracking
- **Health monitoring** - Movement quality assessment
- **AR/VR** - Hand tracking for immersive experiences

---

**Questions?** Check `examples/README_WATCH.md` for detailed guides and patterns.

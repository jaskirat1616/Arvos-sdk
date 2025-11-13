# Basic Server Example

Create a simple WebSocket server to receive ARVOS sensor data.

## Complete Example

```python
import asyncio
from arvos import ArvosServer
from arvos.data_types import IMUData, GPSData, PoseData, CameraFrame, DepthFrame

async def main():
    # Create server
    server = ArvosServer(port=9090)
    
    # Show QR code for easy connection
    server.print_qr_code()
    
    # Connection callbacks
    async def on_connect(client_id: str):
        print(f"✅ Client connected: {client_id}")
    
    async def on_disconnect(client_id: str):
        print(f"👋 Client disconnected: {client_id}")
    
    # Sensor callbacks
    async def on_handshake(handshake):
        print(f"🤝 Device: {handshake.device_name} ({handshake.device_model})")
        print(f"   OS: {handshake.os_version}, App: {handshake.app_version}")
    
    async def on_imu(data: IMUData):
        print(f"📊 IMU: accel={data.linear_acceleration}, gyro={data.angular_velocity}")
    
    async def on_gps(data: GPSData):
        print(f"📍 GPS: {data.latitude:.6f}, {data.longitude:.6f}")
    
    async def on_pose(data: PoseData):
        print(f"🧭 Pose: position={data.position}, tracking={data.tracking_state}")
    
    async def on_camera(frame: CameraFrame):
        print(f"📷 Camera: {frame.width}x{frame.height}, {frame.size_kb:.1f} KB")
    
    async def on_depth(frame: DepthFrame):
        print(f"🔍 Depth: {frame.point_count} points, {frame.size_kb:.1f} KB")
    
    # Register callbacks
    server.on_connect = on_connect
    server.on_disconnect = on_disconnect
    server.on_handshake = on_handshake
    server.on_imu = on_imu
    server.on_gps = on_gps
    server.on_pose = on_pose
    server.on_camera = on_camera
    server.on_depth = on_depth
    
    # Start server
    print("🚀 Server started. Waiting for connections...")
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
```

## Run the Example

```bash
python examples/basic_server.py
```

## Connect from iPhone

1. Open ARVOS app
2. Tap "CONNECT TO SERVER"
3. Scan QR code or enter IP
4. Tap "START STREAMING"

## What You'll See

```
==================================================
ARVOS SERVER - Scan this QR code with your iPhone:
==================================================
[QR CODE]
==================================================
Or manually enter: ws://192.168.1.100:9090
==================================================
🚀 Server started. Waiting for connections...
✅ Client connected: 192.168.1.50:54321
🤝 Device: iPhone (iPhone 15 Pro)
   OS: 17.0, App: 1.0.0
📊 IMU: accel=(0.1, 0.0, -0.01), gyro=(0.01, -0.02, 0.005)
📊 IMU: accel=(0.1, 0.0, -0.01), gyro=(0.01, -0.02, 0.005)
...
```

## Next Steps

- [Protocol Examples](protocols.md) - Try different protocols
- [Visualization Examples](visualization.md) - Visual examples
- [API Reference](../api/python-sdk.md) - Complete API docs


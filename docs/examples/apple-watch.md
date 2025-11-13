# Apple Watch Examples

Receive and process Apple Watch sensor data.

## Basic Watch Receiver

```python
import asyncio
from arvos import ArvosServer
from arvos.data_types import WatchIMUData, WatchAttitudeData, WatchMotionActivityData

async def main():
    server = ArvosServer(port=9090)
    
    # Watch IMU data (50-100 Hz)
    async def on_watch_imu(data: WatchIMUData):
        accel = data.linear_acceleration_array
        gyro = data.angular_velocity_array
        print(f"Watch IMU: accel={accel}, gyro={gyro}")
    
    # Watch attitude/pose
    async def on_watch_attitude(data: WatchAttitudeData):
        import math
        pitch_deg = math.degrees(data.pitch)
        roll_deg = math.degrees(data.roll)
        yaw_deg = math.degrees(data.yaw)
        print(f"Watch Attitude: pitch={pitch_deg:.1f}°, roll={roll_deg:.1f}°, yaw={yaw_deg:.1f}°")
    
    # Watch motion activity
    async def on_watch_activity(data: WatchMotionActivityData):
        print(f"Activity: {data.state} (confidence: {data.confidence:.1%})")
    
    server.on_watch_imu = on_watch_imu
    server.on_watch_attitude = on_watch_attitude
    server.on_watch_activity = on_watch_activity
    
    await server.start()

asyncio.run(main())
```

## Watch Sensor Viewer

Complete viewer with statistics:

```bash
python examples/watch_sensor_viewer.py
```

Features:
- Real-time IMU visualization
- Attitude display
- Motion activity classification
- Statistics and sample rates

## Simple Watch Receiver

Minimal example:

```bash
python examples/simple_watch_receiver.py
```

## Next Steps

- [iOS App - Apple Watch](../ios-app/apple-watch.md) - App setup
- [Examples Overview](overview.md) - All examples
- [API Reference](../api/data-types.md) - Watch data types


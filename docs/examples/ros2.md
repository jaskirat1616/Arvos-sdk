# ROS 2 Integration

Publish ARVOS sensor data to ROS 2 topics.

## Overview

The ROS 2 bridge publishes standard ROS messages from ARVOS sensor data.

## Topics

| Topic | Message Type | Description |
|-------|--------------|-------------|
| `/arvos/imu` | `sensor_msgs/Imu` | IMU data |
| `/arvos/gps` | `sensor_msgs/NavSatFix` | GPS location |
| `/arvos/camera/image_raw` | `sensor_msgs/Image` | Camera frames |
| `/arvos/camera/info` | `sensor_msgs/CameraInfo` | Camera intrinsics |
| `/arvos/depth/points` | `sensor_msgs/PointCloud2` | Depth point clouds |
| `/arvos/tf` | `tf2_msgs/TFMessage` | Transform tree |

## Usage

### Start Bridge

```bash
python examples/ros2_bridge.py
```

### View Topics

```bash
# List topics
ros2 topic list

# Echo IMU data
ros2 topic echo /arvos/imu

# Echo GPS data
ros2 topic echo /arvos/gps
```

### Visualize in RViz

```bash
rviz2
```

Configure RViz to display:
- Camera feed from `/arvos/camera/image_raw`
- Point cloud from `/arvos/depth/points`
- TF tree from `/arvos/tf`

## Example

```python
import asyncio
from arvos import ArvosServer
import rclpy
from sensor_msgs.msg import Imu, NavSatFix, Image, PointCloud2

async def main():
    rclpy.init()
    node = rclpy.create_node('arvos_bridge')
    
    # Create publishers
    imu_pub = node.create_publisher(Imu, '/arvos/imu', 10)
    gps_pub = node.create_publisher(NavSatFix, '/arvos/gps', 10)
    
    server = ArvosServer(port=9090)
    
    async def on_imu(data):
        msg = Imu()
        # Convert ARVOS IMU to ROS message
        # ... conversion code ...
        imu_pub.publish(msg)
    
    server.on_imu = on_imu
    await server.start()

asyncio.run(main())
```

## Next Steps

- [ROS 2 Documentation](https://docs.ros.org)
- [Examples Overview](overview.md) - All examples
- [Protocol Examples](protocols.md) - Protocol examples


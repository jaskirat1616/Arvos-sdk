# Visualization Examples

Visualize ARVOS sensor data in real-time.

## Live Visualization

Real-time sensor data visualization with matplotlib.

```python
import asyncio
from arvos import ArvosServer
import matplotlib.pyplot as plt
import numpy as np

# Setup plots
fig, axes = plt.subplots(2, 2)
accel_plot = axes[0, 0]
gyro_plot = axes[0, 1]
gps_plot = axes[1, 0]
pose_plot = axes[1, 1]

async def main():
    server = ArvosServer(port=9090)
    
    # Update plots with data
    server.on_imu = lambda data: update_imu_plot(data)
    server.on_gps = lambda data: update_gps_plot(data)
    server.on_pose = lambda data: update_pose_plot(data)
    
    await server.start()

asyncio.run(main())
```

## Point Cloud Viewer

3D LiDAR point cloud visualization.

```python
import asyncio
from arvos import ArvosServer
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

async def main():
    server = ArvosServer(port=9090)
    
    async def on_depth(frame):
        points = frame.to_point_cloud()
        if points is not None:
            xyz = points[:, :3]
            visualize_point_cloud(xyz)
    
    server.on_depth = on_depth
    await server.start()

asyncio.run(main())
```

## Camera Viewer

Live camera feed display.

```python
import asyncio
from arvos import ArvosServer
from PIL import Image
import numpy as np

async def main():
    server = ArvosServer(port=9090)
    
    async def on_camera(frame):
        img = frame.to_numpy()
        if img is not None:
            display_image(img)
    
    server.on_camera = on_camera
    await server.start()

asyncio.run(main())
```

## Rerun Visualization

Visualization with Rerun.

```bash
pip install rerun-sdk pillow
python examples/rerun_visualizer.py --port 9090
```

This launches a Rerun viewer and logs all sensor streams.

## Next Steps

- [Basic Server](basic-server.md) - Simple example
- [Protocol Examples](protocols.md) - Protocol examples
- [ROS 2 Integration](ros2.md) - ROS 2 visualization


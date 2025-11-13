# Performance Optimization

Optimize your ARVOS setup for maximum performance.

## Network Optimization

### Use Wired Connection
- Connect computer via Ethernet
- Reduces Wi-Fi congestion
- Lower latency
- More stable

### Optimize Wi-Fi
- Use 5 GHz band (if available)
- Position devices closer
- Reduce interference
- Use dedicated network

### Protocol Selection
- **gRPC** or **QUIC/HTTP3** for maximum performance
- **WebSocket** for good balance
- **HTTP/REST** not ideal for high-frequency data

## Code Optimization

### Async Processing

Process data asynchronously:

```python
async def on_camera(frame):
    # Don't block - process in background
    asyncio.create_task(process_frame(frame))

async def process_frame(frame):
    # Heavy processing here
    img = frame.to_numpy()
    # ... processing ...
```

### Skip Frames

For high-frequency data, skip some frames:

```python
frame_count = 0

async def on_camera(frame):
    global frame_count
    frame_count += 1
    if frame_count % 2 == 0:  # Process every 2nd frame
        process_frame(frame)
```

### Batch Processing

Batch multiple messages:

```python
imu_buffer = []

async def on_imu(data):
    imu_buffer.append(data)
    if len(imu_buffer) >= 100:
        process_batch(imu_buffer)
        imu_buffer.clear()
```

## Sensor Rate Optimization

### Reduce Rates in App
- Lower camera frame rate
- Reduce IMU sample rate
- Disable unused sensors

### Selective Streaming
- Use "IMU Only" mode for telemetry
- Use "RGBD Camera" for 3D reconstruction
- Custom mode for specific needs

## Memory Management

### Process and Discard
- Don't accumulate data indefinitely
- Process and discard immediately
- Use generators for large datasets

### Downsample Point Clouds
- Reduce point cloud density
- Filter by distance
- Use voxel downsampling

## CPU Optimization

### Use NumPy Operations
- Vectorized operations
- Avoid Python loops
- Use compiled libraries

### Parallel Processing
- Use multiprocessing for heavy tasks
- Process frames in parallel
- Utilize all CPU cores

## Example: Optimized Server

```python
import asyncio
from arvos import ArvosServer
import numpy as np

# Batch processing
imu_buffer = []
BATCH_SIZE = 100

async def process_imu_batch(batch):
    # Vectorized processing
    accels = np.array([d.linear_acceleration for d in batch])
    gyros = np.array([d.angular_velocity for d in batch])
    # Process batch...
    pass

async def main():
    server = ArvosServer(port=9090)
    
    async def on_imu(data):
        global imu_buffer
        imu_buffer.append(data)
        if len(imu_buffer) >= BATCH_SIZE:
            await process_imu_batch(imu_buffer)
            imu_buffer.clear()
    
    server.on_imu = on_imu
    await server.start()

asyncio.run(main())
```

## Next Steps

- [Protocol Selection](protocol-selection.md) - Choose the right protocol
- [Best Practices](best-practices.md) - Recommended practices
- [Troubleshooting](troubleshooting.md) - Performance issues


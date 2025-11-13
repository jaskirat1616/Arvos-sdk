# Best Practices

Recommended practices for using ARVOS effectively.

## Code Organization

### Use Async Callbacks

Prefer async callbacks for better performance:

```python
# Good
async def on_imu(data: IMUData):
    await process_imu(data)

# Avoid blocking
def on_imu(data: IMUData):
    time.sleep(1)  # Don't block!
    process_imu(data)
```

### Error Handling

Always handle errors in callbacks:

```python
async def on_camera(frame: CameraFrame):
    try:
        img = frame.to_numpy()
        if img is not None:
            process_image(img)
    except Exception as e:
        print(f"Error processing camera frame: {e}")
```

### Resource Management

Clean up resources properly:

```python
async def main():
    server = ArvosServer(port=9090)
    try:
        await server.start()
    finally:
        await server.stop()
```

## Performance

### Batch Processing

Batch multiple messages for efficiency:

```python
imu_buffer = []

async def on_imu(data: IMUData):
    imu_buffer.append(data)
    if len(imu_buffer) >= 100:
        process_batch(imu_buffer)
        imu_buffer.clear()
```

### Async Processing

Don't block the event loop:

```python
async def on_camera(frame: CameraFrame):
    # Process in background
    asyncio.create_task(heavy_processing(frame))
```

### Selective Processing

Only process what you need:

```python
# Only process every Nth frame
frame_count = 0

async def on_camera(frame: CameraFrame):
    global frame_count
    frame_count += 1
    if frame_count % 5 == 0:  # Every 5th frame
        process_frame(frame)
```

## Data Handling

### Type Safety

Use type hints for better code:

```python
from arvos.data_types import IMUData

async def on_imu(data: IMUData) -> None:
    # Type-safe access
    accel = data.linear_acceleration
    gyro = data.angular_velocity
```

### Data Validation

Validate data before processing:

```python
async def on_pose(data: PoseData):
    if not data.is_tracking_good():
        return  # Skip bad tracking
    
    # Process good tracking data
    process_pose(data)
```

### Memory Management

Don't accumulate data indefinitely:

```python
# Good - process and discard
async def on_imu(data: IMUData):
    result = process_imu(data)
    save_result(result)
    # Data is garbage collected

# Bad - accumulates in memory
imu_data_list = []
async def on_imu(data: IMUData):
    imu_data_list.append(data)  # Memory leak!
```

## Network

### Protocol Selection

Choose the right protocol for your use case:

- **General purpose:** WebSocket
- **High performance:** gRPC
- **Multiple subscribers:** MQTT
- **Simple integration:** HTTP/REST
- **No Wi-Fi:** Bluetooth LE
- **Robotics:** MCAP Stream
- **Ultra-low latency:** QUIC/HTTP3

### Connection Handling

Handle reconnections gracefully:

```python
async def on_disconnect(client_id: str):
    print(f"Client {client_id} disconnected")
    # Clean up resources
    # Prepare for reconnection

async def on_connect(client_id: str):
    print(f"Client {client_id} connected")
    # Initialize resources
```

## Security

### Local Development

For local development:
- Use self-signed certificates for QUIC/HTTP3
- Trust certificates on test devices
- Use local network only

### Production

For production:
- Use proper TLS certificates
- Validate all inputs
- Implement authentication
- Use secure protocols

## Testing

### Unit Tests

Test your callbacks:

```python
def test_imu_processing():
    data = IMUData(
        timestamp_ns=1000,
        angular_velocity=(0.1, 0.2, 0.3),
        linear_acceleration=(1.0, 2.0, 3.0)
    )
    result = process_imu(data)
    assert result is not None
```

### Integration Tests

Test with real server:

```python
async def test_server():
    server = ArvosServer(port=9090)
    # Test server functionality
    await server.start()
    # ... test ...
    await server.stop()
```

## Documentation

### Code Comments

Document complex logic:

```python
async def on_depth(frame: DepthFrame):
    # Parse PLY point cloud format
    # Format: [x, y, z, r, g, b] per point
    points = frame.to_point_cloud()
    if points is not None:
        xyz = points[:, :3]  # Extract 3D positions
        rgb = points[:, 3:]  # Extract RGB colors
```

### Type Hints

Use type hints throughout:

```python
from typing import Optional
from arvos.data_types import IMUData

async def process_imu(data: IMUData) -> Optional[dict]:
    # Process and return result
    pass
```

## Next Steps

- [Protocol Selection](protocol-selection.md) - Choose the right protocol
- [Performance Optimization](performance.md) - Optimize performance
- [Troubleshooting](troubleshooting.md) - Common issues


# Python SDK Overview

The ARVOS Python SDK provides a complete toolkit for receiving and processing sensor data from the ARVOS iOS app.

## Architecture

### Base Server Class

All protocol servers inherit from `BaseArvosServer`:

```python
from arvos.servers import BaseArvosServer

class MyServer(BaseArvosServer):
    async def start(self):
        # Start server
        pass
    
    async def stop(self):
        # Stop server
        pass
    
    def get_connection_url(self) -> str:
        return "my-protocol://..."
    
    def get_protocol_name(self) -> str:
        return "My Protocol"
```

### Unified Callback Interface

All servers share the same callback interface:

```python
server.on_connect = lambda client_id: print(f"Connected: {client_id}")
server.on_imu = lambda data: print(f"IMU: {data}")
server.on_camera = lambda frame: print(f"Camera: {frame}")
# ... etc
```

### Protocol Servers

- `ArvosServer` - WebSocket (default)
- `GRPCArvosServer` - gRPC
- `MQTTArvosServer` - MQTT
- `HTTPArvosServer` - HTTP/REST
- `MCAPStreamServer` - MCAP Stream
- `QUICArvosServer` - QUIC/HTTP3

### Client Class

For connecting to existing servers:

```python
from arvos import ArvosClient

client = ArvosClient()
await client.connect("ws://192.168.1.100:9090")
await client.run()
```

## Data Types

All sensor data is provided as typed dataclasses:

- `IMUData` - IMU sensor data
- `GPSData` - GPS location data
- `PoseData` - ARKit pose data
- `CameraFrame` - Camera frame data
- `DepthFrame` - Depth/LiDAR data
- `WatchIMUData` - Apple Watch IMU
- `WatchAttitudeData` - Apple Watch attitude
- `WatchMotionActivityData` - Watch motion activity

[→ Complete Data Types Reference](../api/data-types.md)

## Features

### Multi-Protocol Support
- 7 streaming protocols
- Unified API across all protocols
- Easy protocol switching

### Type Safety
- Typed dataclasses
- Type hints throughout
- IDE autocomplete support

### Async/Await
- Fully async API
- Non-blocking I/O
- High performance

### Extensible
- Easy to add new protocols
- Custom callback handlers
- Plugin architecture

## Next Steps

- [Installation](installation.md) - Install the SDK
- [Quick Start](quick-start.md) - Your first server
- [API Reference](../api/python-sdk.md) - Complete API docs


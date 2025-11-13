# gRPC Protocol

High-performance protocol using Protocol Buffers - ideal for research applications.

## Overview

gRPC is an industry-standard RPC framework that provides:
- ✅ Very high performance
- ✅ Protocol Buffers (efficient binary format)
- ✅ Bidirectional streaming
- ✅ Type-safe interfaces

## Default Port

**50051**

## Requirements

### iOS
- iOS 18.0 or higher
- gRPC support built-in

### Python
```bash
pip install grpcio grpcio-tools protobuf
```

## Quick Start

### Python Server

```python
import asyncio
from arvos.servers import GRPCArvosServer

async def main():
    server = GRPCArvosServer(host="0.0.0.0", port=50051)
    
    server.on_imu = lambda data: print(f"IMU: {data}")
    await server.start()

asyncio.run(main())
```

### iOS App

1. Open ARVOS app
2. Select **gRPC** protocol
3. Enter server IP and port 50051
4. Connect!

## Features

### Protocol Buffers
- Efficient binary serialization
- Type-safe message definitions
- Smaller payload sizes
- Faster encoding/decoding

### Bidirectional Streaming
- iPhone streams sensor data
- Server can send control messages
- Full duplex communication

### High Performance
- Lower latency than WebSocket
- Higher throughput
- Better CPU efficiency

## Message Format

gRPC uses Protocol Buffers defined in `sensors.proto`:

```protobuf
message SensorMessage {
    uint64 timestamp_ns = 1;
    oneof data {
        IMUData imu = 11;
        GPSData gps = 12;
        PoseData pose = 13;
        // ... etc
    }
    bytes binary_data = 100;
}
```

## Use Cases

- High-performance research applications
- Large-scale data collection
- Real-time processing pipelines
- Production deployments

## Advantages

- ✅ Very high performance
- ✅ Efficient binary format
- ✅ Industry standard
- ✅ Type-safe

## Limitations

- ⚠️ Requires iOS 18+
- ⚠️ More complex setup
- ⚠️ Protocol Buffers learning curve

## Example

See [gRPC Example](../examples/protocols.md#grpc)

## Next Steps

- [Protocol Comparison](comparison.md)
- [WebSocket Protocol](websocket.md) - Simpler alternative


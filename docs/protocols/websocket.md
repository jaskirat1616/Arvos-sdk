# WebSocket Protocol

The default protocol for ARVOS - works everywhere, bidirectional, and easy to use.

## Overview

WebSocket is the default protocol for ARVOS. It provides:
- ✅ Bidirectional communication
- ✅ Works on all networks
- ✅ Good performance
- ✅ Easy to debug

## Default Port

**9090**

## Quick Start

### Python Server

```python
import asyncio
from arvos import ArvosServer

async def main():
    server = ArvosServer(port=9090)
    server.print_qr_code()
    
    server.on_imu = lambda data: print(f"IMU: {data}")
    await server.start()

asyncio.run(main())
```

### iOS App

1. Open ARVOS app
2. Select **WebSocket** protocol (default)
3. Enter server IP and port 9090
4. Connect!

## Features

### Bidirectional Communication
- iPhone sends sensor data
- Server can send control commands
- Real-time feedback

### Automatic Reconnection
- Handles network interruptions
- Automatic reconnection logic
- Message queuing during disconnects

### Message Format

**JSON Messages** (IMU, GPS, Pose):
```json
{
  "type": "imu",
  "timestampNs": 1700000000000,
  "angularVelocity": [0.01, -0.02, 0.005],
  "linearAcceleration": [0.1, 0.0, -0.01]
}
```

**Binary Messages** (Camera, Depth):
```
[Header Size (4 bytes)][JSON Header][Binary Data]
```

## Use Cases

- General purpose streaming
- First-time users
- Most research applications
- Development and testing

## Advantages

- ✅ Works everywhere
- ✅ No special setup
- ✅ Good performance
- ✅ Easy debugging

## Limitations

- ⚠️ Not the fastest (use gRPC for maximum performance)
- ⚠️ Single connection per client

## Example

See [Basic Server Example](../examples/basic-server.md)

## Next Steps

- [Protocol Comparison](comparison.md)
- [gRPC Protocol](grpc.md) - Higher performance alternative


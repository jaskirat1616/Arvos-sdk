# HTTP/REST Protocol

Simple HTTP POST requests - perfect for webhook integrations and simple scripts.

## Overview

HTTP/REST provides:
- ✅ Simple POST requests
- ✅ Easy webhook integration
- ✅ Works with any HTTP client
- ✅ Easy debugging

## Default Port

**8080**

## Quick Start

### Python Server

```python
import asyncio
from arvos.servers import HTTPArvosServer

async def main():
    server = HTTPArvosServer(port=8080)
    
    server.on_imu = lambda data: print(f"IMU: {data}")
    await server.start()

asyncio.run(main())
```

### iOS App

1. Open ARVOS app
2. Select **HTTP/REST** protocol
3. Enter server IP and port 8080
4. Connect!

## Endpoints

### Health Check
```
GET /api/health
```

### Telemetry Data
```
POST /api/telemetry
Content-Type: application/json

{
  "sensorType": "imu",
  "timestampNs": 1700000000000,
  ...
}
```

### Binary Data
```
POST /api/binary
Content-Type: application/octet-stream

[Binary data]
```

## Features

### Simple Integration
- Standard HTTP requests
- Works with any HTTP client
- Easy to test with curl

### Webhook Support
- Integrate with web services
- Cloud function triggers
- API gateway compatibility

### Easy Debugging
- Use browser dev tools
- Standard HTTP debugging
- Clear request/response

## Use Cases

- Webhook integrations
- Cloud functions
- Simple scripts
- REST API compatibility
- Testing and debugging

## Advantages

- ✅ Very simple
- ✅ No special setup
- ✅ Easy debugging
- ✅ Universal compatibility

## Limitations

- ⚠️ Not bidirectional (no server→client)
- ⚠️ Higher overhead per request
- ⚠️ Not ideal for high-frequency data

## Example

See [HTTP Example](../examples/protocols.md#http)

## Next Steps

- [Protocol Comparison](comparison.md)
- [WebSocket Protocol](websocket.md) - Bidirectional alternative


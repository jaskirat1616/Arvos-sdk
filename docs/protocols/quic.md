# QUIC/HTTP3 Protocol

Ultra-low latency protocol - perfect for real-time applications and unstable networks.

## Overview

QUIC/HTTP3 provides:
- ✅ Ultra-low latency
- ✅ Better performance on unstable networks
- ✅ Built-in encryption (TLS)
- ✅ Connection migration

## Default Port

**4433**

## Requirements

### iOS
- iOS 15.0 or higher
- HTTP/3 support built-in

### Python
```bash
pip install aioquic
```

### TLS Certificates

QUIC requires TLS certificates. For local development:

```bash
openssl req -x509 -newkey rsa:2048 \
    -keyout /tmp/arvos-quic.key \
    -out /tmp/arvos-quic-cert.pem \
    -days 365 -nodes
```

## Quick Start

### Python Server

```python
import asyncio
from arvos.servers import QUICArvosServer

async def main():
    server = QUICArvosServer(
        host="0.0.0.0",
        port=4433,
        certfile="/tmp/arvos-quic-cert.pem",
        keyfile="/tmp/arvos-quic.key"
    )
    
    server.on_imu = lambda data: print(f"IMU: {data}")
    await server.start()

asyncio.run(main())
```

### iOS App

1. Open ARVOS app
2. Select **QUIC/HTTP3** protocol
3. Enter server IP and port 4433
4. Connect!

**Note:** For local testing, you may need to install the self-signed certificate on your iPhone.

## Features

### Ultra-Low Latency
- Faster connection establishment
- Reduced head-of-line blocking
- Better on mobile networks

### Network Resilience
- Better performance on packet loss
- Connection migration
- Multiplexing without head-of-line blocking

### Built-in Security
- TLS 1.3 encryption
- No separate TLS handshake
- Secure by default

## Use Cases

- Real-time applications
- Mobile network scenarios
- Unstable network conditions
- Low-latency requirements

## Advantages

- ✅ Ultra-low latency
- ✅ Better on unstable networks
- ✅ Built-in encryption
- ✅ Future-proof protocol

## Limitations

- ⚠️ Requires TLS certificates
- ⚠️ More complex setup
- ⚠️ Requires aioquic library
- ⚠️ Certificate management

## Example

See [QUIC Example](../examples/protocols.md#quic)

## Next Steps

- [Protocol Comparison](comparison.md)
- [gRPC Protocol](grpc.md) - High performance alternative


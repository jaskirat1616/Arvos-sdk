# Protocol Examples

Examples for all 7 streaming protocols.

## WebSocket

Default protocol - works everywhere.

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

## gRPC

High-performance protocol.

```python
import asyncio
from arvos.servers import GRPCArvosServer

async def main():
    server = GRPCArvosServer(host="0.0.0.0", port=50051)
    
    server.on_imu = lambda data: print(f"IMU: {data}")
    await server.start()

asyncio.run(main())
```

## MQTT

IoT-friendly protocol.

**First, start broker:**
```bash
mosquitto -c mosquitto.conf
```

**Then run server:**
```python
import asyncio
from arvos.servers import MQTTArvosServer

async def main():
    server = MQTTArvosServer(host="localhost", port=1883)
    
    server.on_imu = lambda data: print(f"IMU: {data}")
    await server.start()

asyncio.run(main())
```

## HTTP/REST

Simple HTTP POST requests.

```python
import asyncio
from arvos.servers import HTTPArvosServer

async def main():
    server = HTTPArvosServer(port=8080)
    
    server.on_imu = lambda data: print(f"IMU: {data}")
    await server.start()

asyncio.run(main())
```

## Bluetooth LE

No Wi-Fi needed.

```python
import asyncio
from arvos.examples.ble_receiver import main

asyncio.run(main())
```

## MCAP Stream

Robotics standard format.

```python
import asyncio
from arvos.servers import MCAPStreamServer

async def main():
    server = MCAPStreamServer(
        host="0.0.0.0",
        port=17500,
        output_file="output.mcap"
    )
    
    server.on_imu = lambda data: print(f"IMU: {data}")
    await server.start()

asyncio.run(main())
```

## QUIC/HTTP3

Ultra-low latency protocol.

**First, generate certificates:**
```bash
openssl req -x509 -newkey rsa:2048 \
    -keyout /tmp/arvos-quic.key \
    -out /tmp/arvos-quic-cert.pem \
    -days 365 -nodes
```

**Then run server:**
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

## Next Steps

- [Protocol Comparison](../protocols/comparison.md) - Choose the right protocol
- [Basic Server](basic-server.md) - Simple example
- [Visualization](visualization.md) - Visual examples


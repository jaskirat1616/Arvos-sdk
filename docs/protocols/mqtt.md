# MQTT Protocol

IoT-friendly protocol with multi-subscriber support - perfect for distributed systems.

## Overview

MQTT (Message Queuing Telemetry Transport) provides:
- ✅ Multi-subscriber support
- ✅ IoT-friendly architecture
- ✅ Broker-based messaging
- ✅ Quality of Service levels

## Default Port

**1883** (broker port)

## Requirements

### MQTT Broker

Install and start Mosquitto:

```bash
# macOS
brew install mosquitto
mosquitto -c mosquitto.conf

# Linux
sudo apt-get install mosquitto
mosquitto -c mosquitto.conf
```

### Python
```bash
pip install paho-mqtt
```

### Broker Configuration

Create `mosquitto.conf`:

```conf
listener 1883 0.0.0.0
allow_anonymous true
```

## Quick Start

### Start Broker

```bash
mosquitto -c mosquitto.conf
```

### Python Server

```python
import asyncio
from arvos.servers import MQTTArvosServer

async def main():
    server = MQTTArvosServer(host="localhost", port=1883)
    
    server.on_imu = lambda data: print(f"IMU: {data}")
    await server.start()

asyncio.run(main())
```

### iOS App

1. Open ARVOS app
2. Select **MQTT** protocol
3. Enter broker IP and port 1883
4. Connect!

## Features

### Multi-Subscriber
- Multiple Python servers can subscribe
- Same data to all subscribers
- Distributed processing

### Topics

- `arvos/telemetry` - JSON sensor data
- `arvos/binary` - Binary data (camera, depth)

### Quality of Service
- QoS 0: At most once
- QoS 1: At least once
- QoS 2: Exactly once

## Use Cases

- IoT deployments
- Multiple receivers
- Distributed systems
- Broker-based architectures

## Advantages

- ✅ Multi-subscriber support
- ✅ IoT-friendly
- ✅ Reliable delivery (QoS)
- ✅ Standard protocol

## Limitations

- ⚠️ Requires broker setup
- ⚠️ Additional infrastructure
- ⚠️ Broker can be bottleneck

## Example

See [MQTT Example](../examples/protocols.md#mqtt)

## Next Steps

- [Protocol Comparison](comparison.md)
- [HTTP/REST Protocol](http.md) - Simpler alternative


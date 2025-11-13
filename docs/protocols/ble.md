# Bluetooth LE Protocol

Low-bandwidth, cable-free protocol - perfect when Wi-Fi isn't available.

## Overview

Bluetooth Low Energy (BLE) provides:
- ✅ No Wi-Fi needed
- ✅ Low power consumption
- ✅ Cable-free operation
- ✅ Direct device-to-device

## Requirements

### Python
```bash
pip install bleak
```

### Permissions
- Bluetooth enabled on both devices
- Bluetooth permissions granted

## Quick Start

### Python Receiver

```python
import asyncio
from arvos.examples.ble_receiver import main

asyncio.run(main())
```

### iOS App

1. Open ARVOS app
2. Select **Bluetooth LE** protocol
3. App automatically starts advertising
4. Python script discovers and connects

## Features

### No Wi-Fi Required
- Direct Bluetooth connection
- Works anywhere
- No network setup

### Low Power
- BLE is power-efficient
- Longer battery life
- Suitable for mobile use

### Automatic Discovery
- Python script scans for device
- Connects automatically
- No manual pairing needed

## Limitations

### Low Bandwidth
- **Telemetry only** (IMU, GPS, Pose)
- **No camera/depth** (too large for BLE)
- Maximum ~20 KB/s throughput

### Range
- Limited to ~10 meters
- Line of sight helps
- Walls reduce range

## Use Cases

- Field deployments without Wi-Fi
- Low power requirements
- Telemetry-only applications
- Cable-free setups

## Data Format

BLE uses length-prefixed messages:
```
[Length (2 bytes)][JSON Data]
```

Messages are automatically chunked and reassembled.

## Example

See [BLE Example](../examples/protocols.md#ble)

## Next Steps

- [Protocol Comparison](comparison.md)
- [WebSocket Protocol](websocket.md) - Higher bandwidth alternative


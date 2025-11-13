# Protocols Overview

ARVOS supports 7 streaming protocols, each optimized for different use cases.

## Protocol Comparison

| Protocol | Latency | Throughput | Bidirectional | Multi-Client | iOS Version | Setup |
|----------|---------|------------|---------------|--------------|-------------|-------|
| **WebSocket** | Low | High | ✅ | ✅ | 16+ | Low |
| **gRPC** | Very Low | Very High | ✅ | ✅ | 18+ | Medium |
| **MQTT** | Medium | Medium | ✅ | ✅ | 16+ | Medium |
| **HTTP/REST** | Medium | Medium | ❌ | ✅ | 16+ | Low |
| **Bluetooth LE** | Low | Low | ✅ | ❌ | 16+ | Low |
| **MCAP Stream** | Low | High | ✅ | ✅ | 16+ | Low |
| **QUIC/HTTP3** | Very Low | Very High | ✅ | ✅ | 15+ | High |

## Quick Selection Guide

**Need general purpose?** → WebSocket  
**Need high performance?** → gRPC  
**Need multiple subscribers?** → MQTT  
**Need simple integration?** → HTTP/REST  
**No Wi-Fi available?** → Bluetooth LE  
**Robotics research?** → MCAP Stream  
**Ultra-low latency?** → QUIC/HTTP3

## Protocol Details

### WebSocket
- Default protocol
- Works everywhere
- Bidirectional communication
- [→ WebSocket Guide](websocket.md)

### gRPC
- Industry standard
- Protocol Buffers
- High performance
- [→ gRPC Guide](grpc.md)

### MQTT
- IoT-friendly
- Multi-subscriber
- Broker-based
- [→ MQTT Guide](mqtt.md)

### HTTP/REST
- Simple POST requests
- Webhook integration
- Easy debugging
- [→ HTTP Guide](http.md)

### Bluetooth LE
- No Wi-Fi needed
- Low power
- Telemetry only
- [→ BLE Guide](ble.md)

### MCAP Stream
- Robotics standard
- Foxglove compatible
- Streaming format
- [→ MCAP Guide](mcap.md)

### QUIC/HTTP3
- Ultra-low latency
- Better on unstable networks
- TLS required
- [→ QUIC Guide](quic.md)

## Next Steps

- [Protocol Comparison](comparison.md) - Detailed comparison
- [Protocol Selection Guide](../guides/protocol-selection.md) - Choose the right one
- Individual protocol guides for setup instructions


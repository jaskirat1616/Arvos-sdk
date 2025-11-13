# Protocol Selection Guide

Choose the right streaming protocol for your use case.

## Decision Tree

### Step 1: Network Available?

**No Wi-Fi Available?**
→ Use **Bluetooth LE**

**Wi-Fi Available?**
→ Continue to Step 2

### Step 2: Performance Requirements

**Need Maximum Performance?**
→ Use **gRPC** (iOS 18+) or **QUIC/HTTP3** (iOS 15+)

**Standard Performance OK?**
→ Continue to Step 3

### Step 3: Use Case

**Multiple Subscribers Needed?**
→ Use **MQTT**

**Simple Integration / Webhooks?**
→ Use **HTTP/REST**

**Robotics Research / Foxglove?**
→ Use **MCAP Stream**

**General Purpose?**
→ Use **WebSocket** (default)

## Detailed Recommendations

### Use WebSocket When:

- ✅ First-time users
- ✅ General purpose streaming
- ✅ Need bidirectional communication
- ✅ Want simple setup
- ✅ Standard performance is sufficient

**Example:** Most research applications, development, testing

### Use gRPC When:

- ✅ Need maximum performance
- ✅ iOS 18+ available
- ✅ High-throughput requirements
- ✅ Production deployments
- ✅ Protocol Buffers familiarity

**Example:** Large-scale data collection, real-time processing

### Use MQTT When:

- ✅ Multiple subscribers needed
- ✅ IoT deployment
- ✅ Broker-based architecture
- ✅ Distributed processing
- ✅ Quality of Service needed

**Example:** Multiple receivers, cloud processing, IoT systems

### Use HTTP/REST When:

- ✅ Simple webhook integration
- ✅ REST API compatibility
- ✅ Easy debugging needed
- ✅ Cloud function triggers
- ✅ Simple scripts

**Example:** Web services, cloud functions, simple integrations

### Use Bluetooth LE When:

- ✅ No Wi-Fi available
- ✅ Low power requirements
- ✅ Telemetry-only use case
- ✅ Direct device connection
- ✅ Cable-free operation

**Example:** Field deployments, low-power scenarios, telemetry only

### Use MCAP Stream When:

- ✅ Robotics research
- ✅ Foxglove Studio integration
- ✅ Standardized format needed
- ✅ Tool compatibility required
- ✅ Rich metadata needed

**Example:** Robotics research, Foxglove visualization, standardized data

### Use QUIC/HTTP3 When:

- ✅ Ultra-low latency required
- ✅ Unstable network conditions
- ✅ Mobile network scenarios
- ✅ Real-time applications
- ✅ iOS 15+ available

**Example:** Real-time control, mobile networks, unstable connections

## Performance Comparison

### Latency (Lower is Better)

```
QUIC/HTTP3 ≈ gRPC < WebSocket ≈ MCAP ≈ BLE < MQTT ≈ HTTP
```

### Throughput (Higher is Better)

```
gRPC ≈ QUIC/HTTP3 > WebSocket ≈ MCAP > MQTT ≈ HTTP > BLE
```

### Setup Complexity (Lower is Better)

```
WebSocket ≈ HTTP ≈ BLE ≈ MCAP < MQTT ≈ gRPC < QUIC/HTTP3
```

## Quick Reference

| Use Case | Recommended Protocol |
|----------|---------------------|
| First-time user | WebSocket |
| Maximum performance | gRPC |
| Multiple subscribers | MQTT |
| Simple integration | HTTP/REST |
| No Wi-Fi | Bluetooth LE |
| Robotics research | MCAP Stream |
| Ultra-low latency | QUIC/HTTP3 |

## Next Steps

- [Protocol Comparison](../protocols/comparison.md) - Detailed comparison
- [Protocol Guides](../protocols/overview.md) - Setup instructions
- [Troubleshooting](troubleshooting.md) - Common issues


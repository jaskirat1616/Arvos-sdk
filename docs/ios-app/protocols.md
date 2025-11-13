# Protocol Selection in iOS App

How to select and configure streaming protocols in the ARVOS iOS app.

## Protocol Picker

The app includes a protocol picker in the connection sheet:

1. Open **"CONNECT TO SERVER"**
2. Find the **"PROTOCOL"** section
3. Select your desired protocol from the segmented control

## Available Protocols

### WebSocket (Default)

**When to use:**
- General purpose streaming
- First time users
- Most use cases

**Configuration:**
- Host: Your computer's IP address
- Port: 9090 (default)

### gRPC

**When to use:**
- High-performance research applications
- Need Protocol Buffers efficiency
- iOS 18+ available

**Configuration:**
- Host: Your computer's IP address
- Port: 50051 (default)
- Note: Requires iOS 18+

### MQTT

**When to use:**
- Multiple subscribers needed
- IoT deployments
- Broker-based architecture

**Configuration:**
- Host: MQTT broker IP address
- Port: 1883 (default)
- Note: Requires MQTT broker running

### HTTP/REST

**When to use:**
- Simple webhook integrations
- REST API compatibility
- Easy debugging

**Configuration:**
- Host: Your computer's IP address
- Port: 8080 (default)

### Bluetooth LE

**When to use:**
- No Wi-Fi available
- Low power requirements
- Telemetry-only use cases

**Configuration:**
- No host/port needed
- App automatically advertises
- Python script discovers device

### MCAP Stream

**When to use:**
- Robotics research
- Foxglove Studio integration
- Standardized data format

**Configuration:**
- Host: Your computer's IP address
- Port: 17500 (default)

### QUIC/HTTP3

**When to use:**
- Ultra-low latency requirements
- Unstable network conditions
- Mobile network scenarios

**Configuration:**
- Host: Your computer's IP address
- Port: 4433 (default)
- Note: Requires TLS certificates

## Protocol-Specific Settings

Some protocols have additional settings:

### MQTT
- **Client ID**: Auto-generated or custom
- **Topics**: Telemetry and binary topics

### Bluetooth LE
- **Device Name**: Your iPhone's name (auto-detected)

### QUIC/HTTP3
- **TLS**: Automatically enabled (required)

## Connection Process

1. **Select Protocol** - Choose from protocol picker
2. **Enter Host** - Computer's IP address (or scan QR code)
3. **Enter Port** - Protocol default port (auto-filled)
4. **Tap CONNECT** - Establish connection
5. **Tap START** - Begin streaming

## Troubleshooting

### Protocol Not Available

**gRPC:**
- Requires iOS 18+
- Update iOS if needed

**QUIC/HTTP3:**
- Requires iOS 15+
- Update iOS if needed

### Connection Fails

- Check protocol matches server
- Verify port number
- Ensure server is running
- Check firewall settings

[→ Full Troubleshooting Guide](../guides/troubleshooting.md)

## Next Steps

- [Protocol Comparison](../protocols/comparison.md) - Choose the right protocol
- [Usage Guide](usage.md) - Complete app usage guide
- [Examples](../examples/protocols.md) - Protocol examples


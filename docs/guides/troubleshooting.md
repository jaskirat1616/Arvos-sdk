# Troubleshooting Guide

Common issues and solutions for ARVOS.

## Connection Issues

### Can't Connect from iPhone

**Symptoms:**
- Connection fails immediately
- "Connection Failed" error
- Timeout errors

**Solutions:**

1. **Check Network:**
   - Ensure both devices on same Wi-Fi
   - Try pinging: `ping <iphone-ip>`
   - Verify network connectivity

2. **Check Firewall:**
   - macOS: System Settings → Firewall → Allow Python
   - Linux: `sudo ufw allow <port>`
   - Windows: Windows Defender → Allow Python

3. **Check Port:**
   ```bash
   # Test if port is open
   nc -l 9090
   ```

4. **Verify Protocol:**
   - Ensure protocol matches server
   - Check port number
   - Verify server is running

### QR Code Not Scanning

**Solutions:**
- Increase terminal font size
- Use manual IP entry
- Check QR code contains correct IP
- Ensure good lighting

### Protocol-Specific Connection Issues

#### gRPC
- **Requires iOS 18+** - Update iOS if needed
- Check port 50051 is open
- Verify protobuf code generated

#### MQTT
- **Broker must be running:** `mosquitto -c mosquitto.conf`
- Check broker listening on all interfaces (not just localhost)
- Verify broker port (default 1883)

#### HTTP/REST
- Use actual LAN IP (not 0.0.0.0)
- Check App Transport Security settings
- Verify firewall allows port 8080

#### Bluetooth LE
- Enable Bluetooth on both devices
- Ensure app is advertising (BLE toggle on)
- Check Python script has Bluetooth permissions
- Verify devices are within range (~10m)

#### QUIC/HTTP3
- Generate TLS certificates
- Install aioquic: `pip install aioquic`
- For local testing, install self-signed certificate on iPhone
- Verify port 4433 is not blocked

## Data Issues

### No Data Received

**Symptoms:**
- Connected but no data
- Callbacks not firing
- Empty statistics

**Solutions:**

1. **Check Streaming:**
   - Ensure "START STREAMING" tapped in app
   - Verify streaming mode selected
   - Check sensor rates not zero

2. **Check Callbacks:**
   - Verify callbacks registered
   - Check callback function signatures
   - Ensure async/sync matches

3. **Check Protocol:**
   - Verify protocol matches server
   - Check server is receiving data
   - Review server logs

### Incomplete Data

**Symptoms:**
- Missing sensor types
- Partial messages
- Corrupted data

**Solutions:**

1. **Check Streaming Mode:**
   - Verify mode includes desired sensors
   - Check sensor availability on device
   - Review mode configuration

2. **Check Network:**
   - Network instability can cause data loss
   - Try different protocol
   - Check signal strength

3. **Check Bandwidth:**
   - High-frequency data may overwhelm network
   - Reduce sensor rates
   - Use lower quality settings

## Performance Issues

### High Latency

**Symptoms:**
- Delayed data arrival
- Lag in visualization
- Stale timestamps

**Solutions:**

1. **Network:**
   - Use wired connection for computer
   - Optimize Wi-Fi settings
   - Try QUIC/HTTP3 protocol

2. **Protocol:**
   - Use gRPC for maximum performance
   - Avoid HTTP/REST for high-frequency data
   - Consider QUIC/HTTP3

3. **Processing:**
   - Process data asynchronously
   - Don't block in callbacks
   - Use batch processing

### Dropped Frames

**Symptoms:**
- Missing camera frames
- Incomplete point clouds
- Gaps in data

**Solutions:**

1. **Reduce Rates:**
   - Lower camera frame rate
   - Reduce sensor frequencies
   - Disable unused sensors

2. **Network:**
   - Improve Wi-Fi signal
   - Use wired connection
   - Try different protocol

3. **Processing:**
   - Process frames faster
   - Skip some frames if needed
   - Use async processing

### High CPU Usage

**Solutions:**

1. **Optimize Code:**
   - Use NumPy vectorized operations
   - Process asynchronously
   - Batch operations

2. **Reduce Processing:**
   - Skip unnecessary processing
   - Downsample data
   - Use lower quality

3. **Protocol:**
   - Use efficient protocols (gRPC)
   - Avoid HTTP for high-frequency data

## Protocol-Specific Issues

### MQTT: Broker Issues

**Problem:** "Connection refused"

**Solution:**
```bash
# Check broker is running
ps aux | grep mosquitto

# Check broker config
cat mosquitto.conf
# Should have: listener 1883 0.0.0.0
```

### gRPC: Version Issues

**Problem:** "Method not implemented"

**Solution:**
- Regenerate protobuf code
- Check grpcio version compatibility
- Verify iOS 18+ on device

### QUIC/HTTP3: Certificate Issues

**Problem:** "Certificate verification failed"

**Solution:**
- Generate valid certificates
- Install certificate on iPhone
- For local testing, trust self-signed cert

### BLE: Connection Issues

**Problem:** "Device not found"

**Solution:**
- Ensure app is advertising
- Check Bluetooth is enabled
- Verify devices are nearby
- Restart Bluetooth on both devices

## Getting Help

### Check Documentation
- [Protocol Guides](../protocols/overview.md)
- [API Reference](../api/python-sdk.md)
- [Examples](../examples/overview.md)

### Report Issues
- GitHub Issues: [arvos-sdk/issues](https://github.com/jaskirat1616/arvos-sdk/issues)
- Include:
  - Protocol used
  - Error messages
  - Network setup
  - Device information

## Next Steps

- [Protocol Selection](protocol-selection.md) - Choose the right protocol
- [Performance Optimization](performance.md) - Optimize your setup
- [Best Practices](best-practices.md) - Recommended practices


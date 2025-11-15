# ARVOS Troubleshooting

Common issues and how to fix them.

## Can't Connect - "Connection Failed" or "Offline" Error

### Check 1: Is the server running?

Open Terminal and run:
```bash
cd arvos-sdk
python3 examples/basic_server.py
```

You should see: `Server started on...`

### Check 2: Are you on the same WiFi?

Both your iPhone and computer must be on the **same WiFi network**.

- iPhone: Settings → WiFi → check network name
- Mac: Click WiFi icon in menu bar → check network name

They must match exactly!

### Check 3: Find your computer's IP address

**On Mac:**
```bash
ifconfig en0 | grep "inet " | awk '{print $2}'
```

**On Windows:**
```bash
ipconfig
```

Look for an IP like `192.168.1.100` or `10.0.0.5`

Use this IP in the ARVOS app.

---

## University or School WiFi Not Working

School WiFi often blocks devices from talking to each other.

### Solution: Use USB Connection

1. **Connect iPhone to Mac with cable**
2. **iPhone**: Settings → Personal Hotspot → Turn ON
3. **In ARVOS app**: Use `localhost` or `127.0.0.1` as the host

This works because USB creates a direct connection!

### Alternative: Use Phone Hotspot

1. **iPhone**: Settings → Personal Hotspot → Turn ON
2. **Mac**: Connect to your iPhone's WiFi network
3. **In ARVOS app**: Use the IP shown in Personal Hotspot settings

---

## Firewall Blocking Connection

### On Mac:

1. System Preferences → Security & Privacy → Firewall
2. Click "Firewall Options"
3. Find Python or your terminal app
4. Set to "Allow incoming connections"

### On Windows:

1. Windows Security → Firewall
2. Allow Python through firewall

---

## Slow or Lagging Stream

### Lower the frame rate:

In ARVOS app:
- Camera: Try 15 FPS instead of 30 FPS
- Reduce resolution

### Use wired connection:

USB is much faster than WiFi!

---

## MCAP Server Issues

If you're using the MCAP protocol and getting timeouts:

### Make sure you're using the HTTP server:

```bash
python3 examples/mcap_http_server.py
```

NOT the websocket version (`mcap_stream_server.py`)

### Check the port:

MCAP HTTP uses port **17500** by default.

In ARVOS app:
- Protocol: MCAP Stream
- Port: 17500

---

## Watch App Not Connecting

### Check if watch is paired:

iPhone: Watch app → My Watch → check if watch is connected

### Make sure both apps are running:

1. Open ARVOS on **iPhone** first
2. Then open ARVOS on **Watch**
3. Watch should show "Connected" in green

---

## Still Not Working?

### 1. Restart everything:

- Close ARVOS app on iPhone/Watch
- Stop the server (Ctrl+C)
- Start server again
- Open ARVOS app again

### 2. Check the basics:

- [ ] Server is running
- [ ] Same WiFi network (or USB connected)
- [ ] Correct IP address
- [ ] Firewall allows connection
- [ ] Correct port number

### 3. Try the simplest setup first:

```bash
# Use the basic WebSocket server
python3 examples/basic_server.py

# In ARVOS app:
# Protocol: WebSocket
# Host: your-computer-ip
# Port: 9090
```

---

## Need More Help?

- Check the examples folder for working code
- Read the README for each protocol
- Try the web viewer (no setup needed!)

---

## Quick Reference: Default Ports

| Protocol | Port |
|----------|------|
| WebSocket | 9090 |
| gRPC | 50051 |
| MQTT | 1883 |
| HTTP | 8080 |
| MCAP Stream | 17500 |
| QUIC | 4433 |

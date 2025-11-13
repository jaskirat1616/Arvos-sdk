# Quick Start

Get started with ARVOS in under 5 minutes!

## Option 1: Web Viewer (Fastest - 30 seconds)

No Python installation required - works in any browser:

```bash
cd arvos-sdk/web-viewer
./start-viewer.sh    # Mac/Linux
# OR
start-viewer.bat     # Windows
```

Then:
1. Scan the QR code with your iPhone
2. Open the ARVOS app
3. Tap "CONNECT TO SERVER"
4. Tap "START" to stream

[→ Full Web Viewer Guide](../web-viewer/quick-start.md)

---

## Option 2: Python SDK (5 minutes)

### Step 1: Install the SDK

```bash
pip install arvos-sdk
```

Or from source:
```bash
git clone https://github.com/jaskirat1616/arvos-sdk.git
cd arvos-sdk
pip install -e .
```

### Step 2: Create a Simple Server

Create a file `my_server.py`:

```python
import asyncio
from arvos import ArvosServer

async def main():
    server = ArvosServer(port=9090)
    
    # Show QR code for easy connection
    server.print_qr_code()
    
    # Define what to do when data arrives
    async def on_imu(data):
        print(f"📊 IMU: accel={data.linear_acceleration}")
    
    async def on_camera(frame):
        print(f"📷 Camera: {frame.width}x{frame.height}, {frame.size_kb:.1f} KB")
    
    # Register callbacks
    server.on_imu = on_imu
    server.on_camera = on_camera
    
    # Start server
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Run the Server

```bash
python my_server.py
```

### Step 4: Connect from iPhone

1. Open the **ARVOS** app on your iPhone
2. Tap **"CONNECT TO SERVER"**
3. Select **WebSocket** protocol (default)
4. Scan the QR code or enter your computer's IP address
5. Tap **"CONNECT"**
6. Tap **"START STREAMING"**

You should see sensor data appearing in your terminal!

---

## What's Next?

- [Installation Guide](installation.md) - Detailed installation instructions
- [First Connection](first-connection.md) - Troubleshooting your first connection
- [Protocol Examples](../examples/protocols.md) - Try different protocols
- [API Reference](../api/python-sdk.md) - Explore the full API

---

## Common Issues

**Can't connect?**
- Ensure both devices are on the same Wi-Fi network
- Check firewall settings (allow port 9090)
- Try the Web Viewer instead

**QR code not scanning?**
- Increase terminal font size
- Enter IP address manually in the app

[→ Full Troubleshooting Guide](../guides/troubleshooting.md)


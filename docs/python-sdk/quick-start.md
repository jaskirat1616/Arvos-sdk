# Python SDK Quick Start

Create your first ARVOS server in 5 minutes.

## Basic Server

Create a file `my_server.py`:

```python
import asyncio
from arvos import ArvosServer

async def main():
    # Create server
    server = ArvosServer(port=9090)
    
    # Show QR code for easy connection
    server.print_qr_code()
    
    # Define callbacks
    async def on_connect(client_id: str):
        print(f"✅ Client connected: {client_id}")
    
    async def on_imu(data):
        print(f"📊 IMU: accel={data.linear_acceleration}")
    
    async def on_camera(frame):
        print(f"📷 Camera: {frame.width}x{frame.height}")
    
    # Register callbacks
    server.on_connect = on_connect
    server.on_imu = on_imu
    server.on_camera = on_camera
    
    # Start server
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
```

## Run the Server

```bash
python my_server.py
```

## Connect from iPhone

1. Open ARVOS app
2. Tap "CONNECT TO SERVER"
3. Scan QR code or enter IP
4. Tap "START STREAMING"

Data should start flowing!

## Next Steps

- [Protocol Examples](../examples/protocols.md) - Try different protocols
- [API Reference](../api/python-sdk.md) - Explore the API
- [Best Practices](../guides/best-practices.md) - Optimize your code


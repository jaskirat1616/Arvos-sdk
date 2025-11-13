# Clients API

Client classes for connecting to ARVOS servers.

## ArvosClient

WebSocket client for connecting to ARVOS servers.

```python
from arvos import ArvosClient

client = ArvosClient()
```

### Methods

#### `connect(uri: str, timeout: float = 10.0)`
Connect to an ARVOS server.

**Parameters:**
- `uri` (str): WebSocket URI (e.g., "ws://192.168.1.100:9090")
- `timeout` (float): Connection timeout in seconds (default: 10.0)

**Example:**
```python
await client.connect("ws://192.168.1.100:9090")
```

#### `disconnect()`
Disconnect from server.

**Example:**
```python
await client.disconnect()
```

#### `run()`
Main receive loop - call after connect().

**Example:**
```python
await client.run()
```

### Callbacks

Same callback interface as `ArvosServer`:

```python
client.on_connect = lambda: print("Connected")
client.on_imu = lambda data: print(f"IMU: {data}")
client.on_camera = lambda frame: print(f"Camera: {frame}")
# ... etc
```

### Properties

#### `connected: bool`
Connection status.

#### `messages_received: int`
Total messages received.

#### `bytes_received: int`
Total bytes received.

### Example

```python
import asyncio
from arvos import ArvosClient

async def main():
    client = ArvosClient()
    
    client.on_imu = lambda data: print(f"IMU: {data}")
    client.on_camera = lambda frame: print(f"Camera: {frame.width}x{frame.height}")
    
    await client.connect("ws://192.168.1.100:9090")
    await client.run()

asyncio.run(main())
```

## Next Steps

- [Python SDK API](python-sdk.md) - Complete API reference
- [Examples](../examples/overview.md) - Usage examples


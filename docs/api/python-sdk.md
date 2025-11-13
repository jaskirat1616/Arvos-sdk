# Python SDK API Reference

Complete API reference for the ARVOS Python SDK.

## ArvosServer

Main WebSocket server class.

```python
from arvos import ArvosServer

server = ArvosServer(host="0.0.0.0", port=9090)
```

### Methods

#### `start()`
Start the WebSocket server.

```python
await server.start()
```

#### `stop()`
Stop the server and close all connections.

```python
await server.stop()
```

#### `print_qr_code()`
Display QR code for easy connection.

```python
server.print_qr_code()
```

#### `get_websocket_url() -> str`
Get the WebSocket connection URL.

```python
url = server.get_websocket_url()
# Returns: "ws://192.168.1.100:9090"
```

#### `broadcast(message: str)`
Send message to all connected clients.

```python
server.broadcast("Hello, clients!")
```

#### `get_client_count() -> int`
Get number of connected clients.

```python
count = server.get_client_count()
```

### Callbacks

All callbacks can be async or sync functions:

```python
# Async callback
async def on_imu(data: IMUData):
    print(f"IMU: {data}")

# Sync callback
def on_imu(data: IMUData):
    print(f"IMU: {data}")
```

#### Connection Callbacks

- `on_connect(client_id: str)` - Client connected
- `on_disconnect(client_id: str)` - Client disconnected

#### Sensor Callbacks

- `on_handshake(handshake: HandshakeMessage)` - Device info received
- `on_imu(data: IMUData)` - IMU data received
- `on_gps(data: GPSData)` - GPS data received
- `on_pose(data: PoseData)` - Pose data received
- `on_camera(frame: CameraFrame)` - Camera frame received
- `on_depth(frame: DepthFrame)` - Depth frame received
- `on_status(status: dict)` - Status message received
- `on_error(error: str, details: str)` - Error message received

#### Apple Watch Callbacks

- `on_watch_imu(data: WatchIMUData)` - Watch IMU data
- `on_watch_attitude(data: WatchAttitudeData)` - Watch attitude
- `on_watch_activity(data: WatchMotionActivityData)` - Watch activity

## Protocol Servers

All protocol servers inherit from `BaseArvosServer` and share the same interface.

### GRPCArvosServer

```python
from arvos.servers import GRPCArvosServer

server = GRPCArvosServer(host="0.0.0.0", port=50051)
```

### MQTTArvosServer

```python
from arvos.servers import MQTTArvosServer

server = MQTTArvosServer(host="localhost", port=1883)
```

### HTTPArvosServer

```python
from arvos.servers import HTTPArvosServer

server = HTTPArvosServer(port=8080)
```

### MCAPStreamServer

```python
from arvos.servers import MCAPStreamServer

server = MCAPStreamServer(
    host="0.0.0.0",
    port=17500,
    output_file="output.mcap"
)
```

### QUICArvosServer

```python
from arvos.servers import QUICArvosServer

server = QUICArvosServer(
    host="0.0.0.0",
    port=4433,
    certfile="/path/to/cert.pem",
    keyfile="/path/to/key.key"
)
```

## ArvosClient

Client class for connecting to existing servers.

```python
from arvos import ArvosClient

client = ArvosClient()
```

### Methods

#### `connect(uri: str, timeout: float = 10.0)`
Connect to an ARVOS server.

```python
await client.connect("ws://192.168.1.100:9090")
```

#### `disconnect()`
Disconnect from server.

```python
await client.disconnect()
```

#### `run()`
Main receive loop - call after connect().

```python
await client.run()
```

### Callbacks

Same callback interface as `ArvosServer`.

## BaseArvosServer

Abstract base class for all protocol servers.

### Methods

#### `start()`
Start the server (abstract).

#### `stop()`
Stop the server (abstract).

#### `get_connection_url() -> str`
Get connection URL (abstract).

#### `get_protocol_name() -> str`
Get protocol name (abstract).

#### `get_local_ip() -> str`
Get local IP address.

#### `get_statistics() -> dict`
Get server statistics.

#### `reset_statistics()`
Reset statistics counters.

#### `print_connection_info()`
Print connection information.

### Callbacks

All servers share the same callback interface (see ArvosServer above).

## Next Steps

- [Data Types](data-types.md) - Sensor data structures
- [Servers](servers.md) - Protocol server details
- [Clients](clients.md) - Client class details


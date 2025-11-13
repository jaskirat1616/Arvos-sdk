# Protocol Servers API

Complete API reference for all protocol server implementations.

## BaseArvosServer

Abstract base class for all protocol servers.

```python
from arvos.servers import BaseArvosServer

class MyServer(BaseArvosServer):
    async def start(self):
        # Start server
        pass
    
    async def stop(self):
        # Stop server
        pass
    
    def get_connection_url(self) -> str:
        return "my-protocol://..."
    
    def get_protocol_name(self) -> str:
        return "My Protocol"
```

### Common Methods

All servers inherit these methods:

#### `get_local_ip() -> str`
Get the local IP address of this machine.

#### `get_statistics() -> dict`
Get server statistics.

```python
stats = server.get_statistics()
# Returns: {
#     "protocol": "WebSocket",
#     "running": True,
#     "bytes_received": 12345,
#     "messages_received": 100,
#     "connected_clients": 1
# }
```

#### `reset_statistics()`
Reset all statistics counters.

#### `print_connection_info()`
Print connection information to console.

### Common Callbacks

All servers support the same callbacks (see [Python SDK API](python-sdk.md)).

## GRPCArvosServer

gRPC protocol server.

```python
from arvos.servers import GRPCArvosServer

server = GRPCArvosServer(host="0.0.0.0", port=50051)
```

### Parameters

- `host` (str): Host address (default: "0.0.0.0")
- `port` (int): Port number (default: 50051)

### Methods

Same as `BaseArvosServer` plus:
- `start()` - Start gRPC server
- `stop()` - Stop gRPC server
- `get_connection_url()` - Returns `"grpc://<ip>:<port>"`
- `get_protocol_name()` - Returns `"gRPC"`

## MQTTArvosServer

MQTT protocol server.

```python
from arvos.servers import MQTTArvosServer

server = MQTTArvosServer(host="localhost", port=1883)
```

### Parameters

- `host` (str): MQTT broker host
- `port` (int): MQTT broker port (default: 1883)

### Methods

Same as `BaseArvosServer` plus:
- `start()` - Connect to MQTT broker
- `stop()` - Disconnect from broker
- `get_connection_url()` - Returns `"mqtt://<host>:<port>/arvos/telemetry"`
- `get_protocol_name()` - Returns `"MQTT"`

## HTTPArvosServer

HTTP/REST protocol server.

```python
from arvos.servers import HTTPArvosServer

server = HTTPArvosServer(port=8080)
```

### Parameters

- `host` (str): Host address (default: "0.0.0.0")
- `port` (int): Port number (default: 8080)

### Methods

Same as `BaseArvosServer` plus:
- `start()` - Start HTTP server
- `stop()` - Stop HTTP server
- `get_connection_url()` - Returns `"http://<ip>:<port>/api"`
- `get_protocol_name()` - Returns `"HTTP"`

### Endpoints

- `GET /api/health` - Health check
- `POST /api/telemetry` - JSON sensor data
- `POST /api/binary` - Binary data

## MCAPStreamServer

MCAP stream protocol server.

```python
from arvos.servers import MCAPStreamServer

server = MCAPStreamServer(
    host="0.0.0.0",
    port=17500,
    output_file="output.mcap"
)
```

### Parameters

- `host` (str): Host address (default: "0.0.0.0")
- `port` (int): Port number (default: 17500)
- `output_file` (str): Output MCAP file path

### Methods

Same as `BaseArvosServer` plus:
- `start()` - Start MCAP stream server
- `stop()` - Stop server and close MCAP file
- `get_connection_url()` - Returns `"mcap://<ip>:<port>"`
- `get_protocol_name()` - Returns `"MCAP Stream"`

## QUICArvosServer

QUIC/HTTP3 protocol server.

```python
from arvos.servers import QUICArvosServer

server = QUICArvosServer(
    host="0.0.0.0",
    port=4433,
    certfile="/path/to/cert.pem",
    keyfile="/path/to/key.key"
)
```

### Parameters

- `host` (str): Host address (default: "0.0.0.0")
- `port` (int): Port number (default: 4433)
- `certfile` (str): TLS certificate file path
- `keyfile` (str): TLS private key file path

### Methods

Same as `BaseArvosServer` plus:
- `start()` - Start QUIC/HTTP3 server
- `stop()` - Stop server
- `get_connection_url()` - Returns `"https://<ip>:<port>/api"`
- `get_protocol_name()` - Returns `"QUIC/HTTP3"`
- `is_available() -> bool` - Check if QUIC is available (static method)

## Next Steps

- [Python SDK API](python-sdk.md) - Main API reference
- [Data Types](data-types.md) - Sensor data structures
- [Examples](../examples/overview.md) - Usage examples


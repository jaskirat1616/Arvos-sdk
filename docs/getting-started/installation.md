# Installation

Install the ARVOS Python SDK and all dependencies.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Same Wi-Fi network as your iPhone (for Wi-Fi protocols)

## Basic Installation

### From PyPI (Recommended)

```bash
pip install arvos-sdk
```

### From Source

```bash
git clone https://github.com/jaskirat1616/arvos-sdk.git
cd arvos-sdk
pip install -e .
```

## Protocol-Specific Dependencies

The core SDK includes WebSocket support. For other protocols, install additional dependencies:

### gRPC

```bash
pip install grpcio grpcio-tools protobuf
```

### MQTT

```bash
pip install paho-mqtt
# Also install Mosquitto broker
brew install mosquitto        # macOS
sudo apt-get install mosquitto  # Linux
```

### Bluetooth LE

```bash
pip install bleak
```

### MCAP Stream

```bash
pip install mcap
```

### QUIC/HTTP3

```bash
pip install aioquic
```

## Optional Dependencies

### Visualization

```bash
pip install matplotlib pillow
```

### Image Processing

```bash
pip install opencv-python pillow
```

### ROS 2 Integration

```bash
pip install rclpy cv_bridge
```

### Development

```bash
pip install pytest black flake8
```

## Verify Installation

Test your installation:

```python
python -c "import arvos; print(arvos.__version__)"
```

Should output: `1.0.0`

## Next Steps

- [Quick Start](quick-start.md) - Create your first server
- [First Connection](first-connection.md) - Connect your iPhone
- [Protocol Examples](../examples/protocols.md) - Try different protocols


"""
ARVOS Protocol Servers

All protocol server implementations for receiving sensor data from the iOS app.
"""

from .base_server import BaseArvosServer

# HTTP/REST
try:
    from .http_server import HTTPArvosServer
except ImportError:
    HTTPArvosServer = None

# gRPC
try:
    from .grpc_server import GRPCArvosServer
except ImportError:
    GRPCArvosServer = None

# MQTT
try:
    from .mqtt_server import MQTTArvosServer
except ImportError:
    MQTTArvosServer = None

# MCAP Stream
try:
    from .mcap_server import MCAPStreamServer
except ImportError:
    MCAPStreamServer = None

# QUIC/HTTP3
try:
    from .quic_server import QUICArvosServer
except ImportError:
    QUICArvosServer = None

__all__ = [
    "BaseArvosServer",
    "HTTPArvosServer",
    "GRPCArvosServer",
    "MQTTArvosServer",
    "MCAPStreamServer",
    "QUICArvosServer",
]


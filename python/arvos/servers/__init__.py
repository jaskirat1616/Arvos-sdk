"""
Arvos SDK server implementations for different protocols
"""

from .base_server import BaseArvosServer
from .http_server import HTTPArvosServer
from .mcap_server import MCAPStreamServer
from .mqtt_server import MQTTArvosServer
from .grpc_server import GRPCArvosServer

try:
    from .quic_server import QUICArvosServer
    QUIC_AVAILABLE = True
except ImportError:
    QUIC_AVAILABLE = False
    QUICArvosServer = None

__all__ = [
    "BaseArvosServer",
    "HTTPArvosServer",
    "MCAPStreamServer",
    "MQTTArvosServer",
    "GRPCArvosServer",
]

if QUIC_AVAILABLE:
    __all__.append("QUICArvosServer")


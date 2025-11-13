"""
Arvos SDK - Python client library for receiving iPhone sensor data
"""

from .client import ArvosClient
from .data_types import (
    IMUData, GPSData, PoseData, CameraFrame, DepthFrame,
    HandshakeMessage, DeviceCapabilities,
    WatchIMUData, WatchAttitudeData, WatchMotionActivityData
)
from .server import ArvosServer

__version__ = "1.0.0"
__all__ = [
    "ArvosClient",
    "ArvosServer",
    "IMUData",
    "GPSData",
    "PoseData",
    "CameraFrame",
    "DepthFrame",
    "HandshakeMessage",
    "DeviceCapabilities",
    "WatchIMUData",
    "WatchAttitudeData",
    "WatchMotionActivityData",
]

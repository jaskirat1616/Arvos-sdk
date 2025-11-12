"""
Protocol Buffer definitions for Arvos sensors

To generate Python code from .proto files:
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. sensors.proto

This will generate:
    - sensors_pb2.py (message definitions)
    - sensors_pb2_grpc.py (service definitions)
"""


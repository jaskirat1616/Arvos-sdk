"""
gRPC server for receiving sensor data from ARVOS iOS app
"""

import asyncio
import json
from typing import Optional, Iterator

try:
    import grpc
    from concurrent import futures
    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False

from .base_server import BaseArvosServer
from ..client import ArvosClient

# Try to import protobuf generated code
try:
    from ..protos import sensors_pb2, sensors_pb2_grpc
    PROTOBUF_AVAILABLE = True
except ImportError:
    PROTOBUF_AVAILABLE = False
    sensors_pb2 = None
    sensors_pb2_grpc = None


class SensorStreamServicer:
    """gRPC servicer for SensorStream service"""
    
    def __init__(self, base_server: 'GRPCArvosServer'):
        self.base_server = base_server
        self.parser = ArvosClient()
        self._configure_callbacks()
    
    def _configure_callbacks(self):
        """Configure parser callbacks"""
        self.parser.on_handshake = self.base_server.on_handshake
        self.parser.on_imu = self.base_server.on_imu
        self.parser.on_gps = self.base_server.on_gps
        self.parser.on_pose = self.base_server.on_pose
        self.parser.on_camera = self.base_server.on_camera
        self.parser.on_depth = self.base_server.on_depth
        self.parser.on_status = self.base_server.on_status
        self.parser.on_error = self.base_server.on_error
        self.parser.on_watch_imu = self.base_server.on_watch_imu
        self.parser.on_watch_attitude = self.base_server.on_watch_attitude
        self.parser.on_watch_activity = self.base_server.on_watch_activity
    
    def StreamSensors(self, request_iterator: Iterator, context) -> Iterator:
        """Bidirectional streaming RPC"""
        if not PROTOBUF_AVAILABLE:
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details("Protobuf definitions not available")
            return
        
        client_id = context.peer()
        asyncio.create_task(self.base_server._invoke_callback(
            self.base_server.on_connect, client_id
        ))
        self.base_server.connected_clients += 1
        
        try:
            for sensor_msg in request_iterator:
                self.base_server.messages_received += 1
                msg_size = sensor_msg.ByteSize()
                self.base_server.bytes_received += msg_size
                
                # Convert protobuf to JSON for parser
                msg_dict = self._protobuf_to_dict(sensor_msg)
                msg_json = json.dumps(msg_dict)
                
                # Parse and dispatch (use _handle_json_message directly)
                asyncio.create_task(self.parser._handle_json_message(msg_json))
                
                # Yield empty control message (can be extended later)
                yield sensors_pb2.ControlMessage()
        
        except Exception as e:
            print(f"Error in gRPC stream: {e}")
            if self.base_server.on_error:
                asyncio.create_task(self.base_server._invoke_callback(
                    self.base_server.on_error, str(e), None, None
                ))
        finally:
            asyncio.create_task(self.base_server._invoke_callback(
                self.base_server.on_disconnect, client_id
            ))
            self.base_server.connected_clients -= 1
    
    def _protobuf_to_dict(self, message) -> dict:
        """Convert protobuf SensorMessage to dict"""
        # This is a simplified conversion - full implementation would handle all message types
        result = {"timestampNs": message.timestamp_ns}
        
        if message.HasField("handshake"):
            result["sensorType"] = "handshake"
            result["deviceName"] = message.handshake.device_name
            # ... add other fields
        elif message.HasField("imu"):
            result["sensorType"] = "imu"
            # ... convert IMU fields
        # ... handle other message types
        
        return result


class GRPCArvosServer(BaseArvosServer):
    """gRPC server for receiving sensor data"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 50051):
        super().__init__(host, port)
        self.server: Optional[grpc.Server] = None
    
    async def start(self):
        """Start the gRPC server"""
        if not GRPC_AVAILABLE:
            raise ImportError(
                "grpcio is required for gRPC support. "
                "Install it with: pip install grpcio grpcio-tools"
            )
        
        if not PROTOBUF_AVAILABLE:
            raise ImportError(
                "Protobuf definitions not found. "
                "Generate them with: python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. sensors.proto"
            )
        
        self.server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
        sensors_pb2_grpc.add_SensorStreamServicer_to_server(
            SensorStreamServicer(self), self.server
        )
        
        self.server.add_insecure_port(f"{self.host}:{self.port}")
        await self.server.start()
        
        self.running = True
        self.print_connection_info()
        print("✅ gRPC server started. Waiting for connections...")
        print("Press Ctrl+C to stop.\n")
        
        try:
            await self.server.wait_for_termination()
        except asyncio.CancelledError:
            pass
    
    async def stop(self):
        """Stop the gRPC server"""
        self.running = False
        if self.server:
            await self.server.stop(grace=5)
        print("gRPC server stopped")
    
    def get_connection_url(self) -> str:
        """Get connection URL"""
        ip = self.get_local_ip()
        return f"grpc://{ip}:{self.port}"
    
    def get_protocol_name(self) -> str:
        """Get protocol name"""
        return "gRPC"


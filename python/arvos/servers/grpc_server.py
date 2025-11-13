"""
gRPC server for receiving sensor data from ARVOS iOS app.
"""

from __future__ import annotations

import asyncio
import json
import grpc
from concurrent import futures
from typing import Iterator, Optional, Callable, Any

from .base_server import BaseArvosServer
from ..protos import sensors_pb2, sensors_pb2_grpc
from ..client import ArvosClient


class SensorStreamServicer(sensors_pb2_grpc.SensorStreamServicer):
    """gRPC servicer implementation for SensorStream service."""
    
    def __init__(self, base_server: GRPCArvosServer):
        self.base_server = base_server
        self.parser = ArvosClient()
        self._configure_callbacks()
    
    def _configure_callbacks(self):
        """Configure parser callbacks to forward to base server."""
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
    
    def StreamSensors(
        self,
        request_iterator: Iterator[sensors_pb2.SensorMessage],
        context: grpc.ServicerContext
    ) -> Iterator[sensors_pb2.ControlMessage]:
        """
        Bidirectional streaming RPC handler.
        
        Receives sensor messages from iPhone and can send control messages back.
        """
        client_id = f"{context.peer()}"
        
        # Notify connection
        if self.base_server.on_connect:
            try:
                if asyncio.iscoroutinefunction(self.base_server.on_connect):
                    asyncio.create_task(self.base_server.on_connect(client_id))
                else:
                    self.base_server.on_connect(client_id)
            except Exception as e:
                print(f"Error in on_connect callback: {e}")
        
        self.base_server.connected_clients += 1
        
        try:
            # Process incoming sensor messages
            for sensor_msg in request_iterator:
                try:
                    # Update statistics
                    self.base_server.messages_received += 1
                    msg_size = sensor_msg.ByteSize()
                    self.base_server.bytes_received += msg_size
                    
                    # Convert protobuf message to JSON string for parser
                    msg_dict = self._protobuf_to_dict(sensor_msg)
                    msg_json = json.dumps(msg_dict)
                    
                    # Parse and dispatch via ArvosClient
                    asyncio.create_task(self.parser._handle_message(msg_json))
                    
                    # Optionally send acknowledgment
                    # (For now, we just process messages without sending control messages)
                    
                except Exception as e:
                    print(f"Error processing sensor message: {e}")
                    if self.base_server.on_error:
                        try:
                            if asyncio.iscoroutinefunction(self.base_server.on_error):
                                asyncio.create_task(self.base_server.on_error(str(e), None))
                            else:
                                self.base_server.on_error(str(e), None)
                        except Exception as callback_error:
                            print(f"Error in on_error callback: {callback_error}")
        
        except Exception as e:
            print(f"Error in StreamSensors: {e}")
        finally:
            # Notify disconnection
            self.base_server.connected_clients = max(0, self.base_server.connected_clients - 1)
            if self.base_server.on_disconnect:
                try:
                    if asyncio.iscoroutinefunction(self.base_server.on_disconnect):
                        asyncio.create_task(self.base_server.on_disconnect(client_id))
                    else:
                        self.base_server.on_disconnect(client_id)
                except Exception as e:
                    print(f"Error in on_disconnect callback: {e}")
        
        # Return empty iterator (no control messages for now)
        # In the future, we could yield ControlMessage objects here
        return iter([])
    
    def _protobuf_to_dict(self, msg: sensors_pb2.SensorMessage) -> dict:
        """
        Convert protobuf SensorMessage to dictionary format expected by ArvosClient.
        
        This is a simplified conversion - in a production system, you might want
        a more complete mapping.
        """
        result = {
            "timestampNs": msg.timestamp_ns,
            "sensorType": "unknown"
        }
        
        # Determine sensor type from oneof field
        if msg.HasField("imu"):
            result["sensorType"] = "imu"
            imu = msg.imu
            result["angularVelocity"] = [
                imu.angular_velocity.x,
                imu.angular_velocity.y,
                imu.angular_velocity.z
            ] if imu.HasField("angular_velocity") else [0, 0, 0]
            result["linearAcceleration"] = [
                imu.linear_acceleration.x,
                imu.linear_acceleration.y,
                imu.linear_acceleration.z
            ] if imu.HasField("linear_acceleration") else [0, 0, 0]
            result["gravity"] = [
                imu.gravity.x,
                imu.gravity.y,
                imu.gravity.z
            ] if imu.HasField("gravity") else [0, 0, -9.81]
        
        elif msg.HasField("gps"):
            result["sensorType"] = "gps"
            gps = msg.gps
            result["latitude"] = gps.latitude
            result["longitude"] = gps.longitude
            result["altitude"] = gps.altitude
            result["horizontalAccuracy"] = gps.horizontal_accuracy
            result["verticalAccuracy"] = gps.vertical_accuracy
            result["speed"] = gps.speed
            result["course"] = gps.course
        
        elif msg.HasField("pose"):
            result["sensorType"] = "pose"
            pose = msg.pose
            if pose.HasField("position"):
                result["position"] = [
                    pose.position.x,
                    pose.position.y,
                    pose.position.z
                ]
            if pose.HasField("orientation"):
                result["orientation"] = [
                    pose.orientation.x,
                    pose.orientation.y,
                    pose.orientation.z,
                    pose.orientation.w
                ]
            result["trackingState"] = pose.tracking_state
        
        elif msg.HasField("camera_metadata"):
            result["sensorType"] = "camera"
            meta = msg.camera_metadata
            result["width"] = meta.width
            result["height"] = meta.height
            result["format"] = meta.format
            result["compressedSize"] = meta.compressed_size
            if msg.binary_data:
                result["data"] = msg.binary_data
        
        elif msg.HasField("depth_metadata"):
            result["sensorType"] = "depth"
            meta = msg.depth_metadata
            result["pointCount"] = meta.point_count
            result["minDepth"] = meta.min_depth
            result["maxDepth"] = meta.max_depth
            result["format"] = meta.format
            result["dataSize"] = meta.data_size
            if msg.binary_data:
                result["data"] = msg.binary_data
        
        elif msg.HasField("handshake"):
            result["sensorType"] = "handshake"
            hs = msg.handshake
            result["deviceName"] = hs.device_name
            result["deviceModel"] = hs.device_model
            result["osVersion"] = hs.os_version
            result["appVersion"] = hs.app_version
            if hs.HasField("capabilities"):
                caps = hs.capabilities
                result["capabilities"] = {
                    "hasLidar": caps.has_lidar_p,
                    "hasArkit": caps.has_arkit_p,
                    "hasGps": caps.has_gps_p,
                    "hasImu": caps.has_imu_p,
                    "hasWatch": caps.has_watch_p,
                    "supportedModes": list(caps.supported_modes)
                }
        
        elif msg.HasField("status"):
            result["sensorType"] = "status"
            status = msg.status
            result["status"] = status.status
            result["message"] = status.message
            result["sessionId"] = status.session_id
        
        elif msg.HasField("error"):
            result["sensorType"] = "error"
            err = msg.error
            result["error"] = err.error
            result["details"] = err.details
        
        return result


class GRPCArvosServer(BaseArvosServer):
    """gRPC server for receiving sensor data from ARVOS iOS app."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 50051):
        super().__init__(host=host, port=port)
        self._server: Optional[grpc.Server] = None
        self._servicer: Optional[SensorStreamServicer] = None
    
    async def start(self):
        """Start the gRPC server."""
        self.running = True
        self.print_connection_info()
        
        # Create servicer
        self._servicer = SensorStreamServicer(self)
        
        # Create gRPC server
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        sensors_pb2_grpc.add_SensorStreamServicer_to_server(self._servicer, self._server)
        
        # Add insecure port (for local development)
        # In production, use add_secure_port() with TLS credentials
        listen_addr = f"{self.host}:{self.port}"
        self._server.add_insecure_port(listen_addr)
        
        # Start server
        self._server.start()
        print(f"✅ gRPC server started on {listen_addr}")
        print("Listening for sensor data... Press Ctrl+C to stop.\n")
        
        # Keep server running
        try:
            await asyncio.Event().wait()  # Wait indefinitely
        except asyncio.CancelledError:
            pass
    
    async def stop(self):
        """Stop the gRPC server."""
        self.running = False
        if self._server:
            self._server.stop(grace=5)  # 5 second grace period
            await asyncio.sleep(0.1)  # Give it a moment
            print("gRPC server stopped")
    
    def get_connection_url(self) -> str:
        """Get connection URL for this server."""
        ip = self.get_local_ip()
        return f"grpc://{ip}:{self.port}"
    
    def get_protocol_name(self) -> str:
        """Get protocol name."""
        return "gRPC"


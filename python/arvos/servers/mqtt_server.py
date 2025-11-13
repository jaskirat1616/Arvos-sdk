"""
MQTT server for receiving sensor data from ARVOS iOS app
"""

import asyncio
import json
from typing import Optional

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    mqtt = None

from .base_server import BaseArvosServer
from ..client import ArvosClient


class MQTTArvosServer(BaseArvosServer):
    """MQTT server for receiving sensor data"""
    
    def __init__(self, host: str = "localhost", port: int = 1883, 
                 client_id: Optional[str] = None,
                 topic_telemetry: str = "arvos/telemetry",
                 topic_binary: str = "arvos/binary"):
        super().__init__(host, port)
        self.client_id = client_id or f"arvos_server_{id(self)}"
        self.topic_telemetry = topic_telemetry
        self.topic_binary = topic_binary
        self.client: Optional[mqtt.Client] = None
    
    async def start(self):
        """Start the MQTT server"""
        if not MQTT_AVAILABLE:
            raise ImportError(
                "paho-mqtt is required for MQTT support. "
                "Install it with: pip install paho-mqtt"
            )
        
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        try:
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
            
            self.running = True
            self.print_connection_info()
            print("✅ MQTT server started. Waiting for messages...")
            print(f"   Telemetry topic: {self.topic_telemetry}")
            print(f"   Binary topic: {self.topic_binary}")
            print("⚠️  Note: Make sure Mosquitto broker is running!")
            print("   Start it with: mosquitto -c mosquitto.conf")
            print("Press Ctrl+C to stop.\n")
            
            # Keep running
            try:
                await asyncio.Future()
            except asyncio.CancelledError:
                pass
        except Exception as e:
            print(f"❌ Failed to connect to MQTT broker at {self.host}:{self.port}")
            print(f"   Error: {e}")
            print(f"   Make sure Mosquitto broker is running:")
            print(f"   mosquitto -c mosquitto.conf")
            raise ConnectionError(f"Failed to connect to MQTT broker: {e}")
    
    async def stop(self):
        """Stop the MQTT server"""
        self.running = False
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
        print("MQTT server stopped")
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            print(f"✅ Connected to MQTT broker at {self.host}:{self.port}")
            # Subscribe to topics
            client.subscribe(self.topic_telemetry)
            client.subscribe(self.topic_binary)
        else:
            print(f"❌ Failed to connect to MQTT broker. Return code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            self.messages_received += 1
            self.bytes_received += len(msg.payload)
            
            topic = msg.topic
            if topic == self.topic_telemetry:
                # JSON telemetry
                message_str = msg.payload.decode('utf-8')
                asyncio.create_task(self._parser._handle_json_message(message_str))
            elif topic == self.topic_binary:
                # Binary data
                asyncio.create_task(self._parser._handle_binary_message(msg.payload))
        except Exception as e:
            if self.on_error:
                asyncio.create_task(self._invoke_callback(
                    self.on_error, str(e), None, None
                ))
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        print(f"Disconnected from MQTT broker (rc={rc})")
    
    def get_connection_url(self) -> str:
        """Get connection URL"""
        ip = self.get_local_ip()
        return f"mqtt://{ip}:{self.port}"
    
    def get_protocol_name(self) -> str:
        """Get protocol name"""
        return "MQTT"


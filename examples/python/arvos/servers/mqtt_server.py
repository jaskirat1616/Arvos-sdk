"""
MQTT subscriber bridge for receiving ARVOS telemetry.

Requires the `paho-mqtt` package:
    pip install paho-mqtt
"""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Optional

import paho.mqtt.client as mqtt

from .base_server import BaseArvosServer
from ..client import ArvosClient


class MQTTArvosServer(BaseArvosServer):
    """Subscribe to MQTT topics carrying ARVOS telemetry."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 1883,
        telemetry_topic: str = "arvos/telemetry",
        binary_topic: str = "arvos/binary",
        client_id: Optional[str] = None,
    ):
        super().__init__(host=host, port=port)
        self.telemetry_topic = telemetry_topic
        self.binary_topic = binary_topic
        self.client_id = client_id or f"arvos-mqtt-{uuid.uuid4().hex[:8]}"

        self._client = mqtt.Client(client_id=self.client_id, clean_session=True)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect

        self._loop_task: Optional[asyncio.Task] = None
        self._closing = False

        self._parser = ArvosClient()
        self._configure_parser_callbacks()

    def _configure_parser_callbacks(self):
        self._parser.on_handshake = self.on_handshake
        self._parser.on_imu = self.on_imu
        self._parser.on_gps = self.on_gps
        self._parser.on_pose = self.on_pose
        self._parser.on_camera = self.on_camera
        self._parser.on_depth = self.on_depth
        self._parser.on_status = self.on_status
        self._parser.on_error = self.on_error
        self._parser.on_watch_imu = self.on_watch_imu
        self._parser.on_watch_attitude = self.on_watch_attitude
        self._parser.on_watch_activity = self.on_watch_activity

    async def start(self):
        self.running = True
        self._closing = False
        self.print_connection_info()
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: self._client.connect(self.host, self.port, keepalive=60)
        )
        self._client.loop_start()

        self._loop_task = asyncio.create_task(self._run())
        await self._loop_task

    async def _run(self):
        try:
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    async def stop(self):
        self.running = False
        self._closing = True
        self._client.loop_stop()
        self._client.disconnect()
        if self._loop_task:
            self._loop_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._loop_task
        self._loop_task = None

    def get_connection_url(self) -> str:
        return f"mqtt://{self.host}:{self.port}/{self.telemetry_topic}"

    def get_protocol_name(self) -> str:
        return "MQTT"

    # MQTT Callbacks

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to MQTT broker.")
            client.subscribe(self.telemetry_topic)
            client.subscribe(self.binary_topic)
        else:
            print(f"❌ MQTT connection failed (code {rc})")

    def _on_disconnect(self, client: mqtt.Client, userdata, rc):
        if not self._closing:
            print("⚠️ MQTT disconnected unexpectedly.")

    def _on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        asyncio.run_coroutine_threadsafe(self._handle_message_async(msg), asyncio.get_event_loop())

    async def _handle_message_async(self, msg: mqtt.MQTTMessage):
        self._configure_parser_callbacks()
        payload = bytes(msg.payload)
        self.bytes_received += len(payload)
        self.messages_received += 1

        if msg.topic == self.telemetry_topic:
            try:
                text = payload.decode("utf-8")
            except UnicodeDecodeError:
                print(f"⚠️ MQTT payload on {msg.topic} is not valid UTF-8")
                return
            await self._parser._handle_json_message(text)
        elif msg.topic == self.binary_topic:
            await self._parser._handle_binary_message(payload)
        else:
            if self.on_message:
                await self._invoke_callback(self.on_message, msg.topic, payload)



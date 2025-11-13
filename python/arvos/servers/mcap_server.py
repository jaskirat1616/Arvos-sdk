"""
MCAP streaming server for ARVOS.

Accepts length-prefixed JSON envelopes over TCP and writes them to an MCAP file.
Each message envelope should contain:
    {
        "topic": "/sensor/imu",
        "timestampNs": 123456789,
        "payloadEncoding": "json",
        "payload": {... original message ...}
    }
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from mcap.writer import Writer


@dataclass
class MCAPChannel:
    name: str
    channel_id: int
    encoding: str = "json"


class MCAPStreamConnection:
    def __init__(self, writer: Writer, output_path: Path):
        self._writer = writer
        self._output_path = output_path
        self._channels: Dict[str, MCAPChannel] = {}
        self._writer.start(profile="arvos-stream", library="arvos-python-sdk")

    def close(self):
        try:
            self._writer.finish()
        except Exception:
            pass

    def _ensure_channel(self, topic: str, encoding: str) -> int:
        channel = self._channels.get(topic)
        if channel and channel.encoding == encoding:
            return channel.channel_id

        channel_id = self._writer.register_channel(
            topic=topic, message_encoding=encoding, schema_id=0, metadata={}
        )
        self._channels[topic] = MCAPChannel(name=topic, channel_id=channel_id, encoding=encoding)
        return channel_id

    def write_envelope(self, envelope: Dict[str, object]):
        topic = envelope.get("topic", "/misc")
        encoding = str(envelope.get("payloadEncoding", "json"))
        timestamp = int(envelope.get("timestampNs", time.time_ns()))

        payload = envelope.get("payload")
        if payload is None:
            return

        if encoding == "json":
            data_bytes = json.dumps(payload).encode("utf-8")
        elif encoding == "base64":
            import base64

            data_bytes = base64.b64decode(payload)
        else:
            return

        channel_id = self._ensure_channel(str(topic), encoding)
        self._writer.add_message(
            channel_id=channel_id,
            log_time=timestamp,
            publish_time=timestamp,
            data=data_bytes,
        )


class MCAPStreamServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 17500, output_dir: Optional[Path] = None):
        self.host = host
        self.port = port
        self.output_dir = Path(output_dir) if output_dir else Path("mcap_logs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._server: Optional[asyncio.AbstractServer] = None

    async def start(self):
        self._server = await asyncio.start_server(self._handle_client, self.host, self.port)
        addr = ", ".join(str(sock.getsockname()) for sock in self._server.sockets or [])
        print(f"📡 MCAP stream server listening on {addr}")

        async with self._server:
            await self._server.serve_forever()

    async def stop(self):
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer = writer.get_extra_info("peername")
        print(f"✅ MCAP client connected: {peer}")

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_path = self.output_dir / f"arvos-session-{timestamp}.mcap"

        with open(output_path, "wb") as fh:
            connection = MCAPStreamConnection(Writer(fh), output_path)
            try:
                while True:
                    length_bytes = await reader.readexactly(4)
                    length = int.from_bytes(length_bytes, byteorder="little")
                    payload = await reader.readexactly(length)

                    try:
                        envelope = json.loads(payload)
                    except json.JSONDecodeError:
                        continue

                    connection.write_envelope(envelope)
            except asyncio.IncompleteReadError:
                pass
            finally:
                connection.close()
                writer.close()
                await writer.wait_closed()
                print(f"👋 MCAP client disconnected: {peer}")
                print(f"💾 Session saved to {output_path}")


__all__ = ["MCAPStreamServer"]

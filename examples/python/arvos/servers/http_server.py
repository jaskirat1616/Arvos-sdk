"""
HTTP server implementation for receiving sensor data from the iOS app.

The iOS HTTPAdapter sends JSON messages to /api/telemetry and binary frames
to /api/binary via HTTP POST requests. This server parses those requests and
dispatches them through the same callback surface as the WebSocket server.
"""

from __future__ import annotations

import asyncio
import json
from typing import Optional, Tuple, Dict, Any

from .base_server import BaseArvosServer
from ..client import ArvosClient


class HTTPArvosServer(BaseArvosServer):
    """Minimal HTTP server that accepts sensor data posts from the iOS app."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        super().__init__(host=host, port=port)
        self._server: Optional[asyncio.AbstractServer] = None
        self._client_parser = ArvosClient()
        self._configure_parser_callbacks()

    def _configure_parser_callbacks(self):
        """Share callbacks with the ArvosClient parser so we can reuse decoding logic."""
        self._client_parser.on_handshake = self.on_handshake
        self._client_parser.on_imu = self.on_imu
        self._client_parser.on_gps = self.on_gps
        self._client_parser.on_pose = self.on_pose
        self._client_parser.on_camera = self.on_camera
        self._client_parser.on_depth = self.on_depth
        self._client_parser.on_status = self.on_status
        self._client_parser.on_error = self.on_error
        self._client_parser.on_watch_imu = self.on_watch_imu
        self._client_parser.on_watch_attitude = self.on_watch_attitude
        self._client_parser.on_watch_activity = self.on_watch_activity

    async def start(self):
        self.running = True
        self.print_connection_info()
        self._server = await asyncio.start_server(self._handle_connection, self.host, self.port)
        async with self._server:
            await self._server.serve_forever()

    async def stop(self):
        self.running = False
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

    def get_connection_url(self) -> str:
        return f"http://{self.host}:{self.port}/api"

    def get_protocol_name(self) -> str:
        return "HTTP"

    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer = writer.get_extra_info("peername")
        client_id = f"{peer[0]}:{peer[1]}" if isinstance(peer, Tuple) and len(peer) >= 2 else "client"
        self.connected_clients += 1

        await self._invoke_callback(self.on_connect, client_id)

        try:
            request_line = await reader.readline()
            if not request_line:
                return

            method, path, _ = self._parse_request_line(request_line.decode(errors="ignore"))
            headers = await self._read_headers(reader)
            content_length = int(headers.get("content-length", "0"))
            body = await reader.readexactly(content_length) if content_length > 0 else b""

            response_status, response_headers, response_body = await self._handle_request(
                method, path, headers, body, client_id
            )

            self._write_response(writer, response_status, response_headers, response_body)

        except asyncio.IncompleteReadError:
            pass
        finally:
            self.connected_clients = max(0, self.connected_clients - 1)
            await self._invoke_callback(self.on_disconnect, client_id)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def _handle_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: bytes,
        client_id: str,
    ) -> Tuple[int, Dict[str, str], bytes]:
        """Process the HTTP request and dispatch to callbacks."""
        try:
            if method == "GET" and path == "/api/health":
                payload = json.dumps({"status": "ok", "protocol": "HTTP"}).encode()
                return 200, {"Content-Type": "application/json"}, payload

            if method != "POST":
                return 405, {"Content-Type": "text/plain"}, b"Method Not Allowed"

            if path == "/api/telemetry":
                await self._handle_json_message(body.decode("utf-8"))
            elif path == "/api/binary":
                await self._handle_binary_message(body)
            else:
                return 404, {"Content-Type": "text/plain"}, b"Not Found"

            self.messages_received += 1
            self.bytes_received += len(body)
            if self.on_message:
                await self._invoke_callback(self.on_message, client_id, body)

            return 200, {"Content-Type": "application/json"}, b'{"ok": true}'

        except json.JSONDecodeError:
            return 400, {"Content-Type": "text/plain"}, b"Invalid JSON payload"
        except Exception as exc:
            print(f"HTTP server error: {exc}")
            return 500, {"Content-Type": "text/plain"}, b"Internal Server Error"

    async def _handle_json_message(self, message: str):
        await self._client_parser._handle_json_message(message)

    async def _handle_binary_message(self, message: bytes):
        await self._client_parser._handle_binary_message(message)

    @staticmethod
    def _parse_request_line(line: str) -> Tuple[str, str, str]:
        parts = line.strip().split()
        if len(parts) != 3:
            raise ValueError("Malformed HTTP request line")
        return parts[0].upper(), parts[1], parts[2]

    @staticmethod
    async def _read_headers(reader: asyncio.StreamReader) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        while True:
            raw_line = await reader.readline()
            if raw_line in (b"\r\n", b"\n", b""):
                break
            decoded = raw_line.decode("iso-8859-1").strip()
            if ":" in decoded:
                key, value = decoded.split(":", 1)
                headers[key.lower().strip()] = value.strip()
        return headers

    @staticmethod
    def _write_response(
        writer: asyncio.StreamWriter,
        status: int,
        headers: Dict[str, str],
        body: bytes,
    ):
        reason = {
            200: "OK",
            400: "Bad Request",
            404: "Not Found",
            405: "Method Not Allowed",
            500: "Internal Server Error",
        }.get(status, "OK")

        response_lines = [
            f"HTTP/1.1 {status} {reason}",
            *(f"{key}: {value}" for key, value in headers.items()),
            f"Content-Length: {len(body)}",
            "Connection: close",
            "",
        ]
        response = "\r\n".join(response_lines).encode("utf-8") + body
        writer.write(response)



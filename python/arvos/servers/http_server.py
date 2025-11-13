"""
Minimal HTTP server that accepts telemetry POSTs from the ARVOS iOS app.
"""

from __future__ import annotations

import asyncio
import json
import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, Optional, Tuple, Any

from .base_server import BaseArvosServer
from ..client import ArvosClient


class HTTPArvosServer(BaseArvosServer):
    """Threaded HTTP server for sensor telemetry."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        super().__init__(host=host, port=port)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._httpd: Optional[ThreadingHTTPServer] = None
        self._serve_task: Optional[asyncio.Task] = None
        self._parser = ArvosClient()
        self._configure_callbacks()

    def _configure_callbacks(self):
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
        self.print_connection_info()
        self._loop = asyncio.get_running_loop()

        server = self

        class RequestHandler(BaseHTTPRequestHandler):  # pragma: no cover - invoked in separate thread
            def log_message(self, format: str, *args: Any) -> None:
                # Suppress default logging
                return

            def _client_id(self) -> str:
                addr = self.client_address
                return f"{addr[0]}:{addr[1]}" if isinstance(addr, Tuple) and len(addr) >= 2 else "client"

            def _write_json(self, payload: Dict[str, Any], status: int = 200):
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                client_id = self._client_id()
                asyncio.run_coroutine_threadsafe(server._invoke_callback(server.on_connect, client_id), server._loop)
                try:
                    if self.path == "/api/health":
                        self._write_json({"status": "ok", "protocol": "HTTP"}, status=200)
                    else:
                        self.send_error(404, "Not Found")
                finally:
                    asyncio.run_coroutine_threadsafe(server._invoke_callback(server.on_disconnect, client_id), server._loop)

            def do_POST(self):
                client_id = self._client_id()
                asyncio.run_coroutine_threadsafe(server._invoke_callback(server.on_connect, client_id), server._loop)
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    body = self.rfile.read(length) if length > 0 else b""

                    handled = False
                    if self.path == "/api/telemetry":
                        future = asyncio.run_coroutine_threadsafe(
                            server._handle_json_message(body, client_id), server._loop
                        )
                        future.result()
                        self._write_json({"ok": True})
                        handled = True
                    elif self.path == "/api/binary":
                        future = asyncio.run_coroutine_threadsafe(
                            server._handle_binary_message(body, client_id), server._loop
                        )
                        future.result()
                        self._write_json({"ok": True})
                        handled = True
                    else:
                        self.send_error(404, "Not Found")

                    if not handled:
                        return

                except json.JSONDecodeError:
                    self.send_error(400, "Invalid JSON")
                except Exception as exc:  # pragma: no cover - debugging aid
                    print(f"HTTP server error: {exc}")
                    self.send_error(500, "Internal Server Error")
                finally:
                    asyncio.run_coroutine_threadsafe(server._invoke_callback(server.on_disconnect, client_id), server._loop)

        self._httpd = ThreadingHTTPServer((self.host, self.port), RequestHandler)
        self._serve_task = asyncio.create_task(asyncio.to_thread(self._httpd.serve_forever))
        if self._serve_task:
            await self._serve_task

    async def stop(self):
        self.running = False
        if self._httpd:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None
        if self._serve_task:
            self._serve_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._serve_task
            self._serve_task = None

    def get_connection_url(self) -> str:
        return f"http://{self.host}:{self.port}/api"

    def get_protocol_name(self) -> str:
        return "HTTP"

    async def _handle_json_message(self, body: bytes, client_id: str):
        text = body.decode("utf-8") if body else "{}"
        await self._parser._handle_json_message(text)
        if self.on_message:
            await self._invoke_callback(self.on_message, client_id, text)

    async def _handle_binary_message(self, body: bytes, client_id: str):
        await self._parser._handle_binary_message(body)
        if self.on_message:
            await self._invoke_callback(self.on_message, client_id, body)

"""
HTTP/REST server for receiving sensor data from ARVOS iOS app
"""

import asyncio
import json
from typing import Optional

try:
    from aiohttp import web
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    web = None

from .base_server import BaseArvosServer


class HTTPArvosServer(BaseArvosServer):
    """HTTP/REST server for receiving sensor data"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        super().__init__(host, port)
        self.app: Optional[web.Application] = None
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
    
    async def start(self):
        """Start the HTTP server"""
        if not AIOHTTP_AVAILABLE:
            raise ImportError(
                "aiohttp is required for HTTP/REST support. "
                "Install it with: pip install aiohttp"
            )
        
        self.app = web.Application()
        self.app.router.add_get('/api/health', self._handle_health)
        self.app.router.add_post('/api/telemetry', self._handle_telemetry)
        self.app.router.add_post('/api/binary', self._handle_binary)
        
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        self.running = True
        self.print_connection_info()
        print("✅ HTTP server started. Waiting for connections...")
        print("Press Ctrl+C to stop.\n")
        
        # Keep running
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            pass
    
    async def stop(self):
        """Stop the HTTP server"""
        self.running = False
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        print("HTTP server stopped")
    
    async def _handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response({"status": "ok", "protocol": "HTTP/REST"})
    
    async def _handle_telemetry(self, request: web.Request) -> web.Response:
        """Handle telemetry JSON messages"""
        try:
            data = await request.read()
            self.messages_received += 1
            self.bytes_received += len(data)
            
            # Parse JSON and dispatch via ArvosClient
            message_str = data.decode('utf-8')
            # ArvosClient._handle_message accepts string and calls _handle_json_message
            await self._parser._handle_json_message(message_str)
            
            return web.json_response({"status": "ok"})
        except Exception as e:
            if self.on_error:
                await self._invoke_callback(self.on_error, str(e), None, None)
            return web.json_response({"status": "error", "message": str(e)}, status=500)
    
    async def _handle_binary(self, request: web.Request) -> web.Response:
        """Handle binary messages (camera/depth frames)"""
        try:
            data = await request.read()
            self.messages_received += 1
            self.bytes_received += len(data)
            
            # Handle binary data via ArvosClient
            await self._parser._handle_binary_message(data)
            
            return web.json_response({"status": "ok"})
        except Exception as e:
            if self.on_error:
                await self._invoke_callback(self.on_error, str(e), None, None)
            return web.json_response({"status": "error", "message": str(e)}, status=500)
    
    def get_connection_url(self) -> str:
        """Get connection URL"""
        ip = self.get_local_ip()
        return f"http://{ip}:{self.port}/api"
    
    def get_protocol_name(self) -> str:
        """Get protocol name"""
        return "HTTP/REST"


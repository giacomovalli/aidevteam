import asyncio
import websockets
import json
import logging

class WebSocketServer:
    def __init__(self, logger, message_handler=None, host="localhost", port=8765):
        """Initialize WebSocket server with logger and connection details."""
        self.logger = logger
        self.host = host
        self.port = port
        self.message_handler = message_handler

    async def handle_client(self, websocket):
        """Handle incoming WebSocket connections."""
        try:
            self.logger.info(f"New client connected from {websocket.remote_address}")
            async for message in websocket:
                try:
                    data = json.loads(message)
                    self.logger.info(f"Received message: {data}")
                    
                    if self.message_handler:
                        response = await self.message_handler(data)
                    else:
                        response = {"status": "received"}
                    
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    error_response = {"error": "Invalid JSON format"}
                    await websocket.send(json.dumps(error_response))
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("Client disconnected")
        except Exception as e:
            self.logger.error(f"Error handling client: {e}")

    async def _run_server(self):
        """Run the WebSocket server."""
        self.logger.info("WebSocket server started successfully")
        async with websockets.serve(
            self.handle_client, 
            self.host, 
            self.port,
            ping_interval=60,
            ping_timeout=120
        ):
            await asyncio.Future()  # Run forever

    def start(self):
        """Start the WebSocket server listening for connections."""
        self.logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        asyncio.run(self._run_server())

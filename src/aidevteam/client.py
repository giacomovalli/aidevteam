import asyncio
import websockets
import json
import logging

class WebSocketClient:
    def __init__(self, logger, host="localhost", port=8766):
        """Initialize WebSocket client with logger and connection details."""
        self.logger = logger
        self.host = host
        self.port = port
        self.uri = f"ws://{host}:{port}"
        self.websocket = None

    async def connect(self):
        """Connect to the WebSocket server."""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.logger.info(f"Connected to WebSocket server at {self.uri}")
        except Exception as e:
            self.logger.error(f"Failed to connect to WebSocket server: {e}")
            raise

    async def send_message(self, message):
        """Send a message to the WebSocket server."""
        if not self.websocket:
            raise Exception("Not connected to WebSocket server")
        
        try:
            if isinstance(message, dict):
                message = json.dumps(message)
            
            await self.websocket.send(message)
            self.logger.info(f"Sent message: {message}")
            
            response = await self.websocket.recv()
            self.logger.info(f"Received response: {response}")
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            raise

    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            self.logger.info("Disconnected from WebSocket server")
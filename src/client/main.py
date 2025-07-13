import asyncio
import logging
import sys
import threading
from aidevteam.client import WebSocketClient
from aidevteam.server import WebSocketServer

def start_server(logger):
    """Start the WebSocket server in a separate thread."""
    server = WebSocketServer(logger, port=8767)
    server.start()

async def run_client(logger):
    """Run the WebSocket client."""
    client = WebSocketClient(logger, port=8766)
    
    try:
        await client.connect()
        message = {"command": "run crew"}
        response = await client.send_message(message)
        print(f"Server response: {response}")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await client.disconnect()

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logger = logging.getLogger(__name__)

    # Start server in a separate thread
    server_thread = threading.Thread(target=start_server, args=(logger,), daemon=True)
    server_thread.start()
    
    # Give server time to start
    await asyncio.sleep(1)
    
    # Run client
    await run_client(logger)

if __name__ == "__main__":
    asyncio.run(main())
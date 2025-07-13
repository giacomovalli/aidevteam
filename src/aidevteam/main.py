#!/usr/bin/env python
import sys
import warnings
import logging
import threading
import signal
import atexit

from datetime import datetime

from aidevteam.crew import Aidevteam
from aidevteam.server import WebSocketServer

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

inputs = {
        'project_name': 'PrimeMap',
        'project_languages': "c#, Python, Typescript, SQL",
        'project_frameworks': 'Microsoft .NET Core, Angular JS'
    }

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    
    try:
        Aidevteam().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    try:
        Aidevteam().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Aidevteam().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    
    try:
        Aidevteam().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def cleanup_server(server, logger):
    """Cleanup function to properly close the server."""
    logger.info("Shutting down WebSocket server...")
    if hasattr(server, 'cleanup'):
        server.cleanup()

async def handle_message(data):
    """Handle incoming WebSocket messages."""
    if data.get("command") == "run crew":
        try:
            run()
            return {"status": "success", "message": "Crew execution completed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    else:
        return {"status": "received"}

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True
    )
    logger = logging.getLogger(__name__)
    server = WebSocketServer(logger, handle_message, port=8766)
    
    # Register cleanup handlers
    atexit.register(cleanup_server, server, logger)
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        sys.exit(0)
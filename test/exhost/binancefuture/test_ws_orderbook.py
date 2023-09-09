import logging
import unittest
import websockets
import asyncio
from general.logger import setup_logger


class TestWebSocketRelay(unittest.IsolatedAsyncioTestCase):
    # WEBSOCKET_URL = 'ws://127.0.0.1:8765'  # Replace with your WebSocket relay server URL
    # WEBSOCKET_URL = 'ws://ec2-52-198-41-165.ap-northeast-1.compute.amazonaws.com:8765'

    # WEBSOCKET_URL = 'ws://ec2-16-163-156-120.ap-east-1.compute.amazonaws.com:8765'
    logger = setup_logger(__name__, None, logging.INFO)

    async def test_relay_message(self):
        async with websockets.connect(self.WEBSOCKET_URL) as ws:
            # If your relay server sends a message immediately upon connection:
            end_time = asyncio.get_event_loop().time() + 10
            while asyncio.get_event_loop().time() < end_time:
                message = await ws.recv()
                self.logger.info(f'Received message: {message}')
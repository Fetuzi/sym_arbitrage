import os
import asyncio
import websockets
import json
import redis
from general.logger import setup_logger
from config.binancefuture_okx_arb import TIMESTAMP, LOG_DIR, REDIS_HOST, REDIS_PORT, REDIS_PUBSUB, OKX, HK_WS

MAX_RETRIES = 5  # Set maximum retries
RETRY_WAIT_TIME = 5  # Wait time between each retry in seconds
TIMEOUT = 3  # 3 seconds timeout for receiving data

NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(NAME, os.path.join(LOG_DIR, f"{TIMESTAMP}_{NAME}_{OKX}.log"))
logger.info(f"init {NAME}")

async def subscribe_to_websocket(uri, redis_client):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            logger.info(f"Attempting to connect to WebSocket URL: {uri}")
            async with websockets.connect(uri) as websocket:
                retries = 0  # Reset retries if successful connection
                while True:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)
                        data = json.loads(message)['data'][0]
                        logger.info(f"Received data: {data}")

                        # Publish to Redis
                        redis_client.publish(REDIS_PUBSUB, json.dumps({'ex': OKX, 'b': data['bids'][0][0], 'a': data['asks'][0][0]}))
                    except asyncio.TimeoutError:
                        logger.warning("No data received for 3 seconds, retrying...")
                        break
        except Exception as e:
            logger.error(f"Cannot connect to WebSocket server: {e}")
            retries += 1
            logger.info(f"Retrying in {RETRY_WAIT_TIME} seconds...")
            await asyncio.sleep(RETRY_WAIT_TIME)

    logger.error(f"Reached max retries {MAX_RETRIES}. Exiting.")

if __name__ == '__main__':
    # Initialize Redis client
    redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    # Start the WebSocket client
    loop = asyncio.get_event_loop()
    loop.run_until_complete(subscribe_to_websocket(HK_WS, redis_client))

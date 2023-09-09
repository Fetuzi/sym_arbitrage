import os
import asyncio
import websockets
import json
import redis
from general.logger import setup_logger
from config.binancefuture_kucoin_arb import TIMESTAMP, LOG_DIR, REDIS_PUBSUB

NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(NAME, os.path.join(LOG_DIR, f"{TIMESTAMP}_{NAME}_{REDIS_PUBSUB}.log"))
logger.info(f"init {NAME}")


async def subscribe_to_websocket(uri, redis_client):
    async with websockets.connect(uri) as websocket:
        # await websocket.send(json.dumps({
        #     "type": "subscribe",
        #     "channel": "your_channel_here"
        # }))
        # print("Subscribed to WebSocket channel")

        async for message in websocket:
            data = json.loads(message)
            logger.info(f"Received data: {data}")
            # Publish to Redis
            redis_client.publish(REDIS_PUBSUB, json.dumps({'b': data['b'][0], 'a': data['a'][0]}))


if __name__ == '__main__':
    # Initialize Redis client
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    # Start the WebSocket client
    loop = asyncio.get_event_loop()
    loop.run_until_complete(subscribe_to_websocket('ws://your_websocket_server', redis_client))

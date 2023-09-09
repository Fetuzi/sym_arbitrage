import asyncio
import websockets
import json
import redis


async def subscribe_to_websocket(uri, redis_client):
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "type": "subscribe",
            "channel": "your_channel_here"
        }))
        print("Subscribed to WebSocket channel")

        async for message in websocket:
            data = json.loads(message)
            print(f"Received data: {data}")

            # Publish to Redis
            redis_client.publish("your_redis_channel", json.dumps(data))


if __name__ == '__main__':
    # Initialize Redis client
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    # Start the WebSocket client
    loop = asyncio.get_event_loop()
    loop.run_until_complete(subscribe_to_websocket('ws://your_websocket_server', redis_client))

import os
import json
import asyncio
from asyncio import Lock
import websockets
from general.logger import setup_logger
from config.binancefuture_okx_arb import (
    TIMESTAMP,
    LOG_DIR,
    RECORDING_COIN,
    RELAY_PORT
)

NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(
    NAME,
    os.path.join(LOG_DIR, f"{TIMESTAMP}_{NAME}_{RECORDING_COIN}.log")
)
logger.info(f"init {NAME}")

SOURCE_URI = 'wss://ws.okx.com:8443/ws/v5/public'
RECONNECT_DELAY = 5  # Time to wait before attempting to reconnect
DATA_TIMEOUT = 3  # Time to wait before raising a warning for not receiving data


async def heartbeat(websocket, interval=30):
    while True:
        await asyncio.sleep(interval)
        await websocket.ping()
        logger.info("Sent a ping")


async def source_connection(source_uri, relay_to_clients):
    while True:
        try:
            async with websockets.connect(source_uri) as websocket:
                last_received_time = asyncio.get_event_loop().time()

                data = {
                    "op": "subscribe",
                    "args": [{
                        "channel": "books5",
                        "instId": f"{RECORDING_COIN}-USDT-SWAP"
                    }]
                }
                await websocket.send(json.dumps(data))
                response = await websocket.recv()
                logger.info(f"Received response: {response}")

                asyncio.create_task(heartbeat(websocket))

                while True:
                    try:
                        message = await asyncio.wait_for(
                            websocket.recv(), timeout=DATA_TIMEOUT
                        )
                        last_received_time = asyncio.get_event_loop().time()
                        logger.info(f"{message=}")
                        await relay_to_clients(message)
                    except asyncio.TimeoutError:
                        current_time = asyncio.get_event_loop().time()
                        if current_time - last_received_time >= DATA_TIMEOUT:
                            logger.warning("No data received for more than 3 seconds")
                            break

        except Exception as e:
            logger.error(f"Error: {e}")

        logger.info(f"Reconnecting in {RECONNECT_DELAY} seconds...")
        await asyncio.sleep(RECONNECT_DELAY)


clients = set()
clients_lock = Lock()


async def relay_to_clients(message):
    async with clients_lock:
        if clients:
            await asyncio.gather(*(client.send(message) for client in clients))


async def relay_server(websocket, path):
    async with clients_lock:
        clients.add(websocket)
    logger.info(f"New client connected. All clients: {clients}")

    try:
        async for message in websocket:
            pass
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        async with clients_lock:
            clients.remove(websocket)
        logger.info(f"Client disconnected. All clients: {clients}")


start_server = websockets.serve(relay_server, '0.0.0.0', RELAY_PORT)


async def main():
    asyncio.create_task(source_connection(SOURCE_URI, relay_to_clients))
    await start_server


asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()

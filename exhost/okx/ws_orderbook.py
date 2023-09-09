import os
import asyncio
import websockets
import json
from general.logger import setup_logger
from config.binancefuture_kucoin_arb import TIMESTAMP, LOG_DIR, RECORDING_COIN, RELAY_PORT

NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(NAME, os.path.join(LOG_DIR, f"{TIMESTAMP}_{NAME}_{RECORDING_COIN}.log"))
logger.info(f"init {NAME}")

source_uri = f'wss://ws.okx.com:8443/ws/v5/public'

async def heartbeat(websocket, interval=30):
    while True:
        await asyncio.sleep(interval)
        await websocket.ping()
        logger.info("Sent a ping")

# Connection to the source WebSocket server
async def source_connection(source_uri, relay_to_clients):
    async with websockets.connect(source_uri) as websocket:
        # Send subscription message
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

        # Start the heartbeat
        asyncio.create_task(heartbeat(websocket))


        while True:
            message = await websocket.recv()
            logger.info(f"{message=}")
            await relay_to_clients(message)

# Relaying messages to all connected clients
async def relay_to_clients(message):
    if clients:  # Guard against possible empty set
        await asyncio.gather(*(client.send(message) for client in clients))

# Handler for incoming clients to your relay server
async def relay_server(websocket, path):
    clients.add(websocket)
    logger.info(f"New client connected. All clients: {clients}")  # Log client count after new connection

    try:
        async for message in websocket:  # Here, we're just waiting for messages, if any, from the connected client.
            pass                         # For this relay, we don't expect to get any.
    finally:
        clients.remove(websocket)
        logger.info(f"Client disconnected. all clients: {clients}")

clients = set()  # Set to keep track of connected clients

# Starting the relay server
start_server = websockets.serve(relay_server, '0.0.0.0', RELAY_PORT)

async def main():
    # Connect to source WebSocket
    asyncio.create_task(source_connection(source_uri, relay_to_clients))

    # Start relay server
    await start_server

# Run the event loop
asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()
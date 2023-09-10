import os
import asyncio
from asyncio import Lock, TimeoutError
import websockets
from general.logger import setup_logger
from config.binancefuture_okx_arb import TIMESTAMP, LOG_DIR, RECORDING_COIN, RELAY_PORT

NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(NAME, os.path.join(LOG_DIR, f"{TIMESTAMP}_{NAME}_{RECORDING_COIN}.log"))
logger.info(f"init {NAME}")

source_uri = f'wss://fstream.binance.com/ws/{RECORDING_COIN.lower()}usdt@depth5@100ms'

# Connection to the source WebSocket server
async def source_connection(source_uri, relay_to_clients):
    while True:  # Reconnect loop
        try:
            async with websockets.connect(source_uri) as websocket:
                while True:
                    try:
                        logger.info("About to receive message from source WebSocket")
                        message = await asyncio.wait_for(websocket.recv(), timeout=5)  # 5-second timeout
                        logger.info(f"Received: {message=}")
                        await relay_to_clients(message)
                    except TimeoutError:  # Triggered if no message received for 5 seconds
                        logger.warning("No message received for 5 seconds. Reconnecting...")
                        break
        except Exception as e:  # Catches all exceptions including disconnection
            logger.warning(f"WebSocket disconnected due to error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)  # Wait for 5 seconds before attempting to reconnect

clients = set()
clients_lock = Lock()

# Relaying messages to all connected clients
async def relay_to_clients(message):
    async with clients_lock:
        logger.info("Acquired lock, about to send message to clients")
        if clients:
            await asyncio.gather(*(client.send(message) for client in clients))
        logger.info("Message relayed to clients")

async def relay_server(websocket, path):
    async with clients_lock:
        clients.add(websocket)
    logger.info(f"New client connected. All clients: {clients}")

    try:
        logger.info("Listening for incoming messages from client")
        async for message in websocket:
            pass
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        async with clients_lock:
            clients.remove(websocket)
        logger.info(f"Client disconnected. All clients: {clients}")

# Starting the relay server
start_server = websockets.serve(relay_server, '0.0.0.0', RELAY_PORT)

async def main():
    logger.info("About to connect to source WebSocket")
    asyncio.create_task(source_connection(source_uri, relay_to_clients))
    logger.info("Source WebSocket connected")

    logger.info("About to start relay server")
    await start_server
    logger.info("Relay server started")

# Run the event loop
asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()

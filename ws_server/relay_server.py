import asyncio
import websockets

async def relay_server(websocket, path):
    # Open a connection to the target websocket server (for example, ws://example.com/ws)
    async with websockets.connect('ws://example.com/ws') as target_ws:
        # Handle incoming messages from clients and forward them to the target websocket
        consumer_task = asyncio.ensure_future(consumer_handler(websocket, target_ws))
        
        # Handle incoming messages from target websocket and forward them to clients
        producer_task = asyncio.ensure_future(producer_handler(websocket, target_ws))
        
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Clean up tasks
        for task in pending:
            task.cancel()

async def consumer_handler(client_ws, target_ws):
    async for message in client_ws:
        print(f"Received message from client: {message}")
        await target_ws.send(message)

async def producer_handler(client_ws, target_ws):
    async for message in target_ws:
        print(f"Received message from target: {message}")
        await client_ws.send(message)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    server = websockets.serve(relay_server, 'localhost', 8765)
    loop.run_until_complete(server)
    print("Relay server started at ws://localhost:8765")
    loop.run_forever()


import os
from typing import Union
import time
import json
import uuid
from fastapi import FastAPI
from config.binancefuture_okx_arb import LOG_DIR, TIMESTAMP, REDIS_HOST, REDIS_PORT, REDIS_QUEUE
from general.logger import setup_logger
from general.queue import RedisQueueHandler

app = FastAPI()
NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(NAME, os.path.join(LOG_DIR, f"{TIMESTAMP}_{NAME}.log"))
logger.info(f"init {NAME}")

# Initialize Redis connection
queue_handler: Union[RedisQueueHandler, None] = None

@app.on_event("startup")
async def startup_event():
    global queue_handler
    queue_handler = RedisQueueHandler(REDIS_HOST, REDIS_PORT, REDIS_QUEUE)

@app.on_event("shutdown")
async def shutdown_event():
    global queue_handler
    if queue_handler:
        queue_handler.close()

@app.get("/ping")
async def test():
    logger.info("ping is called!")
    return {"pong": int(time.time() * 1000)}

@app.get("/create_order")
async def create_order(
        symbol: str,
        type: str,
        side: str,
        amount: float,
        price: float,
        dry_run: bool = False
):
    logger.info(f'Send request: {symbol=}, {type=}, {side=}, {amount=}, {price=}, {dry_run=}')
    _id = uuid.uuid4().hex
    data = {
        "id": _id,
        "topic": "create",
        "symbol": symbol,
        "type": type,
        "side": side,
        "amount": amount,
        "price": price,
        "dry_run": dry_run
    }

    queue_handler.enqueue(data)

    logger.info(f"{_id}: created!")
    return {_id: "Created"}


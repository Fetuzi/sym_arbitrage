import os
import time
import json
import uuid
from fastapi import FastAPI
import redis
from config.binancefuture_kucoin_arb import LOG_DIR, TIMESTAMP, REDIS_HOST, REDIS_PORT, REDIS_QUEUE
from general.logger import setup_logger

app = FastAPI()
NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(NAME, os.path.join(LOG_DIR, f"{TIMESTAMP}_{NAME}.log"))
logger.info(f"init {NAME}")

# Initialize Redis connection
r = None

@app.on_event("startup")
async def startup_event():
    global r
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

@app.on_event("shutdown")
async def shutdown_event():
    global r
    if r:
        del r

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
        price: float
):
    logger.info(f'Send request: {symbol=}, {type=}, {side=}, {amount=}, {price=}')
    _id = uuid.uuid4().hex
    data = {
        "id": _id,
        "topic": "create",
        "symbol": symbol,
        "type": type,
        "side": side,
        "amount": amount,
        "price": price
    }

    r.rpush(REDIS_QUEUE, json.dumps(data))

    logger.info(f"{_id}: created!")
    return {_id: "Created"}

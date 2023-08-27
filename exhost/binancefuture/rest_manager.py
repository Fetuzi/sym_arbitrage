import os
import time
import json
import uuid
import pika
from fastapi import FastAPI, HTTPException
from config.binancefuture_kucoin_arb import LOG_DIR, TIMESTAMP, RABBIT_MQ_HOST, RABBIT_MQ_PORT, BINANCE_RABBIT_MQ
from logger import setup_logger


app = FastAPI()

logger = setup_logger(__name__, os.path.join(LOG_DIR, f"{TIMESTAMP}_{__name__}.log"))
logger.info(f"init {__name__}")


@app.on_event("startup")
async def startup_event():
    global connection, channel
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_MQ_HOST, port=RABBIT_MQ_PORT))
    channel = connection.channel()
    channel.queue_declare(queue=BINANCE_RABBIT_MQ, durable=True)

@app.on_event("shutdown")
async def shutdown_event():
    global connection
    if connection:
        connection.close()

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
    channel.basic_publish(exchange='',
                          routing_key=BINANCE_RABBIT_MQ,
                          body=json.dumps(data).encode('utf-8'),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))
    logger.info(f"{_id}: created!")
    return {_id: "Created"}


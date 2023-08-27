import os
import ccxt
import pika
import json

from logger import setup_logger
from config.binancefuture_kucoin_arb import (LOG_DIR, TIMESTAMP, BINANCE_API_KEY, BINANCE_SECRET_KEY,
                                             RABBIT_MQ_HOST, RABBIT_MQ_PORT, BINANCE_RABBIT_MQ)

binance = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET_KEY,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        }
})


NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(NAME, os.path.join(LOG_DIR, f"{TIMESTAMP}_{NAME}.log"))
logger.info(f"init {NAME}")


def callback(ch, method, properties, body):
    """Callback function to process the message from the queue."""
    data = json.loads(body)
    logger.info(f" [x] Received {data}")
    if data["topic"] == "create":
        order = binance.create_order(data["symbol"], data["type"], data["side"], data["amount"], data["price"])
        logger.info(f"{order=}")
    else:
        logger.error("Undefined topic.")
    logger.info(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_worker():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_MQ_HOST, port=RABBIT_MQ_PORT))
    channel = connection.channel()

    channel.queue_declare(queue=BINANCE_RABBIT_MQ, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=BINANCE_RABBIT_MQ, on_message_callback=callback)

    logger.info(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == "__main__":
    start_worker()






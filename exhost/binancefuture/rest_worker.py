import os
import ccxt
import pika
import json
import time

from logger import setup_logger
from config.binancefuture_kucoin_arb import (LOG_DIR, TIMESTAMP, BINANCE_API_KEY, BINANCE_SECRET_KEY,
                                             RABBIT_MQ_HOST, RABBIT_MQ_PORT, RABBIT_MQ_REST_NAME)

binance = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET_KEY,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        }
})


logger = setup_logger(__name__, os.path.join(LOG_DIR, f"{TIMESTAMP}_{__name__}.log"))
logger.info(f"init {__name__}")


def callback(ch, method, properties, body):
    """Callback function to process the message from the queue."""
    data = json.loads(body)
    logger.info(f" [x] Received {data['message']}")
    time.sleep(1)
    logger.info(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_worker():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_MQ_HOST, port=RABBIT_MQ_PORT))
    channel = connection.channel()

    channel.queue_declare(queue=RABBIT_MQ_REST_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=RABBIT_MQ_REST_NAME, on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == "__main__":
    start_worker()






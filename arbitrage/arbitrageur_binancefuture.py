import os
import time
import traceback
import json
import redis
import requests

from general.logger import setup_logger
from config.binancefuture_okx_arb import TIMESTAMP, LOG_DIR, RECORDING_COIN, REDIS_HOST, REDIS_PORT, REDIS_PUBSUB, REST_MANAGER, BINANCE, BINANCE_LTC_USDT, OKX, TIME_IN_EXCHANGE, TIME_IN_ARB

NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(NAME, os.path.join(LOG_DIR, f"{TIMESTAMP}_{NAME}_{RECORDING_COIN}.log"))
logger.info(f"init {NAME}")


class SymmetricArbitrage:
    TRANS_STRATEGY = 1.001801531302 * 1.0002
    CREATE_ORDER = REST_MANAGER + '/create_order'

    def __init__(self):
        # status
        self.time = int(time.time() * 1000)
        self.contract = {BINANCE: 0, OKX: 0}
        self.ask = {BINANCE: 0, OKX: 0}
        self.bid = {BINANCE: 0, OKX: 0}
        self.exchange_time = {BINANCE: int(time.time() * 1000), OKX: int(time.time() * 1000)}

        # Redis
        self.redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        self.redis_channel = REDIS_PUBSUB

        # Rest Manager


    def run(self):
        pubsub = None
        try:
            pubsub = self.redis_conn.pubsub()
            pubsub.subscribe(self.redis_channel)

            # Skip the first message (the subscription confirmation)
            confirmation = next(pubsub.listen())
            logger.info(f'Confirmation: {confirmation}')

            for message in pubsub.listen():
                data = json.loads(message['data'].decode('utf-8'))
                logger.info(f'{data=}')

        except Exception as e:
            logger.info(f'Error occurred: {traceback.format_exc()}')
        finally:
            if pubsub:
                pubsub.close()

    def _update(self, data):
        self.time = int(time.time() * 1000)

        self.ask[data['ex']] = data['a']
        self.bid[data['ex']] = data['b']
        self.exchange_time[data['ex']] = data['t']

    def _arb(self):
        time_gap = self.time - min(self.exchange_time[BINANCE], self.exchange_time[OKX]) < TIME_IN_ARB
        time_gap = time_gap and abs(self.exchange_time[BINANCE] - self.exchange_time[OKX]) < TIME_IN_EXCHANGE
        if time_gap and self.bid[BINANCE] > self.ask[OKX] * self.TRANS_STRATEGY:
            logger.info(f"arbitrage: {self.bid[BINANCE]=}, {self.ask[OKX]=}")
            response = requests.get(self.CREATE_ORDER, params={
                "symbol": BINANCE_LTC_USDT,
                "type": "market",
                "side": "sell",
                "amount": 1.0,
                "price": self.bid[BINANCE]
            })



    def _liq(self):
        pass

    def _risk(self):
        pass


if __name__ == '__main__':
    sym = SymmetricArbitrage()
    sym.run()
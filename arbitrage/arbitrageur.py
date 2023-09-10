import os
import time
import traceback
import json
import redis
import requests

from general.logger import setup_logger
from config.binancefuture_okx_arb import TIMESTAMP, LOG_DIR, RECORDING_COIN, REDIS_HOST, REDIS_PORT, REDIS_PUBSUB, REST_MANAGER, BINANCE, OKX, TIME_IN_EXCHANGE, TIME_IN_ARB

NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(NAME, os.path.join(LOG_DIR, f"{TIMESTAMP}_{NAME}_{RECORDING_COIN}.log"))
logger.info(f"init {NAME}")


class SymmetricArbitrage:
    TRANS_STRATEGY = 1.001801531302 * 1.0002
    CREATE_ORDER = REST_MANAGER + '/create_order'

    def __init__(self, ex, symbol, sides):
        # symmetric parameter (either A or B)
        self.ex = ex
        self.symbol = symbol
        self.sides = sides

        # status
        self.time = int(time.time() * 1000)
        self.contract = 0  # BINANCE contract
        self.ask = {BINANCE: 0, OKX: 0}
        self.bid = {BINANCE: 0, OKX: 0}
        self.exchange_time = {BINANCE: int(time.time() * 1000), OKX: int(time.time() * 1000)}

        # Redis
        self.redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        self.redis_channel = REDIS_PUBSUB

    def _execute_order(self, side, dry_run):
        response = requests.get(self.CREATE_ORDER, params={
            "symbol": self.symbol,
            "type": "market",
            "side": side,
            "amount": 1.0,
            "price": (self.ask[self.ex] + self.bid[self.ex]) / 2,  # Pseudo Price for market order
            "dry_run": dry_run
        })
        logger.info(f"{response=}")
        increment = 1 if side == 'buy' else -1
        self.contract = self.contract if dry_run else self.contract + increment

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
                self._update(data)
                self._arb()
                self._liq()

        except Exception as e:
            logger.info(f'Error occurred: {traceback.format_exc()}')
        finally:
            if pubsub:
                pubsub.close()

    def _risk(self):
        if abs(self.contract) >= 1:
            return False
        return True

    def _update(self, data):
        self.time = int(time.time() * 1000)

        self.ask[data['ex']] = data['a']
        self.bid[data['ex']] = data['b']
        self.exchange_time[data['ex']] = data['t']

    def _arb(self):
        time_gap = self.time - min(self.exchange_time[BINANCE], self.exchange_time[OKX]) < TIME_IN_ARB
        time_gap = time_gap and abs(self.exchange_time[BINANCE] - self.exchange_time[OKX]) < TIME_IN_EXCHANGE
        dry_run = not self._risk()  # If pass risk check, not use dry_run
        if time_gap and self.bid[BINANCE] > self.ask[OKX] * self.TRANS_STRATEGY:
            logger.info(f"arbitrage: {self.bid[BINANCE]=}, {self.ask[OKX]=}")
            side = self.sides[0]
            self._execute_order(side, dry_run)
        if time_gap and self.bid[OKX] > self.ask[BINANCE] * self.TRANS_STRATEGY:
            logger.info(f"arbitrage: {self.bid[BINANCE]=}, {self.ask[OKX]=}")
            side = self.sides[0]
            self._execute_order(side, dry_run)

    def _liq(self):
        if self.contract > 0 and self.bid[BINANCE] >= self.ask[OKX]:
            side = self.sides[0]
            logger.info(f"liquidate: {side} 1 contract")
            self._execute_order(side, False)  # Price is arbitrary
        if self.contract < 0 and self.ask[BINANCE] <= self.bid[OKX]:
            side = self.sides[1]
            logger.info(f"liquidate: {side} 1 in contract")
            self._execute_order(side, False)  # Price is arbitrary



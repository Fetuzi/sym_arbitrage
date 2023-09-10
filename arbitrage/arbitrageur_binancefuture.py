from arbitrage.arbitrageur import SymmetricArbitrage
from config.binancefuture_okx_arb import BINANCE, BINANCE_LTC_USDT, TOKYO_SIDE


if __name__ == '__main__':
    sym = SymmetricArbitrage(BINANCE, BINANCE_LTC_USDT, TOKYO_SIDE)
    sym.run()

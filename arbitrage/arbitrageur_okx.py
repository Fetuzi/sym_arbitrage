from arbitrage.arbitrageur import SymmetricArbitrage
from config.binancefuture_okx_arb import OKX, OKX_LTC_USDT, HK_SIDE

if __name__ == '__main__':
    sym = SymmetricArbitrage(OKX, OKX_LTC_USDT, HK_SIDE)
    sym.run()

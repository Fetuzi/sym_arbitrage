import ccxt.async_support as ccxt
from config.binancefuture_kucoin_arb import BINANCE_API_KEY, BINANCE_SECRET_KEY

binance = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET_KEY,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        }
})


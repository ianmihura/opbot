from datetime import datetime
from urllib.parse import quote
import os


def coingecko_history(
        symbol: str,
        start_date: datetime = datetime(2013, 12, 31),
        end_date: datetime = datetime.now()) -> str:
    """Coin history, in USD. Granularity automatic (1 day). 
    Useful for market volume
    Symbol example: 'bitcoin' or 'ethereum'
    Default timestamps: Start (December 31, 2020), End (now)
    """
    s = quote(symbol)
    start = int(start_date.timestamp())
    end = int(end_date.timestamp())
    return f'https://api.coingecko.com/api/v3/coins/{s}/market_chart/range?vs_currency=usd&from={start}&to={end}'


def deribit_history(
        symbol: str,
        resolution: str = '60',
        start_date: datetime = datetime(2020, 12, 31),
        end_date: datetime = datetime.now()) -> str:
    """Contract symbol price history.
    Symbol example: 'BTC-1JUL22-12000-C'
    Resolution: int (minutes) or 1D
    Default timestamps: Start (December 31, 2020), End (now)
    """
    s = quote(symbol)
    r = quote(resolution)
    start = int(start_date.timestamp() * 1000)
    end = int(end_date.timestamp() * 1000)
    return f'https://www.deribit.com/api/v2/public/get_tradingview_chart_data?start_timestamp={start}&end_timestamp={end}&instrument_name={s}&resolution={r}'


def deribit_ticker(symbol: str) -> str:
    """Ticker metadata, greeks and IV. 
    Useful for Benchmark greeks & iv calculations
    Symbol example: 'BTC-1JUL22-12000-C'
    """
    s = quote(symbol)
    return f'https://www.deribit.com/api/v2/public/ticker?instrument_name={s}'


def deribit_all_instruments(
        symbol: str,
        kind: str = 'option',
        expired: bool = False) -> str:
    """Get all instruments.
    Symbol example: 'BTC'
    Kind: 'option' or 'future'
    Expired: 'false' or 'true'
    """
    s = quote(symbol)
    e = 'true' if expired else 'false'
    k = quote(kind)
    return f'https://www.deribit.com/api/v2/public/get_instruments?currency={s}&expired={e}&kind={k}'


def glassnode_history(symbol: str) -> str:
    """Coin price history, in usd, pre 2011, amazing granularity (1h).
    Useful for price history
    Symbol example: 'BTC' or 'ETH'
    """
    GLASS_API = os.environ.get("GLASS_API")
    s = quote(symbol)
    return f'https://api.glassnode.com/v1/metrics/market/price_usd_ohlc?api_key={GLASS_API}&a={s}&i=1h'


def glassnode_tx(symbol: str) -> str:
    """Total amount of on-chain tx
    Symbol example: 'BTC' or 'ETH'
    """
    GLASS_API = os.environ.get("GLASS_API")
    s = quote(symbol)
    return f'https://api.glassnode.com/v1/metrics/transactions/count?api_key={GLASS_API}&a={s}'


def glassnode_volume(symbol: str) -> str:
    """Total volume of coin transacted on-chain
    Symbol example: 'BTC' or 'ETH'
    """
    GLASS_API = os.environ.get("GLASS_API")
    s = quote(symbol)
    return f'https://api.glassnode.com/v1/metrics/transactions/transfers_volume_sum?api_key={GLASS_API}&a={s}'


def glassnode_active(symbol: str) -> str:
    """Addresses active in the last 1 year (send/recieve)
    Symbol example: 'BTC' or 'ETH'
    """
    GLASS_API = os.environ.get("GLASS_API")
    s = quote(symbol)
    return f'https://api.glassnode.com/v1/metrics/supply/active_more_1y_percent?api_key={GLASS_API}&a={s}'


def polygon_history(
        symbol: str,
        start_date: str = datetime(2019, 12, 31),
        end_date: str = datetime.now()) -> str:
    """Coin history, in USD. Max 2 years.
    Useful for granular data last 2 years
    Symbol example: 'BTC' or 'ETH'
    Default timestamps: Start (December 31, 2021), End (now)
    """
    POLY_API = os.environ.get("POLY_API")
    s = quote(symbol)
    s_date = start_date.strftime("%Y-%m-%d")
    e_date = end_date.strftime("%Y-%m-%d")
    return f'https://api.polygon.io/v2/aggs/ticker/X:{s}USD/range/1/hour/{s_date}/{e_date}?adjusted=true&sort=asc&limit=50000&apiKey={POLY_API}'
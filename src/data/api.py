from datetime import datetime
import requests
from urllib.parse import quote
import json


def coingecko_symbol_history(
        symbol: str,
        start_date: datetime = datetime(2020, 12, 31),
        end_date: datetime = datetime.now()) -> str:
    """Coin history, in USD.
    Symbol example: 'bitcoin' or 'ethereum'
    Default timestamps: Start (December 31, 2020), End (now)
    """
    s = quote(symbol)
    start = int(start_date.timestamp())
    end = int(end_date.timestamp())
    return f'https://api.coingecko.com/api/v3/coins/{s}/market_chart/range?vs_currency=usd&from={start}&to={end}'


def deribit_symbol_history(
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


def deribit_vol_index(
        symbol: str,
        resolution: str = '3600',
        start_date: datetime = datetime(2020, 12, 31),
        end_date: datetime = datetime.now()) -> str:
    """Volatility history.
    Symbol example: 'BTC'
    Resolution: int (seconds) or 1D
    Default timestamps: Start (December 31, 2020), End (now)
    """
    r = quote(str(resolution))
    s = quote(symbol)
    start = int(start_date.timestamp() * 1000)
    end = int(end_date.timestamp() * 1000)
    return f'https://www.deribit.com/api/v2/public/get_volatility_index_data?currency={s}&start_timestamp={start}&end_timestamp={end}&resolution={r}'


# Not used yet
def deribit_ticker(symbol: str) -> str:
    """Ticker metadata, greeks and IV.
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


def get_deribit_symbols(coin: str) -> list:
    try:
        api_url = deribit_all_instruments(coin)
        raw = requests.get(api_url)
        data = raw.json()['result']
        symbols = [s['instrument_name'] for s in data if s['kind'] == 'option']

        print('Get Symbols -- Query successful')
        return symbols
    except BaseException:
        print('Get Symbols -- Query fail')
        if raw:
            print(raw.json())
        return []


def get_deribit_symbol(symbol: str) -> dict:
    try:
        api_url = deribit_symbol_history(symbol)
        raw = requests.get(api_url)
        data = raw.json()['result']

        print(symbol, '-- Price history -- Query successful')
        return data
    except BaseException:
        print(symbol, '-- Price history -- Query fail')
        if raw:
            print(raw.json())
        return {}


def get_deribit_vol(symbol: str, end_date=datetime.now()) -> dict:
    try:
        api_url = deribit_vol_index(symbol, end_date=end_date)
        raw = requests.get(api_url)
        data = raw.json()['result']

        print(symbol, end_date, '-- Volatility history -- Query successful')

        if data['continuation']:
            new_end_date = datetime.fromtimestamp(data['continuation'] / 1000)
            data['data'] += get_deribit_vol(symbol, new_end_date)['data']

        return data
    except BaseException:
        print(symbol, end_date, '-- Volatility history -- Query fail')
        if raw:
            print(raw.json())
        return {}


def get_coingecko_symbol(symbol: str) -> dict:
    try:
        api_url = coingecko_symbol_history(symbol)
        raw = requests.get(api_url)
        data = raw.json()

        print(symbol, '-- Price history -- Query successful')
        return data
    except BaseException:
        print(symbol, '-- Price history -- Query fail')
        if raw:
            print(raw.json())
        return {}


def save_deribit_symbols(coin):
    symbols = get_deribit_symbols(coin)
    symbols = symbols[:10]  # for test

    data = dict(zip(symbols, map(get_deribit_symbol, symbols)))

    with open(f'./data/raw/deribit_symbols_{coin}.json', 'w') as raw:
        json.dump(data, raw)


def save_deribit_vol(symbol):
    data = get_deribit_vol(symbol)
    with open(f'./data/raw/deribit_vol_{symbol}.json', 'w') as raw:
        json.dump(data, raw)


def save_coingecko_symbol(symbol):
    data = get_coingecko_symbol(symbol)
    with open(f'./data/raw/coingecko_symbol_{symbol}.json', 'w') as raw:
        json.dump(data, raw)


def main():
    save_deribit_symbols('BTC')
    save_deribit_symbols('ETH')

    save_deribit_vol('BTC')
    save_deribit_vol('ETH')

    save_coingecko_symbol('bitcoin')
    save_coingecko_symbol('ethereum')


if __name__ == "__main__":
    main()

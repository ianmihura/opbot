from datetime import datetime
import os
import time
import requests
import json
import api_endpoints
import functools
from itertools import repeat
import logging


symbols = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH'
}


def safe_query(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            value = func(*args, **kwargs)
            return value
        except BaseException:
            logger = logging.getLogger(__name__)
            logger.info(f'{func.__name__} -- Query fail')
            return {}
    return wrapper


@safe_query
def get_coingecko_symbol(symbol: str, start: datetime) -> dict:
    api_url = api_endpoints.coingecko_history(symbol, start_date=start)
    raw = requests.get(api_url)
    data = raw.json()

    return data


@safe_query
def get_deribit_symbols(coin: str) -> list:
    api_url = api_endpoints.deribit_all_instruments(coin)
    raw = requests.get(api_url)
    data = raw.json()['result']
    symbols = [s['instrument_name'] for s in data if s['kind'] == 'option']

    # TODO: save other data as creation date, ticker size, min trade size, etc...
    return symbols


@safe_query
def get_deribit_symbol(symbol: str, start: datetime) -> dict:
    api_url = api_endpoints.deribit_history(symbol, start_date=start)
    raw = requests.get(api_url)
    data = raw.json()['result']

    return data


@safe_query
def get_deribit_ticker(symbol: str) -> dict:
    api_url = api_endpoints.deribit_ticker(symbol)
    raw = requests.get(api_url)
    data = raw.json()['result']

    return data


@safe_query
def get_deribit_volatility(symbol: str, start_date: datetime, end_date=datetime.now()) -> dict:
    api_url = api_endpoints.deribit_volatility(symbol, start_date=start_date, end_date=end_date)
    raw = requests.get(api_url)
    data = raw.json()['result']

    if data['continuation']:
        new_end_date = datetime.fromtimestamp(data['continuation'] / 1000)
        data['data'] += get_deribit_volatility(symbol, new_end_date)['data']

    return data


@safe_query
def get_glassnode_active(symbol: str) -> dict:
    api_url = api_endpoints.glassnode_active(symbol)
    raw = requests.get(api_url)
    data = raw.json()

    return data


@safe_query
def get_glassnode_volume(symbol: str) -> dict:
    api_url = api_endpoints.glassnode_volume(symbol)
    raw = requests.get(api_url)
    data = raw.json()

    return data


@safe_query
def get_glassnode_tx(symbol: str) -> dict:
    api_url = api_endpoints.glassnode_tx(symbol)
    raw = requests.get(api_url)
    data = raw.json()

    return data


@safe_query
def get_glassnode_history(symbol: str, start: datetime) -> dict:
    api_url = api_endpoints.glassnode_history(symbol, start)
    raw = requests.get(api_url)
    data = raw.json()

    return data


@safe_query
def get_polygon_symbol(symbol: str, start_date: datetime = datetime(2019, 12, 31)) -> dict:
    time.sleep(60/5) # max: 5 requests per second
        
    api_url = api_endpoints.polygon_history(symbol, start_date = start_date)
    raw = requests.get(api_url)
    data = raw.json()

    last_timestamp = data['results'][-1]['t']/1000
    if last_timestamp < datetime.timestamp(datetime.now().replace(hour=0)):
        new_start_date = datetime.fromtimestamp(last_timestamp)
        data['results'] += get_polygon_symbol(symbol, new_start_date)['results']

    return data


def save_asset(coin: str, folder: str, data):
    with open(f'./data/raw/{folder}/{coin}.json', 'w') as raw:
        json.dump(data, raw)


def mkdir_if_exists(path):
    """This function creates a directory, specified in path if it doesn't exist.
    If it does, it does nothing.
    """
    if not os.path.exists(path):
        os.mkdir(path)


def main(start: datetime, end: datetime):
    mkdir_if_exists('./data/raw/onchain')
    mkdir_if_exists('./data/raw/onchain/tx')
    mkdir_if_exists('./data/raw/onchain/volume')
    mkdir_if_exists('./data/raw/onchain/active')
    mkdir_if_exists('./data/raw/contracts')
    mkdir_if_exists('./data/raw/contracts/metadata')
    mkdir_if_exists('./data/raw/contracts/data')
    mkdir_if_exists('./data/raw/underlying')
    mkdir_if_exists('./data/raw/underlying/price')
    mkdir_if_exists('./data/raw/underlying/volume')
    mkdir_if_exists('./data/raw/underlying/recent')
    mkdir_if_exists('./data/raw/underlying/dvol')

    for coin_name, coin in symbols.items():
        contracts = get_deribit_symbols(coin)

        save_asset(coin, 'onchain/tx', get_glassnode_tx(coin))
        save_asset(coin, 'onchain/volume', get_glassnode_volume(coin))
        save_asset(coin, 'onchain/active', get_glassnode_active(coin))
        save_asset(coin, 'contracts/metadata', dict(zip(contracts,
            map(get_deribit_ticker, contracts))))
        save_asset(coin, 'contracts/data', dict(zip(contracts,
            map(get_deribit_symbol, contracts, repeat(start)))))
        save_asset(coin, 'underlying/price', get_glassnode_history(coin, start))
        save_asset(coin, 'underlying/volume', get_coingecko_symbol(coin_name))
        save_asset(coin, 'underlying/recent', get_polygon_symbol(coin, start_date=start))
        save_asset(coin, 'underlying/dvol', get_deribit_volatility(coin, start))


if __name__ == "__main__":
    main()
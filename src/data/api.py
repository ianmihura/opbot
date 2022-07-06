from datetime import datetime
import os
import time
import requests
import json
import api_endpoints
import functools


symbols = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH'
}


def safe_query(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # print('\n')
            # start_time = time.perf_counter()
            value = func(*args, **kwargs)
            # end_time = time.perf_counter()
            # run_time = end_time - start_time
            # print(f"Query {func.__name__!r} in {run_time:.4f} secs")
            return value
        except BaseException:
            print(f'{func.__name__} -- Query fail')
            return {}
    return wrapper


@safe_query
def get_coingecko_symbol(symbol: str) -> dict:
    api_url = api_endpoints.coingecko_history(symbol)
    raw = requests.get(api_url)
    data = raw.json()

    print(symbol, '-- Price history -- Query successful')
    return data


@safe_query
def get_deribit_symbols(coin: str) -> list:
    api_url = api_endpoints.deribit_all_instruments(coin)
    raw = requests.get(api_url)
    data = raw.json()['result']
    symbols = [s['instrument_name'] for s in data if s['kind'] == 'option']

    # TODO: save other data as creation date, ticker size, min trade size, etc...

    print('Get Symbols -- Query successful')
    return symbols


@safe_query
def get_deribit_symbol(symbol: str) -> dict:
    api_url = api_endpoints.deribit_history(symbol)
    raw = requests.get(api_url)
    data = raw.json()['result']

    print(symbol, '-- Price history -- Query successful')
    return data


@safe_query
def get_deribit_ticker(symbol: str) -> dict:
    api_url = api_endpoints.deribit_ticker(symbol)
    raw = requests.get(api_url)
    data = raw.json()['result']

    print(symbol, '-- Ticker -- Query successful')
    return data


@safe_query
def get_glassnode_active(symbol: str) -> dict:
    api_url = api_endpoints.glassnode_active(symbol)
    raw = requests.get(api_url)
    data = raw.json()

    print(symbol, '-- Active addresses -- Query successful')
    return data


@safe_query
def get_glassnode_volume(symbol: str) -> dict:
    api_url = api_endpoints.glassnode_volume(symbol)
    raw = requests.get(api_url)
    data = raw.json()

    print(symbol, '-- Volume on-chain -- Query successful')
    return data


@safe_query
def get_glassnode_tx(symbol: str) -> dict:
    api_url = api_endpoints.glassnode_tx(symbol)
    raw = requests.get(api_url)
    data = raw.json()

    print(symbol, '-- Transactions on-chain -- Query successful')
    return data


@safe_query
def get_glassnode_history(symbol: str) -> dict:
    api_url = api_endpoints.glassnode_history(symbol)
    raw = requests.get(api_url)
    data = raw.json()

    print(symbol, '-- Glassnode price history -- Query successful')
    return data


@safe_query
def get_polygon_symbol(symbol: str, start_date: datetime = datetime(2019, 12, 31)) -> dict:
    time.sleep(60/5) # max: 5 requests per second
        
    api_url = api_endpoints.polygon_history(symbol, start_date = start_date)
    raw = requests.get(api_url)
    data = raw.json()

    print(symbol, start_date, '-- Price history -- Query successful')

    last_timestamp = data['results'][-1]['t']/1000
    if last_timestamp < datetime.timestamp(datetime.now().replace(hour=0)):
        new_start_date = datetime.fromtimestamp(last_timestamp)
        data['results'] += get_polygon_symbol(symbol, new_start_date)['results']

    return data


def save_asset(coin: str, folder: str, data):
    with open(f'./data/raw/{folder}/{coin}.json', 'w') as raw:
        json.dump(data, raw)


def mkdir_if_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)


def main():
    mkdir_if_exists('./data/raw/contracts')
    mkdir_if_exists('./data/raw/contracts/data')
    mkdir_if_exists('./data/raw/contracts/metadata')
    mkdir_if_exists('./data/raw/underlying')
    mkdir_if_exists('./data/raw/underlying/coingecko')
    mkdir_if_exists('./data/raw/underlying/glassnode')
    mkdir_if_exists('./data/raw/underlying/polygon')
    mkdir_if_exists('./data/raw/onchain')
    mkdir_if_exists('./data/raw/onchain/active')
    mkdir_if_exists('./data/raw/onchain/volume')
    mkdir_if_exists('./data/raw/onchain/tx')

    for i in symbols:
        coin = symbols[i]
        
        contracts = get_deribit_symbols(coin)
        contracts = contracts[:10]  # for test

        save_asset(coin, 'onchain/tx', get_glassnode_tx(coin))
        save_asset(coin, 'onchain/volume', get_glassnode_volume(coin))
        save_asset(coin, 'onchain/active', get_glassnode_active(coin))
        save_asset(coin, 'contracts/metadata', dict(zip(contracts, map(get_deribit_ticker, contracts))))
        save_asset(coin, 'contracts/data', dict(zip(contracts, map(get_deribit_symbol, contracts))))
        save_asset(coin, 'underlying/glassnode', get_glassnode_history(coin))
        save_asset(coin, 'underlying/coingecko', get_coingecko_symbol(i))
        save_asset(coin, 'underlying/polygon', get_polygon_symbol(coin))


if __name__ == "__main__":
    main()
from datetime import datetime
import os
import time
import requests
import json
import dotenv
import api_endpoints
import functools


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


# TODO: deribit ticker


# TODO: glassnode_active


# TODO: glassnode_volume


# TODO: glassnode_tx


# TODO: glassnode_history


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


def save_coingecko_symbol(symbol: str):
    symbols = {
        'bitcoin': 'BTC',
        'ethereum': 'ETH'
    }
    data = get_coingecko_symbol(symbol)
    with open(f'./data/raw/underlying/{symbols[symbol]}.json', 'w') as raw:
        json.dump(data, raw)


def save_deribit_symbols(coin: str):
    symbols = get_deribit_symbols(coin)
    symbols = symbols[:10]  # for test

    data = dict(zip(symbols, map(get_deribit_symbol, symbols)))

    with open(f'./data/raw/contracts/{coin}.json', 'w') as raw:
        json.dump(data, raw)


# TODO: deribit ticker


# TODO: glassnode_active


# TODO: glassnode_volume


# TODO: glassnode_tx


# TODO: glassnode_history


def save_polygon_symbol(symbol: str):
    data = get_polygon_symbol(symbol)
    with open(f'./data/raw/underlying/{symbol}.json', 'w') as raw:
        json.dump(data, raw)


def main():
    dotenv.load_dotenv('.env')

    if not os.path.exists('./data/raw/contracts'):
        os.mkdir('./data/raw/contracts')
    if not os.path.exists('./data/raw/underlying'):
        os.mkdir('./data/raw/underlying')

    save_deribit_symbols('BTC')
    save_deribit_symbols('ETH')

    save_polygon_symbol('BTC')
    save_polygon_symbol('ETH')


if __name__ == "__main__":
    # main()

    print(get_coingecko_symbol('bitcoin')['total_volumes'])

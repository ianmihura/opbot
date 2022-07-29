import json
import os
import time
import functools
import pandas as pd
import numpy as np
from datetime import datetime

import finance
from tqdm import tqdm


# TODO: add DVOL to underlying
# TODO: interploate u_volume to be similar to recet


def filter_output_df(condition, column: str):
    """Filters a DataFrame by a condition on a specific column.
    Args:
        condition: a function that takes a value and returns a boolean
        column: the column to filter on
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            df = func(*args, **kwargs)
            if column not in df.columns:
                raise ValueError(f'Column {column} not in DataFrame')
            return df[df[column].apply(condition)]
        return wrapper
    return decorator


def filter_between(inp_df: pd.DataFrame, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Filters a DataFrame by a start and end date.
    Args:
        inp_df: the DataFrame to filter
        start_date: the start date
        end_date: the end date
    """
    start_timestamp = start_date.timestamp()
    end_timestamp = end_date.timestamp()
    return inp_df[(inp_df.index >= start_timestamp) & (inp_df.index <= end_timestamp)]


def get_24h_data(data: list) -> np.ndarray:
    return np.array([[d/24]*24 for d in data]).flatten()


def get_24h_timestamps(timestamps: list) -> list:
    all_timestamps = np.array([[datetime.fromtimestamp(t)]*24 for t in timestamps]).flatten()
    return [datetime.timestamp(d.replace(hour=i%24)) for i,d in enumerate(all_timestamps)]


def get_underlying_recent(coin: str) -> pd.DataFrame:
    """Returns useful data from underlying/recent folder. Polygon API.
    Returns: price, volume, volume weighted, transactions; by timestamp (1h)
    """
    with open(f'./data/raw/underlying/recent/{coin}.json') as json_file:
        data = json.load(json_file)

    u_prices = [d['c'] for d in data['results']]
    u_timestamps = [d['t']/1000 for d in data['results']]
    u_volumes = [d['v'] for d in data['results']]
    u_transactions = [d['n'] for d in data['results']]

    zipped = list(zip(u_timestamps, u_prices, u_volumes, u_transactions))
    return pd.DataFrame(zipped, columns=['t', 'recent_price', 'recent_volume', 'recent_transaction']).set_index('t')


def get_underlying_price(coin: str) -> pd.DataFrame:
    """Returns useful data from underlying/price folder. Glassnode API.
    Returns: open, high, low, close; by timestamp (1h)
    """
    with open(f'./data/raw/underlying/price/{coin}.json') as json_file:
        data = json.load(json_file)

    u_timestamps = [d['t'] for d in data]
    u_open = [d['o']['o'] for d in data]
    u_high = [d['o']['h'] for d in data]
    u_low = [d['o']['l'] for d in data]
    u_close = [d['o']['c'] for d in data]

    zipped = list(zip(u_timestamps, u_open, u_high, u_low, u_close))
    return pd.DataFrame(zipped, columns=['t', 'u_open', 'u_high', 'u_low', 'u_close']).set_index('t')

def get_underlying_volume(coin: str) -> pd.DataFrame:
    """Returns useful data from underlying/volume folder. Coingecko API.
    Returns: volume by timestamp (daily)
    """
    with open(f'./data/raw/underlying/volume/{coin}.json') as json_file:
        data = json.load(json_file)

    correct_time = lambda x: datetime.fromtimestamp(x/1000).replace(hour=0).timestamp()
    u_timestamps = [correct_time(d[0]) for d in data['total_volumes']]
    u_volumes = [d[1] for d in data['total_volumes']]

    all_volumes = get_24h_data(u_volumes)
    all_timestamps = get_24h_timestamps(u_timestamps)

    zipped = list(zip(all_timestamps, all_volumes))
    return pd.DataFrame(zipped, columns=['t', 'u_volume']).set_index('t')


def get_onchain_tx(coin: str) -> pd.DataFrame:
    """Returns useful data from onchain/tx folder.
    Returns: tx by timestamp
    """
    with open(f'./data/raw/onchain/tx/{coin}.json') as json_file:
        data = json.load(json_file)

    u_timestamps = [d['t'] for d in data]
    u_tx = [d['v'] for d in data]

    all_tx = get_24h_data(u_tx)
    all_timestamps = get_24h_timestamps(u_timestamps)

    zipped = list(zip(all_timestamps, all_tx))
    return pd.DataFrame(zipped, columns=['t', 'chain_tx']).set_index('t')


def get_onchain_volume(coin: str) -> pd.DataFrame:
    """Returns useful data from onchain/volume folder.
    Returns: volume by timestamp
    """
    with open(f'./data/raw/onchain/volume/{coin}.json') as json_file:
        data = json.load(json_file)

    u_timestamps = [d['t'] for d in data]
    u_volumes = [d['v'] for d in data]

    all_volumes = get_24h_data(u_volumes)
    all_timestamps = get_24h_timestamps(u_timestamps)

    zipped = list(zip(all_timestamps, all_volumes))
    return pd.DataFrame(zipped, columns=['t', 'chain_volume']).set_index('t')


def get_contract_data(coin: str) -> pd.DataFrame:
    """Returns useful data from contracts/data folder
    Returns: contract data(volume, price) by timestamp, contract
    """
    with open(f'./data/raw/contracts/data/{coin}.json') as json_file:
        data = json.load(json_file)
    contracts = list(data.keys())
    has_data = [bool(data[c]['ticks']) for c in contracts]
    contracts = [c for i, c in enumerate(contracts) if has_data[i]]

    c_v = [data[c]['volume'] for c in contracts]
    c_t = [map(lambda x: x/1000, data[c]['ticks']) for c in contracts]
    c_o = [data[c]['open'] for c in contracts]
    c_l = [data[c]['low'] for c in contracts]
    c_h = [data[c]['high'] for c in contracts]
    c_c = [data[c]['close'] for c in contracts]

    c_name_split = [c.split('-') for c in contracts]

    get_timestamp = lambda d: time.mktime(datetime.strptime(d + '-10',"%d%b%y-%H").timetuple())
    c_expiration = [get_timestamp(c[1]) for c in c_name_split]
    c_strike = [int(c[2]) for c in c_name_split]
    c_is_call = [c[3] == 'C' for c in c_name_split]

    c_zip = lambda i: list(zip(c_t[i], c_v[i], c_o[i], c_l[i], c_h[i], c_c[i]))
    c_data = [c_zip(i) for i, c in enumerate(contracts)]
    
    keys_names = ['contract', 'expiration', 'strike', 'is_call']
    keys = list(zip(contracts, c_expiration, c_strike, c_is_call))

    columns = ['t', 'c_volume','c_open','c_low','c_high','c_close']
    c_dfs = [pd.DataFrame(data, columns=columns).set_index('t') for data in c_data]

    c_df = pd.concat(c_dfs, keys=keys, names=keys_names).reset_index()

    return c_df


def contract_metrics(row) -> dict:
    """Higher order function for contract_df.apply"""
    return finance.metrics(
        s = row['u_close'],
        k = row['strike'],
        r = 0,
        T = (abs((datetime.fromtimestamp(row['expiration']) - datetime.fromtimestamp(row.name)).days)+1) / 365, 
        sigma = row['volatility'],
        p = row['c_close'] * row['u_close'],
        is_call = bool(row['is_call']))


def preprocess(coin: str, start_date: datetime, end_date: datetime):
    """Preprocesses raw data by coin"""
    u_recent_df = get_underlying_recent(coin)
    u_recent_df = filter_between(u_recent_df, start_date, end_date)

    u_price_df = get_underlying_price(coin)
    u_price_df = filter_between(u_price_df, start_date, end_date)

    u_volume_df = get_underlying_volume(coin)
    u_volume_df = filter_between(u_volume_df, start_date, end_date)

    chain_tx_df = get_onchain_tx(coin)
    chain_tx_df = filter_between(chain_tx_df, start_date, end_date)

    chain_volume_df = get_onchain_volume(coin)
    chain_volume_df = filter_between(chain_volume_df, start_date, end_date)

    c_df = get_contract_data(coin)
    c_df = filter_between(c_df, start_date, end_date)

    underlying_df = u_price_df.join(u_volume_df).join(chain_tx_df).join(chain_volume_df).join(u_recent_df)
    underlying_df = underlying_df[~underlying_df.index.duplicated(keep='first')]

    print(f'{coin} -- Preprocess -- calculating volatility')
    underlying_df["volatility"] = finance.volatility(underlying_df["u_close"])
    contract_df = c_df.join(underlying_df, on='t').drop_duplicates()

    print(f'{coin} -- Preprocess -- calculating greeks')
    tqdm.pandas()
    metrics = contract_df.progress_apply(contract_metrics, axis=1, result_type='expand')
    contract_df = contract_df.join(metrics)

    print(f'{coin} -- Preprocess -- all calculations done')
    contract_df = contract_df.drop(columns=[
        'recent_price',
        'recent_volume',
        'recent_transaction',
        'u_open',
        'u_high',
        'u_low',
        'u_close',
        'u_volume',
        'chain_volume',
        'chain_tx'])
    underlying_df.fillna(0).to_csv(f'./data/interim/{coin}_underlying_data.csv')
    contract_df.fillna(0).to_csv(f'./data/interim/{coin}_contracts.csv')


def main(start: datetime, end: datetime):
    pd.set_option('display.float_format', lambda x: '%.6f' % x)
    
    underlying_dir = os.listdir(f'./data/raw/underlying/price')
    coins = [*map(lambda x: x.split('.')[0], underlying_dir)]

    [preprocess(coin, start, end) for coin in coins]


if __name__ == "__main__":
    main()

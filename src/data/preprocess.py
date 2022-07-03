from datetime import datetime
import json
import os
import time
import pandas as pd
import numpy as np

import finance


def get_underlying_data(coin: str):
    """Returns useful data from underlying folder
    Returns: price, volume, volume weighted, transactions; by timestamp
    """
    with open(f'./data/raw/underlying/{coin}.json') as json_file:
        data = json.load(json_file)

        u_prices = [d['c'] for d in data['results']]
        u_timestamps = [d['t'] for d in data['results']]
        u_volumes = [d['v'] for d in data['results']]
        u_volumes_w = [d['vw'] for d in data['results']] # volume weighted average price
        u_transactions = [d['n'] for d in data['results']] # number of transactions

    zipped = np.array(list(zip(u_timestamps, u_prices, u_volumes, u_volumes_w, u_transactions)))
    return pd.DataFrame(zipped, columns=['t', 'price', 'volume', 'volume_weighted', 'transaction']).set_index('t')


def get_volatility_data(coin: str):
    """Returns useful data from volatility folder
    Returns: volatility by timestamp
    """
    with open(f'./data/raw/volatility/{coin}.json') as json_file:
        data = json.load(json_file)

        v_timestamps = [v[0] for v in data['data']]
        v_volatility = [v[4] * 0.01 for v in data['data']]

    zipped = np.array(list(zip(v_timestamps, v_volatility)))
    return pd.DataFrame(zipped, columns=['t', 'volatility']).set_index('t')


def get_contract_data(coin):
    """Returns useful data from symbols folder
    Returns: contract data(volume, price) by timestamp, contract
    """
    with open(f'./data/raw/symbols/{coin}.json') as json_file:
        data = json.load(json_file)
        contracts = list(data.keys())
        has_data = [bool(data[c]['ticks']) for c in contracts]
        contracts = [c for i, c in enumerate(contracts) if has_data[i]]

        c_v = [data[c]['volume'] for c in contracts]
        c_t = [data[c]['ticks'] for c in contracts]
        c_o = [data[c]['open'] for c in contracts]
        c_l = [data[c]['low'] for c in contracts]
        c_h = [data[c]['high'] for c in contracts]
        c_c = [data[c]['close'] for c in contracts]

        c_name_split = [c.split('-') for c in contracts]

        get_timestamp = lambda d: time.mktime(datetime.strptime(d + '-10',"%d%b%y-%H").timetuple())
        c_expiration = [get_timestamp(c[1]) for c in c_name_split]
        c_expiration_days = [abs((datetime.fromtimestamp(exp) - datetime.now()).days) for exp in c_expiration]
        c_strike = [int(c[2]) for c in c_name_split]
        c_is_call = [c[3] == 'C' for c in c_name_split]

        c_zip = lambda i: np.array(list(zip(c_t[i], c_v[i], c_o[i], c_l[i], c_h[i], c_c[i])))
        c_data = [c_zip(i) for i, c in enumerate(contracts)]
    
    keys_names = ['contract', 'expiration', 'expiration_days', 'strike', 'is_call']
    keys = list(zip(contracts, c_expiration, c_expiration_days, c_strike, c_is_call))

    columns = ['t', 'c_volume','open','low','high','close']
    c_dfs = [pd.DataFrame(data, columns=columns).set_index('t') for data in c_data]

    c_df = pd.concat(c_dfs, keys=keys, names=keys_names).reset_index()

    return c_df


def compute_metrics(row):
    return finance.metrics(
        K = row['strike'],
        St = row['price'],
        v = row['volatility'], 
        r = 0,
        t = row['expiration_days'],
        type = 'c' if row['is_call'] else 'p', 
        market_price = row['close'] * row['price'])


def save_to_csv(coin, underlying_df, contract_df):
    underlying_df.to_csv(f'./data/interim/{coin}_underlying_data.csv')
    contract_df.to_csv(f'./data/interim/{coin}_contracts.csv')


def preprocess(coin):
    u_df = get_underlying_data(coin)
    v_df = get_volatility_data(coin)
    c_df = get_contract_data(coin)

    underlying_df = u_df.join(v_df)

    contract_df = c_df.join(underlying_df, on='t').drop_duplicates()
    metrics = contract_df.apply(compute_metrics, axis=1, result_type='expand')
    contract_df = contract_df.join(metrics)

    save_to_csv(coin, underlying_df, contract_df)


def main():

    underlying_dir = os.listdir(f'./data/raw/underlying')
    coins = [*map(lambda x: x.split('.')[0], underlying_dir)]

    [preprocess(coin) for coin in coins]


main()
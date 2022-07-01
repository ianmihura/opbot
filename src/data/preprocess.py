from datetime import datetime
import json
import os
import time
import pandas as pd
import numpy as np


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
    return pd.DataFrame(zipped, columns=['t', 'p', 'v', 'v_w', 'tx'])


def get_volatility_data(coin: str):
    """Returns useful data from volatility folder
    Returns: volatility by timestamp
    """
    with open(f'./data/raw/volatility/{coin}.json') as json_file:
        data = json.load(json_file)

        v_timestamps = [v[0] for v in data['data']]
        v_volatility = [v[4] for v in data['data']]

    zipped = np.array(list(zip(v_timestamps, v_volatility)))
    return pd.DataFrame(zipped, columns=['t', 'vol'])


def get_symbols_data(coin):
    """Returns useful data from symbols folder
    Returns: 
        Data: price(o,l,h,c), volume; by timestamp, 
        Metadata: name, expiration, strike, is_call
    """
    with open(f'./data/raw/symbols/{coin}.json') as json_file:
        data = json.load(json_file)
        contracts = list(data.keys())

        c_name_split = [c.split('-') for c in contracts]
        get_timestamp = lambda d: time.mktime(datetime.strptime(d + '-10',"%d%b%y-%H").timetuple())
        c_expiration = [get_timestamp(c[1]) for c in c_name_split]
        c_strike = [c[2] for c in c_name_split]
        c_is_call = [c[3] == 'C' for c in c_name_split]

        c_v = [data[c]['volume'] for c in contracts]
        c_t = [data[c]['ticks'] for c in contracts]
        c_o = [data[c]['open'] for c in contracts]
        c_l = [data[c]['low'] for c in contracts]
        c_h = [data[c]['high'] for c in contracts]
        c_c = [data[c]['close'] for c in contracts]

        make_contracts_zip = lambda i: np.array(list(zip(c_v[i], c_t[i], c_o[i], c_l[i], c_h[i], c_c[i])))

        c_zip = [make_contracts_zip(i) for i, c in enumerate(contracts) if c_t[i]]

        print(c_zip)


def preprocess(coin):
    u_df = get_underlying_data(coin)
    v_df = get_volatility_data(coin)
    
    underlying_df = v_df.set_index('t').join(u_df.set_index('t'))

    get_insert_list = lambda i, x: [coin, i, x['p'], x['v'], x['v_w'], x['tx'], x['vol']]
    
    # TODO: insert this in underlying data -- not in preprocess file
    print([get_insert_list(i, x) for i, x in underlying_df.iterrows()]) 







# TODO: greeks & iv of all symbols

"""Calculates all Black Scholes information: IV, greeks & fair value
    K : Strike Price
    St: Current Stock Price (underlying)
    v : Volatility % (sigma)
    r : Risk free rate %
    t : Time to expiration in days
    type: Type of option 'c' for call 'p' for put
        default: 'c'
    market_price : Market price of the contract
    """




# TODO: save preprocess data as json - in data/interim




def main():
    underlying_dir = os.listdir(f'./data/raw/underlying')
    coins = [*map(lambda x: x.split('.')[0], underlying_dir)]

    # [preprocess(coin) for coin in coins]


main()
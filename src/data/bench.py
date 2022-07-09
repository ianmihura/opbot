import time
from datetime import datetime
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import finance
import preprocess


def bench_greeks(coin):
    with open(f'./data/raw/contracts/metadata/{coin}.json') as json_file:
        data = json.load(json_file)

    contracts = list(data.keys())
    contracts = [contracts[i] for i,c in enumerate(contracts) if c.split('-')[3] == 'C']
    c_name_split = [c.split('-') for c in contracts]

    get_timestamp = lambda d: time.mktime(datetime.strptime(d + '-10',"%d%b%y-%H").timetuple())
    c_expiration = [get_timestamp(c[1]) for c in c_name_split]
    c_expiration_days = [abs((datetime.fromtimestamp(exp) - datetime.now()).days)+1 for exp in c_expiration]
    c_strike = [int(c[2]) for c in c_name_split]
    c_is_call = [c[3] == 'C' for c in c_name_split]

    df_greeks_o = pd.DataFrame([(
        data[c]['instrument_name'], 
        data[c]['greeks']['delta'], 
        data[c]['greeks']['gamma'], 
        data[c]['greeks']['vega'], 
        data[c]['greeks']['theta'], 
        data[c]['greeks']['rho'], 
        data[c]['mark_iv']/100) for c in contracts], 
        columns=['contract','delta_o','gamma_o','vega_o','theta_o','rho_o','iv_o']
        ).set_index('contract')

    n_greeks = [finance.metrics(
        c_strike[i],
        data[c]['underlying_price'],
        0.739,
        0,
        c_expiration_days[i],
        c_is_call[i],
        data[c]['mark_price'] * data[c]['underlying_price'] if data[c]['mark_price'] 
            else data[c]['last_price'] * data[c]['underlying_price'],
        data[c]['instrument_name']
    ) for i, c in enumerate(contracts)]
    n_greeks = list(zip(contracts, n_greeks))
    
    df_greeks_n = pd.DataFrame([(
        c[0],
        c[1]['delta'],
        c[1]['gamma'],
        c[1]['vega'],
        c[1]['theta'],
        c[1]['rho'],
        c[1]['iv']) for c in n_greeks], 
        columns=['contract','delta_n','gamma_n','vega_n','theta_n','rho_n','iv_n']
        ).set_index('contract')

    df_greeks = df_greeks_n.join(df_greeks_o)

    # df_greeks.to_csv(f'./data/interim/bench/greeks_{coin}.csv')
    # df_greeks = pd.read_csv(f'./data/interim/bench/greeks_{coin}.csv')

    print(df_greeks.to_string())

    # plot_same_axis(df_greeks, 'delta_n', 'delta_o')
    # plot_same_axis(df_greeks, 'gamma_n', 'gamma_o')
    # plot_same_axis(df_greeks, 'vega_n', 'vega_o')
    # plot_same_axis(df_greeks, 'theta_n', 'theta_o')
    # plot_same_axis(df_greeks, 'rho_n', 'rho_o')
    plot_same_axis(df_greeks, 'iv_n', 'iv_o')


def bench_volatility(coin):
    with open(f'./data/raw/underlying/dvol/{coin}.json') as json_file:
        data = json.load(json_file)['data']

    df_dvol = pd.DataFrame(data, columns=['t', 'open', 'high', 'low', 'close']).sort_values(by='t')
    df_dvol['t'] = df_dvol['t'].apply(lambda x: x/1000)
    df_dvol = df_dvol.set_index('t')

    df_price = preprocess.get_underlying_price(coin)
    df_price["volatility"] = finance.compute_volatility(df_price["u_close"])
    df_price['volatility'] = df_price['volatility'].apply(lambda x: x*100)

    df = df_price.join(df_dvol)

    df_cor = pd.DataFrame(list(zip(df.index, df['close'], df['volatility'])), columns=['t', 'close', 'volatility']).set_index('t')

    plot_same_axis(df, 'close', 'volatility')


def plot_dif_axis(df, col1, col2):
    fig, ax1 = plt.subplots()
    x = df.index
    y1 = df[col1]
    y2 = df[col2]

    ax2 = ax1.twinx()
    ax1.plot(x, y1, 'g-')
    ax2.plot(x, y2, 'b-')

    plt.show()


def plot_same_axis(df, col1, col2):
    plt.figure()
    x = df.index
    y1 = df[col1]
    y2 = df[col2]

    plt.plot(x, y1, 'g-')
    plt.plot(x, y2, 'b-')

    plt.show()


def plot_candles(df):
    plt.figure()

    width = .4
    width2 = .05

    up = df[df.close>=df.open]
    down = df[df.close<df.open]

    col1 = 'green'
    col2 = 'red'

    plt.bar(up.index,up.close-up.open,width,bottom=up.open,color=col1)
    plt.bar(up.index,up.high-up.close,width2,bottom=up.close,color=col1)
    plt.bar(up.index,up.low-up.open,width2,bottom=up.open,color=col1)

    plt.bar(down.index,down.close-down.open,width,bottom=down.open,color=col2)
    plt.bar(down.index,down.high-down.open,width2,bottom=down.open,color=col2)
    plt.bar(down.index,down.low-down.close,width2,bottom=down.close,color=col2)

    plt.xticks(rotation=45, ha='right')

    plt.show()


def main():
    bench_greeks('BTC')
    # bench_volatility('BTC')


if __name__ == '__main__':
    main()
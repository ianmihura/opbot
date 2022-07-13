import time
from datetime import datetime
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

import finance
import preprocess


def bench_greeks(coin):
    with open(f'./data/raw/contracts/metadata/{coin}.json') as json_file:
        data = json.load(json_file)

    contracts = list(data.keys())
    # contracts = [contracts[i] for i,c in enumerate(contracts) if int(c.split('-')[2]) < 50_000]
    contracts = [contracts[i] for i,c in enumerate(contracts) if c.split('-')[3] == 'C' and int(c.split('-')[2]) < 50_000]
    c_name_split = [c.split('-') for c in contracts]

    get_timestamp = lambda d: time.mktime(datetime.strptime(d + '-10',"%d%b%y-%H").timetuple())
    c_expiration = [get_timestamp(c[1]) for c in c_name_split]
    c_expiration_days = [abs((datetime.fromtimestamp(exp) - datetime.now()).days)+1+3 for exp in c_expiration]
    c_strike = [int(c[2]) for c in c_name_split]
    c_is_call = [c[3] == 'C' for c in c_name_split]

    df_greeks_o = pd.DataFrame([(
        data[c]['instrument_name'], 
        data[c]['greeks']['delta'], 
        data[c]['greeks']['gamma'], 
        data[c]['greeks']['vega'], 
        data[c]['greeks']['theta'], 
        data[c]['greeks']['rho'], 
        data[c]['mark_iv']/100,
        data[c]['mark_price'] * data[c]['underlying_price']) for c in contracts], 
        columns=['contract','delta_o','gamma_o','vega_o','theta_o','rho_o','iv_o','value_o']
        ).set_index('contract')
    
    iv = np.array([data[c]['mark_iv'] for c in contracts])
    price = np.array([data[c]['mark_price'] * data[c]['underlying_price'] for c in contracts])
    plot_3d_scatter(c_expiration_days, price, iv, 'expiration','price','iv')

    # n_greeks = [finance.metrics(
    #     data[c]['underlying_price'],
    #     c_strike[i],
    #     0,
    #     c_expiration_days[i]/365,
    #     0.739,
    #     data[c]['mark_price'] * data[c]['underlying_price'] if data[c]['mark_price'] else 0.0,
    #     c_is_call[i],
    # ) for i, c in enumerate(contracts)]
    # n_greeks = list(zip(contracts, n_greeks))

    # df_greeks_n = pd.DataFrame([(
    #     c[0],
    #     c[1]['delta'],
    #     c[1]['gamma'],
    #     c[1]['vega'],
    #     c[1]['theta'],
    #     c[1]['rho'],
    #     c[1]['iv'],
    #     c[1]['value']) for c in n_greeks], 
    #     columns=['contract','delta_n','gamma_n','vega_n','theta_n','rho_n','iv_n','value_n']
    #     ).set_index('contract')

    # df_greeks = df_greeks_n.join(df_greeks_o)

    # df_greeks.to_csv(f'./data/interim/bench/greeks_{coin}.csv')
    # df_greeks = pd.read_csv(f'./data/interim/bench/greeks_{coin}.csv')

    # print(df_greeks.to_string())

    # df_cor = get_df_cor(df_greeks, 'delta_n', 'delta_o', 'contract')
    # print(df_cor.corr()) # 0.994038
    # df_cor = get_df_cor(df_greeks, 'gamma_n', 'gamma_o', 'contract')
    # print(df_cor.corr()) # 0.850412
    # df_cor = get_df_cor(df_greeks, 'vega_n', 'vega_o', 'contract')
    # print(df_cor.corr()) # 0.995523
    # df_cor = get_df_cor(df_greeks, 'theta_n', 'theta_o', 'contract')
    # print(df_cor.corr()) # 0.907489
    # df_cor = get_df_cor(df_greeks, 'rho_n', 'rho_o', 'contract')
    # print(df_cor.corr()) # 0.999108
    # df_cor = get_df_cor(df_greeks, 'iv_n', 'iv_o', 'contract')
    # print(df_cor.corr()) # 0.863625 (call) / 0.598525 (all)
    # df_cor = get_df_cor(df_greeks, 'value_n', 'value_o', 'contract')
    # print(df_cor.corr()) # 0.999581

    # print(df_greeks.to_string())

    # plot_same_axis(df_greeks, 'delta_n', 'delta_o')
    # plot_same_axis(df_greeks, 'gamma_n', 'gamma_o')
    # plot_same_axis(df_greeks, 'vega_n', 'vega_o')
    # plot_same_axis(df_greeks, 'theta_n', 'theta_o')
    # plot_same_axis(df_greeks, 'rho_n', 'rho_o')
    # plot_same_axis(df_greeks, 'iv_n', 'iv_o')
    # plot_same_axis(df_greeks, 'value_n', 'value_o')

    # plot_3d_scatter(
    #     np.array(c_expiration_days), 
    #     np.array(c_strike), 
    #     np.array([data[c]['mark_iv'] for c in contracts]), 
    #     'Days to expiration', 'Strike', 'IV')


def get_df_cor(df, col1, col2, i):
    return pd.DataFrame(list(zip(df.index, df[col1], df[col2])), columns=[i, col1, col2]).set_index(i)


def bench_volatility(coin):
    with open(f'./data/raw/underlying/dvol/{coin}.json') as json_file:
        data = json.load(json_file)['data']

    df_dvol = pd.DataFrame(data, columns=['t', 'open', 'high', 'low', 'close']).sort_values(by='t')
    df_dvol['t'] = df_dvol['t'].apply(lambda x: x/1000)
    df_dvol = df_dvol.set_index('t')

    df_price = preprocess.get_underlying_price(coin)
    df_price["volatility"] = finance.volatility(df_price["u_close"])
    df_price['volatility'] = df_price['volatility'].apply(lambda x: x*100)

    df = df_price.join(df_dvol)

    df_cor = pd.DataFrame(list(zip(df.index, df['close'], df['volatility'])), columns=['t', 'close', 'volatility']).set_index('t')

    plot_same_axis(df, 'close', 'volatility')


def bench_greek_model():
    s = np.array([range(10,70,1) for i in range(23)]) # shape = (23, 60)
    I = np.ones((np.shape(s)))
    time = np.arange(1,12.5,0.5)/12
    T = np.array([ele for ele in time for i in range(np.shape(s)[1])]).reshape(np.shape(s))

    contracts = []
    for i in range(np.shape(s)[0]):
        for j in range(np.shape(s)[1]):
            contracts.append(finance.metrics(
                s[i,j],
                40*I[i,j],
                0.1*I[i,j],
                T[i,j],
                0.5*I[i,j],
                0.5*I[i,j],
                False
            ))
    
    # delta = [x['delta'] for x in contracts]
    # delta = np.array(delta).reshape(np.shape(s))

    # gamma = [x['gamma'] for x in contracts]
    # gamma = np.array(gamma).reshape(np.shape(s))

    # theta = [x['theta'] for x in contracts]
    # theta = np.array(theta).reshape(np.shape(s))

    # vega = [x['vega'] for x in contracts]
    # vega = np.array(vega).reshape(np.shape(s))

    # rho = [x['rho'] for x in contracts]
    # rho = np.array(rho).reshape(np.shape(s))

    iv = [x['iv_bi'] for x in contracts]
    iv = np.array(iv).reshape(np.shape(s))
    plot_3d_surface(s, T, iv, zlabel='iv_bi')

    # iv = [x['iv_rn'] for x in contracts]
    # iv = np.nan_to_num(np.array(iv).reshape(np.shape(s)))
    # plot_3d_surface(s, T, iv, zlabel='iv_rn')

    # iv = [x['iv_bi'] for x in contracts]
    # iv = np.array(iv).reshape(np.shape(s))
    # plot_3d_surface(s, T, iv, zlabel='iv_bi')


def bench_iv(coin):
    df = preprocess.get_contract_data(coin).head(10_000)

    iv = [finance.iv_2(
        'c' if c['is_call'] else 'p',
        c['c_close'],
        20_000,
        c['strike'],
        0,
        (c['expiration_days'] + 5) / 365,
        0
    ) for i,c in df.iterrows()]

    print(iv)

    # plot_3d_greeks(c_strike, c_expiration_days, iv, zlabel='Greek')



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


def plot_3d_surface(x, y, z, xlabel='Stock price', ylabel='Time to Expiration', zlabel=''):
    norm = matplotlib.colors.Normalize()
    fig = plt.figure(figsize=(20,11))
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(12,320)
    ax.plot_wireframe(x, y, z, rstride=1, cstride=1)
    ax.plot_surface(x, y, z, facecolors=matplotlib.cm.jet(z),linewidth=0.001, rstride=1, cstride=1, alpha=0.75)
    ax.set_zlim3d(z.min(), z.max())
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    m = matplotlib.cm.ScalarMappable(cmap=matplotlib.cm.jet)
    m.set_array(z)
    cbar = plt.colorbar(m)
    plt.show()


def plot_3d_scatter(x, y, z, xlabel='Stock price', ylabel='Time to Expiration', zlabel=''):
    norm = matplotlib.colors.Normalize()
    fig = plt.figure(figsize=(20,11))
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(12,320)
    # ax.plot_trisurf(x, y, z, linewidth=0.2, antialiased=True, cmap='jet')
    ax.scatter(x, y, z, linewidth=0.2, antialiased=True, cmap='jet')
    ax.set_zlim3d(z.min(), z.max())
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    m = matplotlib.cm.ScalarMappable(cmap=matplotlib.cm.jet)
    m.set_array(z)
    cbar = plt.colorbar(m)
    plt.show()


def main():
    pd.set_option('display.float_format', lambda x: '%.6f' % x)

    bench_greeks('BTC')
    # bench_volatility('BTC')
    # bench_greek_model()

    # bench_iv('BTC')


if __name__ == '__main__':
    main()
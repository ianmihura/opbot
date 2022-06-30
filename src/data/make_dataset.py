from ast import Lambda
import os
import sqlite3
import argparse
import json

import time
import datetime

import create_db
import insert_data


def get_underlying(coin):
    """Get data from underlying folder"""
    with open(f'./data/interim/underlying/{coin}.json') as json_file:
        data = json.load(json_file)
        timestamps = [data['prices'][i][0] for i in data['prices']]
        prices = [data['prices'][i][1] for i in data['prices']]
        volumes = [data['total_volumes'][i][1] for i in data['prices']]
        market_caps = [data['market_caps'][i][1] for i in data['prices']]
        
    with open(f'./data/interim/volatility/{coin}.json') as json_file:
        data = json.load(json_file)
        volatility = [data['data'][i][4] for i in data['data']]

    return timestamps, prices, volumes, market_caps, volatility


def main(args):
    """Runs db scripts to turn interim data (./data/interim)
    into clean data ready to be analyzed (./data/processed/datawarehouse.db)
    """
    raw_folder = './data/interim'

    db_file = args.where if args.where else './data/processed/datawarehouse.db'
    if os.path.exists(db_file):
        os.remove(db_file)
    con = sqlite3.connect(db_file)

    create_db.create(con)

    underlying_dir = os.listdir(f'{raw_folder}/underlying')

    underlying_meta = [*map(lambda x: (x.split('.')[0],), underlying_dir)]
    insert_data.insert_underlying_meta(con, underlying_meta)

    underlying_meta = insert_data.get_underlying_meta(con)
    # underlying_meta[0][0] # TODO: iterate on first index

    for coin in underlying_meta:
        timestamps, prices, volumes, market_caps, volatility = get_underlying(coin[1])
        underlying_data = list(zip()) # TODO: before zip, must verify timestamps

    underlying_data = [] # UNDERLYING_ID, TIMESTAMP, PRICE, VOLUME, M_CAP, VOLATILITY
    contracts_meta = [] # UNDERLYING_ID, NAME, EXPIRATION, CREATION, STRIKE, IS_CALL
    contracts_data = [] # CONTRACT_ID, TIMESTAMP, VOLUME, OPEN, CLOSE, HIGH, LOW, FAIR_PRICE, INT_PRICE, EXT_PRICE, D, V, T, G, R, IV


    with open('./data/raw/symbols/BTC.json') as json_file:
        data = json.load(json_file)
        # contract_name = list(data.keys())[0] # TODO: iterate on this
        # contract_name_split = contract_name.split('-')
        # underlying = contract_name_split[0]
        # expiration_date = contract_name_split[1] + '-10'
        # expiration_element = datetime.datetime.strptime(expiration_date,"%d%b%y-%H")
        # expiration_timestamp = time.mktime(expiration_element.timetuple())
        # strike = contract_name_split[2]
        # is_call = contract_name_split[3] == 'C'

        # volume = data['BTC-30SEP22-21000-P']['volume'][0]
        # timestamp = data['BTC-30SEP22-21000-P']['ticks'][0]
        # _open = data['BTC-30SEP22-21000-P']['open'][0]
        # low = data['BTC-30SEP22-21000-P']['low'][0]
        # high = data['BTC-30SEP22-21000-P']['high'][0]
        # close = data['BTC-30SEP22-21000-P']['close'][0]
        # data['BTC-22JUL22-24000-C']


    # insert_data.insert_underlying_data(con, underlying_data)
    # insert_data.insert_contracts_meta(con, contracts_meta)
    # insert_data.insert_contracts_data(con, contracts_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-where", type=str, help="Where the database will be created.")
    args = parser.parse_args()
    main(args)

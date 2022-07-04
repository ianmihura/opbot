import os
import sqlite3
import argparse
import json
import pandas as pd
import numpy as np

import time
import datetime

import create_db
import insert_data


def _insert_contract_data(row, con=None, contract_id=0):
    return insert_data.insert_contracts_data(con, [
        contract_id,
        row['t'],
        row['c_volume'],
        row['open'],
        row['close'],
        row['high'],
        row['low'],
        row['value'],
        row['value_int'],
        row['value_ext'],
        row['delta'],
        row['vega'],
        row['theta'],
        row['gamma'],
        row['rho'],
        row['iv']
    ])


def _insert_contract_meta(row, con=None, underlying_id=0):
    return insert_data.insert_contracts_meta(con, [
        underlying_id,
        row['contract'],
        row['expiration'],
        row['strike'],
        row['is_call']
    ])


def _insert_underlying_data(row, con=None, underlying_id=0):
    return insert_data.insert_underlying_data(con, [
        underlying_id,
        row['t']/1000,
        row['price'],
        row['volume'],
        row['volume_weighted'],
        row['transaction'],
        row['volatility']
    ])


def create_connection(db_file: str = './data/processed/datawarehouse.db'):
    """Creates the empty db to work with: datawarehouse.db
    Returns a connection object to the specified db"""
    if os.path.exists(db_file):
        os.remove(db_file)
    return sqlite3.connect(db_file)


def insert_underlying_data(con, underlying_id, coin):
    underlying_data_df = pd.read_csv(f'./data/interim/{coin}_underlying_data.csv')
    underlying_data_df = underlying_data_df.fillna(0)
    underlying_data_df.apply(_insert_underlying_data, axis=1, con=con, underlying_id=underlying_id) 
    insert_data.get_underlying_data(con)


def insert_connection(con):
    """Runs db scripts to turn interim data (./data/interim)
    into clean data ready to be analyzed (./data/processed/datawarehouse.db)
    """
    # underlying metadata
    raw_underlying_dir = os.listdir(f'./data/raw/underlying')
    underlying_meta = [*map(lambda x: (x.split('.')[0],), raw_underlying_dir)]
    coins = [u[0] for u in underlying_meta]
    insert_data.insert_underlying_meta(con, underlying_meta)

    # underlying data
    underlying_meta = insert_data.get_underlying_meta(con)
    underlying_ids = [u[0] for u in underlying_meta]
    # TODO: make full array to insert, then insertmany => do one insert for each table
    [insert_underlying_data(con, underlying_ids[i], coin) for i, coin in enumerate(coins)]
    print(insert_data.get_underlying_data(con))

    # # contracts
    # contract_df = pd.read_csv(f'./data/interim/{coins[0]}_contracts.csv') # TODO: iterate
    # contract_df.apply(insert_contract_meta, axis=1, con=con, underlying_id=underlying_ids[0]) # TODO: iterate 
    # contract_ids = insert_data.get_contracts_meta(con)
    # contract_df.apply(insert_contract_data, axis=1, con=con, contract_id=contract_ids[0]) # TODO: iterate 


def main():
    con = create_connection()
    create_db.create(con)

    insert_connection(con)


if __name__ == '__main__':
    main()

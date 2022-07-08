import os
import sqlite3
import pandas as pd

import create_db
import insert_data
import select_data


def create_connection(db_file: str = './data/processed/datawarehouse.db'):
    """Creates the empty db to work with: datawarehouse.db
    Returns a connection object to the specified db"""
    if os.path.exists(db_file):
        os.remove(db_file)
    return sqlite3.connect(db_file)


def insert_underlying_data(con, underlying_id, coin):
    underlying_data_df = pd.read_csv(f'./data/interim/{coin}_underlying_data.csv')
    underlying_data_df = underlying_data_df.fillna(0)
    make_underlying_data = lambda u: [
        underlying_id, 
        u['t'],
        u['u_open'],
        u['u_high'],
        u['u_low'],
        u['u_close'],
        u['u_volume'],
        u['chain_tx'],
        u['chain_volume'],
        u['recent_price'],
        u['recent_volume'],
        u['recent_transaction'],
        u['u_volatility']]
    underlying_data = [make_underlying_data(row) for i, row in underlying_data_df.iterrows()]

    insert_data.insert_underlying_data(con, underlying_data)


def insert_contract_meta(con, underlying_id, coin):
    contract_df = pd.read_csv(f'./data/interim/{coin}_contracts.csv')
    make_contract_meta = lambda c: [
        underlying_id,
        c['contract'],
        c['expiration'],
        c['strike'],
        c['is_call']]
    contract_meta = [make_contract_meta(row) for i, row in contract_df.iterrows()]
    contract_meta = list(set(tuple(sub) for sub in contract_meta))

    insert_data.insert_contracts_meta(con, contract_meta)


def insert_contract_data(con, contract_id):
    coin = contract_id[1].split('-')[0]
    contract_df = pd.read_csv(f'./data/interim/{coin}_contracts.csv')
    contract_df = contract_df[contract_df['contract'] == contract_id[1]]

    make_contract_data = lambda c: [
        contract_id[0],
        c['t'],
        c['c_volume'],
        c['c_open'],
        c['c_close'],
        c['c_high'],
        c['c_low'],
        c['value'],
        c['value_int'],
        c['value_ext'],
        c['delta'],
        c['vega'],
        c['theta'],
        c['gamma'],
        c['rho'],
        c['iv']]
    contract_data = [make_contract_data(row) for i, row in contract_df.iterrows()]

    insert_data.insert_contracts_data(con, contract_data)


def insert_connection(con):
    """Runs db scripts to turn interim data (./data/interim)
    into clean data ready to be analyzed (./data/processed/datawarehouse.db)
    """
    # underlying metadata
    raw_underlying_dir = os.listdir(f'./data/raw/underlying/price')
    underlying_meta = [*map(lambda x: (x.split('.')[0],), raw_underlying_dir)]
    insert_data.insert_underlying_meta(con, underlying_meta)

    # underlying data
    underlying_meta = select_data.get_underlying_meta(con)
    [insert_underlying_data(con, coin[0], coin[1]) for coin in underlying_meta]

    # contracts meta
    [insert_contract_meta(con, coin[0], coin[1]) for coin in underlying_meta]

    # contracts data
    contract_ids = select_data.get_contracts_ids(con)
    [insert_contract_data(con, contract_id) for contract_id in contract_ids]


def main():
    con = create_connection()
    create_db.create(con)

    insert_connection(con)


if __name__ == '__main__':
    main()

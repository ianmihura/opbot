from contextlib import closing
import os
import sqlite3
import argparse


create_meta_table = """CREATE TABLE META (
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	UNDERLYING_ID INTEGER,
    TICK_SIZE FLOAT,
    TAKER_COMMISION FLOAT,
    MAKER_COMMISION FLOAT,
    MIN_TRADE FLOAT,
    FOREIGN KEY(UNDERLYING_ID) REFERENCES UNDERLYING_META(ID)
);"""


create_contracts_meta_table = """CREATE TABLE CONTRACTS_META (
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	UNDERLYING_ID INTEGER,
	NAME VARCHAR(30),
	EXPIRATION TIMESTAMP,
    CREATION TIMESTAMP,
    STRIKE FLOAT,
    IS_CALL BINARY,
    FOREIGN KEY(UNDERLYING_ID) REFERENCES UNDERLYING_META(ID)
);"""


create_contracts_data_table = """CREATE TABLE CONTRACTS_DATA (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
	CONTRACT_ID INTEGER,
	TIMESTAMP TIMESTAMP,
    VOLUME FLOAT,
    OPEN FLOAT,
    CLOSE FLOAT,
    HIGH FLOAT,
    LOW FLOAT,
    FAIR_PRICE FLOAT,
    INT_PRICE FLOAT,
    EXT_PRICE FLOAT,
    D FLOAT,
	V FLOAT,
	T FLOAT,
	G FLOAT,
	R FLOAT,
	IV FLOAT,
    FOREIGN KEY(CONTRACT_ID) REFERENCES CONTRACTS_META(ID)
);"""


create_underlying_meta_table = """CREATE TABLE UNDERLYING_META (
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	NAME VARCHAR(3)
);"""


create_underlying_data_table = """CREATE TABLE UNDERLYING_DATA (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
	UNDERLYING_ID INTEGER,
	TIMESTAMP TIMESTAMP,
    PRICE FLOAT,
    VOLUME FLOAT,
    VOLUME_WEIGHTED FLOAT, -- Volume weighted by average price
    TRANSACTIONS FLOAT, -- Number of transactions
	VOLATILITY FLOAT,
    FOREIGN KEY(UNDERLYING_ID) REFERENCES UNDERLYING_META(ID)
);"""


def create(con):
    with closing(con.cursor()) as cursor:
        cursor.execute(create_underlying_meta_table)
        cursor.execute(create_underlying_data_table)
        cursor.execute(create_contracts_meta_table)
        cursor.execute(create_contracts_data_table)
        cursor.execute(create_meta_table)


def main(args):
    db_file = args.where if args.where else './data/processed/datawarehouse.db'
    
    if os.path.exists(db_file):
        os.remove(db_file)

    con = sqlite3.connect(db_file)

    create(con)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-where", type=str, help="Where the database will be created.")
    args = parser.parse_args()
    main(args)

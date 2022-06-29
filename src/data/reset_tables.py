import sqlite3
import argparse

create_contracts_table = """CREATE TABLE CONTRACTS_METADATA (
	ID integer PRIMARY KEY AUTOINCREMENT,
	P_C binary,
	NAME varchar(30),
	EXPIRATION datetime,
    STRIKE float
);"""

create_underlying_table = """CREATE TABLE UNDERLYING (
	TIMESTAMP timestamp PRIMARY KEY,
    OPEN float,
    CLOSE float,
    HIGH float,
    LOW float,
    VOLUME float,
	VOLATILITY float
);"""

create_variable_table = """CREATE TABLE VARIABLE_DATA (
	TIMESTAMP timestamp PRIMARY KEY AUTOINCREMENT,
	CONTRACT_ID integer FOREIGN KEY REFERENCES CONTRACTS_METADATA(ID),
	PRICE float,
	DELTA float,
	VEGA float,
	THETA float,
	GAMMA float,
	IV float
);"""


def drop_table(connection, table: str) -> str:
    cursor = connection.cursor()
    exist_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';"
    if not (len(cursor.execute(exist_query).fetchall()) > 0):
        cursor.execute("DROP TABLE {};")


def main(args):
    # Assume the database does not exist
    con = sqlite3.connect(args.where)
    cursor = con.cursor()
    cursor.execute(create_contracts_table)
    cursor.execute(create_variable_table)
    cursor.execute(create_underlying_table)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-where", type=str, help="Where the database will be created.")
    args = parser.parse_args()
    main(args)

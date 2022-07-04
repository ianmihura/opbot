from contextlib import closing


def select(con, query: str):
    """Basic select query, used to check correct insetrion
    con: sqlite3 connect object
    table: name of table to query"""
    with closing(con.cursor()) as cursor:
        results = cursor.execute(query).fetchall()
    return results


def get_underlying_meta(con):
    return select(con, 'SELECT * FROM UNDERLYING_META')


def get_underlying_data(con):
    return select(con, 'SELECT * FROM UNDERLYING_DATA')


def get_contracts_meta(con):
    return select(con, 'SELECT * FROM CONTRACTS_META')


def get_contracts_data(con):
    return select(con, 'SELECT * FROM CONTRACTS_DATA')


def insert_many(con, query: str, data: list):
    """Inserts many rows (data) using query
    con: sqlite3 connect object
    query: sql insert query
        form: must have parameterized values: (?, ...)
    data: arbitrary list
    """
    with closing(con.cursor()) as cursor:
        cursor.executemany(query, data)
    con.commit()


def insert_underlying_meta(con, data: list = [('BTC',),('ETH',)]):
    """Inserts to UNDERLYING_META
    con: sqlite3 connect object
    data: list of coin names
        default: ['BTC', 'ETH']
    """
    query = "INSERT INTO UNDERLYING_META (NAME) VALUES (?)"
    insert_many(con, query, data)


def insert_underlying_data(con, data: list = []):
    """Inserts to UNDERLYING_DATA
    con: sqlite3 connect object
    data: list of coins data
        form: [ [underlying_id, timestamp, price, volume, volume_w, transactions, volatility], ...]
    """
    query = """INSERT INTO UNDERLYING_DATA
    (UNDERLYING_ID, TIMESTAMP, PRICE, VOLUME, VOLUME_WEIGHTED, TRANSACTIONS, VOLATILITY) 
    VALUES (?, ?, ?, ?, ?, ?, ?)"""
    print(data)
    insert_many(con, query, data)


def insert_contracts_meta(con, data: list = []):
    """Inserts to CONTRACTS_META
    con: sqlite3 connect object
    data: list of contracts metadata
        form: [ [UNDERLYING_ID, NAME, EXPIRATION, STRIKE, IS_CALL], ...]
    """
    query = """INSERT INTO CONTRACTS_META
    (UNDERLYING_ID, NAME, EXPIRATION, STRIKE, IS_CALL) 
    VALUES (?, ?, ?, ?, ?, ?)"""
    insert_many(con, query, data)


def insert_contracts_data(con, data: list = []):
    """Inserts to CONTRACTS_DATA
    con: sqlite3 connect object
    data: list of coins data
        form: [ [CONTRACT_ID, TIMESTAMP, VOLUME, OPEN, CLOSE, HIGH, LOW, FAIR_PRICE, INT_PRICE, EXT_PRICE, D, V, T, G, R, IV], ...]
    """
    query = """INSERT INTO CONTRACTS_DATA
    (CONTRACT_ID, TIMESTAMP, VOLUME, OPEN, CLOSE, HIGH, LOW, FAIR_PRICE, INT_PRICE, EXT_PRICE, D, V, T, G, R, IV) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    insert_many(con, query, data)


# TODO: insert general metadata





def test():
    import sqlite3 as sq
    con = sq.connect('./data/processed/datawarehouse.db')
    # insert_underlying_data(con, [[1, 123, 0.1, 12, 431, 32],[1, 124, 0.4, 145, 441, 12342]])
    # insert_contracts_meta(con, [[1, 'asdfadsfas', 0.1, 12, 431, 1],[1, 'asdfasdf', 0.4, 145, 441, 0]])
    # insert_contracts_data(con, [[1, 123443, 43, 12,12,12,12,13,0,13, 0.1, 12, 431, -1, -0.1,2],[2, 3443423, 413, 142,112,512,172,13,0,-13, -0.1, -12, 431, -1, -0.1,2]])
    print(select(con, 'CONTRACTS_DATA'))
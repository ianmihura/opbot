from contextlib import closing


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
        form: [ 
            [UNDERLYING_ID, TIMESTAMP, OPEN, HIGH, LOW, CLOSE, 
                VOLUME, CHAIN_TX, CHAIN_VOLUME, RECENT_PRICE, 
                RECENT_VOLUME, RECENT_TX, VOLATILITY], 
            ... ]
    """
    query = """INSERT INTO UNDERLYING_DATA
    (UNDERLYING_ID, TIMESTAMP, OPEN, HIGH, LOW, CLOSE, 
        VOLUME, CHAIN_TX, CHAIN_VOLUME, RECENT_PRICE, 
        RECENT_VOLUME, RECENT_TX, VOLATILITY) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    insert_many(con, query, data)


def insert_contracts_meta(con, data: list = []):
    """Inserts to CONTRACTS_META
    con: sqlite3 connect object
    data: list of contracts metadata
        form: [ 
            [UNDERLYING_ID, NAME, EXPIRATION, STRIKE, IS_CALL], 
            ... ]
    """
    query = """INSERT INTO CONTRACTS_META
    (UNDERLYING_ID, NAME, EXPIRATION, STRIKE, IS_CALL) 
    VALUES (?, ?, ?, ?, ?)"""
    insert_many(con, query, data)


def insert_contracts_data(con, data: list = []):
    """Inserts to CONTRACTS_DATA
    con: sqlite3 connect object
    data: list of coins data
        form: [ 
            [CONTRACT_ID, TIMESTAMP, VOLUME, OPEN, CLOSE, 
                HIGH, LOW, FAIR_PRICE, D, V, T, G, R, IV], 
            ... ]
    """
    query = """INSERT INTO CONTRACTS_DATA
    (CONTRACT_ID, TIMESTAMP, VOLUME, OPEN, CLOSE, 
        HIGH, LOW, FAIR_PRICE, D, V, T, G, R, IV) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    insert_many(con, query, data)


# TODO: insert general metadata


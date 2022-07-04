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


def get_contracts_ids(con):
    return select(con, 'SELECT ID, NAME FROM CONTRACTS_META')


def get_contracts_data(con):
    return select(con, 'SELECT * FROM CONTRACTS_DATA')
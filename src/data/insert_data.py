def convert_entry_to_insert(entry: dict) -> list:
    """This function takes a sample of the data in json format and converts it
    into a list of tuples.
    """
    return list(zip(*entry.values()))


def make_question_marks(n) -> str:
    """This simple function returns a string of the form (?, ..., ?) with
    n question marks.
    """
    return "(?" + ", ?" * (n-1) + ")"


def insert_data_to_table(connection, json_data: list, dest_table: str):
    """This function dumps the data in json_data to dest_table in the database
    through the passed connection object.
    """
    cursor = connection.cursor()
    columns, _ = list(zip(*json_data[0].items()))
    insert_params = list(map(convert_entry_to_insert, json_data))
    question_marks = make_question_marks(insert_params[0])
    cursor.executemany(f"INSERT INTO {dest_table}{str(columns)} {question_marks}", insert_params)

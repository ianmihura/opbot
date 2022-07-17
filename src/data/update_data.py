import sqlite3
import os
import argparse
import logging
import time
from datetime import datetime
from dotenv import find_dotenv, dotenv_values

from preprocess import main as preprocess_main
from api import main as api_main
from insert_dataset import insert_connection

def get_last_point(con):
    cursor = con.cursor()
    cursor.execute("SELECT MAX(TIMESTAMP) FROM UNDERLYING_DATA")
    return cursor.fetchone()[0]


def main(args):
    logger = logging.getLogger(__name__)
    con = sqlite3.connect(os.path.join(args.output_filepath, args.DATA_WAREHOUSE_FILE))
    logger.info("Connected to database")
    while args.continuous_update:
        try:
            start = datetime.fromtimestamp(get_last_point(con))
            end = datetime.now()
            # request, transform and load data to DW
            logger.info(f'requesting data from api')
            api_main(start, end)

            logger.info('preprocessing data (adding greeks)')
            preprocess_main(start, end)
            
            logger.info('inserting data into the destination database')
            insert_connection(con, start, end)  # TODO: add parameters to insert_connection

            time.sleep(args.WAIT_INTERVAL)  # TODO: add to .env file
        except KeyboardInterrupt:
            logger.info('Exiting without saving last iteration')
            time.sleep(5)
            # TODO: save last iteration or better deal with the exception
            break


if __name__ == "__main__":
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    parser = argparse.ArgumentParser(description='Update the data warehouse with new data.')
    parser.add_argument('-i', '--input_filepath', help='input filepath', required=True)
    parser.add_argument('-o', '--output_filepath', help='output filepath', required=True)
    parser.add_argument('-c', '--continuous-update', help='Whether the script will be left running.', action='store_true')
    args = parser.parse_args()
    # add arguments from .env to the namespace 
    args = argparse.Namespace(**vars(args), **dotenv_values(find_dotenv()))
    main(args)

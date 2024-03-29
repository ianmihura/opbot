# -*- coding: utf-8 -*-
import os, shutil
import logging
from dotenv import find_dotenv, dotenv_values

import sqlite3
import argparse

from preprocess import main as preprocess_main
from api import main as api_main
from insert_dataset import insert_connection
import sql_create


def rm_files_recurse(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                rm_files_recurse(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def main(args):
    """ Runs data processing scripts to turn raw data from (../raw) into
    cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('requesting data from api (raw)')
    api_main()

    logger.info('preprocessing data: adding greeks (raw -> interim)')
    preprocess_main()

    logger.info('creating sqlite file')
    db_file_path = os.path.join(args.output_filepath, args.DATA_WAREHOUSE_FILE)
    if os.path.exists(db_file_path):
        os.remove(db_file_path)
    con = sqlite3.connect(db_file_path)

    logger.info('creating sqlite database')
    sql_create.create(con)
    
    logger.info('inserting data into database (interim -> processed)')
    insert_connection(con)

    logger.info('cleanup: delete intermediate files (raw & interim)')
    rm_files_recurse('raw')
    rm_files_recurse('interim')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    parser = argparse.ArgumentParser(description='Run data processing scripts to turn raw data from (../raw) into clean data ready to be analyzed (saved in ../processed).')
    parser.add_argument('-o', '--output-filepath', help='output filepath', required=True)
    args = parser.parse_args()
    # add arguments from .env to the namespace
    args = argparse.Namespace(**vars(args), **dotenv_values(find_dotenv()))
    main(args)

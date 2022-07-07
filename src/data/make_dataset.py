# -*- coding: utf-8 -*-
import os
import logging
from dotenv import find_dotenv, dotenv_values

import sqlite3
from datetime import datetime
import argparse

from preprocess import main as preprocess_main
from api import main as api_main
from insert_dataset import insert_connection


import pdb


def main(args):
    """ Runs data processing scripts to turn raw data from (../raw) into
    cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')
    logger.info(f'requesting data from api')
    api_main()

    logger.info('preprocessing data (adding greeks)')
    preprocess_main()

    # read and connect to the output filepath (destination DW)
    con = sqlite3.connect(os.path.join(args.output_filepath, args.DATA_WAREHOUSE_FILE))
    
    logger.info('inserting data into the destination database')
    insert_connection(con)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    parser = argparse.ArgumentParser(description='Run data processing scripts to turn raw data from (../raw) into clean data ready to be analyzed (saved in ../processed).')
    parser.add_argument('-o', '--output-filepath', help='output filepath', required=True)
    args = parser.parse_args()
    # add arguments from .env to the namespace 
    args = argparse.Namespace(**vars(args), **dotenv_values(find_dotenv()))
    main(args)

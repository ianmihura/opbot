# -*- coding: utf-8 -*-
import os
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from types import SimpleNamespace
import sqlite3
from datetime import datetime

from preprocess import main as preprocess_main
from api import main as api_main
from insert_dataset import insert_connection


import pdb


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
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
    con = sqlite3.connect(os.path.join(output_filepath, 'datawarehouse.db'))
    
    logger.info('inserting data into the destination database')
    insert_connection(con)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()

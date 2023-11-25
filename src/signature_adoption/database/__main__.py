#!/usr/bin/env python

'''database.py: This script places the data from the adoption script into a
SQLite database that can be queried.
'''

# Imports
import argparse
import logging as log
import sqlite3
import json
from datetime import datetime
from .docker import add as docker_add
from .pypi import add as pypi_add
from .huggingface import add as huggingface_add
from .maven import add as maven_add
from ..util.files import valid_path_create, valid_path


# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'

# Define global variables
script_start_time = datetime.now()


# Function to parse arguments
def parse_args():
    ''' This function parses arguments passed to the script.

    returns: the arguments passed to the script.
    '''

    # Create parser
    parser = argparse.ArgumentParser(
        description='This script takes the registry-specific adoption data '
        'stored in Newline Delimited JSON (NDJSON) files and places it into a '
        'SQLite database that can be queried. As a part of this process, the '
        'script will also do some simple data analysis, cleaning, and '
        'normalization.'
    )

    # global arguments
    parser.add_argument(
        '--input',
        '-i',
        dest='input_file',
        metavar='FILE',
        type=str,
        default='./data/-reg-/adoption.ndjson',
        help='The name of the input file for the registry. '
        'Defaults to <./data/-reg-/adoption.ndjson>. '
        'The -reg- will be replaced with the registry name.'
    )
    parser.add_argument(
        '--database',
        '-d',
        dest='db_file',
        metavar='FILE',
        type=str,
        default='./data/adoption.db',
        help='The name of the output database file. Defaults to '
        '<./data/adoption.db>. '
    )
    parser.add_argument(
        '--log',
        '-l',
        type=str,
        default='./logs/database.log',
        metavar='FILE',
        help='The path to the log file. '
        'Defaults to <./logs/database.log>. '
    )
    parser.add_argument(
        '--start',
        '-s',
        type=int,
        default=0,
        help='The starting line to read from the input file. Defaults to 0.'
    )
    parser.add_argument(
        '--stop',
        '-t',
        type=int,
        default=-1,
        help='The stopping line for the input file. Defaults to -1 (EOF).'
    )
    parser.add_argument(
        '--clean',
        '-c',
        action='store_true',
        help='Flag to clear existing data from the database before adding new '
        'data. Defaults to False.'
    )

    # Create subparsers
    subparsers = parser.add_subparsers(
        title='registry',
        description='The registry to add to the database.',
        help='This argument selects the registry to add to the database.',
        dest='registry')

    # Docker subparser
    docker_parser = subparsers.add_parser(
        'docker',
        help='Add Docker Hub adoption data to the database.'
    )
    docker_parser.set_defaults(func=docker_add)

    # PyPI subparser
    pypi_parser = subparsers.add_parser(
        'pypi',
        help='Add PyPI adoption data to the database.'
    )
    pypi_parser.set_defaults(func=pypi_add)

    # HuggingFace subparser
    huggingface_parser = subparsers.add_parser(
        'huggingface',
        help='Add HuggingFace adoption data to the database.'
    )
    huggingface_parser.set_defaults(func=huggingface_add)

    # Maven subparser
    maven_parser = subparsers.add_parser(
        'maven',
        help='Add Maven Central adoption data to the database.'
    )
    maven_parser.set_defaults(func=maven_add)

    # Parse arguments
    args = parser.parse_args()

    # Normalize paths
    args.log = valid_path_create(args.log)
    args.output_file = valid_path_create(args.db_file)
    args.input_file = valid_path(
        args.input_file.replace('-reg-', args.registry))

    return args


# Function to setup the logger
def setup_logger(args):
    ''' This function sets up the logger for the script.
    '''
    # Set up logger
    log_level = log.DEBUG if __debug__ else log.INFO
    log.basicConfig(
        filename=args.log,
        filemode='a',
        level=log_level,
        format=f'%(asctime)s|%(levelname)s|{args.registry}|%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Log start time
    log.info("Starting database.py.")

    # Log arguments
    log.info(f'Arguments: {args}')


def log_finish():
    '''
    Script simply logs time of script completion and total time elapsed.
    '''

    # Log end of script
    log.info('Script completed. Total time:'
             f'{datetime.now()-script_start_time}')


def ensure_db_tables(args):
    '''
    This function ensures that the database tables exist.

    args: The arguments passed to the script.
    '''

    # Log start
    log.info('Ensuring database exists.')

    # Connect to database
    conn = sqlite3.connect(args.db_file)
    cursor = conn.cursor()

    # Clear existing data if requested
    if args.clean:
        log.info('Clearing existing data from database.')
        cursor.execute('DROP TABLE IF EXISTS packages;')
        cursor.execute('DROP TABLE IF EXISTS versions;')
        cursor.execute('DROP TABLE IF EXISTS units;')

    # Create package table
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            registry TEXT NOT NULL,
            UNIQUE (name, registry)
        );
        '''
    )

    # Create version table
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS versions (
            id INTEGER PRIMARY KEY,
            package_id INTEGER NOT NULL,
            date TEXT,
            name TEXT NOT NULL,
            UNIQUE (package_id, name)
            FOREIGN KEY (package_id) REFERENCES packages (id)
        );
        '''
    )

    # Create signature unit table
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY,
            version_id INTEGER NOT NULL,
            package_id INTEGER NOT NULL,
            unit TEXT NOT NULL,
            unit_type TEXT NOT NULL,
            sig_type TEXT NOT NULL,
            has_sig BOOLEAN NOT NULL,
            sig_raw TEXT,
            sig_status TEXT NOT NULL,
            date TEXT,
            UNIQUE (version_id, unit)
            FOREIGN KEY (version_id) REFERENCES versions (id)
            FOREIGN KEY (package_id) REFERENCES packages (id)
        );
        '''
    )

    # Disconnect from database
    conn.commit()
    conn.close()


def add_to_db(args):
    '''
    This function adds adoption data to the database.

    args: The arguments passed to the script.

    returns: None
    '''

    # Open the input file and connect to the database
    log.info(f'Opening input file {args.input_file} and '
             f'connecting to database {args.db_file}')
    with open(args.input_file, 'r') as input_file, \
            sqlite3.connect(args.db_file) as database:

        # Create the cursor
        cursor = database.cursor()

        # Iterate through the input file
        for indx, line in enumerate(input_file):

            if indx < args.start:
                continue
            elif indx >= args.stop and args.stop != -1:
                break

            # print progress
            if indx % 100 == 0:
                log.info(f'Processing line {indx}')
            else:
                log.debug(f'Processing line {indx}')

            # Parse the line
            package = json.loads(line)

            # Add the package to the database using the appropriate function
            args.func(package=package, cursor=cursor)


def main():
    '''
    This is the main function of the script.
    '''
    # Parse arguments
    args = parse_args()

    # Setup logger
    setup_logger(args)

    # Ensure database tables exist
    ensure_db_tables(args)

    # Add data to database
    add_to_db(args)

    # Log finish
    log_finish()


# Classic Python main function
if __name__ == '__main__':
    main()  # Call main function

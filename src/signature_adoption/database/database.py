#!/usr/bin/env python

'''database.py: This script places the data from the adoption script into a
SQLite database that can be queried.
'''

# Imports
import argparse
import logging as log
from datetime import datetime
from docker.database import database as docker_database
from util.files import valid_path_create, valid_path


# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'

# Define global variables
script_start_time = datetime.now()


def docker(args):
    '''
    This function adds adoption data from Docker Hub to the database.

    args: The arguments passed to the script.
    '''
    docker_database()


def pypi(args):
    '''
    This function adds adoption data from PyPI to the database.

    args: The arguments passed to the script.
    '''
    pass


def huggingface(args):
    '''
    This function adds adoption data from HuggingFace to the database.

    args: The arguments passed to the script.
    '''
    pass


def maven(args):
    '''
    This function adds adoption data from Maven Central to the database.

    args: The arguments passed to the script.
    '''
    pass


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
    docker_parser.set_defaults(func=docker)

    # PyPI subparser
    pypi_parser = subparsers.add_parser(
        'pypi',
        help='Add PyPI adoption data to the database.'
    )
    pypi_parser.set_defaults(func=pypi)

    # HuggingFace subparser
    huggingface_parser = subparsers.add_parser(
        'huggingface',
        help='Add HuggingFace adoption data to the database.'
    )
    huggingface_parser.set_defaults(func=huggingface)

    # Maven subparser
    maven_parser = subparsers.add_parser(
        'maven',
        help='Add Maven Central adoption data to the database.'
    )
    maven_parser.set_defaults(func=maven)

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


def main():
    '''
    This is the main function of the script.
    '''
    # Parse arguments
    args = parse_args()

    # Setup logger
    setup_logger(args)

    # Check adoption of signatures the function is set by the subparser
    args.func(args)

    # Log finish
    log_finish()


# Classic Python main function
if __name__ == '__main__':
    main()  # Call main function

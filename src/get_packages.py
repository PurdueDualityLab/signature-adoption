#!/usr/bin/env python

'''get_packages.py: This script gets the repositories and associated metadata for all packages
located in the ecosystems database. It then writes the data to a JSON file.
'''

# Import statements
import psycopg2
import json
import os
import argparse
import logging as log
from util import valid_path_create, valid_path

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"

# Define global variables
script_start_time = datetime.now()

localhost_password = os.environ.get("PSQL_Password") or ''

db_credentials = {
        "dbname": "packages_production",
        "user": "postgres",
        "password": localhost_password,
        "host": "localhost",
        "port": "5432"  # Default PostgreSQL port
        }

# Function to parse arguments
def parse_args():
    ''' This function parses arguments passed to the script.

    returns: args - the arguments passed to the script
    '''
    parser = argparse.ArgumentParser(description='Get tags for all repositories in docker hub.')
    parser.add_argument('--output',
                        type=str,
                        default='./data/packages.json',
                        help='The path to the output file. Defaults to ./data/packages.json.')
    parser.add_argument('--log',
                        type=str,
                        default=f'./logs/get_packages.log',
                        help='The path to the log file. Defaults to ./logs/get_packages.log.')
    args =  parser.parse_args()

    # Normalize paths
    args.output = valid_path_create(args.output)
    args.log = valid_path_create(args.log)

    return args

# Function to setup the logger
def setup_logger(args):
    ''' This function sets up the logger for the script.
    '''
    # Set up logger
    log_level = log.DEBUG if __debug__ else log.INFO
    log.basicConfig(filename=args.log,
                        filemode='a',
                        level=log_level,
                        format='%(asctime)s|%(levelname)s|%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # Log start time
    log.info(f'Starting get_tags script.')


def log_finish():
    '''
    Script simply logs time of script completion and total time elapsed.
    '''

    # Log end of script
    log.info(f'Script completed. Total time: {datetime.now()-script_start_time}')

# Function to get packages from database
def get_packages(args):
    pass

# Classic Python main function
def main():
    # Parse arguments
    args = parse_args()

    # Setup logger
    setup_logger(args)

    # Get args packages from database
    get_packages(args)

    # Log finish
    log_finish()


# Classic Python main function
if __name__ == '__main__':
    main()  # Call main function


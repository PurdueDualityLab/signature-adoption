#!/usr/bin/env python

'''check_adoption.py: This script checks the adoption of signatures for
packages from Docker Hub.
'''

# Imports
import json
import os
import sys
import argparse
import subprocess
import re
import logging as log
from datetime import datetime
from util import valid_path, valid_path_create


# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'

# Define global variables
script_start_time = datetime.now()


# Function to parse arguments
def parse_args():
    ''' This function parses arguments passed to the script.

    returns: args - the arguments passed to the script
    '''
    parser = argparse.ArgumentParser(
        description='Check adoption for packages from Docker Hub.'
        'It takes in a newline delimited json file containing a list of'
        'packages and outputs a newline delimited json file containing'
        'a list of packages with their adoption status.')
    parser.add_argument('--output',
                        type=str,
                        default='./data/docker_adoption.ndjson',
                        help='The path basis to the output files.'
                        'Defaults to ./data/docker_adoption.ndjson.')
    parser.add_argument('--input',
                        type=str,
                        default='./data/docker_packages.ndjson',
                        help='The path to the input file.'
                        'Defaults to ./data/docker_packages.ndjson.')
    parser.add_argument('--log',
                        type=str,
                        default='./logs/docker_check_adoption.log',
                        help='The path to the log file.'
                        'Defaults to ./logs/docker_check_adoption.log.')
    args = parser.parse_args()

    # Normalize paths
    args.input = valid_path(args.input)
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
    log.info('Starting docker_check_adoption.py.')


def log_finish():
    '''
    Script simply logs time of script completion and total time elapsed.
    '''

    # Log end of script
    log.info('Script completed. Total time:'
             f'{datetime.now()-script_start_time}')


def check_adoption(args):
    '''
    This function checks the adoption of signatures for packages from Docker
    Hub.

    args: the arguments passed to the script.
    '''
    pass


# Classic Python main function
def main():
    # Parse arguments
    args = parse_args()

    # Setup logger
    setup_logger(args)

    # Check adoption of signatures
    check_adoption(args)

    # Log finish
    log_finish()


# Classic Python main function
if __name__ == '__main__':
    main()  # Call main function

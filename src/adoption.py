#!/usr/bin/env python

'''check_adoption.py: This script checks the adoption of signatures for
packages from Docker Hub.
'''

# Imports
import argparse
import logging as log
from datetime import datetime
from docker.adoption import adoption as docker_adoption
from util.files import valid_path_create, valid_path


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

    # Create parser
    parser = argparse.ArgumentParser(
        description='Check adoption for packages from Docker Hub.'
        'It takes in a newline delimited json file containing a list of '
        'packages and outputs a newline delimited json file containing '
        'a list of packages with their signature adoption status.')

    # Add arguments
    parser.add_argument('registry',
                        type=str,
                        choices=['docker',
                                 'pypi',
                                 'npm',
                                 'huggingface',
                                 'maven'],
                        help='The registry to check adoption for.')
    parser.add_argument('--input-file',
                        type=str,
                        default='./data/-reg-/packages.ndjson',
                        help='The name of the input file for the registry. '
                        'Defaults to <./data/-reg-/packages.ndjson>. '
                        'The -reg- will be replaced with the registry name.')
    parser.add_argument('--output-file',
                        type=str,
                        default='./data/-reg-/adoption.ndjson',
                        help='The name of the output file for the registry. '
                        'Defaults to <./data/-reg-/adoption.ndjson>. '
                        'The -reg- will be replaced with the registry name.')
    parser.add_argument('--log',
                        type=str,
                        default='./logs/adoption.log',
                        help='The path to the log file. '
                        'Defaults to <./logs/adoption.log.>.')
    parser.add_argument('--start',
                        type=int,
                        default=0,
                        help='The starting line of the input file. '
                        'Defaults to 0.')
    parser.add_argument('--end',
                        type=int,
                        default=-1,
                        help='The ending line of the input file. '
                        'Defaults to -1 (the last line).')
    parser.add_argument('--min-downloads',
                        type=int,
                        default=1,
                        help='The minimum number of downloads for a package '
                        'to be considered for adoption. '
                        'Defaults to 1.')
    parser.add_argument('--min-versions',
                        type=int,
                        default=1,
                        help='The minimum number of versions for a package '
                        'to be considered for adoption. '
                        'Defaults to 1.')

    # Parse arguments
    args = parser.parse_args()

    # Normalize paths
    args.log = valid_path_create(args.log)
    args.output_file = valid_path_create(
        args.output_file.replace('-reg-', args.registry))
    args.input_file = valid_path(
        args.input_file.replace('-reg-', args.registry))

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
                    format=f'%(asctime)s|%(levelname)s|{args.registry}'
                    '|%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

    # Log start time
    log.info("Starting adoption.py.")

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

    # Check adoption of signatures
    if args.registry == 'docker':
        docker_adoption(input_file_path=args.input_file,
                        output_file_path=args.output_file,
                        start=args.start,
                        end=args.end,
                        min_downloads=args.min_downloads,
                        min_versions=args.min_versions)
    elif args.registry == 'pypi':
        pass
    elif args.registry == 'npm':
        pass
    elif args.registry == 'huggingface':
        pass
    elif args.registry == 'maven':
        pass

    # Log finish
    log_finish()


# Classic Python main function
if __name__ == '__main__':
    main()  # Call main function

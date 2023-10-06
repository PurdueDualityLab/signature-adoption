#!/usr/bin/env python

'''check_adoption.py: This script checks the adoption of signatures for
packages from Docker Hub.
'''

# Imports
import json
import argparse
import subprocess
import logging as log
from datetime import datetime
from util.files import valid_path, valid_path_create


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
        'a list of packages with their signature adoption status.')
    parser.add_argument('--output',
                        type=str,
                        default='./data/docker/adoption.ndjson',
                        help='The path basis to the output files.'
                        'Defaults to ./data/docker/adoption.ndjson.')
    parser.add_argument('--input',
                        type=str,
                        default='./data/docker/packages.ndjson',
                        help='The path to the input file.'
                        'Defaults to ./data/docker/packages.ndjson.')
    parser.add_argument('--log',
                        type=str,
                        default='./logs/docker/check_adoption.log',
                        help='The path to the log file.'
                        'Defaults to ./logs/docker/check_adoption.log.')
    parser.add_argument('--start',
                        type=int,
                        default=0,
                        help='The starting line of the input file.'
                        'Defaults to 0.')
    parser.add_argument('--end',
                        type=int,
                        default=-1,
                        help='The ending line of the input file.'
                        'Defaults to -1 (the last line).')
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
    log.info("Starting docker's check_adoption.py.")


def log_finish():
    '''
    Script simply logs time of script completion and total time elapsed.
    '''

    # Log end of script
    log.info('Script completed. Total time:'
             f'{datetime.now()-script_start_time}')


def get_signatures(package_name):
    '''
    This function gets the signatures for a package from Docker Hub.

    package_name: the name of the package.

    returns: the output of the docker trust inspect command.
    '''

    # Check to see if package has signatures
    output = subprocess.run(
        [
            "docker",
            "trust",
            "inspect",
            f"{package_name}",
        ],
        capture_output=True)

    return {"stdout": output.stdout.decode("utf-8"),
            "stderr": output.stderr.decode("utf-8")}


def check_adoption(args):
    '''
    This function checks the adoption of signatures for packages from Docker
    Hub.

    args: the arguments passed to the script.
    '''

    with open(args.input, 'r') as input_file, \
            open(args.output, 'a') as output_file:

        # Read input file
        for i, line in enumerate(input_file):

            # Skip lines and check for end
            if i < args.start:
                continue
            if args.end != -1 and i > args.end:
                break

            # Log progress
            if i % 100 == 0:
                log.info(f'Processing package {i}.')

            # Parse line
            package = json.loads(line)
            package_name = package['name']

            # Get package's signatures
            signatures = get_signatures(package_name)

            # Add signatures to package
            package['signatures'] = signatures

            # Write package to output file
            json.dump(package, output_file, default=str)
            output_file.write('\n')


def main():
    '''
    This is the main function of the script.
    '''
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

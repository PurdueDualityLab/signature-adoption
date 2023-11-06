#!/usr/bin/env python

'''packages.py: This script gets the repositories and associated metadata
for all registries supported by this project.
'''

# Import statements
import argparse
import logging as log
from datetime import datetime
from util.files import valid_path_create, gen_path
from huggingface.packages import packages as huggingface_packages
from docker.packages import packages as docker_packages
from maven.packages import packages as maven_packages
from pypi.packages import packages as pypi_packages

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"

# Define global variables
script_start_time = datetime.now()


# Function to parse arguments
def parse_args():
    ''' This function parses arguments passed to the script.

    returns: args - the arguments passed to the script
    '''
    parser = argparse.ArgumentParser(
        description='Get packages from ecosystems database.'
        'The packages will be written to a Newline Delimited JSON file.')
    parser.add_argument('--output-folder',
                        type=str,
                        default='./data/-eco-',
                        help='The path basis to the output files.'
                        'Defaults to ./data/-eco-'
                        'The -eco- will be replaced with the ecosystem name.')
    parser.add_argument('--output-filename',
                        type=str,
                        default='packages.ndjson',
                        help='The name of the output file for each ecosystem.'
                        'Defaults to packages.ndjson.'
                        'This will be saved in the output-folder.')
    parser.add_argument('--log',
                        type=str,
                        default='./logs/packages.log',
                        help='The path to the log file.'
                        'Defaults to ./logs/packages.log.')
    parser.add_argument('--pypi',
                        '-p',
                        action='store_true',
                        help='Flag to get packages from PyPI.')
    parser.add_argument('--docker',
                        '-d',
                        action='store_true',
                        help='Flag to get packages from Docker Hub.')
    parser.add_argument('--npm',
                        '-n',
                        action='store_true',
                        help='Flag to get packages from npm.')
    parser.add_argument('--maven',
                        '-m',
                        action='store_true',
                        help='Flag to get packages from Maven.')
    parser.add_argument('--huggingface',
                        '-f',
                        action='store_true',
                        help='Flag to get packages from Hugging Face.')
    args = parser.parse_args()

    # Normalize paths
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
    log.info('Starting get_tags script.')


def log_finish():
    '''
    Script simply logs time of script completion and total time elapsed.
    '''

    # Log end of script
    log.info('Script completed. Total time:'
             f'{datetime.now()-script_start_time}')


def get_huggingface_packages(args):
    '''
    This function gets the packages from Hugging Face.

    args: the arguments passed to the script
    '''

    huggingface_packages(
        hf_dump_path=gen_path(
            output_folder=args.output_folder,
            output_file=args.output_file,
            eco='huggingface'),
        simplified_csv_path=gen_path(
            output_folder=args.output_folder,
            output_file='simplified.csv',
            eco='huggingface'))


def get_docker_packages(args):
    '''
    This function gets the packages from Docker Hub.

    args: the arguments passed to the script
    '''

    docker_packages(
        output_path=gen_path(
            output_folder=args.output_folder,
            output_file=args.output_file,
            eco='docker'))


def get_maven_packages(args):
    '''
    This function gets the packages from Maven.

    args: the arguments passed to the script
    '''

    maven_packages(
        output_path=gen_path(
            output_folder=args.output_folder,
            output_file=args.output_file,
            eco='maven'))


def get_pypi_packages(args):
    '''
    This function gets the packages from PyPI.

    args: the arguments passed to the script
    '''

    pypi_packages(
        output_path=gen_path(
            output_folder=args.output_folder,
            output_file=args.output_file,
            eco='pypi'))


# Classic Python main function
def main():
    # Parse arguments
    args = parse_args()

    # Setup logger
    setup_logger(args)

    # Get packages from each of the registries
    if args.huggingface:
        get_huggingface_packages(args)
    if args.docker:
        get_docker_packages(args)
    if args.maven:
        get_maven_packages(args)
    if args.pypi:
        get_pypi_packages(args)

    # Log finish
    log_finish()


# Classic Python main function
if __name__ == '__main__':
    main()  # Call main function

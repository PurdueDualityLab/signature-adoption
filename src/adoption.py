#!/usr/bin/env python

'''adoption.py: This script checks the adoption of signatures for different
registries.
'''

# Imports
import argparse
import logging as log
from datetime import datetime
from docker.adoption import adoption as docker_adoption
from maven.adoption import adoption as maven_adoption
from pypi.adoption import adoption as pypi_adoption
from huggingface.adoption import adoption as huggingface_adoption
from util.files import valid_path_create, valid_path


# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'

# Define global variables
script_start_time = datetime.now()


def docker(args):
    '''
    This function checks the adoption of signatures for packages from Docker
    Hub.

    args: The arguments passed to the script.
    '''
    docker_adoption(
        input_file_path=args.input_file,
        output_file_path=args.output_file
    )


def pypi(args):
    '''
    This function checks the adoption of signatures for packages from PyPI.

    args: The arguments passed to the script.
    '''
    args.download_dir = valid_path_create(args.download_dir, folder=True)
    pypi_adoption(
        input_file_path=args.input_file,
        output_file_path=args.output_file,
        download_path=args.download_dir,
    )


def huggingface(args):
    '''
    This function checks the adoption of signatures for packages from
    HuggingFace.

    args: The arguments passed to the script.
    '''
    args.download_dir = valid_path_create(args.download_dir, folder=True)
    huggingface_adoption(
        input_file_path=args.input_file,
        output_file_path=args.output_file,
        download_path=args.download_dir,
        save=args.save,
    )


def maven(args):
    '''
    This function checks the adoption of signatures for packages from Maven.

    args: The arguments passed to the script.
    '''
    args.download_dir = valid_path_create(args.download_dir, folder=True)
    maven_adoption(
        input_file_path=args.input_file,
        output_file_path=args.output_file,
        download_path=args.download_dir,
    )


# Function to parse arguments
def parse_args():
    ''' This function parses arguments passed to the script.

    returns: the arguments passed to the script.
    '''

    # Create parser
    parser = argparse.ArgumentParser(
        description='Check adoption for packages from a specified registry.'
        'It takes in a newline delimited json file containing a list of '
        'packages and outputs a newline delimited json file containing '
        'a list of packages with their signature adoption status.')

    # global arguments
    parser.add_argument(
        '--input-file',
        type=str,
        default='./data/-reg-/filter.ndjson',
        help='The name of the input file for the registry. '
        'Defaults to <./data/-reg-/filter.ndjson>. '
        'The -reg- will be replaced with the registry name.'
    )
    parser.add_argument(
        '--output-file',
        type=str,
        default='./data/-reg-/adoption.ndjson',
        help='The name of the output file for the registry. '
        'Defaults to <./data/-reg-/adoption.ndjson>. '
        'The -reg- will be replaced with the registry name.'
    )
    parser.add_argument(
        '--log',
        type=str,
        default='./logs/-reg-/adoption.log',
        help='The path to the log file. '
        'Defaults to <./logs/-reg-/adoption.log>. '
        'The -reg- will be replaced with the registry name.'
    )

    # Create subparsers
    subparsers = parser.add_subparsers(
        title='registry',
        description='The registry to check adoption for.',
        help='This argument selects the registry to check adoption for.',
        dest='registry')

    # Docker subparser
    docker_parser = subparsers.add_parser('docker')
    docker_parser.set_defaults(func=docker)

    # PyPI subparser
    pypi_parser = subparsers.add_parser('pypi')
    pypi_parser.set_defaults(func=pypi)

    # HuggingFace subparser
    huggingface_parser = subparsers.add_parser('huggingface')
    huggingface_parser.set_defaults(func=huggingface)
    huggingface_parser.add_argument(
        '--dl-dir',
        '-d',
        metavar='DIR',
        dest='download_dir',
        type=str,
        default='./data/huggingface/downloads/',
        help='The path to the directory to download '
        'files to. Defaults to '
        '<./data/huggingface/downloads/>.'
    )

    # Maven subparser
    maven_parser = subparsers.add_parser('maven')
    maven_parser.set_defaults(func=maven)
    maven_parser.add_argument(
        '--dl-dir',
        '-d',
        metavar='DIR',
        dest='download_dir',
        type=str,
        default='./data/maven/downloads/',
        help='The path to the directory to download '
        'files to. Defaults to '
        '<./data/maven/downloads/>.'
    )

    # Parse arguments
    args = parser.parse_args()

    # Normalize paths
    args.log = valid_path_create(
        args.log.replace('-reg-', args.registry))
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

    # Check adoption of signatures the function is set by the subparser
    args.func(args)

    # Log finish
    log_finish()


# Classic Python main function
if __name__ == '__main__':
    main()  # Call main function

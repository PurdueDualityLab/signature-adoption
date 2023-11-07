#!/usr/bin/env python

'''packages.py: This script gets the repositories and associated metadata
for all registries supported by this project.
'''

# Import statements
import argparse
import logging as log
from datetime import datetime
from util.files import valid_path_create, gen_path, valid_path
from huggingface.packages import packages as huggingface_packages
from docker.packages import packages as docker_packages
from maven.packages import packages as maven_packages
from pypi.packages import packages as pypi_packages

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"

# Define global variables
script_start_time = datetime.now()


def huggingface(args):
    '''
    This function gets the packages from Hugging Face.

    args: the arguments passed to the script
    '''

    output_path = gen_path(
        directory=args.output_folder,
        file=args.output_file,
        ecosystem='huggingface')

    if args.token is None:
        huggingface_packages(
            output_path=output_path,
            token_path=valid_path(
                path=args.token_path
            )
        )
    else:
        huggingface_packages(
            output_path=output_path,
            token=args.token
        )


def docker(args):
    '''
    This function gets the packages from Docker Hub.

    args: the arguments passed to the script
    '''

    docker_packages(
        output_path=gen_path(
            output_folder=args.output_folder,
            output_file=args.output_file,
            eco='docker'))


def maven(args):
    '''
    This function gets the packages from Maven.

    args: the arguments passed to the script
    '''

    maven_packages(
        output_path=gen_path(
            output_folder=args.output_folder,
            output_file=args.output_file,
            eco='maven'))


def pypi(args):
    '''
    This function gets the packages from PyPI.

    args: the arguments passed to the script
    '''

    pypi_packages(
        output_path=gen_path(
            output_folder=args.output_folder,
            output_file=args.output_file,
            eco='pypi'))


# Function to parse arguments
def parse_args():
    ''' This function parses arguments passed to the script.

    returns: args - the arguments passed to the script
    '''

    # Top level parser
    parser = argparse.ArgumentParser(
        description='Get a list of packages and metadata from a specified '
        'registry. The output is a newline delimited JSON file with each '
        'line being a JSON object containing the metadata for a package.')

    # global arguments
    parser.add_argument('--out-dir',
                        dest='output_folder',
                        metavar='DIR',
                        type=str,
                        default='./data/-eco-',
                        help='The directory for the output files. '
                        'Defaults to ./data/-eco-. '
                        'The -eco- will be replaced with the ecosystem name.')
    parser.add_argument('--out-name',
                        dest='output_file',
                        metavar='NAME',
                        type=str,
                        default='packages.ndjson',
                        help='The name of the output file for each ecosystem. '
                        'Defaults to packages.ndjson. '
                        'This will be saved in the output-folder.')
    parser.add_argument('--log-path',
                        dest='log',
                        metavar='FILE',
                        type=str,
                        default='./logs/packages.log',
                        help='The path to the log file. '
                        'Defaults to ./logs/packages.log.')

    # Create subparsers
    subparsers = parser.add_subparsers(
        title='registry',
        description='The registry to get packages from.',
        help='The registry to get a list of packages from.',
        dest='registry',
        required=True)

    # Hugging Face subparser
    huggingface_parser = subparsers.add_parser(
        'huggingface',
        help='Get packages from Hugging Face.')
    huggingface_parser.set_defaults(func=huggingface)
    hf_token_group = huggingface_parser.add_argument_group(
        'HuggingFace Tokens')
    hf_me_group = hf_token_group.add_mutually_exclusive_group()
    hf_me_group.add_argument('--token',
                             dest='token',
                             metavar='TOKEN',
                             type=str,
                             default=None,
                             help='The Hugging Face API token.')
    hf_me_group.add_argument('--token-path',
                             dest='token_path',
                             metavar='FILE',
                             type=str,
                             default='./hftoken.txt',
                             help='The path to the file containing the '
                             'Hugging Face API token. '
                             'Defaults to ./hftoken.txt.')

    # Docker subparser
    docker_parser = subparsers.add_parser(
        'docker',
        help='Get packages from Docker Hub.')
    docker_parser.set_defaults(func=docker)

    # Maven subparser
    maven_parser = subparsers.add_parser(
        'maven',
        help='Get packages from Maven.')
    maven_parser.set_defaults(func=maven)

    # PyPI subparser
    pypi_parser = subparsers.add_parser(
        'pypi',
        help='Get packages from PyPI.')
    pypi_parser.set_defaults(func=pypi)

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
    log.info('Starting packages script.')

    # Log arguments
    log.info(f'Arguments: {args}')


def log_finish():
    '''
    Script simply logs time of script completion and total time elapsed.
    '''

    # Log end of script
    log.info('Script completed. Total time:'
             f'{datetime.now()-script_start_time}')


# Classic Python main function
def main():
    # Parse arguments
    args = parse_args()

    # Setup logger
    setup_logger(args)

    # Call function
    args.func(args)

    # Log finish
    log_finish()


# Classic Python main function
if __name__ == '__main__':
    main()  # Call main function

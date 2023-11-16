#!/usr/bin/env python

'''packages.py: This script gets the repositories and associated metadata
for all registries supported by this project.
'''

# Import statements
import argparse
import logging as log
from datetime import datetime
from signature_adoption.util.files import valid_path_create, gen_path, valid_path
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

    # Call the function, but check if the token is passed as an argument or
    # read from a file
    if args.token is None:
        huggingface_packages(
            output_path=args.output_path,
            token_path=valid_path(
                path=args.token_path
            )
        )
    else:
        huggingface_packages(
            output_path=args.output_path,
            token=args.token
        )


def docker(args):
    '''
    This function gets the packages from Docker Hub.

    args: the arguments passed to the script
    '''

    # Call the function
    docker_packages(output_path=args.output_path)


def maven(args):
    '''
    This function gets the packages from Maven.

    args: the arguments passed to the script
    '''

    # Call the function
    maven_packages(output_path=args.output_path)


def pypi(args):
    '''
    This function gets the packages from PyPI.

    args: the arguments passed to the script
    '''

    # Check the authentication path
    auth_path = args.auth_path
    if auth_path is not None:
        auth_path = valid_path(path=auth_path)

    # Call the function
    pypi_packages(output_path=args.output_path,
                  auth_path=auth_path)


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
    parser.add_argument('--out-path',
                        dest='output_path',
                        metavar='PATH',
                        type=str,
                        default='./data/-eco-/packages.ndjson',
                        help='The path to the output file. '
                        'Defaults to ./data/-eco-/packages.ndjson. '
                        'The -eco- will be replaced with the ecosystem name.')
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
        'HuggingFace Tokens',
        'Pass the Hugging Face API token. This can be passed as an argument '
        'or read from a file. Only one of these options can be used. The '
        'default is to read from a file.')
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
    pypi_parser.add_argument('--auth-path',
                             dest='auth_path',
                             metavar='FILE',
                             type=str,
                             default=None,
                             help='The path to the file containing the Google '
                             'BigQuery authentication information. '
                             'Defaults to None and assumes that the '
                             'authentication information is in the '
                             'GOOGLE_APPLICATION_CREDENTIALS environment '
                             'variable.')

    args = parser.parse_args()

    # Normalize paths
    args.log = valid_path_create(args.log)
    args.output_path = gen_path(
        directory='',
        file=args.output_path,
        ecosystem=args.registry)

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

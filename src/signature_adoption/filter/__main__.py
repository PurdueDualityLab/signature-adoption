#!/usr/bin/env python

'''
__main__.py: This script filters the list of packages for each registry.
'''

# Import statements
import argparse
import logging as log
from datetime import datetime
from ..util.files import valid_path_create, gen_path
from .huggingface import filter as huggingface_filter
from .docker import filter as docker_filter
from .maven import filter as maven_filter
from .pypi import filter as pypi_filter

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

    # Call the function
    huggingface_filter(
        input_path=args.input_path,
        output_path=args.output_path,
        random_select=args.random_select,
        min_downloads=args.min_downloads,
        min_likes=args.min_likes
    )


def docker(args):
    '''
    This function gets the packages from Docker Hub.

    args: the arguments passed to the script
    '''

    # Call the function
    docker_filter(
        input_path=args.input_path,
        output_path=args.output_path,
        random_select=args.random_select,
        min_downloads=args.min_downloads,
        min_versions=args.min_versions
    )


def maven(args):
    '''
    This function gets the packages from Maven.

    args: the arguments passed to the script
    '''

    # Call the function
    maven_filter(
        input_path=args.input_path,
        output_path=args.output_path,
        random_select=args.random_select,
        min_versions=args.min_versions,
        min_dependants=args.min_dependants
    )


def pypi(args):
    '''
    This function gets the packages from PyPI.

    args: the arguments passed to the script
    '''

    # Call the function
    pypi_filter(
        input_path=args.input_path,
        output_path=args.output_path,
        random_select=args.random_select,
        min_versions=args.min_versions
    )


# Function to parse arguments
def parse_args():
    ''' This function parses arguments passed to the script.

    returns: args - the arguments passed to the script
    '''

    # Top level parser
    parser = argparse.ArgumentParser(
        description='This script takes in a newline delimited JSON file of '
        'packages and filters them based on registry specific criteria. '
        'The output is a newline delimited JSON file of packages that meet '
        'the criteria.')

    # global arguments
    parser.add_argument('--input-path',
                        dest='input_path',
                        metavar='PATH',
                        type=str,
                        default='./data/-eco-/packages.ndjson',
                        help='The path to the input file. '
                        'Defaults to ./data/-eco-/packages.ndjson. '
                        'The -eco- will be replaced with the ecosystem name.')
    parser.add_argument('--out-path',
                        dest='output_path',
                        metavar='PATH',
                        type=str,
                        default='./data/-eco-/filter.ndjson',
                        help='The path to the output file. '
                        'Defaults to ./data/-eco-/filter.ndjson. '
                        'The -eco- will be replaced with the ecosystem name.')
    parser.add_argument('--log-path',
                        dest='log',
                        metavar='FILE',
                        type=str,
                        default='./logs/filter.log',
                        help='The path to the log file. '
                        'Defaults to ./logs/filter.log.')

    # Create subparsers
    subparsers = parser.add_subparsers(
        title='registry',
        description='The registry to filter packages from.',
        help='The registry to apply a filter to.',
        dest='registry',
        required=True)

    # Hugging Face subparser
    huggingface_parser = subparsers.add_parser(
        'huggingface',
        help='Filter packages from Hugging Face.')
    huggingface_parser.set_defaults(func=huggingface)
    huggingface_parser.add_argument('--random-select',
                                    dest='random_select',
                                    metavar='N',
                                    type=int,
                                    default=-1,
                                    help='Randomly select N packages. '
                                    'Defaults to -1, which means all.')
    huggingface_parser.add_argument('--min-downloads',
                                    dest='min_downloads',
                                    metavar='N',
                                    type=int,
                                    default=1,
                                    help='The minimum number of downloads. '
                                    'Defaults to 1.')
    huggingface_parser.add_argument('--min-likes',
                                    dest='min_likes',
                                    metavar='N',
                                    type=int,
                                    default=0,
                                    help='The minimum number of likes. '
                                    'Defaults to 0.')

    # Docker subparser
    docker_parser = subparsers.add_parser(
        'docker',
        help='Filter packages from Docker Hub.')
    docker_parser.set_defaults(func=docker)
    docker_parser.add_argument('--random-select',
                               dest='random_select',
                               metavar='N',
                               type=int,
                               default=-1,
                               help='Randomly select N packages. '
                               'Defaults to -1, which means all.')
    docker_parser.add_argument('--min-downloads',
                               dest='min_downloads',
                               metavar='N',
                               type=int,
                               default=1,
                               help='The minimum number of downloads. '
                               'Defaults to 1.')
    docker_parser.add_argument('--min-versions',
                               dest='min_versions',
                               metavar='N',
                               type=int,
                               default=1,
                               help='The minimum number of versions. '
                               'Defaults to 1.')

    # Maven subparser
    maven_parser = subparsers.add_parser(
        'maven',
        help='Filter packages from Maven.')
    maven_parser.set_defaults(func=maven)
    maven_parser.add_argument('--random-select',
                              dest='random_select',
                              metavar='N',
                              type=int,
                              default=-1,
                              help='Randomly select N packages. '
                              'Defaults to -1, which means all.')
    maven_parser.add_argument('--min-versions',
                              dest='min_versions',
                              metavar='N',
                              type=int,
                              default=1,
                              help='The minimum number of versions. '
                              'Defaults to 1.')
    maven_parser.add_argument('--min-dependants',
                              dest='min_dependants',
                              metavar='N',
                              type=int,
                              default=1,
                              help='The minimum number of dependants. '
                              'Defaults to 1.')

    # PyPI subparser
    pypi_parser = subparsers.add_parser(
        'pypi',
        help='Filter packages from PyPI.')
    pypi_parser.set_defaults(func=pypi)
    pypi_parser.add_argument('--random-select',
                             dest='random_select',
                             metavar='N',
                             type=int,
                             default=-1,
                             help='Randomly select N packages. '
                             'Defaults to -1, which means all.')
    pypi_parser.add_argument('--min-versions',
                             dest='min_versions',
                             metavar='N',
                             type=int,
                             default=1,
                             help='The minimum number of versions. '
                             'Defaults to 1.')

    args = parser.parse_args()

    # Normalize paths
    args.log = valid_path_create(args.log)
    args.input_path = gen_path(
        directory="",
        file=args.input_path,
        ecosystem=args.registry)
    args.output_path = gen_path(
        directory="",
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
    log.info('Starting filter script.')

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

#!/usr/bin/env python

'''analysis.py: This script is used to analyze the adoption of all registries
with data.'''

# Imports
import argparse
from datetime import datetime
from util.files import valid_path_create, valid_path


# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'


def pypi(args):
    '''This function is used to analyze the adoption of PyPI.

    args: The arguments passed in from the command line.
    '''
    pass


def maven(args):
    '''This function is used to analyze the adoption of Maven.

    args: The arguments passed in from the command line.
    '''
    pass


def npm(args):
    '''This function is used to analyze the adoption of npm.

    args: The arguments passed in from the command line.
    '''
    pass


def huggingface(args):
    '''This function is used to analyze the adoption of HuggingFace.

    args: The arguments passed in from the command line.
    '''
    pass


def docker(args):
    '''This function is used to analyze the adoption of Docker.

    args: The arguments passed in from the command line.
    '''
    pass


# Function to parse arguments
def parse_args():
    ''' This function parses arguments passed to the script.

    returns: the arguments passed to the script.
    '''

    # Create parser
    parser = argparse.ArgumentParser(
        description='This script is used to analyze the adoption of all '
        'registries with data. The script takes in the ndjson file of '
        'adoption data and outputs a summary json file.')

    # global arguments
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
    parser.add_argument('--maven'
                        '-m',
                        action='store_true',
                        help='Flag to analyze Maven.')
    parser.add_argument('--npm',
                        '-n',
                        action='store_true',
                        help='Flag to analyze npm.')
    parser.add_argument('--pypi',
                        '-p',
                        action='store_true',
                        help='Flag to analyze PyPI.')
    parser.add_argument('--huggingface',
                        '-f',
                        action='store_true',
                        help='Flag to analyze HuggingFace.')
    parser.add_argument('--docker',
                        '-d',
                        action='store_true',
                        help='Flag to analyze Docker.')

    args = parser.parse_args()

    # Normalize paths
    args.output_file = valid_path_create(
        args.output_file.replace('-reg-', args.registry))
    args.input_file = valid_path(
        args.input_file.replace('-reg-', args.registry))

    return args


def main():
    '''
    This is the main function of the script.
    '''
    # Parse arguments
    args = parse_args()

    # Run appropriate analysis
    if args.maven:
        maven(args)
    if args.npm:
        npm(args)
    if args.pypi:
        pypi(args)
    if args.huggingface:
        huggingface(args)
    if args.docker:
        docker(args)

# Classic Python main function
if __name__ == '__main__':
    main()  # Call main function

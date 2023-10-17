#!/usr/bin/env python

'''analysis.py: This script is used to analyze the adoption of all registries
with data.'''

# Imports
import argparse
from datetime import datetime
import json
from util.files import valid_path_create, valid_path


# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'


def pypi(args):
    '''This function is used to analyze the adoption of PyPI.

    args: The arguments passed in from the command line.
    '''

    # Normalize paths
    summary_file = valid_path_create(
        args.summary.replace('-reg-', 'pypi'))
    input_file = valid_path(
        args.input_file.replace('-reg-', 'pypi'))

    # create a summary dictionary
    summary = {
        'total_packages': 0,
        'total_versions': 0,
        'total_signatures': 0,
        'latest_signed': 0,
    }

    package_names = {}

    # open the input file
    with open(input_file, 'r') as f:
        # iterate through the file
        for line in f:
            # load the line as a json object
            package = json.loads(line)

            # increment the total packages
            package_names.add(package['name'])

            # increment the total versions
            summary['total_versions'] += len(package['versions'])

            # iterate through the versions
            for version in package['versions']:
                # increment the total signatures
                summary['total_signatures'] += len(version['signatures'])

                # check if the version is the latest
                if version['latest']:
                    # increment the latest signed
                    summary['latest_signed'] += len(version['signatures'])


def maven(args):
    '''This function is used to analyze the adoption of Maven.

    args: The arguments passed in from the command line.
    '''
    pass


def npm(args):
    '''This function is used to analyze the adoption of npm.

    args: The arguments passed in from the command line.
    '''
    # Normalize paths
    summary_file = valid_path_create(
        args.summary.replace('-reg-', 'npm'))
    input_file = valid_path(
        args.input_file.replace('-reg-', 'npm'))

    # create a summary dictionary
    summary = {
        'total_packages': 0,
        'total_versions': 0,
        'pgp': {
            'total_signatures': 0,
            'latest_signed': 0,
        },
        'ecdsa': {
            'total_signatures': 0,
            'total_good': 0,
            'latest_signed': 0,
        },
        'total_unsigned': 0,
    }

    # open the input file
    with open(input_file, 'r') as f:

        for line in f:

            package = json.loads(line)

            # increment the total packages
            summary['total_packages'] += 1

            # increment the total versions
            summary['total_versions'] += len(package['versions'])

            # iterate through the versions
            for version in package['versions']:
                signatures = version['signatures']

                if signatures is None:
                    summary['total_unsigned'] += 1
                    continue
                if signatures['ecdsa']:
                    summary['ecdsa']['total_signatures'] += 1
                    if signatures['ecdsa'] is True:
                        summary['ecdsa']['total_good'] += 1
                    if version['number'] == package['latest_release_number']:
                        summary['ecdsa']['latest_signed'] += 1
                if signatures['pgp']:










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
    parser.add_argument('--summary-file',
                        type=str,
                        default='./data/-reg-/summary.json',
                        help='The name of the summary file for the registry. '
                        'Defaults to <./data/-reg-/summary.json>. '
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

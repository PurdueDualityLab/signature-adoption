#!/usr/bin/env python

'''analysis.py: This script is used to analyze the adoption of all registries
with data.'''

# Imports
import argparse
from datetime import datetime
import json
from enum import Enum
from util.files import valid_path_create, valid_path


# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'


class PGP_Sig_Status(Enum):
    '''
    This is an enum to represent the status of a PGP signature.
    '''
    GOOD = 1
    BAD = 2
    GOOD_EXPIRED = 3
    EXPIRED = 4
    NO_PUB = 5
    INVALID_PUB = 6
    UNVERIFIABLE = 7


pnt = True


def check_pgp(stderr):
    '''
    This function is used to check if a PGP signature is valid.

    stderr: The stderr output from the gpg command.

    returns: info about signature validity
    '''

    if 'Good signature' in stderr:
        if 'expired' in stderr:
            return PGP_Sig_Status.GOOD_EXPIRED
        return PGP_Sig_Status.GOOD
    elif 'BAD signature' in stderr:
        return PGP_Sig_Status.BAD
    elif 'expired' in stderr:
        return PGP_Sig_Status.EXPIRED
    elif 'No public key' in stderr:
        return PGP_Sig_Status.NO_PUB
    elif 'Invalid public key' in stderr:
        return PGP_Sig_Status.INVALID_PUB
    return PGP_Sig_Status.UNVERIFIABLE

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
        'total_files': 0,
        'total_signatures': 0,
        'total_unsigned': 0,
        PGP_Sig_Status.GOOD.name: 0,
        PGP_Sig_Status.BAD.name: 0,
        PGP_Sig_Status.GOOD_EXPIRED.name: 0,
        PGP_Sig_Status.EXPIRED.name: 0,
        PGP_Sig_Status.NO_PUB.name: 0,
        PGP_Sig_Status.INVALID_PUB.name: 0,
        PGP_Sig_Status.UNVERIFIABLE.name: 0,
    }

    # open the input file
    with open(input_file, 'r') as f:
        # iterate through the file
        for line in f:
            # load the line as a json object
            package = json.loads(line)

            # increment the total packages
            summary['total_packages'] += 1

            for version_name, files in package['versions'].items():
                summary['total_versions'] += 1

                for file in files:
                    summary['total_files'] += 1

                    if file['has_signature'] and file['signature'] is not None:
                        summary['total_signatures'] += 1

                        summary[check_pgp(
                            file['signature']['stderr']).name] += 1
                    else:
                        summary['total_unsigned'] += 1

    # write the summary to the summary file
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=4)


def maven(args):
    '''This function is used to analyze the adoption of Maven.

    args: The arguments passed in from the command line.
    '''
    # Normalize paths
    summary_file = valid_path_create(
        args.summary.replace('-reg-', 'maven'))
    input_file = valid_path(
        args.input_file.replace('-reg-', 'maven'))

    # create a summary dictionary
    summary = {
        'total_packages': 0,
        'total_versions': 0,
        'total_files': 0,
        'total_signatures': 0,
        'total_unsigned': 0,
    }

    # open the input file
    with open(input_file, 'r') as f:
        # iterate through the file
        for line in f:
            # load the line as a json object
            package = json.loads(line)

            # increment the total versions
            summary['total_packages'] += 1
            missing = False

            for version in package['versions']:
                summary['total_versions'] += 1
                if 'files' in version:
                    for file in version['files']:
                        summary['total_files'] += 1

                        if file['has_signature'] \
                                and file['stderr'] is not None \
                                and file['stderr'] != '':

                            summary['total_signatures'] += 1
                        else:
                            summary['total_unsigned'] += 1

            if missing:
                print(package['name'])

    # write the summary to the summary file
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=4)


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
        'pgp_total_signatures': 0,
        'ecdsa_total_signatures': 0,
        'total_unsigned': 0,
    }

    # open the input file
    with open(input_file, 'r') as f:

        for line in f:

            package = json.loads(line)

            # increment the total packages
            summary['total_packages'] += 1

            # iterate through the versions
            for version in package['versions']:

                if 'signatures' not in version:
                    continue

                summary['total_versions'] += 1

                signatures = version['signatures']

                if signatures is None or (
                        signatures['ecdsa'] is None and signatures['pgp'] is None):
                    summary['total_unsigned'] += 1
                    continue
                if signatures['ecdsa'] is not None:
                    summary['ecdsa']['total_signatures'] += 1
                if signatures['pgp'] is not None:
                    summary['pgp']['total_signatures'] += 1

    # write the summary to the summary file
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=4)


def huggingface(args):
    '''This function is used to analyze the adoption of HuggingFace.

    args: The arguments passed in from the command line.
    '''
    # Normalize paths
    summary_file = valid_path_create(
        args.summary.replace('-reg-', 'huggingface'))
    input_file = valid_path(
        args.input_file.replace('-reg-', 'huggingface'))

    # create a summary dictionary
    summary = {
        'total_packages': 0,
        'total_commits': 0,
        'total_signatures': 0,
        'total_unsigned': 0,
        'errsig': 0,
        'bad': 0,
        'good': 0,
        'ambig': 0,
        'expire': 0,
    }

    # open the input file
    with open(input_file, 'r') as f:
        # iterate through the file
        for line in f:
            # load the line as a json object
            package = json.loads(line)

            # increment the total versions
            summary['total_packages'] += 1

            for commit in package['commits']:
                summary['total_commits'] += 1

                if commit['output'] == '' and commit['error'] == '':
                    summary['total_unsigned'] += 1
                else:
                    summary['total_signatures'] += 1
                    if 'ERRSIG' in commit['error']:
                        summary['errsig'] += 1
                    elif 'bad signature' in commit['error']:
                        summary['bad'] += 1
                    elif 'GOODSIG' in commit['error']:
                        summary['good'] += 1
                    elif 'ambiguous' in commit['error']:
                        summary['ambig'] += 1
                    elif 'KEYEXPIRED' in commit['error']:
                        summary['expire'] += 1
                    else:

                        print(commit['error'])

    # write the summary to the summary file
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=4)


def docker(args):
    '''This function is used to analyze the adoption of Docker.

    args: The arguments passed in from the command line.
    '''
    # Normalize paths
    summary_file = valid_path_create(
        args.summary.replace('-reg-', 'docker'))
    input_file = valid_path(
        args.input_file.replace('-reg-', 'docker'))

    # create a summary dictionary
    summary = {
        'total_packages': 0,
        'total_versions': 0,
        'total_signatures': 0,
        'total_unsigned': 0,
    }

    # open the input file
    with open(input_file, 'r') as f:
        # iterate through the file
        for line in f:
            # load the line as a json object
            package = json.loads(line)

            # increment the total versions
            summary['total_packages'] += 1
            summary['total_versions'] += package['versions_count']

            if len(package['signatures']) == 0:
                summary['total_unsigned'] += package['versions_count']
            else:
                summary['total_signatures'] += len(
                    package['signatures'][0]['SignedTags'])

    # write the summary to the summary file
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=4)


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
                        default='./data/-reg-/adoption.ndjson',
                        help='The name of the input file for the registry. '
                        'Defaults to <./data/-reg-/adoption.ndjson>. '
                        'The -reg- will be replaced with the registry name.')
    parser.add_argument('--summary-file',
                        type=str,
                        default='./data/-reg-/summary.json',
                        dest='summary',
                        help='The name of the summary file for the registry. '
                        'Defaults to <./data/-reg-/summary.json>. '
                        'The -reg- will be replaced with the registry name.')
    parser.add_argument('--maven',
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

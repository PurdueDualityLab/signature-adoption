import matplotlib.pyplot as plt
import argparse
import sqlite3
import requests
from pathlib import Path


def parse_args():
    ''' This function parses arguments passed to the script.

    returns: the arguments passed to the script.
    '''

    # Create parser
    parser = argparse.ArgumentParser(
        description='Check public key servers for the public keys.'
    )

    # global arguments
    parser.add_argument(
        'input',
        type=Path,
        default=None,
        help='File with a list of key ids to check.',
    )
    parser.add_argument(
        '--start',
        '-s',
        type=int,
        default=0,
        help='start processing at the Nth key in the input list. ',
    )
    parser.add_argument(
        '--end',
        '-e',
        type=int,
        default=-1,
        help='stop processing after the Nth key in the input list. ',
    )
    # parser.add_argument(
    #     'output',
    #     metavar='OUTPUT',
    #     type=Path,
    #     default=None,
    #     help='The file to save the output to.',
    # )

    # Parse arguments
    args = parser.parse_args()

    return args


def check_key(url_builder, key_id):
    ''' This function checks a key on a key server.

    url_builder: the function to build the URL to check.
    key_id: the key id to check.

    returns: the status code of the check.
    '''

    # Build the URL
    url = url_builder(key_id)

    # Check the key
    response = requests.get(url)
    result = response.status_code

    return result


if __name__ == "__main__":

    # Parse arguments
    args = parse_args()

    # Read the input file
    key_ids = None
    with open(args.input, 'r') as f:
        key_ids = f.readlines()

    # Subset the keys
    key_ids = key_ids[args.start:args.end]

    # Dict for each keyserver
    keyservers = {
        'keyserver.ubuntu.com':
            lambda key_id:
            f'https://keyserver.ubuntu.com/pks/lookup?search={key_id}&'
            'fingerprint=on&op=index',
        'keys.openpgp.org':
            lambda key_id:
            f'https://keys.openpgp.org/search?q={key_id}',
    }

    # Check each key
    for key_id in key_ids:
        key_id = key_id.strip()
        results = [check_key(url_builder, key_id) for url_builder in keyservers.values()]
        print(f'{key_id}: {results}')

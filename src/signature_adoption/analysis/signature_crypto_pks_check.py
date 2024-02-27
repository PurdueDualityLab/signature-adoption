import argparse
import subprocess
import json
from datetime import datetime
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
    parser.add_argument(
        'output',
        metavar='OUTPUT',
        type=Path,
        default=None,
        help='The file to save the output to.',
    )
    parser.add_argument(
        'keyservers',
        metavar='KEYSERVERS',
        type=str,
        nargs='*',
        help='The key servers to check.',
    )

    # Parse arguments
    args = parser.parse_args()

    return args


def check_key(keyserver, key_id):
    ''' This function checks a key on a key server.

    keyserver: the key server to check.
    key_id: the key id to check.

    returns: the result of the check.
    '''

    output = subprocess.run(
        [
            'gpg',
            '--keyserver',
            keyserver,
            '--verbose',
            '--recv-keys',
            key_id,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout.decode("utf-8")

    return output


if __name__ == "__main__":

    # Parse arguments
    args = parse_args()

    # Read the input file
    key_ids = None
    with open(args.input, 'r') as f:
        key_ids = f.readlines()

    # Strip the keys
    key_ids = [key.strip() for key in key_ids]

    # Subset the keys
    key_ids = key_ids[args.start:args.end]

    # Check the keys
    results = {
        'key_ids': key_ids,
        'key_results': {},
    }
    found_keys = set()

    # Iterate over the key servers
    for keyserver in args.keyservers:

        results[keyserver] = {'found_keys': []}
        start_time = datetime.now()
        total = 0
        found = 0

        for key_id in key_ids:

            # Add the key to the results
            if key_id not in results['key_results']:
                results['key_results'][key_id] = {}

            # Check the key
            check = check_key(keyserver, key_id)
            results['key_results'][key_id][keyserver] = check

            # Check if the key was found
            if 'Total number processed: 1' in check:
                found += 1
                results[keyserver]['found_keys'].append(key_id)
                found_keys.add(key_id)
            total += 1

        # Add the results to the key server
        end_time = datetime.now()
        results[keyserver]['time'] = (end_time - start_time).total_seconds()
        results[keyserver]['total'] = total
        results[keyserver]['found'] = found

        # Print the results
        print(f'Processed {total} keys on {keyserver} in '
              f'{results[keyserver]["time"]} seconds.')
        print('Found', found, 'keys.')

    # Add the found keys to the results
    results['found_keys'] = list(found_keys)
    print('Total keys found:', len(found_keys))

    # Find keys that a key server did not find
    # for keyserver in args.keyservers:
    #     print('Keys not found on', keyserver)
    #     for key_id in found_keys:
    #         if key_id not in results[keyserver]['found_keys']:
    #             print(key_id)

    # Save the results
    with open(args.output, 'w') as f:
        f.write(json.dumps(results))

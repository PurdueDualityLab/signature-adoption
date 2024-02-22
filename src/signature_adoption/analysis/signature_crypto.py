import os
import re
import subprocess
import argparse
import random
import sqlite3
from pathlib import Path

# Function to parse arguments


def parse_args():
    ''' This function parses arguments passed to the script.

    returns: the arguments passed to the script.
    '''

    # Create parser
    parser = argparse.ArgumentParser(
        description='Check GPG signatures and report on the types of crypto '
        'used.',
    )

    # global arguments
    parser.add_argument(
        '--random',
        '-r',
        dest='random',
        action='store_true',
        help='randomize the order of the input files.',
    )
    parser.add_argument(
        '--start',
        '-s',
        dest='start',
        metavar='N',
        type=int,
        default=0,
        help='start processing at the Nth file in the input list. '
        'Defaults to <0>.'
    )
    parser.add_argument(
        '--end',
        '-e',
        dest='end',
        metavar='N',
        type=int,
        default=-1,
        help='stop processing after the Nth file in the input list. '
        'Defaults to <-1> (i.e. process all files).'
    )
    parser.add_argument(
        '--database',
        '-d',
        dest='database',
        metavar='DB',
        type=Path,
        default=None,
        help='The SQLite database to store the results in. If not provided, '
        'the results will be stored in the directory path in the "directory" '
        'argument as a file called "crypto.db".'
    )
    parser.add_argument(
        '--clean',
        '-c',
        dest='clean',
        action='store_true',
        help='Clean the database before starting. This will remove any '
        'existing data in the database.'
    )

    def directory_path(directory):
        '''This function returns a valid directory path.

        directory: the directory to check

        returns: the directory path
        '''
        dir_path = Path(directory)
        if not dir_path.is_dir():
            raise argparse.ArgumentTypeError(
                f"{directory} is not a valid directory."
            )
        return dir_path

    parser.add_argument(
        'directory',
        metavar='DIR',
        type=directory_path,
        help='The directory containing the signatures to check.'
    )

    # Parse arguments
    args = parser.parse_args()

    # if the database is not provided, create a default one
    if args.database is None:
        args.database = args.directory / 'crypto.db'

    return args


def list_files(directory):
    '''This function returns a list of all files in a directory.

    directory: the directory to list files from

    returns: a list of all files in the directory
    '''
    files_list = []
    for root, directories, files in os.walk(directory):
        for file in files:
            files_list.append(os.path.join(root, file))
    return files_list


def extract_crypto_info(output):
    '''This function extracts the crypto info from the gpg output.

    output: the gpg output

    returns: the crypto info
    '''

    # Create regex objects
    algo_regex = re.compile(r'algo (\d+)')
    created_regex = re.compile(r'created (\d+)')
    digest_regex = re.compile(r'digest algo (\d+)')
    data_regex = re.compile(r'data: \[(\d+) bits\]')
    keyid_regex = re.compile(r'keyid: (\w+)')

    # Find matches in the string
    algo_match = algo_regex.search(output)
    created_match = created_regex.search(output)
    digest_match = digest_regex.search(output)
    data_match = data_regex.search(output)
    keyid_match = keyid_regex.search(output)

    # Extract the matched groups
    algo = algo_match.group(1) if algo_match else None
    created = created_match.group(1) if created_match else None
    digest = digest_match.group(1) if digest_match else None
    data = data_match.group(1) if data_match else None
    keyid = keyid_match.group(1) if keyid_match else None

    return algo, created, digest, data, keyid


def init_db(args):
    '''This function creates the database.

    args: the arguments passed to the script
    '''
    # Create the database
    conn = sqlite3.connect(args.database)
    c = conn.cursor()

    # If cleaning the database, drop the table
    if args.clean:
        c.execute('DROP TABLE IF EXISTS crypto')

    # Create the table
    c.execute(
        '''CREATE TABLE IF NOT EXISTS crypto (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            algo INTEGER,
            created INTEGER,
            digest INTEGER,
            data INTEGER,
            keyid TEXT
        )'''
    )

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()


if __name__ == "__main__":

    # Parse arguments
    args = parse_args()

    # List files
    files = list_files(args.directory)
    print(f'Found {len(files)} files in {args.directory}')

    # randomize the list of files if the random flag is set
    if args.random:
        random.shuffle(files)

    # Narrow down the list of files
    files = files[args.start:args.end]

    # Initialize the database
    init_db(args)

    # Connect to the database
    with sqlite3.connect(args.database) as conn:
        c = conn.cursor()

        # For each file, extract the crypto info and insert into the database
        for indx, file in enumerate(files):

            if indx % 250 == 0:
                print(f'[{args.database}]: '
                      f'Processing file {indx} of {len(files)}')

            output = subprocess.run(
                [
                    'gpg',
                    '--list-packets',
                    file
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            ).stdout.decode("utf-8")
            # print(f'{output}')

            # find the crypto info
            algo, created, digest, data, keyid = extract_crypto_info(output)

            # insert into db
            c.execute(
                'INSERT INTO crypto '
                '(filename, algo, created, digest, data, keyid) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (file, algo, created, digest, data, keyid)
            )

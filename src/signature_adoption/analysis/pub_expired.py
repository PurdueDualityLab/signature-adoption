import re
from datetime import datetime
import argparse
import sqlite3
from pathlib import Path

# Function to parse arguments


def parse_args():
    ''' This function parses arguments passed to the script.

    returns: the arguments passed to the script.
    '''

    # Create parser
    parser = argparse.ArgumentParser(
        description='Check the dates of the signature and public key when '
        ' expired.'
    )

    # global arguments
    parser.add_argument(
        'database',
        metavar='DB',
        type=Path,
        help='The SQLite database to query'
    )
    parser.add_argument(
        'registry',
        metavar='REGISTRY',
        type=str,
        choices=['maven', 'pypi', 'huggingface', 'docker'],
        help='The registry to query.',
    )
    parser.add_argument(
        '--clean',
        '-c',
        dest='clean',
        action='store_true',
        help='Clean the database before starting. This will remove any '
        'existing data in the exp_pub_keys table.'
    )

    # Parse arguments
    args = parser.parse_args()

    return args


def extract_info(output):
    '''This function extracts the crypto info from the gpg output.

    output: the gpg output

    returns: the crypto info
    '''

    # Create regex objects
    sig_create_regex = re.compile(r'Signature made \w+ (\d+ \w+ \d+)')
    pub_exp_regex = re.compile(r'expired \w+ (\d+ \w+ \d+)')

    # Find matches in the string
    sig_create_match = sig_create_regex.search(output)
    pub_exp_match = pub_exp_regex.search(output)

    # Extract the matched groups
    sig_create = sig_create_match.group(1) if sig_create_match else None
    pub_exp = pub_exp_match.group(1) if pub_exp_match else None

    return sig_create, pub_exp


def init_db(args):
    '''This function creates the database.

    args: the arguments passed to the script
    '''
    # Create the database
    conn = sqlite3.connect(args.database)
    c = conn.cursor()

    # If cleaning the database, drop the table
    if args.clean:
        c.execute('DROP TABLE IF EXISTS exp_pub_keys')

    # Create the table
    c.execute(
        '''CREATE TABLE IF NOT EXISTS exp_pub_keys (
            id INTEGER PRIMARY KEY,
            unit_id INTEGER NOT NULL,
            sig_create TEXT NOT NULL,
            pub_exp TEXT NOT NULL,
            sig_after_pub INTEGER NOT NULL,
            diff_days INTEGER NOT NULL,
            FOREIGN KEY (unit_id) REFERENCES units (id)
        )'''
    )

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()


if __name__ == "__main__":

    # Parse arguments
    args = parse_args()

    # Connect to the database
    result = None
    with sqlite3.connect(args.database) as conn:
        c = conn.cursor()

        # insert into db
        c.execute(
            '''
            SELECT u.sig_raw, u.id
            FROM units u
            JOIN packages p on p.id = u.package_id
            WHERE u.has_sig = 1
                AND p.registry = ?
                AND u.sig_status = 'EXP_PUB'
            ''',
            (args.registry,)
        )

        # Get the results
        result = c.fetchall()

    # Done with query, print the total
    total = len(result)
    print(f'Found {total} expired signatures.')

    # Initialize the database
    init_db(args)

    # Connect to the database
    with sqlite3.connect(args.database) as conn:

        # Get the cursor
        c = conn.cursor()

        # Loop through the results
        for row in result:

            # Get the signature and unit id
            sig = row[0]
            unit_id = row[1]

            # Extract the crypto info
            sig_create, pub_exp = extract_info(sig)

            # convert to datetime
            sig_create = datetime.strptime(sig_create, '%d %b %Y')
            pub_exp = datetime.strptime(pub_exp, '%d %b %Y')
            diff_days = (pub_exp - sig_create).days

            # Insert into the database
            c.execute(
                '''
                INSERT INTO exp_pub_keys
                    (unit_id, sig_create, pub_exp, sig_after_pub, diff_days)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (
                    unit_id,
                    sig_create,
                    pub_exp,
                    1 if sig_create > pub_exp else 0,
                    diff_days,
                )
            )

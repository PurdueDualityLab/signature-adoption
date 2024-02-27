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
        description='Check if there is a new version with good signatures.'
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
        choices=['maven', 'pypi'],
        help='The registry to query.',
    )

    # Parse arguments
    args = parser.parse_args()

    return args


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
            SELECT e.pub_exp, p.id
            FROM exp_pub_keys e
            JOIN units u on u.id = e.unit_id
            JOIN packages p on p.id = u.package_id
            WHERE e.sig_after_pub = 0
                AND p.registry = ?
            GROUP BY e.pub_exp, p.id
            ''',
            (args.registry,)
        )

        # Get the results
        result = c.fetchall()

        mapping = {}
        for date, pid in result:
            date = datetime.strptime(date[:10], '%Y-%m-%d')
            if pid in mapping:
                mapping[pid].append(date)
            else:
                mapping[pid] = [date]


        # for each package, get the latest date
        for pid, dates in mapping.items():
            mapping[pid] = max(dates)


        # print number of signatures with expired public key
        total = len(mapping)
        print(f'Found {total} packages with expired public keys.')

        new_available = 0

        # Loop through the results
        for package_id, date in mapping.items():

            c.execute(
                '''
                SELECT v.id
                from versions v
                JOIN packages p on p.id = v.package_id
                WHERE p.id = ?
                    AND v.date > ?
                ''',
                (
                    package_id,
                    date,
                )
            )

            # Get the results
            versions = [v[0] for v in c.fetchall()]

            if not versions:
                continue

            # Iterate through versions and try to find a version with all good signatures
            for version in versions:
                c.execute(
                    '''
                    SELECT u.sig_status
                    FROM units u
                    JOIN versions v on v.id = u.version_id
                    WHERE v.id = ?
                    ''',
                    (version,)
                )

                units = [u[0] for u in c.fetchall()]
                good = True

                for unit in units:
                    if unit != 'GOOD':
                        good = False
                        break

                if good:
                    new_available += 1
                    break

        print(f'Of these packages {new_available} have a version released after the public key expired with all good signatures.')

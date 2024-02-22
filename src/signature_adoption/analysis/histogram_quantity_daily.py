import matplotlib.pyplot as plt
import argparse
import sqlite3
from datetime import datetime
from pathlib import Path


def parse_args():
    ''' This function parses arguments passed to the script.

    returns: the arguments passed to the script.
    '''

    # Create parser
    parser = argparse.ArgumentParser(
        description='Create a histogram plot of the adoption rates each day.',
    )

    # global arguments
    parser.add_argument(
        'database',
        metavar='DB',
        type=Path,
        help='The SQLite database to query.',
    )
    parser.add_argument(
        'registry',
        metavar='REGISTRY',
        type=str,
        choices=['maven', 'pypi', 'huggingface', 'docker'],
        help='The registry to query.',
    )
    parser.add_argument(
        'start',
        metavar='YYYY-MM-DD',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        help='The start date for the histogram.',
    )
    parser.add_argument(
        'end',
        metavar='YYYY-MM-DD',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        help='The end date for the histogram.',
    )
    parser.add_argument(
        'output',
        metavar='OUTPUT',
        type=Path,
        help='The file to save the output to.',
    )

    # Parse arguments
    args = parser.parse_args()

    return args


if __name__ == "__main__":

    # Parse arguments
    args = parse_args()

    # None results
    results = None

    # Connect to the database
    with sqlite3.connect(args.database) as conn:
        cursor = conn.cursor()

        # Get the time of the RSA
        cursor.execute(
            '''
            select strftime('%Y-%m-%d', u.date) as date,
                   u.has_sig,
                   count(u.unit)
            from units u
            join packages p on u.package_id = p.id
            where p.registry = ?
                and u.date between ? and ?
            group by date, u.has_sig
            ''',
            (
                args.registry,
                args.start.strftime('%Y-%m-%d'),
                args.end.strftime('%Y-%m-%d'),
            ),
        )
        results = cursor.fetchall()

    # Create the histogram
    dates = {}

    for date, has_sig, count in results:
        if date not in dates:
            dates[date] = {'signed': 0, 'unsigned': 0}
        if has_sig:
            dates[date]['signed'] += count
        else:
            dates[date]['unsigned'] += count

    # calculate percentages
    for date in dates:
        total = dates[date]['signed'] + dates[date]['unsigned']
        percent = dates[date]['signed'] / total * 100
        dates[date]['percentage'] = percent
        if percent > 80:
            print(date, percent, total)

    # Create the plot
    plt.hist([date['percentage'] for date in dates.values()], bins=100)
    plt.xlabel('Percentage of signed artifacts')
    plt.ylabel('Number of days')
    plt.title(f'Adoption of signed artifacts in {args.registry}')
    plt.tight_layout()
    plt.savefig(args.output)

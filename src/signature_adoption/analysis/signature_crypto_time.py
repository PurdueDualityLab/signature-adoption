import matplotlib.pyplot as plt
import argparse
import sqlite3
from pathlib import Path


def parse_args():
    ''' This function parses arguments passed to the script.

    returns: the arguments passed to the script.
    '''

    # Create parser
    parser = argparse.ArgumentParser(
        description='Create time reports for the RSA',
    )

    # global arguments
    parser.add_argument(
        'database',
        metavar='DB',
        type=Path,
        default=None,
        help='The SQLite database to query.',
    )
    parser.add_argument(
        'output',
        metavar='OUTPUT',
        type=Path,
        default=None,
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
            select strftime('%Y-%m', created, 'unixepoch') as month,
                   ((((data-1)/512)+1)*512) as data_up,
                   count(filename) as occurrences
            from crypto
            where algo = 1
                and date(created, 'unixepoch') between '2015-01-01'
                    and '2023-09-30'
            group by month, data_up
            '''
        )
        results = cursor.fetchall()

    months = {}
    data_ups = set()
    for month, data_up, occurrences in results:
        if month not in months:
            months[month] = {}
        months[month][data_up] = occurrences
        data_ups.add(data_up)

    # calculate percentages
    for month in months:
        for data_up in data_ups:
            if data_up not in months[month]:
                months[month][data_up] = 0
        total = sum(months[month].values())
        for data_up in data_ups:
            months[month][data_up] = months[month][data_up] / total * 100

    # plot the data
    for data_up in data_ups:
        plt.plot(
            [month for month in months],
            [months[month][data_up] for month in months],
            label=f'{data_up} bytes'
        )

    plt.xlabel('Month')
    plt.ylabel('Percentage')
    plt.title('RSA data size over time')
    plt.xticks([month for month in months][::6], rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.savefig(args.output)

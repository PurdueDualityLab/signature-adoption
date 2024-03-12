import matplotlib.pyplot as plt
import argparse
import sqlite3
import scipy.stats
from datetime import datetime, timedelta
from pathlib import Path


def parse_args():
    ''' This function parses arguments passed to the script.

    returns: the arguments passed to the script.
    '''

    # Create parser
    parser = argparse.ArgumentParser(
        description='Conduct an ANOVA test on the percentage of signed units '
        'between registries and use a tukey test to compare them.',
    )

    # global arguments
    parser.add_argument(
        'database',
        metavar='DB',
        type=Path,
        help='The SQLite database to query.',
    )
    parser.add_argument(
        'start',
        metavar='YYYY-MM-DD',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        help='Start date',
    )
    parser.add_argument(
        'end',
        metavar='YYYY-MM-DD',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        help='End date',
    )
    parser.add_argument(
        '--boxplot',
        '-b',
        metavar='OUTPUT',
        type=Path,
        default=None,
        help='The file to save the boxplot to.',
    )

    # Parse arguments
    args = parser.parse_args()

    return args


def get_sample(database, registry, start, end):
    ''' This function gets the sample data from the database.

    database: the database to query.
    registry: the registry to query.
    start: the start date.
    end: the end date.

    returns: the sample data.
    '''

    # None results
    results = None

    # Connect to the database
    with sqlite3.connect(database) as conn:
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
                registry,
                start.strftime('%Y-%m-%d'),
                end.strftime('%Y-%m-%d'),
            ),
        )
        results = cursor.fetchall()

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

    return [v['percentage'] for v in dates.values()]


if __name__ == "__main__":

    # Parse arguments
    args = parse_args()

    # Get the samples
    maven = get_sample(args.database, 'maven', args.start, args.end)
    pypi = get_sample(args.database, 'pypi', args.start, args.end)
    docker = get_sample(args.database, 'docker', args.start, args.end)
    huggingface = get_sample(
        args.database, 'huggingface', args.start, args.end)

    # Create boxplot
    if args.boxplot:
        plt.boxplot([maven, pypi, docker, huggingface],
                    labels=['maven', 'pypi', 'docker', 'huggingface'])
        plt.xticks(rotation=90)
        plt.ylabel('Percentage of signed units')
        plt.tight_layout()
        plt.savefig(args.boxplot)

    # Conduct ANOVA test
    f, p = scipy.stats.f_oneway(maven, pypi, docker, huggingface)

    # Print results
    print('F-statistic:', f)
    print('p-value:', p)

    # Conduct tukey test
    tukey = scipy.stats.tukey_hsd(maven, pypi, docker, huggingface)

    # Print tables
    print(tukey)

    # Print better sig digits for p values
    # for i in range(4):
    #     for j in range(4):
    #         print(f'{i} vs {j}:', tukey.pvalue[i][j])

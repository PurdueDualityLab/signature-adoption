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
        description='Conduct a t-test on the percentage of signed units '
        'before and after a certain date.',
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
        'intervention',
        metavar='YYYY-MM-DD',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        help='Intervention date',
    )
    parser.add_argument(
        'span',
        metavar='DAYS',
        type=int,
        help='Number of days to include in the before and after periods.',
    )
    parser.add_argument(
        '--alternative',
        '-a',
        dest='alternative',
        choices=['two-sided', 'less', 'greater'],
        default='two-sided',
        help='The alternative hypothesis to test. Default is two-sided. '
        'less: mean of first sample is less than mean of second sample. '
        'greater: mean of first sample is greater than mean of second sample. '
        'two-sided: means are not equal.',
    )
    parser.add_argument(
        '--output',
        '-o',
        metavar='OUTPUT',
        type=Path,
        default=None,
        help='The file to save the output to.',
    )

    # Parse arguments
    args = parser.parse_args()

    return args


def get_sample(database, registry, start, end):
    ''' This function gets the sample data from the database.

    database: the database to query.
    registry: the registry to query.
    start: the start date for the sample.
    end: the end date for the sample.

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


def calc_effect_size(t_stat, n1, n2):
    ''' This function calculates the effect size.

    t_stat: the t-statistic.
    n1: the number of samples in the first sample.
    n2: the number of samples in the second sample.

    returns: the effect size.
    '''

    # calculate the degrees of freedom
    df = n1 + n2 - 2

    # calculate the effect size
    return t_stat / (df ** 0.5)


if __name__ == "__main__":

    # Parse arguments
    args = parse_args()

    # Create start and end dates
    start = args.intervention - timedelta(days=args.span)
    end = args.intervention + timedelta(days=args.span)

    # Get the samples
    before = get_sample(args.database, args.registry, start, args.intervention)
    after = get_sample(args.database, args.registry, args.intervention, end)

    # Plot the samples if output is provided
    if args.output:
        plt.hist(before, bins=30, alpha=0.5, range=(0, 20), label='Before')
        plt.hist(after, bins=30, alpha=0.5, range=(0, 20), label='After')
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.savefig(args.output)

    # Print basic statistics
    print('Before')
    print(f'Mean: {sum(before) / len(before)}')
    print(f'Std: {scipy.stats.tstd(before)}')
    print('After')
    print(f'Mean: {sum(after) / len(after)}')
    print(f'Std: {scipy.stats.tstd(after)}')

    # Perform the t-test
    t_stat, p_value, = scipy.stats.ttest_ind(
        before,
        after,
        alternative=args.alternative,
    )

    # print the results
    print(f't-statistic: {t_stat}')
    print(f'p-value: {p_value}')
    print(f'effect size: {calc_effect_size(t_stat, len(before), len(after))}')

    print(before)
    print(after)

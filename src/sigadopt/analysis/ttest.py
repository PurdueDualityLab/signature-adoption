'''
ttest.py: This script is used to calculate the T-Test for the adoption of
signatures.
'''

import matplotlib.pyplot as plt
import scipy.stats
import logging
from datetime import datetime, timedelta

# Set up logging
log = logging.getLogger(__name__)


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
    with database as conn:
        cursor = conn.cursor()

        # Get the time of the RSA
        log.info(f'Running query on registry: {registry}')
        cursor.execute(
            '''
            SELECT
                (
                    CASE
                        WHEN v.date is not null
                        THEN strftime('%Y-%m-%d', v.date)
                        ELSE strftime('%Y-%m-%d', a.date)
                    END
                ) AS my_date,
                a.has_sig,
                count(a.id)
            FROM artifacts a
            JOIN versions v ON a.version_id = v.id
            JOIN packages p ON v.package_id = p.id
            WHERE p.registry_id = ?
                AND (
                    CASE
                        WHEN v.date is not null
                        THEN v.date
                        ELSE a.date
                    END
                ) BETWEEN ? and ?
            GROUP by my_date, a.has_sig
            ''',
            (
                registry,
                start.strftime('%Y-%m-%d'),
                end.strftime('%Y-%m-%d'),
            ),
        )
        results = cursor.fetchall()

        dates = {}

        # parse the results
        log.info('Parsing results...')
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


def run(database, registry, intervention, span, alternative, output):
    '''
    This function generates a LaTeX table of the results.

    database: A database connection
    output: The path to save the histogram to. If None, no chart is generated.
    '''

    # Create start and end dates
    start = intervention - timedelta(days=span)
    end = intervention + timedelta(days=span)

    # Get the samples
    before = get_sample(database, registry, start, intervention)
    after = get_sample(database, registry, intervention, end)

    # Plot the samples if output is provided
    if output:
        plt.hist(before, bins=30, alpha=0.5, range=(0, 20), label='Before')
        plt.hist(after, bins=30, alpha=0.5, range=(0, 20), label='After')
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.savefig(output)

    # log.info basic statistics
    log.info('Before')
    log.info(f'Mean: {sum(before) / len(before)}')
    log.info(f'Std: {scipy.stats.tstd(before)}')
    log.info('After')
    log.info(f'Mean: {sum(after) / len(after)}')
    log.info(f'Std: {scipy.stats.tstd(after)}')

    # Perform the t-test
    t_stat, p_value, = scipy.stats.ttest_ind(
        before,
        after,
        alternative=alternative,
    )

    # log.info the results
    log.info(f't-statistic: {t_stat}')
    log.info(f'p-value: {p_value}')
    log.info(f'effect size: {calc_effect_size(t_stat, len(before), len(after))}')

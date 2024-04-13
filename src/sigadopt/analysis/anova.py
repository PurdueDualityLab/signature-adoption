'''
anova.py: This script is used to calculate the ANOVA for the adoption of
signatures.
'''

import matplotlib.pyplot as plt
import scipy.stats
import logging
from sigadopt.util.database import Registry

# Set up logging
log = logging.getLogger(__name__)


def get_sample(database, registry_id):
    ''' This function gets the sample data from the database.

    database: the database to query.
    registry: the registry to query.

    returns: the sample data.
    '''

    # None results
    results = None

    # Connect to the database
    with database as conn:
        cursor = conn.cursor()

        # Get the time of the RSA
        log.info(f'Running anova query for registry: {registry_id}')
        cursor.execute(
            '''
            select
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
            where p.registry_id = ?
            group by my_date, a.has_sig
            ''',
            (
                registry_id,
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


def run(database, boxplot):
    '''
    This function generates a LaTeX table of the results.

    database: A database connection
    boxplot: The path to save the boxplot to. If None, no boxplot is generated.
    '''

    # Get the samples
    huggingface = get_sample(database, Registry.HUGGINGFACE)
    docker = get_sample(database, Registry.DOCKER)
    maven = get_sample(database, Registry.MAVEN)
    pypi = get_sample(database, Registry.PYPI)

    # Create boxplot
    if boxplot:
        log.info('Creating boxplot')
        plt.boxplot([maven, pypi, docker, huggingface],
                    labels=['maven', 'pypi', 'docker', 'huggingface'])
        plt.xticks(rotation=90)
        plt.ylabel('Percentage of signed units')
        plt.tight_layout()
        plt.savefig(boxplot)

    # Conduct ANOVA test
    log.info('Running ANOVA test')
    f, p = scipy.stats.f_oneway(maven, pypi, docker, huggingface)

    # Print results
    log.info(f'F-statistic: {f}')
    log.info(f'p-value: {p}')

    # Conduct tukey test
    log.info('Running Tukey test')
    tukey = scipy.stats.tukey_hsd(maven, pypi, docker, huggingface)

    # Print tables
    log.info(tukey)

'''
plot_failures.py: This script is used to plot the quality of signatures over
time for each registry.
'''

import matplotlib.pyplot as plt
import logging
from sigadopt.util.database import Registry

# Set up logging
log = logging.getLogger(__name__)


def run(database, output, registry_id):
    '''
    This function plots the quality of signatures over time for each registry.

    database: A database connection
    output: The path to write the LaTeX table to.
    registry_id: The registry to plot.
    '''
    results = None

    with database:

        cursor = database.cursor()

        # Execute the query
        log.info('Executing query...')

        # SQL query to get the adoption rates by week
        cursor.execute(
            '''
            WITH VersionRanked AS (
                SELECT
                    a.date as adate,
                    v.date as vdate,
                    ROW_NUMBER() OVER
                    (
                        PARTITION BY p.id ORDER BY v.date, a.date
                    ) AS version_rank
                FROM artifacts a
                JOIN versions v ON a.version_id = v.id
                JOIN packages p ON v.package_id = p.id
                WHERE p.registry_id = ?
            )
            SELECT
                (
                    CASE
                        WHEN vdate is not null THEN strftime('%Y-%m', vdate)
                        ELSE strftime('%Y-%m', adate)
                    END
                ) AS month,
                SUM(
                    CASE WHEN version_rank = 1 THEN 1 ELSE 0 END
                    ) AS first_versions,
                SUM(
                    CASE WHEN version_rank > 1 THEN 1 ELSE 0 END
                ) AS non_first_versions
            FROM
                VersionRanked
            GROUP BY
                month
            ORDER BY
                month;
            ''',
            (registry_id,)
        )

    # Fetch the results
    results = cursor.fetchall()

    # Extract data for plotting
    data = {
        "months": [],
        "first": [],
        "non_first": []
    }

    # Unpack the results
    log.info('Unpacking results...')
    for month_start, first, non_first in results:
        data['months'].append(month_start)
        data['first'].append(first)
        data['non_first'].append(non_first)

    # Plot the pypi adoption data
    log.info('Plotting data...')
    titles = {
        Registry.DOCKER: 'Docker',
        Registry.PYPI: 'PyPI',
        Registry.MAVEN: 'Maven Central',
        Registry.HUGGINGFACE: 'Hugging Face'
    }
    plt.plot(data['months'], data['non_first'],
             linestyle='-', label='Non-First Versions')
    plt.plot(data['months'], data['first'],
             linestyle='--', label='First Versions')
    plt.xlabel('Month', fontsize=15)
    plt.ylabel('Artifacts Published per Month', fontsize=15)
    plt.title(
        f'First vs. Non-First Artifacts on {titles[registry_id]}',
        fontsize=19
    )
    plt.xticks(data['months'][::4], rotation=90, fontsize=11)
    plt.yticks(fontsize=11)
    plt.tight_layout()
    plt.legend(fontsize=10)
    plt.savefig(output, dpi=300)

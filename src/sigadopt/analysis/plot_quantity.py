'''
plot_quantity.py: This script is used to plot the quantity of signatures over
time for each registry.
'''

import matplotlib.pyplot as plt
import logging
from sigadopt.util.database import Registry

# Set up logging
log = logging.getLogger(__name__)


def run(database, output):
    '''
    This function plots the quantity of signatures over time for each registry.

    database: A database connection
    output: The path to write the LaTeX table to.
    '''

    results = None

    with database:

        cursor = database.cursor()

        # SQL query to get the adoption rates by week
        query = '''
            SELECT p.registry_id,
                (
                    CASE
                        WHEN v.date is not null THEN strftime('%Y-%m', v.date)
                        ELSE strftime('%Y-%m', a.date)
                    END
                ) AS month_start,
                COUNT(a.id) AS total_units,
                SUM(a.has_sig) AS signed_units
            FROM artifacts a
            JOIN versions v on a.version_id = v.id
            JOIN packages p on v.package_id = p.id
            GROUP BY p.registry_id, month_start
        '''

        # Execute the query
        log.info('Executing query...')
        cursor.execute(query)

        # Fetch the results
        results = cursor.fetchall()

    # Extract data for plotting
    data = {
        "docker":
        {
            "months": [],
            "adoption_rates": []
        },
        "pypi":
        {
            "months": [],
            "adoption_rates": []
        },
        "maven":
        {
            "months": [],
            "adoption_rates": []
        },
        "huggingface":
        {
            "months": [],
            "adoption_rates": []
        },
    }

    # Calculate adoption rates and collect data for plotting
    log.info('Calculating adoption rates...')
    for registry, month_start, total_units, signed_units in results:
        reg_text = Registry(registry).name.lower()
        adoption_rate = (signed_units / total_units) * \
            100 if total_units != 0 else 0
        data[reg_text]['months'].append(month_start)
        data[reg_text]['adoption_rates'].append(adoption_rate)

    # Plot the adoption rates over time
    log.info('Plotting adoption rates...')
    plt.plot(data['maven']['months'], data['maven']['adoption_rates'],
             label='Maven Central')
    plt.plot(data['docker']['months'], data['docker']['adoption_rates'],
             label='Docker Hub')
    plt.plot(data['huggingface']['months'], data['huggingface']['adoption_rates'],
             label='HuggingFace')
    plt.plot(data['pypi']['months'], data['pypi']['adoption_rates'],
             label='PyPI')
    plt.axvline(x='2018-03', color='c', linestyle=':',
                label='PyPI PGP De-emphasis')
    plt.axvline(x='2019-04', color='k', linestyle='-.',
                label='Docker Hub Attack')
    plt.axvline(x='2019-09', color='m', linestyle=':',
                label='Docker Hub Update')
    plt.axvline(x='2021-12', color='tab:gray', linestyle='-.',
                label='SolarWinds Attack')
    plt.axvline(x='2023-05', color='y', linestyle=':',
                label='PyPI PGP Removal')
    plt.xlabel('Month', fontsize=15)
    plt.ylabel('Signature Quantity (%)', fontsize=15)
    plt.title('Quantity of Signatures Over Time', fontsize=19)
    plt.xticks(data['maven']['months'][::4], rotation=90, fontsize=11)
    plt.yticks(fontsize=11)
    plt.tight_layout()
    plt.legend(fontsize=10)
    plt.savefig(output, dpi=600)

'''
plot_quality.py: This script is used to plot the quality of signatures over
time for each registry.
'''

import matplotlib.pyplot as plt
import logging
from sigadopt.util.database import Registry, SignatureStatus

# Set up logging
log = logging.getLogger(__name__)


def run(database, output):
    '''
    This function plots the quality of signatures over time for each registry.

    database: A database connection
    output: The path to write the LaTeX table to.
    '''
    results = None

    with database:

        cursor = database.cursor()

        # Execute the query
        log.info('Executing query...')
        cursor.execute(
            '''
            SELECT
                p.registry_id,
                (
                    CASE
                        WHEN v.date is not null THEN strftime('%Y-%m', v.date)
                        ELSE strftime('%Y-%m', a.date)
                    END
                ) AS month,
                COUNT(CASE WHEN a.has_sig = 1 THEN 1 END) AS artifacts_signed,
                COUNT(CASE WHEN s.status = ? THEN 1 END) AS artifacts_good
            FROM sig_check s
            JOIN artifacts a ON s.artifact_id = a.id
            JOIN versions v ON a.version_id = v.id
            JOIN packages p ON v.package_id = p.id
            WHERE (a.has_sig = 1 OR s.status = ?)
            GROUP BY
                p.registry_id, month
            ORDER BY
                p.registry_id, month;
            ''',
            (SignatureStatus.GOOD, SignatureStatus.GOOD)
        )

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
    for registry, month_start, total_signed, total_good in results:
        reg_text = Registry(registry).name.lower()
        adoption_rate = (total_good / total_signed) * \
            100 if total_signed != 0 else 0
        data[reg_text]['months'].append(month_start)
        data[reg_text]['adoption_rates'].append(adoption_rate)


# Plot the adoption rates over time
    log.info('Plotting adoption rates...')
    plt.plot(data['maven']['months'], data['maven']['adoption_rates'],
             linestyle=':', label='Maven Central', linewidth=2)
    plt.plot(data['docker']['months'], data['docker']['adoption_rates'],
             linestyle='-.', label='Docker Hub', linewidth=2)
    plt.plot(data['huggingface']['months'], data['huggingface']['adoption_rates'],
             linestyle='--', label='HuggingFace', linewidth=2)
    plt.plot(data['pypi']['months'], data['pypi']['adoption_rates'],
             linestyle='-', label='PyPI', linewidth=2)
    plt.axvline(x='2018-03', color='c', linestyle='--',
                label='PyPI PGP De-emphasis')
    plt.axvline(x='2019-04', color='k', linestyle='-.',
                label='Docker Hub Attack')
    plt.axvline(x='2019-09', color='m', linestyle=':',
                label='Docker Hub Update')
    plt.axvline(x='2023-05', color='y', linestyle='-',
                label='PyPI PGP Removal')
    plt.xlabel('Month', fontsize=15)
    plt.ylabel('Signature Quality (% Good Signatures)', fontsize=15)
    plt.title('Quality of Signatures Over Time', fontsize=19)
    plt.xticks(data['maven']['months'][::6], rotation=90, fontsize=11)
    plt.yticks(fontsize=11)
    plt.tight_layout()
    plt.legend(fontsize=11)
    plt.savefig(output, dpi=300)

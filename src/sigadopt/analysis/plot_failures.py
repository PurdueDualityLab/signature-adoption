'''
plot_failures.py: This script is used to plot the quality of signatures over
time for each registry.
'''

import matplotlib.pyplot as plt
import logging
from sigadopt.util.database import Registry, SignatureStatus

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
            SELECT
                (
                    CASE
                        WHEN v.date is not null THEN strftime('%Y-%m', v.date)
                        ELSE strftime('%Y-%m', a.date)
                    END
                ) AS month,
                COUNT(CASE WHEN a.has_sig = 1 THEN 1 END) AS units_with_sig,
                COUNT(CASE WHEN s.status = ? THEN 1 END) as good,
                COUNT(CASE WHEN s.status = ? THEN 1 END) as no_sig,
                COUNT(CASE WHEN s.status = ? THEN 1 END) as bad_sig,
                COUNT(CASE WHEN s.status = ? THEN 1 END) as exp_sig,
                COUNT(CASE WHEN s.status = ? THEN 1 END) as exp_pub,
                COUNT(CASE WHEN s.status = ? THEN 1 END) as no_pub,
                COUNT(CASE WHEN s.status = ? THEN 1 END) as rev_pub,
                COUNT(CASE WHEN s.status = ? THEN 1 END) as bad_pub
            FROM sig_check s
            JOIN artifacts a ON s.artifact_id = a.id
            JOIN versions v ON a.version_id = v.id
            JOIN packages p ON v.package_id = p.id
            WHERE (a.has_sig = 1 OR s.status = ? )
            AND p.registry_id = ?
            GROUP BY month
            ORDER BY month;
            ''',
            (
                SignatureStatus.GOOD,
                SignatureStatus.NO_SIG,
                SignatureStatus.BAD_SIG,
                SignatureStatus.EXP_SIG,
                SignatureStatus.EXP_PUB,
                SignatureStatus.NO_PUB,
                SignatureStatus.REV_PUB,
                SignatureStatus.BAD_PUB,
                SignatureStatus.GOOD,
                registry_id,)
        )

        # Fetch the results
        results = cursor.fetchall()

    # Extract data for plotting
    data = {
        "months": [],
        "NO_SIG": [],
        "BAD_SIG": [],
        "EXP_SIG": [],
        "EXP_PUB": [],
        "NO_PUB": [],
        "REV_PUB": [],
        "BAD_PUB": [],
    }

    # Calculate adoption rates and collect data for plotting
    log.info('Calculating adoption rates...')
    for (
        month_start,
        total_signed,
        total_good,
        total_no_sig,
        total_bad_sig,
        total_exp_sig,
        total_exp_pub,
        total_no_pub,
        total_rev_pub,
        total_bad_pub
    ) in results:

        denom = total_signed - total_good
        data['months'].append(month_start)
        data['BAD_SIG'].append(
            total_bad_sig / denom * 100 if denom != 0 else 0)
        data['EXP_SIG'].append(
            total_exp_sig / denom * 100 if denom != 0 else 0)
        data['EXP_PUB'].append(
            total_exp_pub / denom * 100 if denom != 0 else 0)
        data['NO_PUB'].append(
            total_no_pub / denom * 100 if denom != 0 else 0)
        data['REV_PUB'].append(
            total_rev_pub / denom * 100 if denom != 0 else 0)
        data['BAD_PUB'].append(
            total_bad_pub / denom * 100 if denom != 0 else 0)

    titles = {
        Registry.DOCKER: 'Docker',
        Registry.PYPI: 'PyPI',
        Registry.MAVEN: 'Maven Central',
        Registry.HUGGINGFACE: 'Hugging Face'
    }

    plt.plot(data['months'], data['BAD_SIG'],
             linestyle='-', label='Bad Signature')
    plt.plot(data['months'], data['EXP_SIG'],
             linestyle='-', label='Expired Signature')
    plt.plot(data['months'], data['EXP_PUB'],
             linestyle='-', label='Expired Public Key')
    plt.plot(data['months'], data['NO_PUB'],
             linestyle='-', label='No Public Key')
    plt.plot(data['months'], data['REV_PUB'],
             linestyle='-', label='Revoked Public Key')
    plt.plot(data['months'], data['BAD_PUB'],
             linestyle='-', label='Bad Public Key')
    plt.xlabel('Month', fontsize=15)
    plt.ylabel('Percent of Signatures', fontsize=15)
    plt.title(f'{titles[registry_id]} Failure Modes Over Time', fontsize=19)
    plt.xticks(data['months'][::4], rotation=90, fontsize=11)
    plt.yticks(fontsize=11)
    plt.tight_layout()
    plt.legend(fontsize=10)
    plt.savefig(output, dpi=600)

'''
metric.py: This script is used to generate a metric table of the results.
'''

import json2latex
import json
import logging
from sigadopt.util.database import Registry
from sigadopt.util.number_things import pc_str

# Set up logging
log = logging.getLogger(__name__)


def run(database, output, out_json=False):
    '''
    This function plots the quality of signatures over time for each registry.

    database: A database connection
    output: The path to write the output to.
    json: Whether to output the results as JSON.
    '''
    results = None
    results2 = None

    with database:

        cursor = database.cursor()

        # Execute the query
        log.info('Executing query 1...')
        cursor.execute(
            '''
            WITH FirstSignedArtifact AS (
                SELECT DISTINCT
                    p.id AS package_id,
                    MIN(
                        CASE
                            WHEN v.date is not null THEN v.date ELSE a.date
                        END
                    ) AS first_signed_date
                FROM artifacts a
                JOIN versions v on a.version_id = v.id
                JOIN packages p on v.package_id = p.id
                WHERE
                    a.has_sig = 1
                GROUP BY
                    package_id
            )
            SELECT
                p.registry_id,
                AVG(
                    CASE
                        WHEN a.has_sig = 1
                        AND (
                            CASE
                                WHEN v.date is not null THEN v.date ELSE a.date
                            END
                        ) > fsa.first_signed_date
                            THEN 1
                        ELSE 0
                    END
                ) AS probability_subsequent_signed
            FROM artifacts a
            JOIN versions v on a.version_id = v.id
            JOIN packages p on v.package_id = p.id
            JOIN FirstSignedArtifact fsa ON p.id = fsa.package_id
            GROUP BY p.registry_id
            ORDER BY p.registry_id;
            '''
        )

        # Fetch the results
        results = cursor.fetchall()

        log.info('Executing query 2...')
        # Execute the query
        cursor.execute(
            '''
            SELECT
                p.registry_id,
                COUNT(a.id) AS total_units,
                SUM(
                    CASE
                        WHEN a.has_sig = 1 THEN 1 ELSE 0
                    END
                ) AS signed_units,
                AVG(
                    CASE
                        WHEN a.has_sig = 1 THEN 1.0 ELSE 0.0
                    END
                ) AS chance_signed
            FROM artifacts a
            JOIN versions v ON a.version_id = v.id
            JOIN packages p ON v.package_id = p.id
            GROUP BY p.registry_id;
            '''
        )

        # Fetch the results
        results2 = cursor.fetchall()

    log.info('Registry : chance after first | normal chance')
    for x in range(0, len(results)):
        log.info(f'{results[x][0]}: {results[x][1]} | {results2[x][3]}')

    data = {}

    for registry, metric in results:
        reg_tex = Registry(registry).name.lower()
        if reg_tex not in data:
            data[reg_tex] = {}
        data[reg_tex]['metric'] = metric
        data[reg_tex]['metric_p'] = pc_str(metric, precision=2)

    for registry, total, signed, chance in results2:
        reg_tex = Registry(registry).name.lower()
        if reg_tex not in data:
            data[reg_tex] = {}
        data[reg_tex]['total'] = total
        data[reg_tex]['signed'] = signed
        data[reg_tex]['chance_p'] = pc_str(chance, precision=2)

    with open(output, 'w') as f:
        if out_json:
            json.dump(data, f, indent=4)
        else:
            json2latex.dump('metric', data, f)

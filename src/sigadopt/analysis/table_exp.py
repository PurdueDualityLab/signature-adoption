'''
table_crypto.py: This script is used to generate a LaTeX table for the
cryptographic algorithms used in the signatures.
'''

import json
import json2latex
import logging
import re
import statistics
from datetime import datetime
from sigadopt.util.number_things import human_format, pc_str
from sigadopt.util.database import SignatureStatus, Registry

# Set up logging
log = logging.getLogger(__name__)


def find_upgrade_paths(database, registry, dates, result):

    with database:

        # Create a cursor
        cursor = database.cursor()

        # Execute the query
        log.info(f'Executing upgrade paths query on {registry}...')

        mapping = {}
        for sig_create, pub_exp, delta, pid in dates:
            if pid not in mapping:
                mapping[pid] = []
            mapping[pid].append(pub_exp)

        for pid, dates in mapping.items():
            mapping[pid] = max(dates)

        log.info(f'Found {len(mapping)} packages with expired keys')

        new_available = 0

        # Loop through the results
        for package_id, date in mapping.items():

            cursor.execute(
                '''
                SELECT v.id
                from artifacts a
                JOIN versions v on a.version_id = v.id
                JOIN packages p on p.id = v.package_id
                WHERE p.id = ?
                    AND 
                    (
                        CASE
                            WHEN v.date is not null THEN v.date
                            ELSE a.date
                        END
                    )
                    > ?
                ''',
                (
                    package_id,
                    date,
                )
            )

            # Get the results
            versions = [v[0] for v in cursor.fetchall()]

            if not versions:
                continue

            # Iterate through versions and try to find a version with all good signatures
            for version in versions:
                cursor.execute(
                    '''
                    SELECT s.status
                    FROM sig_check s
                    JOIN artifacts a on a.id = s.artifact_id
                    JOIN versions v on v.id = a.version_id
                    WHERE v.id = ?
                    ''',
                    (version,)
                )

                units = [u[0] for u in cursor.fetchall()]
                good = True

                for unit in units:
                    if unit != SignatureStatus.GOOD:
                        good = False
                        break

                if good:
                    new_available += 1
                    break

        registry_text = Registry(registry).name.lower()
        result[registry_text]['upgrade_paths'] = {
                'total': {
                    'count':len(mapping),
                    'human': human_format(len(mapping)),
                },
                'upgradable': {
                    'count': new_available,
                    'human': human_format(new_available),
                    'percent': pc_str(new_available, len(mapping)),
                }
        }



def get_exp_keys(database, registry, result):

    with database:

        # Create a cursor
        cursor = database.cursor()

        # Execute the query
        log.info(f'Executing expired keys query on {registry}...')
        cursor.execute(
            '''
            SELECT s.raw, p.id
            FROM sig_check s
            JOIN artifacts a on a.id = s.artifact_id
            JOIN versions v on v.id = a.version_id
            JOIN packages p on p.id = v.package_id
            WHERE a.has_sig = 1
                AND p.registry_id = ?
                AND s.status = ?
            ''',
            (registry, SignatureStatus.EXP_PUB)
        )

        for row in cursor.fetchall():
            sig_create, pub_exp = extract_info(row[0])

            if sig_create and pub_exp:
                result.append(
                    (
                        sig_create,
                        pub_exp,
                        pub_exp - sig_create,
                        row[1]
                    ))
            else:
                log.warning(
                    'Could not extract the crypto info from the gpg output.')


def extract_info(output):
    '''This function extracts the crypto info from the gpg output.

    output: the gpg output

    returns: the crypto info
    '''

    # Create regex objects
    sig_create_regex = re.compile(r'Signature made \w+ (\d+ \w+ \d+)')
    pub_exp_regex = re.compile(r'expired \w+ (\d+ \w+ \d+)')

    # Find matches in the string
    sig_create_match = sig_create_regex.search(output)
    pub_exp_match = pub_exp_regex.search(output)

    # Extract the matched groups
    sig_create = sig_create_match.group(1) if sig_create_match else None
    pub_exp = pub_exp_match.group(1) if pub_exp_match else None

    # Convert the date to a datetime object
    if sig_create:
        sig_create = datetime.strptime(sig_create, '%d %b %Y')
    if pub_exp:
        pub_exp = datetime.strptime(pub_exp, '%d %b %Y')

    return sig_create, pub_exp


def run(database, output, out_json):
    '''
    This function generates a LaTeX table of the results.

    database: A database connection
    output: The path to write the LaTeX table to.
    out_json: Whether to output the results as JSON.
    '''

    # Results dictionary
    result = {}
    maven_dates = []
    pypi_dates = []

    # Get the data
    log.info('Checking Maven')
    get_exp_keys(database, Registry.MAVEN, maven_dates)

    log.info('Checking PyPI')
    get_exp_keys(database, Registry.PYPI, pypi_dates)

    # Calculate the number of expired keys
    log.info('Calculating the number of expired keys')
    maven_exp_before = len([d for d in maven_dates if d[0] > d[1]])
    maven_exp_after = len([d for d in maven_dates if d[0] < d[1]])
    result['maven'] = {
        'total': len(maven_dates),
        'pub_exp_before': {
            'count': maven_exp_before,
            'human': human_format(maven_exp_before),
            'percent': pc_str(maven_exp_before, len(maven_dates)),
        },
        'pub_exp_after': {
            'count': maven_exp_after,
            'human': human_format(maven_exp_after),
            'percent': pc_str(maven_exp_after, len(maven_dates)),
        },
        'median_remaining': '{:.2f}'.format(
            statistics.median(
                [d[2].days for d in maven_dates if d[0] < d[1]]
            )/365
        ),
    }

    # Calculate the number of expired keys
    pypi_exp_before = len([d for d in pypi_dates if d[0] > d[1]])
    pypi_exp_after = len([d for d in pypi_dates if d[0] < d[1]])
    result['pypi'] = {
        'total': len(pypi_dates),
        'pub_exp_before': {
            'count': pypi_exp_before,
            'human': human_format(pypi_exp_before),
            'percent': pc_str(pypi_exp_before, len(pypi_dates)),
        },
        'pub_exp_after': {
            'count': pypi_exp_after,
            'human': human_format(pypi_exp_after),
            'percent': pc_str(pypi_exp_after, len(pypi_dates)),
        },
        'median_remaining': '{:.2f}'.format(
            statistics.median(
                [d[2].days for d in pypi_dates if d[0] < d[1]]
            )/365
        ),
    }

    # Work on figuring out upgrade paths
    log.info('Calculating upgrade paths')
    find_upgrade_paths(database, Registry.MAVEN, maven_dates, result)
    find_upgrade_paths(database, Registry.PYPI, pypi_dates, result)

    print(json.dumps(result, indent=4))
    # Write the data to a LaTeX table
    log.info(f'Writing LaTeX table to {output}')
    with open(output, 'w') as f:
        if out_json:
            json.dump(result, f, indent=4)
        else:
            json2latex.dump('expkeys', result, f)

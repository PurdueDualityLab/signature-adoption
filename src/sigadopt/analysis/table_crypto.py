
'''
table_crypto.py: This script is used to generate a LaTeX table for the
cryptographic algorithms used in the signatures.
'''

import json
import json2latex
import logging
from sigadopt.util.number_things import human_format, pc_str
from sigadopt.util.database import SignatureStatus, Registry

# Set up logging
log = logging.getLogger(__name__)

algo_map = {
    1: 'rsa',
    3: 'rsasignonly',
    17: 'dsa',
    19: 'ecdsa',
    22: 'eddsa',
}


def count_algos(database, result, registry):

    with database:

        # Create a cursor
        cursor = database.cursor()

        # Execute the query
        log.info(f'Executing algo count query on {registry}...')
        cursor.execute(
            '''
                with reg_packets as (
                    select l.*
                    from list_packets l
                    join signatures s on s.id = l.signature_id
                    join artifacts a on a.id = s.artifact_id
                    join versions v on v.id = a.version_id
                    join packages p on p.id = v.package_id
                    where p.registry_id = ?
                )
                select
                    algo,
                    count(id),
                    (count(id)*100.0/(select count(id) from reg_packets))
                        as percent
                from reg_packets r
                group by algo
                order by percent
            ''',
            (registry,)
        )

        # Fetch all rows
        rows = cursor.fetchall()

        # Organize the data in a dictionary
        log.info('Organizing the data...')
        for algo, count, percent in rows:
            print(algo, count, percent)
            reg_text = Registry(registry).name.lower()
            if reg_text not in result:
                result[reg_text] = {}
            algo_text = algo_map.get(int(algo), f'{algo}')
            result[reg_text][algo_text] = {
                'count': count,
                'human': human_format(count),
                'percent': pc_str(percent, denom=100, precision=2),
            }

        print(result[Registry(registry).name.lower()])


def count_RSA_key(database, result, registry):

    with database:

        # Create a cursor
        cursor = database.cursor()

        # Execute the query
        log.info(f'Executing key count query on {registry}...')
        cursor.execute(
            '''
                with reg_packets as (
                    select l.*
                    from list_packets l
                    join signatures s on s.id = l.signature_id
                    join artifacts a on a.id = s.artifact_id
                    join versions v on v.id = a.version_id
                    join packages p on p.id = v.package_id
                    where p.registry_id = ?
                        and l.algo = 1
                )
                select
                    ((((data-1)/512)+1)*512) as data_up,
                    count(id),
                    (count(id)*100.0/(select count(id) from reg_packets))
                        as percent
                from reg_packets r
                group by data_up
                order by percent
            ''',
            (registry,)
        )

        # Fetch all rows
        rows = cursor.fetchall()

        # Organize the data in a dictionary
        log.info('Organizing the data...')
        reg_text = Registry(registry).name.lower()

        result[reg_text][algo_map[1]]['key_sizes'] = {}

        for data_up, count, percent in rows:
            result[reg_text][algo_map[1]]['key_sizes'][data_up] = {
                'count': count,
                'human': human_format(count),
                'percent': pc_str(percent, denom=100, precision=3),
            }


def run(database, output, out_json):
    '''
    This function generates a LaTeX table of the results.

    database: A database connection
    output: The path to write the LaTeX table to.
    out_json: Whether to output the results as JSON.
    '''

    # Results dictionary
    result = {}

    # Get the data
    log.info('Checking Maven')
    count_algos(database, result, Registry.MAVEN)
    count_RSA_key(database, result, Registry.MAVEN)

    log.info('Checking PyPI')
    count_algos(database, result, Registry.PYPI)
    count_RSA_key(database, result, Registry.PYPI)

    algo_set = set()
    algo_set |= result['maven'].keys()
    algo_set |= result['pypi'].keys()

    for algo in algo_set:
        for reg in ['maven', 'pypi']:
            if algo not in result[reg]:
                result[reg][algo] = {
                    'count': 0,
                    'human': human_format(0),
                    'percent': pc_str(0, precision=2),
                }

    key_sizes = set()
    key_sizes |= result['maven']['rsa']['key_sizes'].keys()
    key_sizes |= result['pypi']['rsa']['key_sizes'].keys()

    for key_size in key_sizes:
        for reg in ['maven', 'pypi']:
            if key_size not in result[reg]['rsa']['key_sizes']:
                result[reg]['rsa']['key_sizes'][key_size] = {
                    'count': 0,
                    'human': human_format(0),
                    'percent': pc_str(0, precision=3),
                }

    # Write the data to a LaTeX table
    log.info(f'Writing LaTeX table to {output}')
    with open(output, 'w') as f:
        if out_json:
            json.dump(result, f, indent=4)
        else:
            json2latex.dump('crypto', result, f)

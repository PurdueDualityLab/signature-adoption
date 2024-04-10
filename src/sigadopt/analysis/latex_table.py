'''
latex_table.py: This script is used to generate a LaTeX table of the results.
'''

import json2latex
import logging
from sigadopt.util.number_things import human_format, pc_str
from sigadopt.util.database import SignatureStatus, Registry

# Set up logging
log = logging.getLogger(__name__)


def unit_count(database, result):
    '''
    This function counts the number of units in each registry.

    database: A database connection
    result: A dictionary to store the results in.
    '''

    with database:

        # Create a cursor
        cursor = database.cursor()

        # Query to count the number of units in each registry
        query = '''
            SELECT p.registry_id, COUNT(a.id) as count
            FROM artifacts a
            JOIN versions v on a.version_id = v.id
            JOIN packages p on v.package_id = p.id
            GROUP BY p.registry_id
        '''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Organize the data in a dictionary
        for registry, package_count in rows:

            if registry not in result:
                result[registry] = {}
            result[registry]['num_artifacts'] = package_count
            result[registry]['num_artifacts_h'] = human_format(package_count)


def version_count(database, result):
    '''
    This function counts the number of versions in each registry.

    database: A database connection
    result: A dictionary to store the results in.
    '''

    with database:

        # Create a cursor
        cursor = database.cursor()

        # Query to count the number of versions in each registry
        query = '''
            SELECT p.registry_id, COUNT(v.id) as count
            FROM  versions v
            JOIN packages p on v.package_id = p.id
            GROUP BY p.registry_id
        '''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Organize the data in a dictionary
        for registry, package_count in rows:
            result[registry]['num_versions'] = package_count
            result[registry]['num_versions_h'] = human_format(package_count)


def package_count(database, result):
    '''
    This function counts the number of packages in each registry.

    database: A database connection
    result: A dictionary to store the results in.
    '''

    with database:

        # Create a cursor
        cursor = database.cursor()

        # Query to count the number of versions in each registry
        query = '''
            SELECT p.registry_id, COUNT(v.id) as count
            FROM  versions v
            JOIN packages p on v.package_id = p.id
            GROUP BY p.registry_id
        '''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Organize the data in a dictionary
        for registry, package_count in rows:
            result[registry]['num_packages'] = package_count
            result[registry]['num_packages_h'] = human_format(package_count)


def sig_statuses(database, result):
    '''
    This function counts the number of sig_status in each registry.

    database: A database connection
    result: A dictionary to store the results in.
    '''

    with database:

        # Create a cursor
        cursor = database.cursor()

        # Query to get the count of each sig_status for each registry
        query = '''
            SELECT p.registry_id, s.status, count(s.id) as count
            from sig_check s
            JOIN artifacts a on a.id = s.artifact_id
            JOIN versions v on a.version_id = v.id
            JOIN packages p on v.package_id = p.id
            GROUP BY p.registry_id, s.status
        '''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Possible statuses
        statuses = {
            'no_sig',
            'good'
            'bad_sig',
            'exp_sig',
            'exp_pub',
            'rev_pub',
            'bad_pub',
            'no_pub',
        }

        # Organize the data in a dictionary
        for registry, sig_status, count in rows:
            stat_txt = SignatureStatus(sig_status).name.lower()
            result[registry][stat_txt] = count
            result[registry][stat_txt + '_h'] = human_format(count)

        # Calculate the percentages
        for registry, sig_status, count in rows:
            stat_txt = SignatureStatus(sig_status).name.lower()
            if stat_txt == 'no_sig':
                denominator = result[registry]['num_artifacts']
                result[registry][stat_txt + '_p'] = pc_str(count, denominator)
                result[registry]['signed_p'] = pc_str(
                    denominator - count, denominator)
                result[registry]['signed_h'] = human_format(
                    denominator - count)
                result[registry]['signed'] = denominator - count
            else:
                denominator = result[registry]['num_artifacts'] - \
                    result[registry]['no_sig']
                result[registry][stat_txt + '_p'] = pc_str(count, denominator)

        # Check for missing sig_status
        for registry, data in result.items():
            for status in statuses:
                if status not in data:
                    result[registry][status] = 0
                    result[registry][status + '_p'] = '0.0%'
                    result[registry][status + '_h'] = '0'


def run(database, output):
    '''
    This function generates a LaTeX table of the results.

    database: A database connection
    output: The path to write the LaTeX table to.
    '''

    # Results dictionary
    result = {}

    # Get the data
    log.info('Counting units')
    unit_count(database, result)
    log.info('Counting versions')
    version_count(database, result)
    log.info('Counting packages')
    package_count(database, result)
    log.info('Counting sig statuses')
    sig_statuses(database, result)

    reg_ids = list(result.keys())
    for key in reg_ids:
        result[Registry(key).name.lower()] = result.pop(key)

    # Write the data to a LaTeX table
    log.info(f'Writing LaTeX table to {output}')
    with open(output, 'w') as f:
        json2latex.dump('data', result, f)

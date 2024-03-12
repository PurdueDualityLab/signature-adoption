import sqlite3
import json2latex
import json
from ..util.number_things import human_format, pc_str

# Connect to the SQLite database
# Replace 'your_database.db' with the actual name of your database
output = 'data/results/data.tex'
result = {}
conn = sqlite3.connect('data/adoption.db')
cursor = conn.cursor()


def unit_count():
    # Query to count the number of units in each registry
    query = '''
        SELECT p.registry, COUNT(*) as count
        FROM units u
        JOIN packages p ON u.package_id = p.id
        GROUP BY p.registry
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


def version_count():
    # Query to count the number of versions in each registry
    query = '''
        SELECT p.registry, COUNT(*) as count
        FROM versions v
        JOIN packages p ON v.package_id = p.id
        GROUP BY p.registry
    '''

    # Execute the query
    cursor.execute(query)

    # Fetch all rows
    rows = cursor.fetchall()

    # Organize the data in a dictionary
    for registry, package_count in rows:
        result[registry]['num_versions'] = package_count
        result[registry]['num_versions_h'] = human_format(package_count)


def package_count():
    # Query to count the number of packages in each registry
    query = '''
        SELECT p.registry, COUNT(*) as count
        FROM packages p
        GROUP BY p.registry
    '''

    # Execute the query
    cursor.execute(query)

    # Fetch all rows
    rows = cursor.fetchall()

    # Organize the data in a dictionary
    for registry, package_count in rows:
        result[registry]['num_packages'] = package_count
        result[registry]['num_packages_h'] = human_format(package_count)


def sig_statuses():
    # Query to get the count of each sig_status for each registry
    query = '''
        SELECT p.registry, u.sig_status, COUNT(*) as count
        FROM units u
        JOIN packages p ON u.package_id = p.id
        GROUP BY p.registry, u.sig_status
    '''

    # Execute the query
    cursor.execute(query)

    # Fetch all rows
    rows = cursor.fetchall()

    # Close the database connection
    conn.close()

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
        result[registry][sig_status.lower()] = count
        result[registry][sig_status.lower() + '_h'] = human_format(count)

    # Calculate the percentages
    for registry, sig_status, count in rows:
        if sig_status.lower() == 'no_sig':
            denominator = result[registry]['num_artifacts']
            result[registry][sig_status.lower() + '_p'] = pc_str(count,
                                                                 denominator)
            result[registry]['signed_p'] = pc_str(
                denominator - count, denominator)
            result[registry]['signed_h'] = human_format(denominator - count)
            result[registry]['signed'] = denominator - count
        else:
            denominator = result[registry]['num_artifacts'] - \
                result[registry]['no_sig']
            result[registry][sig_status.lower() + '_p'] = \
                pc_str(count, denominator)

    # Check for missing sig_status
    for registry, data in result.items():
        for status in statuses:
            if status not in data:
                result[registry][status] = 0
                result[registry][status + '_p'] = '0.0%'
                result[registry][status + '_h'] = '0'


unit_count()
version_count()
package_count()
sig_statuses()

# print(json.dumps(result, indent=4))

with open(output, 'w') as f:
    json2latex.dump('data', result, f)

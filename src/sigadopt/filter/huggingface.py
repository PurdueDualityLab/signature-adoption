'''
huggingface.py: This script filters the list of packages from HuggingFace.
'''

# Import statements
import logging
import random
from sigadopt.util.database import Registry, clean_db


def filter(
    input_conn,
    output_conn,
    min_date,
    max_date,
    min_versions,
    max_versions,
    random_select
):
    '''
    This function filters HuggingFace packages.

    input_conn: the connection to the input database.
    output_conn: the connection to the output database.
    min_date: the minimum date of the package and its versions/artifacts.
    max_date: the maximum date of the package and its versions/artifacts.
    min_versions: the minimum number of versions for a package.
    max_versions: the maximum number of versions for a package.
    random_select: the number of packages to randomly select.
    '''

    # Create a logger
    log = logging.getLogger(__name__)

    # Get the versions from Hugging Face with the specified date range
    log.debug('Collecting all Hugging Face versions inside the date range.')
    versions = None
    with input_conn:
        curr = input_conn.cursor()
        curr.execute(
            '''
                SELECT v.*
                FROM versions v
                JOIN packages p ON v.package_id = p.id
                WHERE p.registry_id = ?
                AND v.date
                BETWEEN ? AND ?
            ''',
            (
                Registry.HUGGINGFACE,
                min_date,
                max_date
            )
        )
        versions = curr.fetchall()

    # Filter the packages based on the number of versions
    log.debug('Filtering packages based on the number of versions.')

    # First we need to count how many versions exist inside of the date range
    # for each package
    pv_link = {}

    # Iterate through versions
    for version in versions:

        # Get the package id
        package_id = version[1]

        # If the package id is not in the dictionary, add it
        if package_id not in pv_link:
            pv_link[package_id] = []

        # Add the version to the list of versions for the package
        pv_link[package_id].append(version)

    # Filter the packages based on the number of versions
    pv_link = {
        package_id: versions for package_id, versions in pv_link.items()
        if min_versions <= len(versions) <= max_versions
    }

    # Randomly select packages if needed
    if random_select != -1:
        log.debug('Randomly selecting packages.')

        # Randomly select N packages
        selected = random.sample(pv_link.keys(), random_select)

        # Filter the packages based on the selected packages
        pv_link = {
            package_id: versions for package_id, versions in pv_link.items()
            if package_id in selected
        }

    # Get a list of selected packages
    selected_packages = []
    log.debug('Collecting selected pacakges.')
    with input_conn:
        curr = input_conn.cursor()

        for package_id in pv_link.keys():
            curr.execute(
                '''
                    SELECT *
                    FROM packages
                    WHERE id = ?
                ''',
                (package_id,)
            )
            selected_packages.append(curr.fetchone())

    # Clear the output database for Hugging Face
    log.debug('Cleaning the output database.')
    clean_db(output_conn, Registry.HUGGINGFACE)

    # Update selected packages with version count
    log.debug('Updating selected packages with version count.')
    for package in selected_packages:
        new_package = list(package)
        new_package[3] = len(pv_link[package[0]])
        package = tuple(new_package)

    # Insert selected packages into the output database
    log.debug('Inserting selected packages into the output database.')
    with output_conn:
        curr = output_conn.cursor()
        curr.executemany(
            '''
                INSERT INTO packages (
                    id, name, registry_id, versions_count, latest_release_date,
                    first_release_date, downloads, downloads_period
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            selected_packages
        )

    # Insert selected versions into the outpt database
    log.debug('Inserting selected versions into the output database.')

    # Get the selected versions
    selected_versions = [v for versions in pv_link.values() for v in versions]

    # Insert the selected versions
    with output_conn:
        curr = output_conn.cursor()
        curr.executemany(
            '''
                INSERT INTO versions (id, package_id, name, date)
                VALUES (?, ?, ?, ?)
            ''',
            selected_versions
        )

'''
pypi.py: This script gets the repositories and associated metadata from PyPI.
'''

# Import statements
import os
import logging
from google.cloud import bigquery
from sigadopt.util.database import clean_db


def packages(output_conn, auth_path=None, clean=False):
    '''
    This function gets a list of and packages and associated metadata from
    pypi using the ecosystems database.

    output_conn: The path to the output database.
    auth_path: The path to the authentication file.
    clean: Whether to clear the tables for PyPI before adding the new data.

    returns: None
    '''

    # Setup logger
    log = logging.getLogger(__name__)

    # If there is an authentication path, add it to the environment variable
    if auth_path:
        log.info(f'Adding authentication path {auth_path} to environment.')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(auth_path.resolve())

    # Log start of function
    log.info("Getting packages from PyPI.")

    # Create the client for the bigquery database
    client = bigquery.Client()

    # Create the query
    query = (
        '''
            SELECT name, version, filename, blake2_256_digest, upload_time,
            download_url, has_signature
            FROM `bigquery-public-data.pypi.distribution_metadata`
        '''
    )

    # Run the query
    query_job = client.query(query)

    # Get the results
    results = query_job.result()

    # Create dict for packages
    packages = {}

    # Loop through results
    for row in results:

        name = row[0]
        version = row[1]
        filename = row[2]
        digest = row[3]
        upload_time = str(row[4])
        download_url = row[5]
        has_signature = row[6]

        file_obj = {
            'filename': filename,
            'digest': digest,
            'upload_time': upload_time,
            'download_url': download_url,
            'has_signature': has_signature
        }

        # Check if package is in dict
        if name in packages:
            # If the version is in the dictionary
            if version in packages[name]:
                packages[name][version][digest] = file_obj
            else:
                packages[name][version] = {digest: file_obj}
        else:
            packages[name] = {version: {digest: file_obj}}

    # Clear the packages table
    if clean:
        log.info('Clearing tables for PyPI.')
        clean_db(output_conn, 4)

    # Insert packages into output database
    log.info('Adding packages to the output database.')
    with output_conn:

        # Create cursor
        output_curr = output_conn.cursor()

        # Iterate through packages
        for name, versions in packages.items():

            # Insert package into output database
            output_curr.execute(
                '''
                    INSERT INTO packages (registry_id, name, versions_count)
                    VALUES (?, ?, ?);
                ''',
                (
                    4,               # PyPI registry_id
                    name,            # Package name
                    len(versions),   # Number of versions
                )
            )

            # Get package id
            package_id = output_curr.lastrowid

            # Iterate through versions
            for version, files in versions.items():

                # Insert versions into output database
                output_curr.execute(
                    '''
                        INSERT INTO versions (package_id, name)
                        VALUES (?, ?);
                        ''',
                    (package_id, version)
                )

                # Get version id
                version_id = output_curr.lastrowid

                # Iterate through files
                for digest, file in files.items():

                    # Insert files into output database
                    output_curr.execute(
                        '''
                            INSERT INTO artifacts (version_id, name, type,
                                has_sig, digest, date)
                            VALUES (?, ?, ?, ?, ?, ?);
                            ''',
                        (
                            version_id,             # Version id
                            file['filename'],       # File name
                            'file',                 # File type
                            file['has_signature'],  # Has signature
                            file['digest'],         # Digest
                            file['upload_time']     # Date
                        )
                    )

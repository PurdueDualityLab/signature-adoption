#!/usr/bin/env python

'''packages.py: This script gets the repositories and associated metadata
for pypi repositories. It then saves the data to a ndjson file.
'''

# Import statements
import json
import os
import logging as log
from google.cloud import bigquery

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"


# Function to get the repositories and associated metadata
def packages(output_path, auth_path):
    '''
    This function gets a list of and packages and associated metadata from
    pypi using the ecosystems database.

    output_path: The path to the output file.
    auth_path: The path to the authentication file.

    returns: None
    '''

    # Log start of function
    log.info("Getting packages from PyPI.")

    # If there is an authentication path, add it to the environment variable
    if auth_path is not None:
        log.info(f'Adding authentication path {auth_path} to environment.')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = auth_path

    # Create the client for the bigquery database
    client = bigquery.Client()

    # Create the query
    query = (
        'SELECT name, version, filename, python_version, blake2_256_digest, '
        'upload_time, download_url, has_signature\n'
        'FROM `bigquery-public-data.pypi.distribution_metadata`\n')
    query_without_newlines = query.replace('\n', ' ')
    log.info(f'Query: {query_without_newlines}')

    # Run the query
    query_job = client.query(query)

    # Get the results
    results = query_job.result()

    # Create json object
    packages = {}

    # Loop through results
    for row in results:

        name = row[0]
        version = row[1]
        filename = row[2]
        python_version = row[3]
        blake2_256_digest = row[4]
        upload_time = str(row[5])
        download_url = row[6]
        has_signature = row[7]

        file_obj = {
            'filename': filename,
            'python_version': python_version,
            'blake2_256_digest': blake2_256_digest,
            'upload_time': upload_time,
            'download_url': download_url,
            'has_signature': has_signature
        }

        # Check if package is in json object
        if name in packages:
            # If the version is in the dictionary
            if version in packages[name]:
                packages[name][version].append(file_obj)
            else:
                packages[name][version] = [file_obj]
        else:
            packages[name] = {version: [file_obj]}

    # Open file
    log.info(f'Opening file {output_path} for writing.')
    with open(output_path, 'a') as f:
        for name, versions in packages.items():
            json.dump(
                {
                    'name': name,
                    'num_versions': len(versions),
                    'versions': versions
                },
                f, default=str)
            f.write('\n')

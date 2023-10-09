#!/usr/bin/env python

'''get_packages.py: This script gets the packages for given date ranges from PyPI.
'''


# Imports for this script
import json
import os
import logging as log
from datetime import datetime
from google.cloud import bigquery


# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'


# Dates for the query
dates = [
    '2015-08-11',
    '2018-03-22',
    '2022-10-26',
    '2023-05-23',
    '2023-08-04']

# File paths for the files used in this script
base_path = '..'
packages_paths = []
for i in range(len(dates)-1):
    packages_paths.append(base_path + f'/data/packages_{dates[i]}_{dates[i+1]}.json')


log_path = base_path + f'/logs/get_packages.log'

# Ensure the log folder exists
if not os.path.exists(base_path + '/logs'):
    os.mkdir(base_path + '/logs')
    print(f'Created logs folder.')

# Ensure the data folder exists
if not os.path.exists(base_path + '/data'):
    os.mkdir(base_path + '/data')
    print(f'Created data folder.')

# Set up logger
log_level = log.DEBUG if __debug__ else log.INFO
log.basicConfig(filename=log_path,
                    filemode='a',
                    level=log_level,
                    format='%(asctime)s|%(levelname)s|%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Log start time
log.info(f'Starting get_packages script.')
script_start_time = datetime.now()


def log_finish():
    '''
    Script simply logs time of script completion and total time elapsed.
    '''

    # Log end of script
    log.info(f'Script completed. Total time: {datetime.now()-script_start_time}')


def get_packages(start_date: str, end_date: str):
    '''
    This function gets the packages from the PyPI bigquery database.

    start_date: The start date for the query.

    end_date: The end date for the query.
    
    return: Package metadata from the PyPI bigquery database.
    '''

    # Create the client for the bigquery database
    client = bigquery.Client()

    # Create the query
    query = (
        'SELECT name, version, filename, python_version, blake2_256_digest, upload_time, download_url, has_signature\n' 
        'FROM `bigquery-public-data.pypi.distribution_metadata`\n' 
        f'WHERE upload_time > TIMESTAMP("{start_date} 00:00:00")\n' 
        f'AND upload_time < TIMESTAMP("{end_date} 00:00:00")')
    query_without_newlines = query.replace('\n', ' ')
    log.info(f'Query: {query_without_newlines}')

    # Run the query
    query_job = client.query(query)

    # Get the results
    results = query_job.result()

    return results


# Iterate through date ranges
for i in range(len(dates)-1):

    # Get the packages
    log.info(f'Getting packages between {dates[i]} and {dates[i+1]}')
    results = get_packages(dates[i], dates[i+1])

    # Create json object
    packages = []
    for row in results:
        packages.append({
            'name': row[0],
            'version': row[1],
            'filename': row[2],
            'python_version': row[3],
            'blake2_256_digest': row[4],
            'upload_time': str(row[5]),
            'download_url': row[6],
            'has_signature': row[7]})
        
    # Write to file
    log.info(f'Writing packages to {packages_paths[i]}')
    with open(packages_paths[i], 'w') as f:
        json.dump(packages, f, indent=4)
    

# Log finish
log_finish()
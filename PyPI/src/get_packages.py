#!/usr/bin/env python

'''get_packages.py: This script gets the packages for given date ranges from PyPI.
'''


# Imports for this script
import requests
import json
import sys
import os
import logging as log
from datetime import datetime
import time
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
packages_paths = [
    base_path + f'/data/packages_{dates[0]}_{dates[1]}.json',
    base_path + f'/data/packages_{dates[1]}_{dates[2]}.json',
    base_path + f'/data/packages_{dates[2]}_{dates[3]}.json',
    base_path + f'/data/packages_{dates[3]}_{dates[4]}.json']
log_path = base_path + f'/logs/get_packages.log'

# Ensure the log folder exists
if not os.path.exists(base_path + '/logs'):
    os.mkdir(base_path + '/logs')
    log.info(f'Created logs folder.')

# Ensure the data folder exists
if not os.path.exists(base_path + '/data'):
    os.mkdir(base_path + '/data')
    log.info(f'Created data folder.')

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


def get_packages(start_date, end_date):
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
        'SELECT name, version, filename, python_version, blake2_256_digest, upload_time, download_url' 
        'FROM `bigquery-public-data.pypi.distribution_metadata`' 
        f'WHERE upload_time > TIMESTAMP("{start_date} 00:00:00")' 
        f'AND upload_time < TIMESTAMP("{end_date} 00:00:00")')

    # Run the query
    query_job = client.query(query)

    # Get the results
    results = query_job.result()

    return results


# Testing
results = get_packages('2023-05-23', '2023-05-24')

# Print first 10 rows
for row in results:
    print(row)

# Iterate through date ranges
# for i in range(len(dates)-1):
    # Get the packages
    # results = get_packages(dates[i], dates[i+1])

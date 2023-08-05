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
date_1 = '2015-08-11'
date_2 = '2018-03-22'
date_3 = '2022-10-26'
date_4 = '2023-05-23'
date_5 = '2023-08-04'

# File paths for the files used in this script
base_path = '..'
packages_path = base_path + '/data/packages.json'
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
    # query = (
    #     'SELECT name, version, filename, python_version, blake2_256_digest' 
    #     'FROM `bigquery-public-data.pypi.distribution_metadata`' 
    #     f'WHERE upload_time > TIMESTAMP("{start_date} 00:00:00")' 
    #     f'AND upload_time < TIMESTAMP("{end_date} 00:00:00")')
    query = (
    'SELECT name FROM `bigquery-public-data.usa_names.usa_1910_2013` '
    'WHERE state = "TX" '
    'LIMIT 100')


    # Run the query
    query_job = client.query(query)

    # Get the results
    results = query_job.result()

    print (results)


get_packages(start_date=date_1, end_date=date_2)


    



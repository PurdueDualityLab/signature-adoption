#!/usr/bin/env python

'''sort_dates.py: This script sorts the results from check_adoption.py by date.
'''

# Import statements
import json
import logging as log
import sys
import os
from datetime import datetime


# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"

# get run id, start, and stop from command line
if len(sys.argv) < 1:
    print("Usage: python sort_dates.py [run_id] [start] [stop]")
    sys.exit(1)

# save variables from command line
target_file = sys.argv[1]

# Base file paths
base_path = '..'
log_path = base_path + f'/logs/sort_dates.log'

# Ensure the log folder exists
if not os.path.exists(base_path + '/logs'):
    os.mkdir(base_path + '/logs')
    print(f'Created logs folder.')

# Set up logger
log_level = log.DEBUG if __debug__ else log.INFO
log.basicConfig(filename=log_path,
                    filemode='a',
                    level=log_level,
                    format='%(asctime)s|%(levelname)s|%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Log start time
log.info(f'Starting sort_dates script.')
script_start_time = datetime.now()

def log_finish():
    '''
    Script simply logs time of script completion and total time elapsed.
    '''

    # Log end of script
    log.info(f'Script completed. Total time: {datetime.now()-script_start_time}')


# Dates for the sorting
dates = [
    '2015-08-11',
    '2018-03-22',
    '2022-10-26',
    '2023-05-23',
    '2023-08-04']


# Read in the file
with open(target_file, 'r') as f:
    data = json.load(f)

# Sort the data by date
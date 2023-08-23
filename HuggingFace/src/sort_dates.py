#!/usr/bin/env python

'''sort_dates.py: This script sorts the results from check_adoption.py by date.
'''

# Import statements
import json
import logging as log
import sys
import os
from datetime import datetime
from datetime import date

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
    datetime(2015, 8, 11),
    datetime(2018, 3, 22),
    datetime(2022, 10, 26),
    datetime(2023, 5, 23),
    datetime(2023, 8, 4)]

# Read in the file
data = None
with open(target_file, 'r') as f:
    data = json.load(f)

# Sort the data by date
sorted_data = {}

# Iterate through all dates
log.info(f'Sorting data by date.')
for indx in range(len(dates)-1):

    log.info(f'Sorting data for {dates[indx]} to {dates[indx+1]}.')

    # Add the date to the sorted data
    date_key = dates[indx].strftime( "%Y-%m-%d %H:%M:%S")
    sorted_data[date_key] = {
        'total_packages': 0,
        'total_commits': 0,
        'signed_commits': 0,
        'unsigned_commits': 0,
        'valid_signed_commits': 0,
        'invalid_signed_commits': 0,
        'signed_packages': 0,
        'unsigned_packages': 0,
        'repos': []
    }
    
    # Iterate through all registries
    for repo in data['registries']:

        # List to store commits in the date range
        commits_in_range = []

        # Iterate through all commits
        for commit in repo['commits']:

            # If the commit is in the date range, add it to the list
            commit_date = datetime.strptime(commit['time'], "%Y-%m-%d %H:%M:%S")  
            if commit_date >= dates[indx] and commit_date <= dates[indx+1]:
                commits_in_range.append(commit)
        
        # If there are commits in the date range, add to the sorted data
        if commits_in_range:
            
            # Iterate through commits to update totals
            signed_package = False
            for commit in commits_in_range:
                if commit['error'] == "" and commit['output'] == "":
                    sorted_data[date_key]['unsigned_commits'] += 1
                else:
                    signed_package = True
                    sorted_data[date_key]['signed_commits'] += 1
                    if "gpg: Good signature" in commit['error']:
                        sorted_data[date_key]['valid_signed_commits'] += 1
                    else:
                        sorted_data[date_key]['invalid_signed_commits'] += 1

            # Update package counts
            if signed_package:
                sorted_data[date_key]['signed_packages'] += 1
            else:
                sorted_data[date_key]['unsigned_packages'] += 1

            sorted_data[date_key]['total_packages'] += 1
            sorted_data[date_key]['total_commits'] += len(commits_in_range)

            # Add the registries and commits to the sorted data
            sorted_data[date_key]['repos'].append({
                'name': repo['name'],
                'url': repo['url'],
                'downloads': repo['downloads'],
                'last_modified': repo['last_modified'],
                'signed': signed_package,
                'commits': commits_in_range
            })


# Write the sorted data to a file
sorted_file = f'{target_file.rstrip(".json")}_sorted.json'
log.info(f'Writing sorted data to {sorted_file}.')
with open(sorted_file, 'w') as f:
    json.dump(sorted_data, f, indent=4)

# Log finish
log_finish()
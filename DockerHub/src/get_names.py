#!/usr/bin/env python3

'''get_names.py: This script gets the names of all repositories in docker hub.
'''

import requests
import os
import logging as log
from datetime import datetime

__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'

# Base url for dockerhub api
docker = 'https://hub.docker.com/v2'

# Base url for ecosystems api
ecosystems = 'https://packages.ecosyste.ms/api/v1'

# File paths for the files used in this script
base_path = '..'
names_path = base_path + '/data/names.txt'
log_path = base_path + f'/logs/names.log'

# Ensure the log folder exists
if not os.path.exists(base_path + '/logs'):
    os.mkdir(base_path + '/logs')
    log.info(f'Created logs folder.')

# Ensure the data folder exists
if not os.path.exists(base_path + '/data'):
    os.mkdir(base_path + '/data')
    log.info(f'Created data folder.')

# Set up logger
log_level = log.DEBUG if os.environ.get('DEBUG') else log.INFO
log.basicConfig(filename=log_path,
                    filemode='w',
                    level=log_level,
                    format='%(asctime)s|%(levelname)s|%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Log start time
log.info(f'Starting get_names script.')
script_start_time = datetime.now()

def log_finish():
    '''
    Script simply logs time of script completion and total time elapsed.
    '''

    # Log end of script
    log.info(f'Script completed. Total time: {datetime.now()-script_start_time}')




# Get a page of results from ecosystems
def get_ecosystems_page(page=1):
    '''
    This function takes in a page number and returns the results for that page.

    page: the page of results to fetch. Default is 1.

    returns: the list of names for a given page.
    '''

    # Get the page of results
    response = requests.get(ecosystems + f'/registries/hub.docker.com/package_names?page={page}&per_page=1000')

    # Return the response code and names
    return response.status_code, response.json()


# Get official repository names from docker hub
def get_official_dockerhub():
    '''
    This function gets the names of all official repositories from docker hub.

    returns: the list of names for official repositories.
    '''

    # Log start of function
    log.info(f'Getting official dockerhub names.')

    # List to hold names
    names = []

    # Iterate through pages until there is no next page
    page = 1
    next_page = True
    while next_page:

        # Get the page of results
        response = requests.get(docker + f'/repositories/official/?page={page}&page_size=100')

        # Get all names from the page
        for result in response.json()['results']:
            names.append(f'{result["namespace"]}/{result["name"]}')

        # If there is a next page, increment page
        if response.json()['next']:
            page += 1

        # Otherwise, we are done
        else:   
            next_page = False

    # Log end of function
    log.info(f'Got {len(names)} official dockerhub names.')

    # Return the list of names
    return names


# Open the names file and get names
with open(names_path, 'w') as names_file:

    # Log start of getting names
    log.info(f'Getting names from ecosyste.ms.')
    
    # Iterate through ecosystems pages until there is a non-200 response
    page = 1
    complete = False
    while not complete:
        
        # Get the page of results
        status_code, names = get_ecosystems_page(page)

        # If the status code is not 200, we are done
        if status_code != 200:
            complete = True
        
        # Otherwise, write the names to the file
        else:
            for name in names:
                names_file.write(name + '\n')
            page += 1


    # Log end of getting names from ecosystems
    log.info(f'Got {page} pages of names from ecosyste.ms.')


    # Get official images from docker hub api
    official_names = get_official_dockerhub()

    # Write the official names to the file
    log.info(f'Writing official names to file.')
    for name in official_names:
        names_file.write(name + '\n')


# Log the end of the script
log_finish()

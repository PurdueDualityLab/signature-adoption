#!/usr/bin/env python3

'''get_tags.py: This script gets the tags for each repository on DockerHub.
'''

import requests
import json
import sys
import os
import logging as log
from datetime import datetime

__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'

# Base url for dockerhub api
docker = 'https://hub.docker.com/v2'

# Check to see if command line args are correct
if len(sys.argv) != 3:
    print('Usage: python get_tags.py <start_repository> <stop_repository>')
    exit(-1)

# Get the start and stop parameters from the command line args
start_repository = int(sys.argv[1])
stop_repository = int(sys.argv[2])

# File paths for the files used in this script
base_path = '..'
names_path = base_path + '/data/names.txt'
tags_path = base_path + f'/data/tags{start_repository}-{stop_repository}.json'
log_path = base_path + f'/logs/get_tags{start_repository}-{stop_repository}.log'

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
log.info(f'Starting get_tags script.')
script_start_time = datetime.now()


def log_finish():
    '''
    Script simply logs time of script completion and total time elapsed.
    '''

    # Log end of script
    log.info(f'Script completed. Total time: {datetime.now()-script_start_time}')



def get_tags(repository_name, page=1):
    """
    This function takes in the name of a repository on docker hub and returns
    all tags associated with it.

    repository_name: the name of the target repository

    page: start page of results to fetch. Default is 1, going past the number of
    pages available returns an error.

    returns: the list of tags for a given registry.
    """


    log.debug(f'Starting tag retrevial for {repository_name}. '
             f'Page {page}.')

    
    # Create a request for the dockerhub api
    tags_req = f'{docker}/repositories/{repository_name}/'\
               f'tags/?page_size=100&page={page}'
    

    # Get response from the api
    response = requests.get(tags_req)
    code = response.status_code


    # Check for rate limiting
    if code == 429:
        log.error(f'Recieved status_code {code} - rate limiting. '
                  f'{repository_name} failed to download. Exiting.')
        log_finish()
        exit(-1)

    
    # This means there might be an error
    if code != 200:
        log.warning(f'Recieved status code {code} for {repository_name}.')
        return None

    # If there are more results on the next page, continue to get results
    if response.json()['next'] != None:
        return response.json()['results'] + \
               get_tags(repository_name=repository_name, page=page+1)
    
    # End of tags, return all responses
    else:
        return response.json()['results']




tag_data = []

# Open file containing all of the repository names
log.info(f'Opening {names_path}.')
with open(names_path, 'r', newline='') as name_file:

    # Get to the right place in the file
    log.info(f'Skipping the first {start_repository} repositories.')
    for x in range(start_repository):
        name_file.readline()
    
    # Read the correct number of repository names
    log.info(f'Beginning to loop through the selected repositories.')
    for x in range(start_repository, stop_repository):

        # Get next repo name and get tags for it
        repo_name = name_file.readline().strip()
        repo_tags = get_tags(repository_name=repo_name)

        # if repo_tags is None, then there was an problem - skip this repo
        if repo_tags == None:
            log.warning(f'Skipping {repo_name}.')
            continue

        # Get the number of tags
        count_tags = len(repo_tags)

        # Append the data to the json list
        tag_data.append({
            'name':repo_name,
            'count_tags':count_tags,
            'tags':repo_tags
        })

# Open up the json file
log.info(f'Writing json to {tags_path}.')
with open(tags_path, 'w') as tags_file:

    # Write data to file
    tags_file.write(json.dumps(tag_data))


# Done
log_finish()
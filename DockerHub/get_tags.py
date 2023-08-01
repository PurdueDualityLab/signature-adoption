#!/usr/bin/env python3

'''get_tags.py: This script gets the tags for each repository on DockerHub.
'''

import requests
import json
import sys
import logging as log
from datetime import datetime

__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'

# Base url for dockerhub api
docker = 'https://hub.docker.com/v2'

# Get the start and stop parameters from the command line args
start_repository = int(sys.argv[1])
stop_repository = int(sys.argv[2])

# File paths for the files used in this script
base_path = '/home/tschorle/DockerHub'
names_path = base_path + '/data/names.txt'
tags_path = base_path + f'/data/tags{start_repository}-{stop_repository}.json'
log_path = base_path + f'/logs/tags{start_repository}-{stop_repository}.log'

# Set up logger
log.basicConfig(filename=log_path,
                    filemode='w',
                    level=log.DEBUG,
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

    page: the page of results to fetch. Default is 1, going past the number of
    pages available returns an error.

    returns: the list of tags for a given registry.
    """


    log.info(f'Starting tag retrevial for {repository_name}. '
             f'Page {page}.')

    
    # Create a request for the dockerhub api
    tags_req = f'{docker}/repositories/{repository_name}/'\
               f'tags/?page_size=100&page={page}'
    log.debug(f'Request: {tags_req}')
    

    # Get response from the api
    response = requests.get(tags_req)
    code = response.status_code


    # Check for rate limiting
    if code == 429:
        log.error(f'Recieved status_code {code} - rate limiting. '
                  f'{repository_name} failed to download. Exiting.')
        log_finish()
        exit(-1)

    
    # This means there is an error
    if code != 200:
        log.warning(f'Recieved status code {code}.')
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

        # Get next repo name
        repo_name = name_file.readline().strip()
        repo_tags = get_tags(repository_name=repo_name)
        count_tags = len(repo_tags) if repo_tags != None else None

        # Append the data to the list
        tag_data.append({
            'name':repo_name,
            'count_tags':count_tags,
            'tags':repo_tags
        })

# Open up the json file
log.info(f'Opening {tags_path}.')
with open(tags_path, 'w') as tags_file:

    # Write data to file
    tags_file.write(json.dumps(tag_data))


# Done
log_finish()
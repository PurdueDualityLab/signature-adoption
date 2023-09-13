#!/usr/bin/env python

'''get_tags.py: This script gets the tags for each repository on DockerHub.
'''

import time
import requests
import json
import sys
import os
import argparse
import logging as log
from datetime import datetime

__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'

# Base url for dockerhub api
docker = 'https://hub.docker.com/v2'



# Use argparse to get command line args
parser = argparse.ArgumentParser(description='Get tags for all repositories in docker hub.')
parser.add_argument('--output',
                    type=str,
                    default='../data/names_tags.json',
                    help='The path to the output file. Defaults to ../data/names_tags.json.')
parser.add_argument('--log',
                    type=str,
                    default=f'../logs/get_tags.log',
                    help='The path to the log file. Defaults to ../logs/get_tags.log.')
parser.add_argument('--start',
                    type=int,
                    default=0,
                    help='The index to start at. Defaults to 0')
parser.add_argument('--stop',
                    type=int,
                    default=-1,
                    help='The index to stop at. Defaults to -1')
parser.add_argument('--source',
                    type=str,
                    default='../data/names.txt',
                    help='The path to the list of repository names. Defaults to ../data/names.txt.')
parser.add_argument('--retry',
                    type=int,
                    default=3,
                    help='The number of times to retry a request before giving up. Defaults to 3.')
args = parser.parse_args()

# Function to ensure an argument path is valid
def valid_path_create(path, folder=False):
    '''
    Function to ensure an argument path is valid. Creates the path if it does not exist.
    '''
    path = os.path.abspath(path) + ('/' if folder else '')
    try:
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            print(f'Path {dirname} does not exist! Creating!')
            os.makedirs(dirname)
    except:
        print(f'{dirname} is not writable! Exiting!')
        exit(-1)

    return path

# Function to ensure an argument path is valid
def valid_path(path):
    '''
    Function to ensure an argument path is valid.
    '''
    path = os.path.abspath(path)
    if not os.path.exists(path):
        print(f'Path {path} does not exist! Exiting!')
        exit(-1)
    return path

# Normalize paths
args.output = valid_path_create(args.output)
args.log = valid_path_create(args.log)
args.source = valid_path(args.source)

# Set up logger
log_level = log.DEBUG if __debug__ else log.INFO
log.basicConfig(filename=args.log,
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
    all tags associated with it and rate limits for following requests.

    repository_name: the name of the target repository

    page: start page of results to fetch. Default is 1, going past the number of
    pages available returns an error.

    returns: the json response for a given registry and the amount of time to wait
    before the next request.
    """


    log.debug(f'Starting tag retrevial for {repository_name}. '
             f'Page {page}.')

    
    # Create a request for the dockerhub api
    tags_req = f'{docker}/repositories/{repository_name}/'\
               f'tags/?page_size=100&page={page}'
    

    # Get response from the api
    response = requests.get(tags_req)
    json_response = response.json()
    code = response.status_code
    headers = response.headers

    # Get rate limiting information
    remaining_requests = int(headers['X-RateLimit-Remaining'])
    reset_time = int(headers['X-RateLimit-Reset'])
    wait_time = 0

    # This means there might be an error
    if code != 200:
        log.warning(f'Recieved status code {code} for {repository_name}.')
        return None

    # Logic for rate limiting
    if code == 429:
        log.warning(f'Rate limiting.')
        reset_time = int(headers['X-Retry-After'])
        wait_time = reset_time-datetime.timestamp(datetime.now())
        json_response = None
    elif remaining_requests == 0:
        wait_time = reset_time-datetime.timestamp(datetime.now())
    
    # Return the response and wait time
    return json_response, wait_time

def get_all_tags(repository_name):


        # If there is a wait time, wait
        # if wait_time > 0:
        #     log.info(f'Waiting {wait_time} seconds.')
        # #     time.sleep(wait_time)

        # # If there are more results on the next page, continue to get results
        # if response.json()['next'] != None:
        #     return response.json()['results'] + \
        #         get_tags(repository_name=repository_name, page=page+1)
        
        # # End of tags, return all responses
        # else:
        #     return response.json()['results']

    return None



tag_data = []

# Open file containing all of the repository names
log.info(f'Opening {args.source}.')
with open(args.source, 'r', newline='') as name_file:

    # Get to the right place in the file
    log.info(f'Skipping the first {args.start} repositories.')
    for x in range(args.start):
        name_file.readline()
    
    # Read the correct number of repository names
    log.info(f'Beginning to loop through the selected repositories.')
    x = args.start
    while(x < args.stop or args.stop == -1):

        # Increment the counter
        x += 1

        # Get next repo name and get tags for it
        next_line = name_file.readline()
        if next_line == '':
            break
        

        repo_name = next_line.strip()
        
        repo_tags = get_all_tags(repository_name=repo_name)

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
log.info(f'Writing json to {args.output}.')
with open(args.output, 'w') as tags_file:

    # Write data to file
    tags_file.write(json.dumps(tag_data))


# Done
log_finish()
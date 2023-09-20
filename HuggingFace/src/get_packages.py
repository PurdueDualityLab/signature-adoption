#!/usr/bin/env python

'''get_packages.py: This script gets the repositories and associated metadata from HuggingFace.
A full data dump is saved in a json file, and a simplified csv is also created.
'''

# Import statements
import json
import os
import csv
from datetime import datetime
import logging as log
from huggingface_hub.hf_api import ModelInfo, list_models

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"

# Base url for HuggingFace api
huggingface = 'https://huggingface.co/api'

# File paths for the files used in this script
base_path = '..'
log_path = base_path + f'/logs/get_hf_dump.log'
hf_dump_path = base_path + '/data/hf_dump.json'
hf_token_path = base_path + '/src/hf_token.txt'
simplified_csv_path = base_path + '/data/simplified.csv'

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
log.info(f'Starting get_hf_dump script.')
script_start_time = datetime.now()

def log_finish():
    '''
    Script simply logs time of script completion and total time elapsed.
    '''

    # Log end of script
    log.info(f'Script completed. Total time: {datetime.now()-script_start_time}')


# Read in token for huggingface api
log.info(f'Reading in token for HuggingFace API.')
with open(hf_token_path, 'r') as f:
    hf_token = f.read().strip()

# Get list of all models on HuggingFace
log.info(f'Getting list of all models on HuggingFace.')
model_list = list_models(full=True, 
                        cardData=True,
                        fetch_config=True, 
                        token=hf_token)

# Convert list of models to list of dictionaries
log.info(f'Converting list of models to list of dictionaries.')
repo_list = []
model: ModelInfo
for model in list(iter(model_list)):
    modelDict: dict = model.__dict__
    modelDict["siblings"] = [file.__dict__ for file in modelDict["siblings"]]
    repo_list.append(modelDict)

# free up memory
del model_list

# Save list of dictionaries to json file
log.info(f'Saving list of repositories to {hf_dump_path}')
with open(hf_dump_path, 'w') as f:
    json.dump(repo_list, f, indent=4)

# Create a simplified csv of data
log.info(f'Creating simplified csv of data at {simplified_csv_path}')
with open(simplified_csv_path, 'w', newline='') as f:
    
    # Create csv writer
    writer = csv.writer(f)

    for repo in repo_list:
        writer.writerow([
            repo['id'],
            f"https://huggingface.co/{repo['id']}",
            repo['downloads'],
            repo['lastModified']
        ])

# Log finish
log_finish()
#!/usr/bin/env python

'''packages.py: This script gets the repositories and associated metadata from
HuggingFace. A full data dump is saved in an ndjson file, and a simplified csv
is also created.
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


def hf_data_dump(hf_dump_path='packages.ndjson',
                 hf_token_path='hf_token.txt',
                 simplified_csv_path='simplified.csv'):
    ''' This function gets the repositories and associated metadata from
    HuggingFace. A full data dump is saved in an ndjson file, and a simplified
    csv is also created.

    hf_dump_path: The path to save the full data dump to.
    hf_token_path: The path to the file containing the HuggingFace API token.
    simplified_csv_path: The path to save the simplified csv to.

    returns: None
    '''

    log.info('Starting Hugging Face data dump.')

    # Read in token for huggingface api
    log.info('Reading in token for HuggingFace API.')
    with open(hf_token_path, 'r') as f:
        hf_token = f.read().strip()

    # Get list of all models on HuggingFace
    log.info('Getting list of all models on HuggingFace.')
    model_list = list_models(full=True,
                             cardData=True,
                             fetch_config=True,
                             token=hf_token)

    # Convert list of models to list of dictionaries
    log.info('Converting list of models to list of dictionaries.')
    repo_list = []
    model: ModelInfo
    for model in list(iter(model_list)):
        modelDict: dict = model.__dict__
        modelDict["siblings"] = [
            file.__dict__ for file in modelDict["siblings"]]
        repo_list.append(modelDict)

    # free up memory
    del model_list

    # Save list of dictionaries to json file
    log.info(f'Saving of repositories to {hf_dump_path}')
    with open(hf_dump_path, 'a') as f:
        for repo in repo_list:
            json.dump(repo, f, default=str)
            f.write('\n')

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

#!/usr/bin/env python

'''packages.py: This script gets the repositories and associated metadata from
HuggingFace. A full data dump is saved in an ndjson file, and a simplified csv
is also created.
'''

# Import statements
import json
import logging as log
from huggingface_hub.hf_api import ModelInfo, list_models

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"


def packages(output_path='packages.ndjson',
             token_path='hf_token.txt',
             token=None,):
    '''
    This function gets the repositories and associated metadata from
    HuggingFace. A full data dump is saved in an ndjson file.

    output_path: The path to save the full data dump to.
    token_path: The path to the file containing the HuggingFace API token.
    token: The HuggingFace API token. If this is provided, token_path is
    ignored.

    returns: None
    '''

    log.info('Starting HuggingFace package collection.')

    # Read in token for huggingface api
    hf_token = token
    if hf_token is None:
        log.info('Reading in token for HuggingFace API.')
        with open(token_path, 'r') as f:
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
        modelDict["url"] = f"https://huggingface.co/{modelDict['id']}"
        repo_list.append(modelDict)

    # free up memory
    del model_list

    # Save list of dictionaries to ndjson file
    log.info(f'Saving of repositories to {output_path}')
    with open(output_path, 'a') as f:
        for repo in repo_list:
            json.dump(repo, f, default=str)
            f.write('\n')

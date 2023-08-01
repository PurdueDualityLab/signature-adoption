#!/usr/bin/env python3

'''get_names.py: This script gets the names of all repositories in docker hub.
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
ecosystems = 'https://packages.ecosyste.ms/api/v1'
local_log_file_path = '/home/tschorle/DockerHub/names.txt'

response = None
x = 0


with open(local_log_file_path, 'a', newline='') as log_file:
    while(x < 1000):

        x+=1
        get_names = f'/registries/hub.docker.com/package_names?page={x}&per_page=1000'

        response = requests.get(ecosystems + get_names)

        if response.status_code != 200:
            break

        for name in response.json():
            log_file.write(name + '\n')

#!/usr/bin/env python

'''analysis.py: This script is used to analyze the adoption of all registries
with data.'''

# Imports
import argparse
import logging as log
from datetime import datetime
from docker.adoption import adoption as docker_adoption
from maven.adoption import adoption as maven_adoption
from npm.adoption import adoption as npm_adoption
from util.files import valid_path_create, valid_path


# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'

# Define global variables
script_start_time = datetime.now()

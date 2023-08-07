#!/usr/bin/env python

'''get_repositories.py: This script gets the repositories and associated metadata from HuggingFace.
'''

# Import statements
import requests
import json
import os
import sys
import pandas as pd
from pathlib import Path
import logging as log

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"


# Base url for HuggingFace api
huggingface = 'https://huggingface.co/api'

# File paths for the files used in this script
base_path = '..'

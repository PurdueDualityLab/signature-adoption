#!/usr/bin/env python

'''
database.py This script adds Docker Hub adoption data to the specified
database.
'''

# Imports
import json
import subprocess
import logging as log
from .. import util


# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'


def database():
    '''
    This function adds adoption data from Docker Hub to the database.
    '''

    util.signature_parser.test()


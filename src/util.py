#!/usr/bin/env python

'''util.py: This script contains utility functions for the signature adoption repo.
'''

# Import statements
import os

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"

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

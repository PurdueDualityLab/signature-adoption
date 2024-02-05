#!/usr/bin/env python

'''files.py: This script contains utility functions for file handling.'''

# Import statements
import os

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"


# Function to ensure an argument path is valid
def valid_path_create(path, folder=False):
    '''
    Function to ensure an argument path is valid. Creates the path if it does
    not exist.

    path: the path to check.

    folder: whether or not the path is a folder.

    returns: the absolute path if it is valid.
    '''
    path = os.path.abspath(path) + ('/' if folder else '')
    try:
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            print(f'Path {dirname} does not exist! Creating!')
            os.makedirs(dirname)
    except Exception as e:
        print(e)
        print(f'{dirname} is not writable! Exiting!')
        exit(-1)

    return path


# Function to ensure an argument path is valid
def valid_path(path):
    '''
    Function to ensure an argument path is valid.

    path: the path to check.

    returns: the absolute path if it is valid.
    '''
    path = os.path.abspath(path)
    if not os.path.exists(path):
        print(f'Path {path} does not exist! Exiting!')
        exit(-1)
    return path


# Function to generate path
def gen_path(directory, file, ecosystem, replace='-reg-', create=True):
    '''
    This function generates a file path given a directory, file, and ecosystem.
    It ensures the path exists, and creates directories if they do not exist
    by default Replaces instances of the replace word in the directory or file
    with the ecosystem name.

    directory: the path to the folder.

    file: the name of the file.

    ecosystem: the ecosystem name.

    replace: the word to replace in the directory or file name.

    create: whether or not to create directories if they do not exist.

    returns: the path to the file.
    '''
    if replace is not None or replace != '':
        directory = directory.replace(replace, ecosystem)
        file = file.replace(replace, ecosystem)

    path = os.path.join(directory,
                        file)
    if create:
        path = valid_path_create(path)
    else:
        path = valid_path(path)

    return path

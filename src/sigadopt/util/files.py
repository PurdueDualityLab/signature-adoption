'''
files.py: This script contains utility functions for file handling.
'''

# Import statements
from pathlib import Path
from argparse import ArgumentError
import requests
import logging
import os

# Create a logger
log = logging.getLogger(__name__)


def download_file(remote_file_url, local_file_path):
    '''
    This function downloads a file to a local path using requests.

    remote_file_url: url of file to download.
    local_file_path: path to save file to.

    returns: Binary of file if successful, None otherwise.
    '''
    response = requests.get(remote_file_url)

    if not response:
        log.error(f'Could not download file {remote_file_url}.')
        return None
    if response.status_code != 200:
        log.error(f'Could not download file {remote_file_url}. '
                  f'Code: {response.status_code}')
        return None

    # Write the file
    with open(local_file_path, "wb") as local_file:
        local_file.write(response.content)
    local_file.close()

    # Return binary of file is downloaded
    return response.content


def remove_file(file_path):
    '''
    This function removes a file.

    file_path: the path to the file.

    returns: None
    '''
    try:
        Path(file_path).unlink()
        log.debug(f'Removed file {file_path}.')
    except Exception as e:
        log.error(f'Could not remove file {file_path}.')
        log.error(e)


def path_exists(path, dir=False):
    '''
    This function checks if a path exists. If it does not, it raises an
    ArgumentError.

    path: the path to check.
    dir: whether or not the path is a directory.

    returns: the path if it exists.
    '''

    # Create a Path object
    path = Path(path)

    # Check if the path exists
    if not path.exists():
        log.error(f'Path {path} does not exist!')
        raise ArgumentError(None, f'Path {path} does not exist!')

    elif path.is_dir() and not dir:
        raise ArgumentError(
            None, f'Path {path} is a directory! It should be a file!')

    elif path.is_file() and dir:
        raise ArgumentError(
            None, f'Path {path} is a file! It should be a directory!')

    log.debug(f'Path {path} exists!')

    return path


def path_create(path, dir=False):
    '''
    This function creates a path if it does not exist. It also checks to ensure
    that a path is not a directory if it is supposed to be a file.

    path: the path to create.
    dir: whether or not the path is a directory.

    returns: the path.
    '''

    # Create a Path object
    path = Path(path)

    # Check if the path exists
    if not path.exists():
        log.info(f'Path {path} does not exist! Creating!')

        # Create the path
        try:
            if dir:
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()

        # Catch exceptions
        except Exception as e:
            print('owch')
            log.error(e)
            log.error(f'{path} is not writable! Exiting!')
            exit(-1)

    elif path.is_dir() and not dir:
        raise ArgumentError(
            None, f'Path {path} is a directory! It should be a file!')

    elif path.is_file() and dir:
        raise ArgumentError(
            None, f'Path {path} is a file! It should be a directory!')

    return path


def dir_create(path):
    return path_create(path, dir=True)


# Function to ensure an argument path is valid
def valid_path_create(path, folder=False):
    '''
    Function to ensure an argument path is valid. Creates the path if it does
    not exist.

    path: the path to check.

    folder: whether or not the path is a folder.

    returns: the absolute path if it is valid.
    '''
    return path_create(path, dir=folder)


# Function to ensure an argument path is valid
def valid_path(path):
    '''
    Function to ensure an argument path is valid.

    path: the path to check.

    returns: the absolute path if it is valid.
    '''
    return path_exists(path)


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

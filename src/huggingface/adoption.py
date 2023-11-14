#!/usr/bin/env python

'''
adoption.py: This script checks the adoption of signatures for packages from
Hugging Face.
'''

# Import statements
import json
import os
import subprocess
import shutil
import tarfile
import logging as log
from git import Repo

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"


def clone_repo(repo_url: str, repo_path: str) -> Repo:
    '''
    This function clones a repository and returns the Repo object.

    repo_url: The url of the repository.
    repo_path: The path to the repository.

    return: The Repo object. None if the repository could not be cloned.
    '''

    # Create a placeholder Repo object
    repo = None

    # Try to clone the repository
    log.debug(f'Cloning {repo_url} to {repo_path}.')
    try:
        repo = Repo.clone_from(repo_url, repo_path, bare=True)
    except Exception as e:
        log.warning(f'Could not clone {repo_url}!')
        log.warning(e)

    return repo


def check_commits(repo: Repo, repo_path: str) -> []:
    '''
    This function checks the commits in a repository and returns a list of
    dictionaries containing the commit information.

    repo: The Repo object.
    repo_path: The path to the repository.

    return: A list of dictionaries containing the commit information.
    '''

    # Create a list to store commit data
    commits_data = []

    for commit in repo.iter_commits():

        hexsha = commit.hexsha
        commit_time = commit.committed_datetime.strftime(
            "%Y-%m-%d %H:%M:%S")
        commit_author = commit.author.name

        # Verify the commit
        command = ["git", "verify-commit", "--raw", hexsha]
        output = subprocess.run(
            command, cwd=repo_path, capture_output=True, text=True)

        # Add commit to verification data
        commits_data.append({
            "hexsha": hexsha,
            "time": commit_time,
            "author": commit_author,
            "signature": {
                'stdout': output.stdout,
                'stderr': output.stderr,
            }
        })

    return commits_data


def delete_repo(repo_path: str) -> None:
    '''
    This function deletes a repository.

    repo_path: The path to the repository.

    return: None.
    '''

    log.debug(f'Removing repository {repo_path}.')
    try:
        shutil.rmtree(repo_path)
    except Exception as e:
        log.warning(f'Could not remove {repo_path}!')
        log.warning(e)


def tar_repo(repo_path: str) -> None:
    '''
    This function creates a tar file of a repository.

    repo_path: The path to the repository.

    return: None.
    '''

    log.debug(f'Saving repository {repo_path} as a tar file.')
    try:
        tar_path = f'{repo_path}.tar'
        tar = tarfile.open(tar_path, 'w')
        tar.add(repo_path, arcname=os.path.basename(repo_path))
        tar.close()
    except Exception as e:
        log.warning(f'Could not save {repo_path} as a tar file!')
        log.warning(e)


def adoption(
    input_file_path: str,
    output_file_path: str,
    download_dir: str,
    save: bool = False
):
    '''
    This function checks the adoption of signatures for packages from Hugging
    Face. It takes a newline delimited JSON file and outputs a newline
    delimited JSON file with the signatures added.

    input_file_path: the path to the input file.

    output_file_path: the path to the output file.

    download_dir: the directory to download the files to.

    save: whether or not to save the downloaded files. If so, they will be
    saved in the download_dir and the folders will be turned into tar files.

    returns: None.
    '''

    # Log start of script and open files
    log.info('Checking adoption of signatures for packages from Hugging Face.')
    log.info(f'Input file: {input_file_path}')
    log.info(f'Output file: {output_file_path}')
    log.info(f'Download directory: {download_dir}')

    with open(input_file_path, 'r') as input_file, \
            open(output_file_path, 'a') as output_file:

        # Read input file
        for indx, line in enumerate(input_file):

            # Log progress
            if indx % 100 == 0:
                log.info(f'Processing package {indx}.')

            # Parse line
            package = json.loads(line)

            # Extract package information and create local name and repo path
            model_id = package['id']
            local_name = model_id.replace('/', '-')
            repo_path = os.path.join(download_dir, local_name)

            # Clone the repository
            repo = clone_repo(package['url'], repo_path)

            # Check for a valid repository and check commits for signatures
            commits_data = None
            if repo is not None:
                commits_data = check_commits(repo, repo_path)

            # Add signature adoption to package
            package['commits'] = commits_data

            # Write package to output file
            json.dump(package, output_file, default=str)
            output_file.write('\n')

            # If save, save the repository as a tar file
            if save:
                tar_repo(repo_path)

            # Delete the repository
            delete_repo(repo_path)

    log.info('Finished checking adoption of signatures for packages from '
             'Hugging Face.')

#!/usr/bin/env python

'''check_adoption.py: This script checks the adoption of git commmit signatures.
It uses the simplified version of the HF dump to check a subset of the repositories.
'''

# Import statements
import json
import os
import subprocess
import shutil
import tarfile
import time
import logging as log
from datetime import datetime
import pandas 
import argparse
from git import Repo

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"

# Use argparse to get command line arguments
parser = argparse.ArgumentParser(description='Check adoption of git commit signatures.')
parser.add_argument('output',
                    type=str,
                    default='../data/verification_data.json',
                    help='The output file name. Defaults to ../data/verification_data.json.')
parser.add_argument('--start',
                    type=int,
                    default=0,
                    help='The index to start at. Defaults to 0')
parser.add_argument('--stop',
                    type=int,
                    default=-1,
                    help='The index to stop at. Defaults to -1')
parser.add_argument('--dloc',
                    type=str,
                    default='../temp/',
                    help='The path to the download folder. Defaults to ../temp/')
parser.add_argument('-s',
                    '--save',
                    action='store_true',
                    help='Save the bare repos as tar files. Default behavior is to delete files after checking.')
parser.add_argument('--source',
                    type=str,
                    default='../data/simplified.csv',
                    help='The path to the simplified csv. Defaults to ../data/simplified.csv.')
parser.add_argument('--delay',
                    type=float,
                    default=0,
                    help='The delay between requests in seconds.')
parser.add_argument('--log',
                    type=str,
                    default='../logs/check_adoption.log',
                    help='The path to the log file. Defaults to ../logs/check_adoption.log.')
args = parser.parse_args()

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

# Normalize paths
args.output = valid_path_create(args.output)
args.log = valid_path_create(args.log)
args.dloc = valid_path_create(args.dloc, folder=True)
args.source = valid_path(args.source)

# Set up logger
log_level = log.DEBUG if __debug__ else log.INFO
log.basicConfig(filename=args.log,
                filemode='a',
                level=log_level,
                format='%(asctime)s|%(levelname)s|%(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')

# Log start time
log.info(f'Starting check_adoption script.')
script_start_time = datetime.now()

def log_finish():
    '''
    Script simply logs time of script completion and total time elapsed.
    '''

    # Log end of script
    log.info(f'Script completed. Total time: {datetime.now()-script_start_time}')

# json variable to store commit data
verification_data = {
    "start_index": args.start,
    "stop_index": args.stop,
    "collection_start_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "total_packages": 0,
    "total_commits": 0,
    "signed_commits": 0,
    "unsigned_commits": 0,
    "signed_packages": 0,
    "unsigned_packages": 0,
    "valid_signatures": 0,
    "invalid_signatures": 0,
    "clone_failures": 0,
    "repos": [],
    "failed_repos": [] 
}

# Function to clone and verify signatures in a repository
def clone_verify(model_id, repo_url, downloads, last_modified):
    '''
    This function clones a repository and verifies the signatures of all commits.
    
    repo_url: The url of the repository to clone.
    '''
    # extract name of repository and create path
    local_name = ''.join(model_id.split('/'))
    repo_path = os.path.join(args.dloc, local_name)
    
    # Delay if necessary
    if args.delay > 0:
        time.sleep(args.delay)

    # Try to clone the repository
    try:
        log.info(f'Cloning {model_id} to {repo_path}.')
        repo = Repo.clone_from(repo_url, repo_path, bare=True)
    except:
        log.warning(f'Could not clone {model_id}!')
        verification_data["clone_failures"] += 1
        repo = None
    

    # Check for a valid repository
    if repo is not None:

        # Create a list to store commit data
        commits_data = []

        # loop through each commit in the repository
        log.info(f'Verifying signatures for {model_id}.')

        package_signed = False

        for commit in repo.iter_commits():

            hexsha = commit.hexsha
            commit_time = commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S")
            commit_author = commit.author.name

            # Verify the commit            
            command = ["git", "verify-commit", "--raw", hexsha]
            output = subprocess.run(command, cwd=repo_path, capture_output=True, text=True)

            # Check if the commit is signed
            if output.stderr == "" and output.stdout == "":
                verification_data["unsigned_commits"] += 1
            else:
                package_signed = True
                verification_data["signed_commits"] += 1
                if "gpg: Good signature" in output.stderr:
                    verification_data["valid_signatures"] += 1
                else:
                    verification_data["invalid_signatures"] += 1

            # Add commit to verification data
            commits_data.append({
                "hexsha": hexsha,
                "time": commit_time,
                "author": commit_author,
                "output": output.stdout,
                "error": output.stderr
            })

        # Update package counts
        if package_signed:
            verification_data["signed_packages"] += 1
        else:
            verification_data["unsigned_packages"] += 1

        # Update total counts
        verification_data["total_packages"] += 1
        verification_data["total_commits"] += len(commits_data)

        # Add repository to verification data
        log.info(f'Checked {len(commits_data)} commits for {model_id}.')
        verification_data["repos"].append({
            "name": model_id,
            "url": repo_url,
            "downloads": downloads,
            "last_modified": last_modified,
            "signed": package_signed,
            "commits": commits_data
        })

    else:
        # Add empty repository to verification data
        log.warning(f'Could not verify signatures for {model_id}.')
        verification_data["failed_repos"].append({
            "name": model_id,
            "url": repo_url,
            "downloads": downloads,
            "last_modified": last_modified,
            "signed": False,
            "commits": []
        })

    # Create a tar file of the repository
    if args.save:
        tar_path = os.path.join(args.dloc, f'{local_name}.tar')
        tar = tarfile.open(tar_path, 'w')
        tar.add(repo_path, arcname=local_name)
        tar.close()
        log.info(f'Repository {repo_path} saved as {tar_path}.')

    # Remove the repository
    try:
        shutil.rmtree(repo_path)
        log.info(f'Repository {repo_path} removed successfully.')
    except Exception as e:
        log.warning(f'Repository {repo_path} removal failure...')
    
# Read in the simplified csv
log.info(f'Reading in simplified csv.')
df = pandas.read_csv(args.source, header=None)

# Start iterating through the repositories
log.info(f'Iterating through repositories between {args.start} and {args.stop}.')
for index, row in df.iloc[args.start:args.stop].iterrows():
    clone_verify(row[0], row[1], row[2], row[3])

# Save verification data to json file
log.info(f'Saving verification data to {args.output}.')
with open(args.output, 'w') as f:
    json.dump(verification_data, f, indent=4)

# Log finish
log_finish()

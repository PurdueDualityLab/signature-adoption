#!/usr/bin/env python

'''check_adoption.py: This script checks the adoption of git commmit signatures.
It uses the simplified version of the HF dump to check a subset of the repositories.
'''

# Import statements
import json
import os
import subprocess
import shutil
import sys
import logging as log
from datetime import datetime
import pandas 
from git import Repo

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"

# get run id, start, and stop from command line
if len(sys.argv) < 3:
    print("Usage: python check.py [run_id] [start] [stop]")
    sys.exit(1)

# save variables from command line
run_id = sys.argv[1]
start_index = int(sys.argv[2])
stop_index = int(sys.argv[3])

# Base file paths
base_path = '..'
log_path = base_path + f'/logs/check_adoption_{run_id}.log'
hf_dump_path = base_path + '/data/hf_dump.json'
simplified_csv_path = base_path + '/data/simplified.csv'
temp_path = base_path + '/temp'

# Ensure the log folder exists
if not os.path.exists(base_path + '/logs'):
    os.mkdir(base_path + '/logs')
    print(f'Created logs folder.')

# Ensure the data folder exists
if not os.path.exists(base_path + '/data'):
    os.mkdir(base_path + '/data')
    print(f'Created data folder.')

# Ensure the temp folder exists
if not os.path.exists(temp_path):
    os.mkdir(temp_path)
    print(f'Created temp folder.')

# Set up logger
log_level = log.DEBUG if __debug__ else log.INFO
log.basicConfig(filename=log_path,
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
    "run_id": run_id,
    "start_index": start_index,
    "stop_index": stop_index,
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
    repo_path = f"{temp_path}/{''.join(model_id.split('/')).rstrip('.git')}"
    
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

    # Remove the repository
    try:
        shutil.rmtree(repo_path)
        log.info(f'Repository {repo_path} removed successfully.')
    except Exception as e:
        log.warning(f'Repository {repo_path} removal failure...')


# Read in the simplified csv
log.info(f'Reading in simplified csv.')
df = pandas.read_csv(simplified_csv_path, header=None)

# Start iterating through the repositories
log.info(f'Iterating through repositories between {start_index} and {stop_index}.')
for index, row in df.iloc[start_index:stop_index].iterrows():
    clone_verify(row[0], row[1], row[2], row[3])

# Save verification data to json file
log.info(f'Saving verification data to {base_path}/data/verification_data_{run_id}.json')
with open(f'{base_path}/data/verification_data_{run_id}.json', 'w') as f:
    json.dump(verification_data, f, indent=4)

# Log finish
log_finish()

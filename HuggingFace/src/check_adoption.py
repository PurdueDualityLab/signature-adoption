#!/usr/bin/env python

'''check_adoption.py: This script checks the adoption of git commmit signatures.
'''

# Import statements
import json
import os
import subprocess
import shutil
import sys
import csv
import logging as log
from datetime import datetime
from pandas import DataFrame
from git import Repo

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"

# Base file paths
base_path = '..'
log_path = base_path + f'/logs/get_hf_dump.log'
hf_dump_path = base_path + '/data/hf_dump.json'
csv_path = base_path + '/data/simplified.csv'

# Ensure the log folder exists
if not os.path.exists(base_path + '/logs'):
    os.mkdir(base_path + '/logs')
    log.info(f'Created logs folder.')

# Ensure the data folder exists
if not os.path.exists(base_path + '/data'):
    os.mkdir(base_path + '/data')
    log.info(f'Created data folder.')

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


# get run id, start, and stop from command line
if len(sys.argv) < 3:
    print("Usage: python check.py [run_id] [start] [stop]")
    log.error("Usage: python check.py [run_id] [start] [stop]")
    sys.exit(1)





log_file = f'/home/tschorle/HFSigning/check_log_{sys.argv[1]}.csv'
json_file = '/home/tschorle/HFSigning/data.json'
url_file = '/home/tschorle/HFSigning/urls.txt'
temp_space = '/scratch/bell/tschorle/top50'
private_key_path = '/home/tschorle/.ssh/id_ed25519'


git_ssh_cmd = f"ssh -i {private_key_path}"
git_ssh_env = {'GIT_SSH_COMMAND': git_ssh_cmd}


start = int(sys.argv[2])
stop = int(sys.argv[3])


def shrinkDataFrame(df: DataFrame, shrinkage: float = 0.1) -> DataFrame:
    if shrinkage >= 1:
        return df

    dfSize: int = len(df)
    lastRow: int = int(dfSize * shrinkage)

    return df.iloc[0:lastRow, :]


def clone_verify(repo_url, rank):
    # Clone the repository
    repo_name = repo_url.split('/')[-1].rstrip('.git')
    repo_path = f"{temp_space}/{repo_name}.git"
    
    try:
        repo = Repo.clone_from(repo_url, repo_path, bare=True, env=git_ssh_env)
        print(f'Cloned {repo_name} to {repo_path}.')
    except:
        print(f'Could not clone {repo_name}!')
        repo = 'Clone Failure'
    

    # Verify commit signatures
    with open(log_file, "a", newline="\n") as f:

        logger_writer = csv.writer(f)
        
        if repo is not 'Clone Failure':
            for commit in repo.iter_commits():
                hexsha = commit.hexsha
                command = ["git", "verify-commit", "--raw", hexsha]
                output = subprocess.run(command, cwd=repo_path, capture_output=True, text=True)

                logger_writer.writerow([rank, repo_url, hexsha, output.stdout, output.stderr])

            print(f'Commits checked.')
        else:
            logger_writer.writerow([rank, repo_url, 'FAIL', 'FAIL', 'FAIL'])
            print('Clone failure logged.')

    


    # Remove the repository
    try:
        shutil.rmtree(repo_path)
        print(f'Repository {repo_path} removed successfully.')
    except:
        print(f'Repository {repo_path} removal failure.')



# print(f"Loading into DataFrame...")
# df: DataFrame = pandas.read_json(json_file)

# print(f"Sorting DataFrame rows by download...")
# df.sort_values(by="downloads", ascending=False, inplace=True)
# df.reset_index(inplace=True)

# print(f"Reducing the size of the DataFrame to...")
# df = shrinkDataFrame(df)

print('Loading in urls...')
urls = []
with open(url_file, 'r') as f:
    urls = f.readlines()
urls = [url.strip() for url in urls]

print('beginning verification...')

for rank in range(start, stop):
    clone_verify(urls[rank],rank)





# names: List[str] = [f"{id}" for id in df["id"]]
# downloads: List[int] = [dl for dl in df['downloads']]

# dir = '/scratch/bell/tschorle/top50/'
# repo_outputs = []
# repo_commits = []
# repo_good_commits = []

# for x in range(1,51):

#     repo_path = dir+str(f'{x:02d}')
#     repo = Repo(repo_path)

#     commits = list(repo.iter_commits())
#     repo_commits.append(len(commits))

#     outputs = []

#     for commit in commits:
#         commit_hash = str(commit)
#         command = ["git", "verify-commit", commit_hash]
#         output = subprocess.run(command, cwd=repo_path, capture_output=True, text=True)
#         outputs.append(output.stdout)

#     repo_outputs.append(outputs)
#     repo_good_commits.append(sum([output is not '' for output in outputs]))


# data = zip(names, downloads, repo_commits, repo_good_commits)

# with open(f"./check.csv", "w", newline="\n") as f:
#     f.writelines([f'{name}, {dl}, {commits}, {good_commits}\n' for (name, dl, commits, good_commits) in data])

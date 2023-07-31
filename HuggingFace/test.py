from git import Repo
import subprocess
from typing import List
import pandas
import numpy as np
from pandas import DataFrame
import shutil
import sys
import csv

repo = Repo('/home/tschorle/PTMTorrent')
log_file = 'test.csv'

# Verify commit signatures
with open(log_file, "a", newline="\n") as f:

    logger_writer = csv.writer(f)
    
    if repo is not 'Clone Failure':
        for commit in repo.iter_commits():
            hexsha = commit.hexsha
            command = ["git", "verify-commit", "--raw", hexsha]
            output = subprocess.run(command, cwd='/home/tschorle/PTMTorrent', capture_output=True, text=True)

            logger_writer.writerow([hexsha, output.stdout, output.stderr])

        print(f'Commits checked.')
    else:
        print('Clone failure logged.')
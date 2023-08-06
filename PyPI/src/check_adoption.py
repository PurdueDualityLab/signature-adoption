#!/usr/bin/env python

'''check_adoption.py: This script checks the adoption of signatures for packages from PyPI.

filename: The name of the package metadata file.
'''

import csv
import json
import os
import sys
import subprocess
import time
import re
import logging as log
from datetime import datetime


# Author information
__author__ = 'Taylor R. Schorlemmer and Rajeev Sashti'
__email__ = 'tschorle@purdue.edu'

# File paths for the files used in this script
base_path = '..'
log_path = base_path + f'/logs/check_adoption.log'

# Ensure the log folder exists
if not os.path.exists(base_path + '/logs'):
    os.mkdir(base_path + '/logs')
    print(f'Created logs folder.')

# Set up logger
log_level = log.DEBUG if __debug__ else log.INFO
log.basicConfig(filename=log_path,
                    filemode='a',
                    level=log_level,
                    format='%(asctime)s|%(levelname)s|%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def log_finish():
    '''
    Script simply logs time of script completion and total time elapsed.
    '''

    # Log end of script
    log.info(f'Script completed. Total time: {datetime.now()-script_start_time}')

# Log start time
log.info(f'Starting get_packages script.')
script_start_time = datetime.now()

# Check for correct number of arguments
if len(sys.argv) != 2:
    log.error(f'Incorrect number of arguments. Expected 1, got {len(sys.argv)-1}.')
    sys.exit(1)

# Store the package path
package_path = base_path+'/data/'+sys.argv[1]

# Ensure the package file exists
if not os.path.exists(package_path):
    log.error(f'Package file {package_path} does not exist.')
    sys.exit(1)

# Extract the date range from the package file name
date_range = sys.argv[1][sys.argv[1].find('_')+1:sys.argv[1].find('.')]
log.info(f'Checking signature adoption between {date_range} using {package_path}.')


def url_construction(digest: str, filename: str) -> str:
    '''
    This function constructs the url for the package file.
    
    digest: The digest of the package file.
    
    filename: The name of the package file.

    return: The url for the package file.
    '''

    # Construct the url
    prefix = "https://files.pythonhosted.org/packages/"
    hash_section = f"{digest[0:2]}/{digest[2:4]}/{digest[4:]}/"
    url = prefix + hash_section + filename

    return url


def check_package_range(path: str) -> None:
    '''
    This function reads a json file containing package information and checks the adoption of signatures for each package.
    
    path: The path to the json file containing package information.
    '''

    # Read the json file
    log.info(f'Reading json file {path}.')
    with open(path, 'r') as f:
        packages = json.load(f)

        # Check the adoption of signatures for each package
        for package in packages:
            

        




valid_count = 0
total_count = 0


with open(log_file, 'a', newline='') as logger:

    logger_writer = csv.writer(logger)

    for line in infile:

        filename = line['filename']
        url = url_construction(line)

        ### need to use data in each line of .csv to first do wget on the correct urls, then run the gpg statement
        subprocess.run(['wget', url], capture_output=True)
        subprocess.run(['wget', url+'.asc'], capture_output=True)

        # os.system(f"wget {url}")
        # os.system(f"wget {url}.asc")
        # os.system("clear")

        time.sleep(0.001)
        ### based on return msg of gpg command, can then assess validity of signature
        output = subprocess.run(["gpg", "--keyserver-options", "auto-key-retrieve", 
        "--keyserver", "keyserver.ubuntu.com", "--verify", f"{filename}.asc", f"{filename}"], capture_output=True)

        if re.search("Good signature", str(output.stderr)):
            valid_count += 1

        total_count += 1

        logger_writer.writerow([line['name'], line['version'], line['filename'], line['python_version'], line['blake2_256_digest'], output.stdout, output.stderr])

        subprocess.run(['rm', '-r', filename])
        subprocess.run(['rm', '-r', filename+'.asc'])

    #     ### should probably remove packages at the end of the loop to prevent any buildup
    #     os.system(f"rm -r {filename}")
    #     os.system(f"rm -r {filename}.asc")

print(time.localtime())


# print(f"Valid signatures: {valid_count}\nTotal signatures: {total_count}")
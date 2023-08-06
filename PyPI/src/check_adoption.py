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
adoption_path = base_path + f'/data/adoption_{date_range}.json'
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

        
# Counters for stats we care about
total_packages = 0
total_signed = 0
total_unsigned = 0
total_signed_valid = 0
total_signed_invalid = 0

# create a json structure to store information about the packages
adoption = {
    'total_packages': total_packages,
    'total_signed': total_signed,
    'total_unsigned': total_unsigned,
    'total_signed_valid': total_signed_valid,
    'total_signed_invalid': total_signed_invalid,
    'signed_packages': []
}

# Read the json file
log.info(f'Reading json file {package_path}.')
with open(package_path, 'r') as f:
    packages = json.load(f)

    # Check the adoption of signatures for each package
    for package in packages:
        total_packages += 1

        # Check if the package has a signature
        if package['has_signature']:
            total_signed += 1

            # Create url and download files
            filename = package['filename']
            url = url_construction(digest=package['blake2_256_digest'], 
                                   filename=filename)
            subprocess.run(['wget', url], capture_output=True)
            subprocess.run(['wget', url+'.asc'], capture_output=True)

            # time.sleep(0.001)

            # Run the gpg verify command
            output = subprocess.run(
                [
                    "gpg", 
                    "--keyserver-options", 
                    "auto-key-retrieve", 
                    "--keyserver", 
                    "keyserver.ubuntu.com", 
                    "--verify", 
                    f"{filename}.asc", 
                    f"{filename}"
                ], 
                capture_output=True)
            
            # Use regex to check if the signature is valid
            if re.search("Good signature", str(output.stderr)):
                total_signed_valid += 1
            else:
                total_signed_invalid += 1

            
            # Add the package to the json structure
            adoption['signed_packages'].append({
                'name': package['name'],
                'version': package['version'],
                'filename': package['filename'],
                'python_version': package['python_version'],
                'blake2_256_digest': package['blake2_256_digest'],
                'upload_time': package['upload_time'],
                'download_url': package['download_url'],
                'file_url': url,
                'stdout': output.stdout.decode('utf-8'),
                'stderr': output.stderr.decode('utf-8')
            })

            # Remove the files
            subprocess.run(['rm', '-r', filename])
            subprocess.run(['rm', '-r', filename+'.asc'])

        # If there aren't any signatures, 
        else:
            total_unsigned += 1

# Update the stats
adoption['total_packages'] = total_packages
adoption['total_signed'] = total_signed
adoption['total_unsigned'] = total_unsigned
adoption['total_signed_valid'] = total_signed_valid
adoption['total_signed_invalid'] = total_signed_invalid

# Write the json file
log.info(f'Writing json file {adoption_path}.')
with open(adoption_path, 'w') as f:
    json.dump(adoption, f) 

# Log end of script
log_finish()
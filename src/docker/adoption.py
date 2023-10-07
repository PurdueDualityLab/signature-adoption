#!/usr/bin/env python

'''
adoption.py: This script checks the adoption of signatures for packages from
Docker Hub.
'''

# Imports
import json
import subprocess
import logging as log


# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'


def get_signatures(package_name):
    '''
    This function gets the signatures for a package from Docker Hub.

    package_name: the name of the package.

    returns: the output of the docker trust inspect command.
    '''

    # Check to see if package has signatures
    output = subprocess.run(
        [
            "docker",
            "trust",
            "inspect",
            f"{package_name}",
        ],
        capture_output=True)

    return json.loads(output.stdout), output.stderr.decode("utf-8")


def adoption(input_file_path,
             output_file_path,
             start=0,
             end=-1,
             min_downloads=1,
             min_versions=1):
    '''
    This function checks the adoption of signatures for packages from Docker
    Hub. It takes a newline delimited JSON file and outputs a newline
    delimited JSON file with the signatures added.

    input_file_path: the path to the input file.

    output_file_path: the path to the output file.

    start: the line to start on. Default is 0 (start of file).

    end: the line to end on. Default is -1 (end of file).

    min_downloads: the minimum number of downloads for a package to be
    considered. Default is 1.

    min_versions: the minimum number of versions for a package to be
    considered. Default is 1.

    returns: None.
    '''

    # Log start of script and open files
    log.info('Checking adoption of signatures for packages from Docker Hub.')
    log.info(f'Input file: {input_file_path}')
    log.info(f'Output file: {output_file_path}')

    with open(input_file_path, 'r') as input_file, \
            open(output_file_path, 'a') as output_file:

        # Read input file
        for i, line in enumerate(input_file):

            # Skip lines and check for end
            if i < start:
                continue
            if end != -1 and i > end:
                break

            # Log progress
            if i % 100 == 0:
                log.info(f'Processing package {i}.')

            # Parse line
            package = json.loads(line)
            package_name = package['name']

            # Check for minimum downloads
            if package['downloads'] < min_downloads:
                continue

            # Check for minimum versions
            if package['versions_count'] < min_versions:
                continue

            # Get package's signatures
            signatures, stderr = get_signatures(package_name)

            # Add signatures to package
            package['signatures'] = signatures
            package['stderr'] = stderr

            # Write package to output file
            json.dump(package, output_file, default=str)
            output_file.write('\n')

    log.info('Finished checking adoption of signatures for packages from '
             'Docker Hub.')

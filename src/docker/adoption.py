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


def adoption(input_file_path, output_file_path):
    '''
    This function checks the adoption of signatures for packages from Docker
    Hub. It takes a newline delimited JSON file and outputs a newline
    delimited JSON file with the signatures added.

    input_file_path: the path to the input file.

    output_file_path: the path to the output file.

    returns: None.
    '''

    # Log start of script and open files
    log.info('Checking adoption of signatures for packages from Docker Hub.')
    log.info(f'Input file: {input_file_path}')
    log.info(f'Output file: {output_file_path}')

    with open(input_file_path, 'r') as input_file, \
            open(output_file_path, 'w') as output_file:

        # Read input file
        for indx, line in enumerate(input_file):

            # Log progress
            if indx % 100 == 0:
                log.info(f'Processing package {indx}.')
            else:
                log.debug(f'Processing package {indx}.')

            # Parse line
            package = json.loads(line)
            package_name = package['name']

            # Get package's signatures
            signatures, stderr = get_signatures(package_name)

            # Add signatures to package
            package['signatures'] = {
                'dct': signatures,
                'stderr': stderr
            }

            # Write package to output file
            json.dump(package, output_file, default=str)
            output_file.write('\n')

    log.info('Finished checking adoption of signatures for packages from '
             'Docker Hub.')

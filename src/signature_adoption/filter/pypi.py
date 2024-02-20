#!/usr/bin/env python

'''filter.py: This script filters the list of packages from PyPI.
'''

# Import statements
import logging as log
import random
import json
from datetime import datetime

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"

# Function to filter the packages


def filter(input_path,
           output_path,
           random_select=-1,
           min_versions=1,
           min_date=None):
    '''
    This function filters PyPI packages.

    input_path: the path to the input file.
    output_path: the path to the output file.
    random_select: the number of packages to randomly select. If -1, all.
    min_versions: the minimum number of versions.
    min_date: the minimum date of the package. If None, no minimum date.
    '''

    # Initialize the list of packages
    selected = []

    # Open the input and output files
    with open(input_path, 'r') as input_file:

        # Iterate over the lines in the input file
        for indx, line in enumerate(input_file):

            # Log the progress
            if indx % 1000 == 0:
                log.info(f'Processing line {indx}')

            # Load the line as JSON
            package = json.loads(line)

            # Check if the package has enough versions
            if package['num_versions'] < min_versions:
                continue

            # Check if we have a min_date, if so filter the versions
            if min_date is not None:

                # Remove all files uploaded before min_date
                for version_name, version in package['versions'].items():
                    package['versions'][version_name] = {
                        file_hash: file for file_hash, file
                        in version.items()
                        if datetime.strptime(
                            # Truncate the upload time to the second, this is
                            # necessary but kind of a hack
                            file['upload_time'][0:19],
                            '%Y-%m-%d %H:%M:%S'
                        ) >= min_date
                    }

                # Remove all empty versions
                package['versions'] = {
                    version_name: version for version_name, version
                    in package['versions'].items()
                    if version
                }

                # update the number of versions and check if the package still
                # has enough versions
                package['num_versions'] = len(package['versions'])
                if package['num_versions'] < min_versions:
                    continue

            # Add the package to the list
            selected.append(package)

    # Log length of list
    log.info(f'Length after filter: {len(selected)}')

    # If random_select is -1, set it to the length of the list
    if random_select == -1:
        random_select = len(selected)

    # Randomly select the packages
    selected = random.sample(selected, random_select)

    # Log length of list
    log.info(f'Length after sample: {len(selected)}')

    # Write the packages to the output file
    with open(output_path, 'w') as output_file:
        for package in selected:
            json.dump(package, output_file)
            output_file.write('\n')

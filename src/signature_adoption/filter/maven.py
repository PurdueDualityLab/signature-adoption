#!/usr/bin/env python

'''filter.py: This script filters the list of packages from Maven Central.
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
           min_dependants=0,
           min_date=datetime(2015, 1, 1)):
    '''
    This function filters Maven Central packages.

    input_path: the path to the input file.
    output_path: the path to the output file.
    random_select: the number of packages to randomly select. If -1, all.
    min_versions: the minimum number of versions.
    min_dependants: the minimum number of dependants.
    min_date: the minimum date of the package.
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

            # Cont if the package doesn't have the min downloads or versions
            if package['dependent_repos_count'] < min_dependants and \
                    package['versions_count'] < min_versions:
                continue

            # Cont if latest release date is less than min_date
            latest_release_date = datetime.strptime(
                package['latest_release_published_at'].split('.')[0],
                '%Y-%m-%d %H:%M:%S'
            )
            if latest_release_date < min_date:
                continue

            # Remove all versions that are less than min_date
            versions = package['versions']
            package['versions'] = [
                version for version in versions if
                datetime.strptime(
                    version['published_at'].split('.')[0],
                    '%Y-%m-%d %H:%M:%S'
                )
                >= min_date
            ]

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

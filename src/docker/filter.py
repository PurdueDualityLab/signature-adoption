#!/usr/bin/env python

'''filter.py: This script filters the list of packages from Docker Hub.
'''

# Import statements
import logging as log
import random
import json

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"

# Function to filter the packages


def filter(input_path,
           output_path,
           random_select=-1,
           min_downloads=1,
           min_versions=1):
    '''
    This function filters DockerHub packages.

    input_path: the path to the input file.
    output_path: the path to the output file.
    random_select: the number of packages to randomly select. If -1, all.
    min_downloads: the minimum number of downloads.
    min_versions: the minimum number of versions.
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

            if package['downloads'] is None or \
                    package['versions_count'] is None:
                continue

            # Check if the package has enough downloads and likes
            if package['downloads'] >= min_downloads and \
                    package['versions_count'] >= min_versions:

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

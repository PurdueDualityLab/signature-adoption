#!/usr/bin/env python

'''
adoption.py: This script checks the adoption of signatures for packages from
Maven Central.
'''

# Imports
import json
import subprocess
import requests
import logging as log
from bs4 import BeautifulSoup


# Author information
__author__ = 'Taylor R. Schorlemmer and Andy Ko'
__email__ = 'tschorle@purdue.edu'


def get_files(maven_central_url, package_name, version_number):
    '''
    This function gets the files for a package from Maven Central.

    maven_central_url: the URL for Maven Central.

    package_name: the name of the package to get the files for.

    version_number: the version number of the package to get the files for.

    returns: the files for the package and corresponding extensions.
    '''

    # Construct the url
    repo_url = maven_central_url + package_name + '/' + version_number + '/'

    # Get the html from the given url
    response = requests.get(repo_url)

    # Check to see if we got a response
    if not response:
        return None

    files = []

    # Find all a tags - this is where the files are
    soup = BeautifulSoup(response.text, "html.parser")
    for a_tag in soup.find_all("a"):

        # if the href includes a forward slash the entry is another sub-dir
        href = a_tag.get("href")
        if '/' not in href:
            files.append(href)

    # Sort the files by length
    file_names = sorted(files, key=len)

    # TODO: This is a hacky way to get the unique files and their extensions.
    #       There is probably a better way to do this.
    unique_files = []

    while len(file_names) > 0:

        name = file_names[0]
        subset = [f for f in file_names if f.startswith(name)]
        file_names = [f for f in file_names if f not in subset]
        subset = [f[len(name):] for f in subset]
        subset = [f for f in subset if f != '']

        unique_files.append((name, subset))


def check_signatures(package):
    '''
    This function gets the signatures for a package from Maven Central.

    package: the package to get the signatures for.

    returns: the signatures for the package.
    '''

    # Maven Central URL
    maven_central_url = 'https://repo1.maven.org/maven2/'

    # Parse package name
    package_name = package['name']
    package_name = package_name.replace('.', '/').replace(':', '/')

    # Iterate through versions
    for version in package['versions']:
        version_number = version['number']

        files = get_files(maven_central_url, package_name, version_number)


def adoption(input_file_path,
             output_file_path,
             start=0,
             end=-1,
             min_versions=1):
    '''
    This function checks the adoption of signatures for packages from Maven
    Central. It takes a newline delimited JSON file and outputs a newline
    delimited JSON file with the signatures added.

    input_file_path: the path to the input file.

    output_file_path: the path to the output file.

    start: the line to start on. Default is 0 (start of file).

    end: the line to end on. Default is -1 (end of file).

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

            # Check for minimum versions
            versions_count = package['versions_count']
            versions_count = 0 if versions_count is None else versions_count
            if versions_count < min_versions:
                continue

    log.info('Finished checking adoption of signatures for packages from '
             'Maven Central.')

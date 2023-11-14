#!/usr/bin/env python

'''adoption.py: This script checks the adoption of signatures for packages from
PyPI.
'''

import json
import subprocess
import logging as log


# Author information
__author__ = 'Taylor R. Schorlemmer and Rajeev Sashti'
__email__ = 'tschorle@purdue.edu'


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


def adoption(input_file_path, output_file_path, download_dir):
    '''
    This function checks the adoption of signatures for packages from
    PyPI. It takes a newline delimited JSON file and outputs a newline
    delimited JSON file with the signatures added.

    input_file_path: the path to the input file.
    output_file_path: the path to the output file.
    download_dir: the directory to download the files to.

    returns: None.
    '''

    # Log start of script and open files
    log.info('Checking adoption of signatures for packages from PyPI.')
    log.info(f'Input file: {input_file_path}')
    log.info(f'Output file: {output_file_path}')
    log.info(f'Download directory: {download_dir}')

    with open(input_file_path, 'r') as input_file, \
            open(output_file_path, 'a') as output_file:

        # Read input file
        for indx, line in enumerate(input_file):

            # Log progress
            if indx % 100 == 0:
                log.info(f'Processing package {indx}.')

            # Parse line
            package = json.loads(line)

            # Add placeholder for signature adoption
            package['signature'] = None

            # Check if the package has a signature
            if package['has_signature']:

                # Create url and download files
                filename = package['filename']
                url = url_construction(digest=package['blake2_256_digest'],
                                       filename=filename)
                subprocess.run(['wget', url], capture_output=True)
                subprocess.run(['wget', url+'.asc'], capture_output=True)

                # Run the gpg verify command
                output = subprocess.run(
                    [
                        "gpg",
                        "--keyserver-options",
                        "auto-key-retrieve",
                        "--keyserver",
                        "keyserver.ubuntu.com",
                        "--verify",
                        "--verbose",
                        f"{filename}.asc",
                        f"{filename}"
                    ],
                    capture_output=True)

                # Add signature adoption to package
                package['signature'] = {
                    'stdout': output.stdout.decode("utf-8"),
                    'stderr': output.stderr.decode("utf-8")
                }

                # Write package to output file
                json.dump(package, output_file, default=str)
                output_file.write('\n')

                # Remove the files
                subprocess.run(['rm', '-r', filename])
                subprocess.run(['rm', '-r', filename+'.asc'])

    log.info('Finished checking adoption of signatures for packages from '
             'PyPI.')

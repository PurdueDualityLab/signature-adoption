#!/usr/bin/env python

'''get_packages.py: This script gets the repositories and associated metadata
for all packages located in the ecosystems database. It then writes the data to
a JSON file.
'''

# Import statements
import psycopg2
import json
import os
import argparse
import logging as log
from datetime import datetime
from util import valid_path_create

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"

# Define global variables
script_start_time = datetime.now()

localhost_password = os.environ.get("PSQL_Password") or ''

db_credentials = {
    "dbname": "packages_production",  # Ecosystems database name
    "user": "postgres",  # Default PostgreSQL user
    "password": localhost_password,  # Password for user
    "host": "localhost",  # Database host
    "port": "5432"  # Default PostgreSQL port
}


# Function to parse arguments
def parse_args():
    ''' This function parses arguments passed to the script.

    returns: args - the arguments passed to the script
    '''
    parser = argparse.ArgumentParser(
        description='Get packages from ecosystems database.'
        'The packages will be written to a Newline Delimited JSON file.')
    parser.add_argument('--output',
                        type=str,
                        default='./data/packages_-eco-.ndjson',
                        help='The path basis to the output files.'
                        'Defaults to ./data/packages_-eco-.ndjson.'
                        'The -eco- will be replaced with the ecosystem name.')
    parser.add_argument('--log',
                        type=str,
                        default='./logs/get_packages.log',
                        help='The path to the log file.'
                        'Defaults to ./logs/get_packages.log.')
    parser.add_argument('--pypi',
                        '-p',
                        action='store_true',
                        help='Flag to get packages from PyPI.')
    parser.add_argument('--docker',
                        '-d',
                        action='store_true',
                        help='Flag to get packages from Docker Hub.')
    parser.add_argument('--npm',
                        '-n',
                        action='store_true',
                        help='Flag to get packages from npm.')
    parser.add_argument('--maven',
                        '-m',
                        action='store_true',
                        help='Flag to get packages from Maven.')
    args = parser.parse_args()

    # Normalize paths
    args.output = valid_path_create(args.output)
    args.log = valid_path_create(args.log)

    return args


# Function to setup the logger
def setup_logger(args):
    ''' This function sets up the logger for the script.
    '''
    # Set up logger
    log_level = log.DEBUG if __debug__ else log.INFO
    log.basicConfig(filename=args.log,
                    filemode='a',
                    level=log_level,
                    format='%(asctime)s|%(levelname)s|%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

    # Log start time
    log.info('Starting get_tags script.')


def log_finish():
    '''
    Script simply logs time of script completion and total time elapsed.
    '''

    # Log end of script
    log.info('Script completed. Total time:'
             f'{datetime.now()-script_start_time}')


# Function to get packages from database
def get_packages(args):

    log.info('Getting packages from database.')

    # Connect to database
    conn = psycopg2.connect(**db_credentials)
    cur_pkgs = conn.cursor()
    cur_vrsns = conn.cursor()

    # Query to get packages
    query_pkgs = '''
        SELECT * FROM packages
        WHERE ecosystem = %s;
    '''

    # Query to get versions
    query_vrsns = '''
        SELECT * FROM versions
        WHERE package_id = %s;
    '''

    # List of ecosystems
    ecosystems = []
    if args.pypi:
        ecosystems.append('pypi')
    if args.docker:
        ecosystems.append('docker')
    if args.npm:
        ecosystems.append('npm')
    if args.maven:
        ecosystems.append('maven')

    # Function to generate output path
    def gen_output_path(output, eco):
        return output.replace('-eco-', eco)

    # Get packages for each ecosystem
    for ecosystem in ecosystems:

        log.info(f'Getting packages for {ecosystem} ecosystem.')

        # Open new file for each ecosystem
        eco_file = gen_output_path(args.output, ecosystem)
        log.info(f'Opening file {eco_file} for writing.')
        with open(eco_file, 'a') as f:

            # Execute query and get first package
            cur_pkgs.execute(query_pkgs, (ecosystem,))
            package = cur_pkgs.fetchone()

            # Get column names
            p_col = [desc[0] for desc in cur_pkgs.description]
            v_col = None

            # Iterate through each package
            while package:

                # Jsonify package
                json_package = dict(zip(p_col, package))

                # Get versions for each package
                cur_vrsns.execute(query_vrsns, (json_package['id'],))
                versions = cur_vrsns.fetchall()

                # Get column names
                if v_col is None:
                    v_col = [desc[0] for desc in cur_vrsns.description]

                # Jsonify versions
                versions = [dict(zip(v_col, version)) for version in versions]

                # Add versions to package
                json_package['versions'] = versions

                # Write package to file
                json.dump(json_package, f, default=str)
                f.write('\n')

                # Get next package
                package = cur_pkgs.fetchone()

    # Close database connection
    conn.close()


# Classic Python main function
def main():
    # Parse arguments
    args = parse_args()

    # Setup logger
    setup_logger(args)

    # Get args packages from database
    get_packages(args)

    # Log finish
    log_finish()


# Classic Python main function
if __name__ == '__main__':
    main()  # Call main function

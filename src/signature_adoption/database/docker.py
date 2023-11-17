#!/usr/bin/env python

'''
database.py This script adds Docker Hub adoption data to the specified
database.
'''

# Imports
import json
import logging as log
import sqlite3

# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'


def database(input_file_path, database_file_path, start, stop):
    '''
    This function adds adoption data from Docker Hub to the database.

    input_file_path: The path to the input file.
    database_file_path: The path to the database file.
    start: The starting line number.
    stop: The ending line number. If -1, then to the end.
    '''

    # Open the input file and connect to the database
    log.info(f'Opening input file {input_file_path} and '
             f'connecting to database {database_file_path}')
    with open(input_file_path, 'r') as input_file, \
            sqlite3.connect(database_file_path) as database:

        # Create the cursor
        cursor = database.cursor()

        # Iterate through the input file
        for indx, line in enumerate(input_file):

            if indx < start:
                continue
            elif indx >= stop and stop != -1:
                break

            # print progress
            if indx % 100 == 0:
                log.info(f'Processing line {indx}')
            else:
                log.debug(f'Processing line {indx}')

            # Parse the line
            package = json.loads(line)

            # Insert the package into the database
            cursor.execute(
                'INSERT INTO packages (name, registry) VALUES (?, ?)',
                (package['name'], 'docker')
            )
            package_id = cursor.lastrowid
            package_signatures = package['signatures']['dct']

            # Iterate through the versions
            for version in package['versions']:

                # Insert the version into the database
                cursor.execute(
                    'INSERT INTO versions (package_id, date, name) '
                    'VALUES (?, ?, ?)',
                    (package_id, version['published_at'], version['number'])
                )
                version_id = cursor.lastrowid

                # Search for signature
                signature = None
                if package_signatures:
                    finder = (s for s in package_signatures[0]['SignedTags']
                              if s['SignedTag'] == version['number'])
                    signature = next(finder, None)

                # Insert the signature into the database
                cursor.execute(
                    'INSERT INTO units (version_id, package_id, unit, '
                    'sig_type, has_sig, sig_raw, sig_status, date) VALUES '
                    '(?, ?, ?, ?, ?, ?, ?, ?)',
                    (
                        version_id,
                        package_id,
                        version['number'],
                        'dct',
                        signature is not None,
                        json.dumps(signature),
                        'GOOD' if signature else 'NONE',
                        version['published_at']
                    )
                )

        # Commit the changes
        log.info('Committing changes to database')
        database.commit()

    # We're done
    log.info('Completed processing input file.')

#!/usr/bin/env python

'''
docker.py This script adds Docker Hub adoption data to the specified database.
'''

# Imports
import json

# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'


def add(package, cursor):
    '''
    This function adds adoption data from a Docker Hub package to the database.

    package: the package to add to the database.
    cursor: the cursor to use to add the package to the database.
    '''

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
            'INSERT INTO units (version_id, package_id, unit, unit_type,'
            'sig_type, has_sig, sig_raw, sig_status, date) VALUES '
            '(?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                version_id,
                package_id,
                version['number'],
                'tag',
                'dct',
                signature is not None,
                json.dumps(signature),
                'GOOD' if signature else 'NO_SIG',
                version['published_at']
            )
        )
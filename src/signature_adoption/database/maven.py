#!/usr/bin/env python

'''
maven.py This script adds Maven Central adoption data to the specified
database.
'''

# Imports
from ..util.signature_parser import parse_pgp

# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'


def add(package, cursor):
    '''
    This function adds adoption data from a Maven Central package to the
    database.

    package: the package to add to the database.
    cursor: the cursor to use to add the package to the database.
    '''

    # Insert the package into the database
    cursor.execute(
        'INSERT INTO packages (name, registry) VALUES (?, ?)',
        (package['name'], 'maven')
    )
    package_id = cursor.lastrowid

    # Iterate through the versions
    for version in package['versions']:

        # Insert the version into the database
        cursor.execute(
            'INSERT INTO versions (package_id, date, name) '
            'VALUES (?, ?, ?)',
            (package_id, version['published_at'], version['number'])
        )
        version_id = cursor.lastrowid

        # Iterate through units
        for file in version['files']:

            cursor.execute(
                'INSERT INTO units (version_id, package_id, unit, unit_type,'
                'sig_type, has_sig, sig_raw, sig_status, date) VALUES '
                '(?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    version_id,
                    package_id,
                    file['name'],
                    'file',
                    'pgp',
                    file['has_signature'],
                    file['stderr'],
                    parse_pgp(file['stderr']),
                    version['published_at']
                )
            )

#!/usr/bin/env python

'''
huggingface.py This script adds Hugging Face adoption data to the specified
database.
'''

# Imports
from ..util.signature_parser import parse_gcs

# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'


def add(package, cursor):
    '''
    This function adds adoption data from a Hugging Face package to the
    database.

    package: the package to add to the database.
    cursor: the cursor to use to add the package to the database.
    '''

    # Insert the package into the database
    cursor.execute(
        'INSERT INTO packages (name, registry) VALUES (?, ?)',
        (package['id'], 'huggingface')
    )
    package_id = cursor.lastrowid

    # Iterate through the versions
    for version in package['commits']:

        # Insert the version into the database
        cursor.execute(
            'INSERT INTO versions (package_id, date, name) '
            'VALUES (?, ?, ?)',
            (package_id, version['time'], version['hexsha'])
        )
        version_id = cursor.lastrowid

        # Insert the signature into the database
        cursor.execute(
            'INSERT INTO units (version_id, package_id, unit, unit_type,'
            'sig_type, has_sig, sig_raw, sig_status, date) VALUES '
            '(?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                version_id,
                package_id,
                version['hexsha'],
                'commit',
                'gcs',
                version['signature']['stderr'] != '',
                version['signature']['stderr'],
                parse_gcs(version['signature']['stderr']),
                version['time']
            )
        )

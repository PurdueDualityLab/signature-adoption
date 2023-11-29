#!/usr/bin/env python

'''
pypi.py This script adds PyPI adoption data to the specified database.
'''

# Imports
from ..util.signature_parser import parse_pgp

# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'


def add(package, cursor):
    '''
    This function adds adoption data from a PyPI package to the database.

    package: the package to add to the database.
    cursor: the cursor to use to add the package to the database.
    '''

    # Insert the package into the database
    cursor.execute(
        'INSERT INTO packages (name, registry) VALUES (?, ?)',
        (package['name'], 'pypi')
    )
    package_id = cursor.lastrowid

    # Iterate through the versions
    for version_name, files in package['versions'].items():

        # Insert the version into the database
        cursor.execute(
            'INSERT INTO versions (package_id, date, name) '
            'VALUES (?, ?, ?)',
            (package_id, list(files.values())[0]['upload_time'], version_name)
        )
        version_id = cursor.lastrowid

        # Iterate through units
        for file in files.values():

            # Get raw signature
            raw = None if file['signature'] is None else \
                    file['signature']['stderr']

            cursor.execute(
                'INSERT INTO units (version_id, package_id, unit, unit_type,'
                'sig_type, has_sig, sig_raw, sig_status, date) VALUES '
                '(?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    version_id,
                    package_id,
                    file['filename'],
                    'file',
                    'pgp',
                    file['has_signature'],
                    raw,
                    parse_pgp(raw),
                    file['upload_time']
                )
            )

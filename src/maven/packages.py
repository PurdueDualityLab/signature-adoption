#!/usr/bin/env python

'''packages.py: This script gets the repositories and associated metadata
for maven central repositories. It then saves the data to a ndjson file.
'''

# Import statements
import json
import os
import logging as log
import psycopg2

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"


# Function to get the repositories and associated metadata
def packages(output_path):
    '''
    This function gets a list of and packages and associated metadata from
    maven central using the ecosystems database.

    output_path: The path to the output file.
    '''

    # Log start of function
    log.info("Getting packages from Maven Central.")

    # Get database password or use default 'postgres'
    localhost_password = os.environ.get("PSQL_Password") or 'postgres'

    # Set database credentials
    db_credentials = {
        "dbname": "packages_production",  # Ecosystems database name
        "user": "postgres",  # Default PostgreSQL user
        "password": localhost_password,  # Password for user
        "host": "localhost",  # Database host
        "port": "5432"  # Default PostgreSQL port
    }

    # Connect to database
    conn = psycopg2.connect(**db_credentials)
    cur_pkgs = conn.cursor()
    cur_vrsns = conn.cursor()

    # Query to get packages
    query_pkgs = '''
        SELECT * FROM packages
        WHERE ecosystem = maven;
    '''

    # Query to get versions
    query_vrsns = '''
        SELECT * FROM versions
        WHERE package_id = %s;
    '''

    # Open file
    log.info(f'Opening file {output_path} for writing.')
    with open(output_path, 'a') as f:

        # Execute query and get first package
        cur_pkgs.execute(query_pkgs)
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

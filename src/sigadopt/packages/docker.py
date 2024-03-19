'''
docker.py: This script gets the repositories and associated metadata from
Docker Hub.
'''

# Import statements
import os
import logging
import psycopg2
from sigadopt.util.database import clean_db


def packages(output_conn, clean=False):
    '''
    This function gets a list of and packages and associated metadata from
    docker hub using the ecosystems database. It writes the data to a database.

    output_conn: A connection to the output database.
    clean: Whether to clear the tables for Docker Hub before adding the new
    data.
    '''

    # Log start of function
    log = logging.getLogger(__name__)
    log.info("Getting packages from Docker Hub.")

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
    input_conn = psycopg2.connect(**db_credentials)
    input_cursor = input_conn.cursor()

    # Query to get packages
    query_pkgs = '''
        SELECT id, name, versions_count, latest_release_published_at,
            first_release_published_at, downloads, downloads_period
        FROM packages
        WHERE registry_id = 28;
    '''

    # Query to get versions
    query_vrsns = '''
        SELECT number, published_at
        FROM versions
        WHERE package_id = %s;
    '''

    # Get packages
    input_cursor.execute(query_pkgs)
    packages = input_cursor.fetchall()

    # Clear the packages table
    if clean:
        log.info('Clearing tables for Docker Hub.')
        clean_db(output_conn, 2)

    # Insert packages into output database
    log.info('Inserting packages into output database.')
    with output_conn:

        # Create cursor
        output_curr = output_conn.cursor()

        # Iterate through packages
        for p in packages:

            # Insert package into output database
            output_curr.execute(
                '''
                    INSERT INTO packages (registry_id, name, versions_count,
                        latest_release_date, first_release_date, downloads,
                        downloads_period)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                    ''',
                (
                    2,      # Docker Hub registry_id
                    p[1],   # Package name
                    p[2],   # Number of versions
                    p[3],   # Latest release date
                    p[4],   # First release date
                    p[5],   # Downloads
                    p[6]    # Downloads period
                )
            )

            # Get package id
            package_id = output_curr.lastrowid

            # Get versions for this package
            input_cursor.execute(query_vrsns, (p[0],))
            versions = input_cursor.fetchall()

            # Insert versions into output database
            output_curr.executemany(
                '''
                    INSERT INTO versions (package_id, name, date)
                    VALUES (?, ?, ?);
                    ''',
                [(package_id, v[0], v[1]) for v in versions]
            )

    # Close database connection
    input_conn.close()

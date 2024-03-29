'''
maven.py: This script gets the repositories and associated metadata from Maven
Central.
'''

# Import statements
import os
import logging
import psycopg2
from sigadopt.util.database import clean_db


def packages(output_conn, clean=False):
    '''
    This function gets a list of and packages and associated metadata from
    maven central using the ecosystems database. It writes the data to a
    database.

    output_conn: A connection to the output database.
    clean: Whether to clear the tables for Maven Central before adding the new
    data.
    '''

    # Log start of function
    log = logging.getLogger(__name__)

    # Get database password or use default 'postgres'
    log.info("Connecting to input database.")
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

    # Get packages
    log.info('Getting packages from Maven Central.')
    input_cursor.execute(
        '''
            SELECT id, name, versions_count, latest_release_published_at,
                first_release_published_at, downloads, downloads_period
            FROM packages
            WHERE registry_id = 22;
        ''')
    packages = input_cursor.fetchall()

    # Clean output database
    if clean:
        log.info('Clearing tables for Maven Central.')
        clean_db(output_conn, 3)

    # Insert packages into output database
    log.info('Inserting packages into output database.')
    with output_conn:

        # Create cursor
        output_curr = output_conn.cursor()

        # Variable to hold package id links
        package_ids = {}

        # Iterate through packages
        for indx, p in enumerate(packages):

            # Insert package into output database
            output_curr.execute(
                '''
                    INSERT INTO packages (registry_id, name, versions_count,
                        latest_release_date, first_release_date, downloads,
                        downloads_period)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                ''',
                (
                    3,      # Maven registry_id
                    p[1],   # Package name
                    p[2],   # Number of versions
                    p[3],   # Latest release date
                    p[4],   # First release date
                    p[5],   # Downloads
                    p[6],   # Downloads period
                )
            )

            # Get package id
            package_ids[p[0]] = output_curr.lastrowid

        # Commit changes
        log.info('Committing packages to output database.')
        output_conn.commit()

        # Get all versions
        log.info('Getting versions from Maven Central.')
        input_cursor.execute('''
            SELECT v.package_id, v.number, v.published_at
            FROM versions v
            JOIN packages p
            ON v.package_id = p.id
            WHERE p.registry_id = 22;
        ''')
        versions = input_cursor.fetchall()

        # Insert versions into output database
        log.info('Inserting versions into output database.')
        output_curr.executemany(
            '''
                INSERT INTO versions (package_id, name, date)
                VALUES (?, ?, ?);
            ''',
            [(package_ids[v[0]], v[1], v[2]) for v in versions]
        )

        # Commit changes
        log.info('Committing versions to output database.')
        output_conn.commit()

    # Close database connection
    input_conn.close()

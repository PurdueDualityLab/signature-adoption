'''
filter.py: This module contains a class to filter packages from different
registries.
'''

# Imports
import logging
import sqlite3
from sigadopt.util.stage import Stage


class Filter(Stage):
    '''
    This class filters the packages from different registries.
    '''

    def __init__(self, args):
        '''
        This function initializes the class.

        args: The arguments passed to the script.
        '''
        self.log = logging.getLogger(__name__)
        self.log.debug('Initializing Filter stage...')
        self.args = args
        self.log.debug(f'{self.args=}')

    def huggingface(self):
        '''
        This function gets the packages from Hugging Face.
        '''
        pass

    def docker(self):
        '''
        This function gets the packages from Docker Hub.
        '''
        pass

    def maven(self):
        '''
        This function gets the packages from Maven.
        '''
        pass

    def pypi(self):
        '''
        This function gets the packages from PyPI.
        '''
        pass

    def ensure_db(self):
        '''
        This function ensures the database is available.

        return: The connection to the database.
        '''

        self.log.info('Ensuring database is available.')

        # Connect to the database
        conn = None
        try:
            conn = sqlite3.connect(self.args.output)
        except sqlite3.Error as e:
            self.log.error(f'Error connecting to the database: {e}')
            exit(-1)

        # Check to see if the database is actually a database

        # Clear existing data if requested
        if self.args.clean:
            self.log.info('Clearing existing data from database.')
            with conn:
                cursor = conn.cursor()
                self.log.debug('Dropping registries table.')
                cursor.execute('DROP TABLE IF EXISTS registries;')
                self.log.debug('Dropping packages table.')
                cursor.execute('DROP TABLE IF EXISTS packages;')
                self.log.debug('Dropping versions table.')
                cursor.execute('DROP TABLE IF EXISTS versions;')
                self.log.debug('Dropping artifacts table.')
                cursor.execute('DROP TABLE IF EXISTS artifacts;')

        # Create registry table
        with conn:
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS registries (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    UNIQUE (name)
                );
                '''
            )
            conn.execute(
                '''
                INSERT OR IGNORE INTO registries (name)
                VALUES ('Hugging Face');
                '''
            )
            conn.execute(
                '''
                INSERT OR IGNORE INTO registries (name)
                VALUES ('Docker Hub');
                '''
            )
            conn.execute(
                '''
                INSERT OR IGNORE INTO registries (name)
                VALUES ('Maven Central');
                '''
            )
            conn.execute(
                '''
                INSERT OR IGNORE INTO registries (name)
                VALUES ('PyPI');
                '''
            )

        # Create package table
        with conn:
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS packages (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    registry_id INTEGER NOT NULL,
                    versions_count INTEGER,
                    latest_release_date TEXT,
                    first_release_date TEXT,
                    downloads INTEGER,
                    downloads_period TEXT,
                    UNIQUE (name, registry_id),
                    FOREIGN KEY (registry_id) REFERENCES registries (id)
                );
                '''
            )

        # Create version table
        with conn:
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS versions (
                    id INTEGER PRIMARY KEY,
                    package_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    date TEXT,
                    UNIQUE (package_id, name)
                    FOREIGN KEY (package_id) REFERENCES packages (id)
                );
                '''
            )

        # Create artifact table
        with conn:
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS artifacts (
                    id INTEGER PRIMARY KEY,
                    version_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    has_sig INTEGER NOT NULL,
                    digest TEXT,
                    date TEXT,
                    UNIQUE (version_id, name),
                    FOREIGN KEY (version_id) REFERENCES versions (id)
                );
                '''
            )

        # Return the connection
        self.log.debug('Database is available.')
        return conn

    def run(self):
        '''
        This function runs the stage.
        '''
        self.log.debug('Running Packages stage.')

        # Connect to the database
        self.conn = self.ensure_db()

        # Call the appropriate function this is set in the subparser defined
        # in the local __init__.py
        self.args.reg_func(self)

        # Close the database
        self.conn.close()
        self.log.debug('Closed database.')

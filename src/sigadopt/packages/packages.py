'''
packages.py: This module contains a class to get packages from different
registries.
'''

# Imports
import logging
import sqlite3
from sigadopt.util.stage import Stage
from sigadopt.packages.huggingface import packages as huggingface_packages
from sigadopt.packages.docker import packages as docker_packages
from sigadopt.packages.maven import packages as maven_packages
from sigadopt.packages.pypi import packages as pypi_packages


class Packages(Stage):
    '''
    This class gets the packages from different registries.
    '''

    def __init__(self, args):
        '''
        This function initializes the class.

        args: The arguments passed to the script.
        '''
        self.log = logging.getLogger(__name__)
        self.log.debug('Initializing Packages stage...')
        self.args = args
        self.log.debug(f'{self.args=}')

    def huggingface(self):
        '''
        This function gets the packages from Hugging Face.
        '''
        huggingface_packages(
            output_conn=self.conn,
            token_path=self.args.token_path,
            token=self.args.token,
            clean=self.args.clean
        )

    def docker(self):
        '''
        This function gets the packages from Docker Hub.
        '''
        docker_packages(
            output_conn=self.conn,
            clean=self.args.clean
        )

    def maven(self):
        '''
        This function gets the packages from Maven.
        '''
        maven_packages(
            output_conn=self.conn,
            clean=self.args.clean
        )

    def pypi(self):
        '''
        This function gets the packages from PyPI.
        '''
        pypi_packages(
            output_conn=self.conn,
            auth_path=self.args.auth_path,
            clean=self.args.clean
        )

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

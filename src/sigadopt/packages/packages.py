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
        if self.args.token is None:
            huggingface_packages(
                output_path=self.args.output,
                token_path=self.args.token_path
            )
        else:
            huggingface_packages(
                output_path=self.args.output,
                token=self.args.token
            )

    def docker(self):
        '''
        This function gets the packages from Docker Hub.
        '''
        docker_packages(output=self.args.output)

    def maven(self):
        '''
        This function gets the packages from Maven.
        '''
        maven_packages(output_path=self.args.output)

    def pypi(self):
        '''
        This function gets the packages from PyPI.
        '''
        pypi_packages(output_path=self.args.output,
                      auth_path=self.args.auth_path)

    def ensure_db(self):
        '''
        This function ensures the database is available.

        return: The connection to the database.
        '''

        # Connect to the database
        conn = None
        try:
            conn = sqlite3.connect(self.args.output)
        except sqlite3.Error as e:
            self.log.error(f'Error connecting to the database: {e}')
            exit(-1)

        # Clear existing data if requested
        if self.args.clean:
            self.log.info('Clearing existing data from database.')
            with conn:
                cursor = conn.cursor()
                cursor.execute('DROP TABLE IF EXISTS packages;')
                cursor.execute('DROP TABLE IF EXISTS versions;')

        # Create package table
        with conn:
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS packages (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    registry TEXT NOT NULL,
                    UNIQUE (name, registry)
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
                    date TEXT,
                    name TEXT NOT NULL,
                    UNIQUE (package_id, name)
                    FOREIGN KEY (package_id) REFERENCES packages (id)
                );
                '''
            )

        # Return the connection
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

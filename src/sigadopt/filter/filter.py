'''
filter.py: This module contains a class to filter packages from different
registries.
'''

# Imports
import logging
import sqlite3
from sigadopt.util.stage import Stage
from sigadopt.filter.huggingface import filter as huggingface_filter
from sigadopt.filter.docker import filter as docker_filter
from sigadopt.filter.maven import filter as maven_filter
from sigadopt.filter.pypi import filter as pypi_filter


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

    def copy_db(self, input_conn, output_path, registry):
        '''
        This function copies the input database to the output database for the
        selected registry.

        input_conn: The input database connection.
        output_path: The path to the output database.
        registry: The registry number.
        '''

        self.log.debug(f'Copying database for registry: {registry}.')


        # Turn output_path into a string
        output_path = str(output_path)

        with input_conn:

            # Create input/output cursor
            input_cursor = input_conn.cursor()

            # Attach the output databse
            input_cursor.execute(f'ATTACH DATABASE "{output_path}" AS output')

            # Copy the packages from the input database to the output database
            input_cursor.execute(
                '''
                    INSERT INTO output.packages
                    SELECT * FROM packages
                    WHERE registry = ?
                ''',
                (registry,)
            )

            # Commit the changes
            input_conn.commit()

            # Copy the versions from the input database to the output database
            input_cursor.execute(
                '''
                    INSERT INTO output.versions
                    SELECT v.* FROM versions v
                    JOIN packages p ON v.package_id = p.id
                    WHERE p.registry = ?
                ''',
                (registry,)
            )

            # Commit the changes
            input_conn.commit()

            # Copy the artifacts from the input database to the output database
            input_cursor.execute(
                '''
                    INSERT INTO output.artifacts
                    SELECT a.* FROM artifacts a
                    JOIN versions v ON a.version_id = v.id
                    JOIN packages p ON v.package_id = p.id
                    WHERE p.registry = ?
                ''',
                (registry,)
            )

            # Commit the changes
            input_conn.commit()

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

    def ensure_db(self, db):
        '''
        This function ensures the database is available.

        db: The path to the database.

        return: The connection to the database.
        '''

        self.log.info('Ensuring database is available.')

        # Connect to the database
        conn = None
        try:
            conn = sqlite3.connect(db)
        except sqlite3.Error as e:
            self.log.error(f'Error connecting to the database: {e}')
            exit(-1)

        # Check to see if the database is available
        if conn is None:
            self.log.error(f'Error connecting to the database: {db}')
            exit(-1)

        # Return the connection
        self.log.debug(f'Connected to database: {db}')
        return conn

    def run(self):
        '''
        This function runs the stage.
        '''
        self.log.debug('Running Packages stage.')

        # Ensure the input/output database is available
        self.input_conn = self.ensure_db(self.args.input)
        self.output_conn = self.ensure_db(self.args.output)

        # Call the appropriate function this is set in the subparser defined
        # in the local __init__.py
        self.args.reg_func(self)

        # Close the databases
        self.input_conn.close()
        self.output_conn.close()
        self.log.debug('Closed databases.')

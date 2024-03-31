'''
filter.py: This module contains a class to filter packages from different
registries.
'''

# Imports
import logging
from sigadopt.util.database import connect_db, init_db
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

    def huggingface(self):
        '''
        This function gets the packages from Hugging Face.
        '''
        huggingface_filter(
            input_conn=self.input_conn,
            output_conn=self.output_conn,
            min_date=self.args.min_date,
            max_date=self.args.max_date,
            min_versions=self.args.min_versions,
            max_versions=self.args.max_versions,
            random_select=self.args.random_select
        )

    def docker(self):
        '''
        This function gets the packages from Docker Hub.
        '''
        docker_filter(
            input_conn=self.input_conn,
            output_conn=self.output_conn,
            min_date=self.args.min_date,
            max_date=self.args.max_date,
            min_versions=self.args.min_versions,
            max_versions=self.args.max_versions,
            random_select=self.args.random_select
        )

    def maven(self):
        '''
        This function gets the packages from Maven.
        '''
        maven_filter(
            input_conn=self.input_conn,
            output_conn=self.output_conn,
            min_date=self.args.min_date,
            max_date=self.args.max_date,
            min_versions=self.args.min_versions,
            max_versions=self.args.max_versions,
            random_select=self.args.random_select
        )

    def pypi(self):
        '''
        This function gets the packages from PyPI.
        '''
        pypi_filter(
            input_conn=self.input_conn,
            output_conn=self.output_conn,
            min_date=self.args.min_date,
            max_date=self.args.max_date,
            min_versions=self.args.min_versions,
            max_versions=self.args.max_versions,
            random_select=self.args.random_select
        )

    def all(self):
        '''
        This function gets the packages from all registries.
        '''
        self.huggingface()
        self.docker()
        self.maven()
        self.pypi()

    def run(self):
        '''
        This function runs the stage.
        '''
        self.log.info('Running Filter stage.')

        # Ensure the input/output database is available
        self.input_conn = connect_db(self.args.input)
        self.output_conn = connect_db(self.args.output)
        init_db(self.output_conn)

        # Call the appropriate function this is set in the subparser defined
        # in the local __init__.py
        self.args.reg_func(self)

        # Close the databases
        self.log.info('Filter stage complete. Closing databases.')
        self.input_conn.close()
        self.output_conn.close()

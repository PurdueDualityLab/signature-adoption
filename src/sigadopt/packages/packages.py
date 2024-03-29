'''
packages.py: This module contains a class to get packages from different
registries.
'''

# Imports
import logging
from sigadopt.util.database import connect_db, init_db
from sigadopt.util.stage import Stage
from sigadopt.packages.huggingface import packages as huggingface_packages
from sigadopt.packages.docker import packages as docker_packages
from sigadopt.packages.maven import packages as maven_packages
from sigadopt.packages.pypi import packages as pypi_packages
from sigadopt.packages.hfcommits import packages as hfcommits_packages


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
            output_conn=self.output_conn,
            token_path=self.args.token_path,
            token=self.args.token,
            clean=self.args.clean
        )

    def hfcommits(self):
        '''
        This function updates the database with the commits from Hugging Face.
        '''
        hfcommits_packages(
            output_conn=self.output_conn,
            token_path=self.args.token_path,
            token=self.args.token,
            clean=self.args.clean,
        )

    def docker(self):
        '''
        This function gets the packages from Docker Hub.
        '''
        docker_packages(
            output_conn=self.output_conn,
            clean=self.args.clean
        )

    def maven(self):
        '''
        This function gets the packages from Maven.
        '''
        maven_packages(
            output_conn=self.output_conn,
            clean=self.args.clean
        )

    def pypi(self):
        '''
        This function gets the packages from PyPI.
        '''
        pypi_packages(
            output_conn=self.output_conn,
            auth_path=self.args.auth_path,
            clean=self.args.clean
        )

    def run(self):
        '''
        This function runs the stage.
        '''
        self.log.info('Running Packages stage.')

        # Connect to the database and initialize it
        self.output_conn = connect_db(self.args.output)
        init_db(self.output_conn)

        # Call the appropriate function this is set in the subparser defined
        # in the local __init__.py
        self.args.reg_func(self)

        # Close the database
        self.log.info('Packages stage complete. Closing output database.')
        self.output_conn.close()

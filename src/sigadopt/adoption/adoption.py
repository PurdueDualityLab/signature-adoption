'''
adoption.py: This module contains a class to check sig adoption from different
registries.
'''

# Imports
import logging
from sigadopt.util.database import connect_db, init_db
from sigadopt.util.stage import Stage
from sigadopt.adoption.huggingface import adoption as huggingface_adoption
from sigadopt.adoption.docker import adoption as docker_adoption
from sigadopt.adoption.maven import adoption as maven_adoption
from sigadopt.adoption.pypi import adoption as pypi_adoption


class Adoption(Stage):
    '''
    This class checks signature adoption for packages in each registry.
    '''

    def __init__(self, args):
        '''
        This function initializes the class.

        args: The arguments passed to the script.
        '''
        self.log = logging.getLogger(__name__)
        self.log.debug('Initializing Adoption stage...')
        self.args = args
        self.log.debug(f'{self.args=}')

    def huggingface(self):
        '''
        This function gets the packages from Hugging Face.
        '''
        huggingface_adoption(
            input_conn=self.input_conn,
            output_conn=self.output_conn,
        )

    def docker(self):
        '''
        This function gets the packages from Docker Hub.
        '''
        docker_adoption(
            input_conn=self.input_conn,
            output_conn=self.output_conn,
        )

    def maven(self):
        '''
        This function gets the packages from Maven.
        '''
        maven_adoption(
            input_conn=self.input_conn,
            output_conn=self.output_conn,
        )

    def pypi(self):
        '''
        This function gets the packages from PyPI.
        '''
        pypi_adoption(
            input_conn=self.input_conn,
            output_conn=self.output_conn,
        )

    def run(self):
        '''
        This function runs the stage.
        '''
        self.log.info('Running Adoption stage.')

        # Ensure the input/output database is available
        self.input_conn = connect_db(self.args.input)
        self.output_conn = connect_db(self.args.output)
        init_db(self.output_conn)

        # Call the appropriate function this is set in the subparser defined
        # in the local __init__.py
        self.args.reg_func(self)

        # Close the databases
        self.log.info('Adoption stage complete. Closing databases.')
        self.input_conn.close()
        self.output_conn.close()


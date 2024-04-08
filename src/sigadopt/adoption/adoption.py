'''
adoption.py: This module contains a class to check sig adoption from different
registries.
'''

# Imports
import logging
from sigadopt.util.database import connect_db, init_db, clean_db, Registry, \
    CleanLevel
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

        version: The version to get the package for.
        '''
        pass

    def docker(self):
        '''
        This function gets the packages from Docker Hub.

        version: The version to get the package for.
        '''
        pass

    def maven(self):
        '''
        This function gets the packages from Maven.

        version: The version to get the package for.
        '''
        maven_adoption(
            self.database,
            self.args.download_dir,
            self.args.start,
            self.args.stop
        )

    def pypi(self):
        '''
        This function gets the packages from PyPI.

        version: The version to get the package for.
        '''
        pypi_adoption(
            self.database,
            self.args.download_dir,
            self.args.start,
            self.args.stop
        )

    def run(self):
        '''
        This function runs the stage.
        '''
        self.log.info('Running Adoption stage.')

        # Ensure the input/output database is available
        self.database = connect_db(self.args.database)
        init_db(self.database)

        # If cleaning the database, do so
        if self.args.clean:
            if self.args.registry_id is not Registry.PYPI:
                clean_db(
                    self.database,
                    self.args.registry_id,
                    CleanLevel.ARTIFACTS
                )
            else:
                clean_db(
                    self.database,
                    self.args.registry_id,
                    CleanLevel.SIGNATURES
                )

        # Get the registry function
        reg_func = {
            Registry.HUGGINGFACE: self.huggingface,
            Registry.DOCKER: self.docker,
            Registry.MAVEN: self.maven,
            Registry.PYPI: self.pypi,
        }
        reg_func = reg_func[self.args.registry_id]
        reg_func()

        # Close the databases
        self.log.info('Adoption stage complete. Closing database.')
        self.database.close()

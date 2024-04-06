'''
adoption.py: This module contains a class to check sig adoption from different
registries.
'''

# Imports
import logging
from sigadopt.util.database import connect_db, init_db, Registry
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

    def huggingface(self, version):
        '''
        This function gets the packages from Hugging Face.

        version: The version to get the package for.
        '''
        pass

    def docker(self, version):
        '''
        This function gets the packages from Docker Hub.

        version: The version to get the package for.
        '''
        pass

    def maven(self, version):
        '''
        This function gets the packages from Maven.

        version: The version to get the package for.
        '''
        pass

    def pypi(self, version):
        '''
        This function gets the packages from PyPI.

        version: The version to get the package for.
        '''
        pass

    def get_versions(self):
        '''
        This function gets a list of all versions in the start stop range for
        the selected registry.

        returns: A list of all versions in the start stop range in the selected
        registry.
        '''

        # Initialize the versions list
        versions = None

        # Create the cursor
        with self.database:
            curr = self.database.cursor()

            # Execute the query
            curr.execute(
                '''
                    SELECT p.id, p.name, v.id, v.name
                    FROM packages p
                    JOIN versions v ON p.id = v.package_id
                    WHERE registry_id = ?;
                ''',
                (self.args.registry_id,)
            )

            # Fetch the data
            versions = curr.fetchall()
            self.log.debug(f'Found {len(versions)} versions for the registry.')

        # Subset versions in the start stop range
        versions = versions[self.args.start:self.args.stop]

        # Return the versions
        return versions

    def run(self):
        '''
        This function runs the stage.
        '''
        self.log.info('Running Adoption stage.')

        # Ensure the input/output database is available
        self.database = connect_db(self.args.database)
        init_db(self.database)

        # Get a list of all versions for the registry
        self.log.info('Getting list of all versions for the registry.')
        versions = self.get_versions()
        num_selected = len(versions)
        self.log.info(f'Selected {num_selected} versions for the registry.')

        # Get the registry function
        reg_func = {
            Registry.HUGGINGFACE: self.huggingface,
            Registry.DOCKER: self.docker,
            Registry.MAVEN: self.maven,
            Registry.PYPI: self.pypi,
        }
        reg_func = reg_func[self.args.registry_id]

        # Loop through the versions
        for indx, version in enumerate(versions):
            if indx % 100 == 0:
                self.log.debug(f'Processing version {indx} of {num_selected}.')
            reg_func(version)

        # Close the databases
        self.log.info('Adoption stage complete. Closing databases.')
        self.input_conn.close()
        self.output_conn.close()

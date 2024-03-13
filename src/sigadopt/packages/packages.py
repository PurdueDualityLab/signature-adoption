'''
packages.py: This module contains a class to get packages from different
registries.
'''

# Imports
import logging
from sigadopt.util.stage import Stage


class Packages(Stage):
    '''
    This class gets the packages from different registries.
    '''

    def __init__(self, args):
        '''
        This function initializes the class.

        args: The arguments passed to the script.
        '''
        self.args = args
        self.log = logging.getLogger(__name__)
        self.log.debug('Initializing Packages stage...')

    def huggingface(self):
        '''
        This function gets the packages from Hugging Face.
        '''
        print('Hugging Face')

    def docker(self):
        '''
        This function gets the packages from Docker Hub.
        '''
        print('Docker Hub')

    def maven(self):
        '''
        This function gets the packages from Maven.
        '''
        print('Maven')

    def pypi(self):
        '''
        This function gets the packages from PyPI.
        '''
        print('PyPI')

    def run(self):
        '''
        This function runs the stage.
        '''
        self.log.debug('Running Packages stage...')

        # Call the appropriate function this is set in the subparser defined
        # in the local __init__.py
        self.args.reg_func(self)

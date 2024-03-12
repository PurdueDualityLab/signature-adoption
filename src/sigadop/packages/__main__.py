#!/usr/bin/env python

'''
__main__.py: This script gets the repositories and associated metadata
for all registries supported by this project.
'''

# Import statements
import argparse
import logging as log
from datetime import datetime
from pathlib import Path
from ..util.files import valid_path_create, gen_path, valid_path
from .huggingface import packages as huggingface_packages
from .docker import packages as docker_packages
from .maven import packages as maven_packages
from .pypi import packages as pypi_packages

# authorship information
__author__ = "Taylor R. Schorlemmer"
__email__ = "tschorle@purdue.edu"


class Packages:

    # Define global variables
    script_start_time = datetime.now()

    def huggingface(self, args):
        '''
        This function gets the packages from Hugging Face.

        args: the arguments passed to the script
        '''

        # Call the function, but check if the token is passed as an argument or
        # read from a file
        if args.token is None:
            huggingface_packages(
                output_path=args.output_path,
                token_path=valid_path(
                    path=args.token_path
                )
            )
        else:
            huggingface_packages(
                output_path=args.output_path,
                token=args.token
            )

    def docker(self, args):
        '''
        This function gets the packages from Docker Hub.

        args: the arguments passed to the script
        '''

        # Call the function
        docker_packages(output_path=args.output_path)

    def maven(self, args):
        '''
        This function gets the packages from Maven.

        args: the arguments passed to the script
        '''

        # Call the function
        maven_packages(output_path=args.output_path)

    def pypi(self, args):
        '''
        This function gets the packages from PyPI.

        args: the arguments passed to the script
        '''

        # Check the authentication path
        auth_path = args.auth_path
        if auth_path is not None:
            auth_path = valid_path(path=auth_path)

        # Call the function
        pypi_packages(output_path=args.output_path,
                      auth_path=auth_path)

    # Function to parse arguments

    def parse_args(self):
        ''' This function parses arguments passed to the script.

        returns: args - the arguments passed to the script
        '''

        # Top level parser
        parser = argparse.ArgumentParser(
            description='Get a list of packages and metadata from a specified '
            'registry. The output is a newline delimited JSON file with each '
            'line being a JSON object containing the metadata for a package.',
            prog=__name__,
        )

        # global arguments
        parser.add_argument('--out-path',
                            dest='output_path',
                            metavar='PATH',
                            type=str,
                            default='./data/-reg-/packages.ndjson',
                            help='The path to the output file. '
                            'Defaults to ./data/-reg-/packages.ndjson. '
                            'The -reg- will be replaced with the ecosystem name.')
        parser.add_argument('--log',
                            '-l',
                            dest='log',
                            metavar='PATH',
                            type=Path,
                            default=None,
                            help='The path to the log file. If not provided, the '
                            'log will be written to stderr. ')
        parser.add_argument('--log-level',
                            dest='log_level',
                            metavar='LEVEL',
                            type=str,
                            default='WARNING',
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                            help='Set the log level. Defaults to WARNING. This '
                            'will print to the log destination.')

        # Create subparsers
        subparsers = parser.add_subparsers(
            title='registry',
            description='The registry to get packages from.',
            help='The registry to get a list of packages from.',
            dest='registry',
            required=True)

        # Hugging Face subparser
        huggingface_parser = subparsers.add_parser(
            'huggingface',
            help='Get packages from Hugging Face.')
        huggingface_parser.set_defaults(func=Packages.huggingface)
        hf_token_group = huggingface_parser.add_argument_group(
            'HuggingFace Tokens',
            'Pass the Hugging Face API token. This can be passed as an argument '
            'or read from a file. Only one of these options can be used. The '
            'default is to read from a file.')
        hf_me_group = hf_token_group.add_mutually_exclusive_group()
        hf_me_group.add_argument('--token',
                                 dest='token',
                                 metavar='TOKEN',
                                 type=str,
                                 default=None,
                                 help='The Hugging Face API token.')
        hf_me_group.add_argument('--token-path',
                                 dest='token_path',
                                 metavar='FILE',
                                 type=str,
                                 default='./hftoken.txt',
                                 help='The path to the file containing the '
                                 'Hugging Face API token. '
                                 'Defaults to ./hftoken.txt.')

        # Docker subparser
        docker_parser = subparsers.add_parser(
            'docker',
            help='Get packages from Docker Hub.')
        docker_parser.set_defaults(func=Packages.docker)

        # Maven subparser
        maven_parser = subparsers.add_parser(
            'maven',
            help='Get packages from Maven.')
        maven_parser.set_defaults(func=Packages.maven)

        # PyPI subparser
        pypi_parser = subparsers.add_parser(
            'pypi',
            help='Get packages from PyPI.')
        pypi_parser.set_defaults(func=Packages.pypi)
        pypi_parser.add_argument('--auth-path',
                                 dest='auth_path',
                                 metavar='FILE',
                                 type=str,
                                 default=None,
                                 help='The path to the file containing the Google '
                                 'BigQuery authentication information. '
                                 'Defaults to None and assumes that the '
                                 'authentication information is in the '
                                 'GOOGLE_APPLICATION_CREDENTIALS environment '
                                 'variable.')

        args = parser.parse_args()

        # Normalize paths
        args.log = valid_path_create(args.log)
        args.output_path = gen_path(
            directory='',
            file=args.output_path,
            ecosystem=args.registry)

        return args

    def setup_logger(self, args):
        ''' This function sets up the logger for the script.
        '''

        handler = {
            'level': 'DEBUG' if args.verbose else 'WARNING',
            'class': 'logging.StreamHandler' if not args.log
            else 'logging.FileHandler',
            'filename': args.log,
            'mode': 'a',
            'formatter': 'standard',
        }

        log_config = {
            'version': 1,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s|%(levelname)s|%(name)s|%(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S',
                },
            },
            'handlers': {
                'default': handler,
            },
        }

        # Set up logger
        log_level = log.DEBUG if __debug__ else log.INFO
        log.basicConfig(
            filename=args.log,
            filemode='a',
            level=log_level,
            format=f'%(asctime)s|%(levelname)s|{args.registry}|%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Log start time
        log.info('Starting packages script.')

        # Log arguments
        log.info(f'Arguments: {args}')

    def log_finish(self):
        '''
        Script simply logs time of script completion and total time elapsed.
        '''

        # Log end of script
        log.info('Script completed. Total time:'
                 f'{datetime.now()-self.script_start_time}')

    def __init__(self):
        '''
        Initializes the class.
        '''
        print(f'{__name__=}')
        print(f'{__package__=}')
        print(f'{__file__=}')
        print(f'{__doc__=}')
        print(f'{self.__class__=}')

        # Parse arguments
        self.args = self.parse_args()

        # Setup logger
        self.setup_logger(self.args)

    def start(self):
        '''
        This function starts the collection of packages.
        '''
        # Call function
        self.args.func(self.args)

        # Log finish
        self.log_finish()


# Classic Python main function
if __name__ == '__main__':
    Packages().start()  # Call main function

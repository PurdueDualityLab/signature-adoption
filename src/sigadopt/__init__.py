
'''
__init__.py: This is the __init__ file for the top level sigadopt package.
'''

# Imports
import logging.config
import argparse
from pathlib import Path
from sigadopt.packages import add_arguments as packages_add_arguments

# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'

# Setup logging
logging.config.dictConfig(
    {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s|%(levelname)s|%(name)s|%(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'default': {
                'level': 'WARNING',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': 'DEBUG',
                'propagate': True
            },
        }
    }
)


# Create top level parser
parser = argparse.ArgumentParser(
    description='Get a list of packages and metadata from a specified ',
)

# global arguments
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
                    default=None,
                    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                    help='Set the log level. Defaults to WARNING. This '
                    'will print to the log destination.')


# Create subparsers
pipeline_stage_parser = parser.add_subparsers(
    title='subcommands',
    description='valid subcommands',
    help='additional help'
)
packages_add_arguments(pipeline_stage_parser)
filter_parser = pipeline_stage_parser.add_parser(
    'filter',
    help='Filter packages from different registries.'
)
adoption_parser = pipeline_stage_parser.add_parser(
    'adoption',
    help='Check the adoption of signatures for different registries.'
)

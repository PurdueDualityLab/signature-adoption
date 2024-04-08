
'''
__init__.py: This is the __init__ file for the top level sigadopt package.
'''

# Imports
import logging.config
import argparse
from sigadopt.util.files import path_create
from sigadopt.packages import add_arguments as packages_add_arguments
from sigadopt.filter import add_arguments as filter_add_arguments
from sigadopt.adoption import add_arguments as adoption_add_arguments

# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'


# Setup logging
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s|%(levelname)s|%(name)s|%(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "stderr": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler"
            },
        },
        "loggers": {
            "": {
                "handlers": [
                    "stderr",
                ],
                "level": "DEBUG",
                "propagate": True
            },
        }
    }
)


# Create top level parser
parser = argparse.ArgumentParser(
    description='This script checks the adoption of signatures for different '
    'registries. This occurs in multiple pipeline stages. Please use the '
    'appropriate subcommand for the stage you want to run. These stages '
    'include: 1) getting a list of packages, 2) applying a pre-filter to the '
    'list of packages, 3) checking adoption of signatures for the list of '
    'packages, 4) applying a post-filter to the list of packages, and 5) '
    'running a final analysis on the list of packages.'
)

# global arguments
parser.add_argument('--log',
                    '-l',
                    dest='log',
                    metavar='PATH',
                    type=path_create,
                    default=None,
                    help='The path to the log file. If not provided, the '
                    'log will be written to stderr. ')
parser.add_argument('--log-level',
                    dest='log_level',
                    metavar='LEVEL',
                    type=str.upper,
                    default=None,
                    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                    help='Set the log level. Defaults to WARNING. This '
                    'will print to the log destination.')


# Create subparsers
pipeline_stage_parser = parser.add_subparsers(
    title='pipeline-stage',
    dest='pipeline_stage',
    description='which stage of the pipeline to run',
    help='additional help',
    metavar='STAGE',
    # required=True,
)
packages_add_arguments(pipeline_stage_parser)
filter_add_arguments(pipeline_stage_parser)
adoption_add_arguments(pipeline_stage_parser)

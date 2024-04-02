'''
__init__.py: This is the __init__ file for the adoption subpackage.
'''

# Imports
from datetime import datetime
from sigadopt.adoption.adoption import Adoption
from sigadopt.util.files import path_exists, path_create


def add_hf_args(registry_parser):
    '''
    This function creates and adds arguments to the Hugging Face subparser.

    registry_parser: The subparser for the stage.
    '''

    # Hugging Face subparser
    huggingface_parser = registry_parser.add_parser(
        'huggingface',
        help='Check signature adoption on Hugging Face.'
    )

    # Set the function to use in the stage class
    huggingface_parser.set_defaults(reg_func=Adoption.huggingface)

    # Add Hugging Face specific arguments


def add_pypi_args(registry_parser):
    '''
    This function creates and adds arguments to the PyPI subparser.

    registry_parser: The subparser for the stage.
    '''

    # PyPI subparser
    pypi_parser = registry_parser.add_parser(
        'pypi',
        help='Check signature adoption on PyPI.'
    )

    # Set the function to use in the stage class
    pypi_parser.set_defaults(reg_func=Adoption.pypi)

    # Add PyPI specific arguments


def add_docker_args(registry_parser):
    '''
    This function creates and adds arguments to the Docker subparser.

    registry_parser: The subparser for the stage.
    '''

    # Docker subparser
    docker_parser = registry_parser.add_parser(
        'docker',
        help='Check signature adoption on Docker Hub.'
    )

    # Set the function to use in the stage class
    docker_parser.set_defaults(reg_func=Adoption.docker)

    # Add PyPI specific arguments


def add_maven_args(registry_parser):
    '''
    This function creates and adds arguments to the Maven subparser.

    registry_parser: The subparser for the stage.
    '''

    # Maven subparser
    maven_parser = registry_parser.add_parser(
        'maven',
        help='Check signature adoption on Maven.'
    )

    # Set the function to use in the stage class
    maven_parser.set_defaults(reg_func=Adoption.maven)

    # Add Maven specific arguments


def add_arguments(top_parser):
    '''
    This function adds arguments to the top level parser.

    top_parser: The top level parser for the script.
    '''

    # Create a parser for the packages stage
    parser = top_parser.add_parser(
        'adoption',
        help='Check signature adoption on different registries.'
    )

    # Add stage specific arguments
    parser.add_argument(
        'input',
        metavar='INPUT_DB',
        type=path_exists,
        help='The path to the input databse file.'
    )
    parser.add_argument(
        'output',
        metavar='OUTPUT_DB',
        type=path_create,
        help='The path to the output database file. This can be set to the '
        'input database file to overwrite the input database file. Clears the '
        'output database file for the selected registry before copying.'
    )
    # Give the parser a stage class to use
    parser.set_defaults(stage=Adoption)

    # Create subparsers for each registry
    registry_parser = parser.add_subparsers(
        title='registry',
        description='The registry to check adoption on.',
        help='The registry to check adoption on.',
        dest='registry',
        metavar='REGISTRY',
        required=True
    )

    # Add subparser specific arguments
    add_hf_args(registry_parser)
    add_pypi_args(registry_parser)
    add_docker_args(registry_parser)
    add_maven_args(registry_parser)

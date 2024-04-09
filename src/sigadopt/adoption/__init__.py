'''
__init__.py: This is the __init__ file for the adoption subpackage.
'''

# Imports
from sigadopt.adoption.adoption import Adoption
from sigadopt.util.files import path_exists, path_create, dir_create
from sigadopt.util.database import Registry


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
    huggingface_parser.set_defaults(registry_id=Registry.HUGGINGFACE)

    # Add Hugging Face specific arguments
    # huggingface_parser.add_argument(
    #     'download_dir',
    #     metavar='DIR',
    #     type=dir_create,
    #     help='The path to the directory to download files to.'
    # )


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
    pypi_parser.set_defaults(registry_id=Registry.PYPI)

    # Add PyPI specific arguments
    pypi_parser.add_argument(
        'download_dir',
        metavar='DIR',
        type=dir_create,
        help='The path to the directory to download files to.'
    )


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
    docker_parser.set_defaults(registry_id=Registry.DOCKER)

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
    maven_parser.set_defaults(registry_id=Registry.MAVEN)

    # Add Maven specific arguments
    maven_parser.add_argument(
        'download_dir',
        metavar='DIR',
        type=dir_create,
        help='The path to the directory to download files to.'
    )


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
        'database',
        metavar='DATABASE',
        type=path_exists,
        help='The path to the database file. Will modify this file.'
    )
    parser.add_argument(
        '--start',
        '-s',
        type=int,
        default=0,
        help='The start index for the packages to check. Defaults to 0. '
        'Inclusive.'
    )
    parser.add_argument(
        '--stop',
        '-e',
        type=int,
        default=-1,
        help='The stop index for the packages to check. If set to -1, goes to '
        'the end of the file. Defaults to -1. Exclusive.'
    )
    parser.add_argument(
        '--clean',
        '-c',
        action='store_true',
        help='Clean the adoption data before starting. Defaults to False.'
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
        # required=True
    )

    # Add subparser specific arguments
    add_hf_args(registry_parser)
    add_pypi_args(registry_parser)
    add_docker_args(registry_parser)
    add_maven_args(registry_parser)

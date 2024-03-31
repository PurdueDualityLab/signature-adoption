'''
__init__.py: This is the __init__ file for the filter subpackage.
'''

# Imports
from datetime import datetime
from sigadopt.filter.filter import Filter
from sigadopt.util.files import path_exists, path_create


def add_hf_args(registry_parser):
    '''
    This function creates and adds arguments to the Hugging Face subparser.

    registry_parser: The subparser for the stage.
    '''

    # Hugging Face subparser
    huggingface_parser = registry_parser.add_parser(
        'huggingface',
        help='Filter packages from Hugging Face.'
    )

    # Set the function to use in the stage class
    huggingface_parser.set_defaults(reg_func=Filter.huggingface)

    # Add Hugging Face specific arguments


def add_pypi_args(registry_parser):
    '''
    This function creates and adds arguments to the PyPI subparser.

    registry_parser: The subparser for the stage.
    '''

    # PyPI subparser
    pypi_parser = registry_parser.add_parser(
        'pypi',
        help='Filter packages from PyPI.'
    )

    # Set the function to use in the stage class
    pypi_parser.set_defaults(reg_func=Filter.pypi)

    # Add PyPI specific arguments


def add_docker_args(registry_parser):
    '''
    This function creates and adds arguments to the Docker subparser.

    registry_parser: The subparser for the stage.
    '''

    # Docker subparser
    docker_parser = registry_parser.add_parser(
        'docker',
        help='Filter packages from Docker Hub.'
    )

    # Set the function to use in the stage class
    docker_parser.set_defaults(reg_func=Filter.docker)

    # Add PyPI specific arguments


def add_maven_args(registry_parser):
    '''
    This function creates and adds arguments to the Maven subparser.

    registry_parser: The subparser for the stage.
    '''

    # Maven subparser
    maven_parser = registry_parser.add_parser(
        'maven',
        help='Filter packages from Maven.'
    )

    # Set the function to use in the stage class
    maven_parser.set_defaults(reg_func=Filter.maven)

    # Add Maven specific arguments

def add_all_args(registry_parser):
    '''
    This function creates and adds arguments to the All subparser.

    registry_parser: The subparser for the stage.
    '''

    # All subparser
    all_parser = registry_parser.add_parser(
        'all',
        help='Filter packages from all registries.'
    )

    # Set the function to use in the stage class
    all_parser.set_defaults(reg_func=Filter.all)


def add_arguments(top_parser):
    '''
    This function adds arguments to the top level parser.

    top_parser: The top level parser for the script.
    '''

    # Create a parser for the packages stage
    parser = top_parser.add_parser(
        'filter',
        help='Filter packages from different registries.'
    )

    # Add stage specific arguments
    parser.add_argument(
        'input',
        metavar='PATH',
        type=path_exists,
        help='The path to the input databse file. Defaults to '
    )
    parser.add_argument(
        'output',
        metavar='PATH',
        type=path_create,
        help='The path to the output database file. This can be set to the '
        'input database file to overwrite the input database file. Clears the '
        'output database file for the selected registry before copying.'
    )
    parser.add_argument(
        '--max-date',
        '-D',
        dest='max_date',
        metavar='YYYY-MM-DD',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        default=datetime.now(),
        help='The maximum date of the package and its versions/artifacts. In '
        'the format YYYY-MM-DD. If not provided, defaults to today.'
    )
    parser.add_argument(
        '--min-date',
        '-d',
        dest='min_date',
        metavar='YYYY-MM-DD',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        default=datetime.fromtimestamp(0),
        help='The minimum date of the package and its versions/artifacts. In '
        'the format YYYY-MM-DD. If not provided, defaults to epoch.'
    )
    parser.add_argument(
        '--random-select',
        '-r',
        dest='random_select',
        metavar='N',
        type=int,
        default=-1,
        help='Randomly select N packages. Defaults to -1, which means all.'
    )
    parser.add_argument(
        '--min-versions',
        '-v',
        dest='min_versions',
        metavar='N',
        type=int,
        default=0,
        help='The minimum number of versions a package must have to be '
        'included. Defaults to 0.'
    )
    parser.add_argument(
        '--max-versions',
        '-V',
        dest='max_versions',
        metavar='N',
        type=int,
        default=None,
        help='The maximum number of versions a package can have to be '
        'included. Defaults to None.'
    )

    # Give the parser a stage class to use
    parser.set_defaults(stage=Filter)

    # Create subparsers for each registry
    registry_parser = parser.add_subparsers(
        title='registry',
        description='The registry to filter on.',
        help='The registry to filter on.',
        dest='registry',
        metavar='REGISTRY',
        required=True
    )

    # Add subparser specific arguments
    add_hf_args(registry_parser)
    add_pypi_args(registry_parser)
    add_docker_args(registry_parser)
    add_maven_args(registry_parser)
    add_all_args(registry_parser)

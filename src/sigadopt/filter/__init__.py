'''
__init__.py: This is the __init__ file for the filter subpackage.
'''

# Imports
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
        help='Get packages from Hugging Face.'
    )

    # Set the function to use in the stage class
    huggingface_parser.set_defaults(reg_func=Filter.huggingface)

    # Add Hugging Face specific arguments
    hf_token_group = huggingface_parser.add_argument_group(
        'HuggingFace Tokens',
        'Pass the Hugging Face API token. This can be passed as an argument '
        'or read from a file. Only one of these options can be used. The '
        'default is to read from a file.')
    hf_me_group = hf_token_group.add_mutually_exclusive_group()
    hf_me_group.add_argument(
        '--token',
        dest='token',
        metavar='TOKEN',
        type=str,
        default=None,
        help='The Hugging Face API token.'
    )
    hf_me_group.add_argument(
        '--token-path',
        dest='token_path',
        metavar='FILE',
        type=path_exists,
        default=path_exists('./hftoken.txt'),
        help='The path to the file containing the Hugging Face API token. '
        'Defaults to ./hftoken.txt.'
    )


def add_pypi_args(registry_parser):
    '''
    This function creates and adds arguments to the PyPI subparser.

    registry_parser: The subparser for the stage.
    '''

    # PyPI subparser
    pypi_parser = registry_parser.add_parser(
        'pypi',
        help='Get packages from PyPI.'
    )

    # Set the function to use in the stage class
    pypi_parser.set_defaults(reg_func=Filter.pypi)

    # Add PyPI specific arguments
    pypi_parser.add_argument(
        '--auth-path',
        '-a',
        dest='auth_path',
        metavar='PATH',
        type=path_exists,
        default=None,
        help='The path to the file containing the Google BigQuery '
        'authentication information. Defaults to None and assumes that the '
        'authentication information is in the GOOGLE_APPLICATION_CREDENTIALS '
        'environment variable.'
    )


def add_docker_args(registry_parser):
    '''
    This function creates and adds arguments to the Docker subparser.

    registry_parser: The subparser for the stage.
    '''

    # Docker subparser
    docker_parser = registry_parser.add_parser(
        'docker',
        help='Get packages from Docker Hub.'
    )

    # Set the function to use in the stage class
    docker_parser.set_defaults(reg_func=Filter.docker)


def add_maven_args(registry_parser):
    '''
    This function creates and adds arguments to the Maven subparser.

    registry_parser: The subparser for the stage.
    '''

    # Maven subparser
    maven_parser = registry_parser.add_parser(
        'maven',
        help='Get packages from Maven.'
    )

    # Set the function to use in the stage class
    maven_parser.set_defaults(reg_func=Filter.maven)


def add_arguments(top_parser):
    '''
    This function adds arguments to the top level parser.

    top_parser: The top level parser for the script.
    '''

    # Create a parser for the packages stage
    parser = top_parser.add_parser(
        'packages',
        help='Get packages from different registries.'
    )

    # Add stage specific arguments
    parser.add_argument(
        '--output',
        '-o',
        dest='output',
        metavar='PATH',
        type=path_create,
        default=path_create('./data/packages.db'),
        help='The path to the output database file. Defaults to '
        './data/packages.db.',
    )
    parser.add_argument(
        '--clean',
        '-c',
        dest='clean',
        action='store_true',
        help='Flag to clear existing data from the database before adding new '
        'data. Defaults to False.'
    )

    # Give the parser a stage class to use
    parser.set_defaults(stage=Filter)

    # Create subparsers for each registry
    registry_parser = parser.add_subparsers(
        title='registry',
        description='The registry to get packages from.',
        help='The registry to get a list of packages from.',
        dest='registry',
        metavar='REGISTRY',
        required=True
    )

    # Add subparser specific arguments
    add_hf_args(registry_parser)
    add_pypi_args(registry_parser)
    add_docker_args(registry_parser)
    add_maven_args(registry_parser)

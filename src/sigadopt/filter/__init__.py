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
    huggingface_parser.add_argument(
        '--min-downloads',
        dest='min_downloads',
        metavar='N',
        type=int,
        default=1,
        help='The minimum number of downloads. Defaults to 1.'
    )
    huggingface_parser.add_argument(
        '--min-likes',
        dest='min_likes',
        metavar='N',
        type=int,
        default=0,
        help='The minimum number of likes. Defaults to 0.'
    )
    huggingface_parser.add_argument(
        '--min-versions',
        dest='min_versions',
        metavar='N',
        type=int,
        default=1,
        help='The minimum number of versions. Defaults to 1.'
    )


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
    pypi_parser.add_argument(
        '--min-versions',
        dest='min_versions',
        metavar='N',
        type=int,
        default=1,
        help='The minimum number of versions. Defaults to 1.'
    )


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
    docker_parser.add_argument(
        '--min-downloads',
        dest='min_downloads',
        metavar='N',
        type=int,
        default=1,
        help='The minimum number of downloads. Defaults to 1.'
    )
    docker_parser.add_argument(
        '--min-versions',
        dest='min_versions',
        metavar='N',
        type=int,
        default=1,
        help='The minimum number of versions. Defaults to 1.'
    )


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
    maven_parser.add_argument(
        '--min-versions',
        dest='min_versions',
        metavar='N',
        type=int,
        default=1,
        help='The minimum number of versions. '
        'Defaults to 1.'
    )
    maven_parser.add_argument(
        '--min-dependants',
        dest='min_dependants',
        metavar='N',
        type=int,
        default=1,
        help='The minimum number of dependants. '
        'Defaults to 1.'
    )


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
        '--input',
        '-i',
        dest='input_path',
        metavar='PATH',
        type=path_exists,
        default=path_exists('./data/packages.db'),
        help='The path to the input databse file. Defaults to '
                './data/packages.db.'
    )
    parser.add_argument(
        '--output',
        '-o',
        dest='output',
        metavar='PATH',
        type=path_create,
        default=path_create('./data/filter.db'),
        help='The path to the output database file. Defaults to '
        './data/filter.db. This can be set to the input database file to '
        'overwrite the input database file.'
    )
    parser.add_argument(
        '--max-date',
        dest='max_date',
        metavar='YYYY-MM-DD',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        default=None,
        help='The maximum date of the package and its versions/artifacts. In '
        'the format YYYY-MM-DD. If not provided, no maximum date.'
    )
    parser.add_argument(
        '--min-date',
        dest='min_date',
        metavar='YYYY-MM-DD',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        default=None,
        help='The minimum date of the package and its versions/artifacts. In '
        'the format YYYY-MM-DD. If not provided, no minimum date.'
    )
    parser.add_argument(
        '--random-select',
        dest='random_select',
        metavar='N',
        type=int,
        default=-1,
        help='Randomly select N packages. Defaults to -1, which means all.'
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

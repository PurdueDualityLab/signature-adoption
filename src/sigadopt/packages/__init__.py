'''
__init__.py: This is the __init__ file for the packages subpackage.
'''


def add_arguments(top_parser):
    parser = top_parser.add_parser(
        'packages',
        help='Get packages from different registries.'
    )
    parser.add_argument('--out-path',
                        dest='output_path',
                        metavar='PATH',
                        type=str,
                        default='./data/-reg-/packages.ndjson',
                        help='The path to the output file. '
                        'Defaults to ./data/-reg-/packages.ndjson. '
                        'The -reg- will be replaced with the ecosystem name.')
    # Create subparsers
    registry_parser = parser.add_subparsers(
        title='registry',
        description='The registry to get packages from.',
        help='The registry to get a list of packages from.',
        dest='registry',
        required=True)

    # Hugging Face subparser
    huggingface_parser = registry_parser.add_parser(
        'huggingface',
        help='Get packages from Hugging Face.')

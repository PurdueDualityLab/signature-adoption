'''
__init__.py: This is the __init__ file for the pre-filter subpackage.
'''


def add_arguments(top_parser):
    parser = top_parser.add_parser(
        'pre-filter',
        help='Pre-filter packages before checking adoption.'
    )
    parser.add_argument('--out-path',
                        dest='output_path',
                        metavar='PATH',
                        type=str,
                        default='./data/-reg-/packages.ndjson',
                        help='The path to the output file. '
                        'Defaults to ./data/-reg-/packages.ndjson. '
                        'The -reg- will be replaced with the ecosystem name.')

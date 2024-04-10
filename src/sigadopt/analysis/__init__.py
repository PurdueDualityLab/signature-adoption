'''
__init__.py: This is the __init__ file for the analysis subpackage.
'''

# Imports
from sigadopt.analysis.analysis import Analysis
from sigadopt.util.files import path_exists, path_create
from sigadopt.util.database import Registry


def add_metric(type_parser):
    '''
    This function computes the metric for the adoption of signatures.

    type_parser: The subparser for the stage.
    '''

    func_parser = type_parser.add_parser(
        'metric',
        help='Calculate the probability of publishing a signature after a '
        'signature has already been published.'
    )

    # Set the function to use in the stage class
    func_parser.set_defaults(type_func=Analysis.metric)

    # Add Maven specific arguments
    func_parser.add_argument(
        'output',
        metavar='PATH',
        type=path_create,
        help='The path to the output LaTeX file.'
    )

    func_parser.add_argument(
        '--json',
        '-j',
        action='store_true',
        help='Output the results as JSON instead of LaTeX.'
    )


def add_latex_table(type_parser):
    '''
    This function adds the LaTeX table subparser to the registry parser.

    type_parser: The subparser for the stage.
    '''

    func_parser = type_parser.add_parser(
        'latex_table',
        help='Create a LaTeX table of the results.'
    )

    # Set the function to use in the stage class
    func_parser.set_defaults(type_func=Analysis.latex_table)

    # Add Maven specific arguments
    func_parser.add_argument(
        'output',
        metavar='PATH',
        type=path_create,
        help='The path to the output LaTeX file.'
    )
    func_parser.add_argument(
        '--json',
        '-j',
        action='store_true',
        help='Output the results as JSON instead of LaTeX.'
    )


def add_latex_table_1yr(type_parser):
    '''
    This function adds the LaTeX table subparser to the registry parser.

    type_parser: The subparser for the stage.
    '''

    func_parser = type_parser.add_parser(
        'latex_table_1yr',
        help='Create a LaTeX table of the results from 2023.'
    )

    # Set the function to use in the stage class
    func_parser.set_defaults(type_func=Analysis.latex_table_1yr)

    # Add Maven specific arguments
    func_parser.add_argument(
        'output',
        metavar='PATH',
        type=path_create,
        help='The path to the output LaTeX file.'
    )
    func_parser.add_argument(
        '--json',
        '-j',
        action='store_true',
        help='Output the results as JSON instead of LaTeX.'
    )


def add_plot_failures(type_parser):
    '''
    This function plots the types of failures over time.

    type_parser: The subparser for the stage.
    '''

    func_parser = type_parser.add_parser(
        'plot_failures',
        help='Plot the types of failures over time.'
    )

    # Set the function to use in the stage class
    func_parser.set_defaults(type_func=Analysis.plot_failures)

    # Add Maven specific arguments
    func_parser.add_argument(
        'registry',
        type=lambda x: Registry[x.upper()],
        help='The registry to plot. '
        f'Options: {",".join([r.name.lower() for r in Registry])}'
    )
    func_parser.add_argument(
        'output',
        metavar='PATH',
        type=path_create,
        help='The path to the output plot.'
    )

def add_plot_new_artifacts(type_parser):
    '''
    This function plots the amount of new artifacts over time compared to the
    total number of artifacts.

    type_parser: The subparser for the stage.
    '''

    func_parser = type_parser.add_parser(
        'plot_new_artifacts',
        help='Plot the amount of new artifacts over time compared to the total'
        ' number of artifacts.'
    )

    # Set the function to use in the stage class
    func_parser.set_defaults(type_func=Analysis.plot_new_artifacts)

    # Add Maven specific arguments
    func_parser.add_argument(
        'registry',
        type=lambda x: Registry[x.upper()],
        help='The registry to plot. '
        f'Options: {",".join([r.name.lower() for r in Registry])}'
    )
    func_parser.add_argument(
        'output',
        metavar='PATH',
        type=path_create,
        help='The path to the output plot.'
    )

def add_plot_quality(type_parser):
    '''
    This function plots the quality of adoption over time.

    type_parser: The subparser for the stage.
    '''

    func_parser = type_parser.add_parser(
        'plot_quality',
        help='Plot the quality of adoption over time.'
    )

    # Set the function to use in the stage class
    func_parser.set_defaults(type_func=Analysis.plot_quality)

    # Add Maven specific arguments
    func_parser.add_argument(
        'output',
        metavar='PATH',
        type=path_create,
        help='The path to the output plot.'
    )


def add_plot_quantity(type_parser):
    '''
    This function plots the quantity of adoption over time.

    type_parser: The subparser for the stage.
    '''

    func_parser = type_parser.add_parser(
        'plot_quantity',
        help='Plot the quantity of adoption over time.'
    )

    # Set the function to use in the stage class
    func_parser.set_defaults(type_func=Analysis.plot_quantity)

    # Add Maven specific arguments
    func_parser.add_argument(
        'output',
        metavar='PATH',
        type=path_create,
        help='The path to the output plot.'
    )


def add_arguments(top_parser):
    '''
    This function adds arguments to the top level parser.

    top_parser: The top level parser for the script.
    '''

    # Create a parser for the packages stage
    parser = top_parser.add_parser(
        'analysis',
        help='Perform analysis on the checked packages.'
    )

    # Add stage specific arguments
    parser.add_argument(
        'database',
        metavar='DATABASE',
        type=path_exists,
        help='The path to the database file.'
    )

    # Give the parser a stage class to use
    parser.set_defaults(stage=Analysis)

    # Create subparsers for each registry
    type_parser = parser.add_subparsers(
        title='type',
        description='The type of analysis to perform.',
        help='The type of analysis to perform.',
        dest='type',
        metavar='TYPE',
        # required=True
    )

    # Add subparser specific arguments
    add_latex_table(type_parser)
    add_latex_table_1yr(type_parser)
    add_plot_quantity(type_parser)
    add_plot_quality(type_parser)
    add_plot_failures(type_parser)
    add_plot_new_artifacts(type_parser)
    add_metric(type_parser)

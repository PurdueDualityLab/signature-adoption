'''
__init__.py: This is the __init__ file for the analysis subpackage.
'''

# Imports
from datetime import datetime
from sigadopt.analysis.analysis import Analysis
from sigadopt.util.files import path_exists, path_create
from sigadopt.util.database import Registry


def add_ttest(type_parser):
    '''
    This function computes the T-Test for the adoption of signatures.

    type_parser: The subparser for the stage.
    '''

    func_parser = type_parser.add_parser(
        'ttest',
        help='Calculate the T-Test for the adoption of signatures.'
    )

    # Set the function to use in the stage class
    func_parser.set_defaults(type_func=Analysis.ttest)

    # Add type specific arguments
    func_parser.add_argument(
        'registry',
        type=lambda x: Registry[x.upper()],
        help='The registry to query.'
        f'Options: {",".join([r.name.lower() for r in Registry])}'
    )
    func_parser.add_argument(
        'intervention',
        metavar='YYYY-MM-DD',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        help='Intervention date',
    )
    func_parser.add_argument(
        'span',
        metavar='DAYS',
        type=int,
        help='Number of days to include in the before and after periods.',
    )
    func_parser.add_argument(
        '--alternative',
        '-a',
        dest='alternative',
        choices=['two-sided', 'less', 'greater'],
        default='two-sided',
        help='The alternative hypothesis to test. Default is two-sided. '
        'less: mean of first sample is less than mean of second sample. '
        'greater: mean of first sample is greater than mean of second sample. '
        'two-sided: means are not equal.',
    )
    func_parser.add_argument(
        '--output',
        '-o',
        metavar='PATH',
        type=path_create,
        default=None,
        help='The file to save the historgram to. If not provided, the '
        'histogram will not be generated.'
    )


def add_anova(type_parser):
    '''
    This function computes the ANOVA for the adoption of signatures.

    type_parser: The subparser for the stage.
    '''

    func_parser = type_parser.add_parser(
        'anova',
        help='Calculate the ANOVA for the adoption of signatures.'
    )

    # Set the function to use in the stage class
    func_parser.set_defaults(type_func=Analysis.anova)

    # Add type specific arguments
    func_parser.add_argument(
        '--boxplot',
        '-b',
        metavar='PATH',
        type=path_create,
        default=None,
        help='The path to the output boxplot. If not provided, the boxplot '
        'will not be generated.'
    )


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

    # Add type specific arguments
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


def add_table_summary(type_parser):
    '''
    This function adds the LaTeX table subparser to the registry parser.

    type_parser: The subparser for the stage.
    '''

    func_parser = type_parser.add_parser(
        'table_summary',
        help='Create a LaTeX table of the summary results.'
    )

    # Set the function to use in the stage class
    func_parser.set_defaults(type_func=Analysis.table_summary)

    # Add type specific arguments
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


def add_table_summary_1yr(type_parser):
    '''
    This function adds the LaTeX table subparser to the registry parser.

    type_parser: The subparser for the stage.
    '''

    func_parser = type_parser.add_parser(
        'table_summary_1yr',
        help='Create a LaTeX table of the results from 2023.'
    )

    # Set the function to use in the stage class
    func_parser.set_defaults(type_func=Analysis.table_summary_1yr)

    # Add type specific arguments
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

    # Add type specific arguments
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

    # Add type specific arguments
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

    # Add type specific arguments
    func_parser.add_argument(
        'output',
        metavar='PATH',
        type=path_create,
        help='The path to the output plot.'
    )


def add_plot_rsa(type_parser):
    '''
    This function plots the RSA data size over time.

    type_parser: The subparser for the stage.
    '''

    func_parser = type_parser.add_parser(
        'plot_rsa',
        help='Plot the RSA data size over time.'
    )

    # Set the function to use in the stage class
    func_parser.set_defaults(type_func=Analysis.plot_rsa)

    # Add type specific arguments
    func_parser.add_argument(
        'registry',
        type=lambda x: Registry[x.upper()],
        help='The registry to query.'
        f'Options: {",".join([r.name.lower() for r in Registry])}'
    )
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

    # Add type specific arguments
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
    add_table_summary(type_parser)
    add_table_summary_1yr(type_parser)
    add_plot_quantity(type_parser)
    add_plot_quality(type_parser)
    add_plot_failures(type_parser)
    add_plot_new_artifacts(type_parser)
    add_metric(type_parser)
    add_anova(type_parser)
    add_ttest(type_parser)
    add_plot_rsa(type_parser)

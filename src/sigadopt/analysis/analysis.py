'''
analysis.py: This script is used to analyze the adoption of all registries
with data.
'''
import logging
from sigadopt.util.database import connect_db
from sigadopt.analysis.latex_table import run as latex_table
from sigadopt.analysis.latex_table_1yr import run as latex_table_1yr
from sigadopt.analysis.plot_quantity import run as plot_quantity
from sigadopt.analysis.plot_quality import run as plot_quality
from sigadopt.analysis.plot_failures import run as plot_failures
from sigadopt.analysis.plot_new_artifacts import run as plot_new_artifacts
from sigadopt.analysis.metric import run as metric
from sigadopt.analysis.anova import run as anova
from sigadopt.analysis.ttest import run as ttest
from sigadopt.analysis.plot_rsa import run as plot_rsa


class Analysis:
    '''
    This class is used to analyze the adoption of all registries with data.
    '''

    def __init__(self, args):
        '''
        This function initializes the class.

        args: The arguments passed to the script.
        '''
        self.log = logging.getLogger(__name__)
        self.log.debug('Initializing Analysis stage...')
        self.args = args
        self.log.debug(f'{self.args=}')

    def plot_rsa(self):
        '''
        This function generates a plot of the RSA data size over time.
        '''
        plot_rsa(self.database, self.args.output, self.args.registry)

    def anova(self):
        '''
        This function computes the ANOVA for the adoption rates.
        '''
        anova(self.database, self.args.boxplot)

    def ttest(self):
        '''
        This function computes the T-Test for the adoption rates.
        '''
        ttest(
            self.database,
            self.args.registry,
            self.args.intervention,
            self.args.span,
            self.args.alternative,
            self.args.output,
        )

    def latex_table(self):
        '''
        This function generates a LaTeX table of the results.
        '''
        latex_table(self.database, self.args.output, self.args.json)

    def latex_table_1yr(self):
        '''
        This function generates a LaTeX table of the results from 2023.
        '''
        latex_table_1yr(self.database, self.args.output, self.args.json)

    def plot_quantity(self):
        '''
        This function generates a plot of the quantity of adoptions.
        '''
        plot_quantity(self.database, self.args.output)

    def plot_quality(self):
        '''
        This function generates a plot of the quality of adoptions.
        '''
        plot_quality(self.database, self.args.output)

    def plot_failures(self):
        '''
        This function generates a plot of the failures over time for a given
        registry.
        '''
        plot_failures(self.database, self.args.output, self.args.registry)

    def plot_new_artifacts(self):
        '''
        This function generates a plot of the failures over time for a given
        registry.
        '''
        plot_new_artifacts(self.database, self.args.output, self.args.registry)

    def metric(self):
        '''
        This function calculates the probability of signatures after the first
        signature.
        '''
        metric(self.database, self.args.output, self.args.json)

    def run(self):
        '''
        This function runs the stage.
        '''
        self.log.info('Running Analysis stage.')

        # Ensure the input/output database is available
        self.database = connect_db(self.args.database)

        # Run the subcommand
        self.args.type_func(self)

        # Close the databases
        self.log.info('Analysis stage complete. Closing database.')
        self.database.close()

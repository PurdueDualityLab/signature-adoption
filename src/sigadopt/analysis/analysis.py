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

    def latex_table(self):
        '''
        This function generates a LaTeX table of the results.
        '''
        latex_table(self.database, self.args.output)

    def latex_table_1yr(self):
        '''
        This function generates a LaTeX table of the results from 2023.
        '''
        latex_table_1yr(self.database, self.args.output)

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

#!/usr/bin/env python3

'''
__main__.py: This script checks the adoption of signatures for different
registries.
'''

import logging
from datetime import datetime
from sigadopt import parser

# Global variables
log = logging.getLogger(__name__)
start_time = datetime.now()


def main():
    '''
    This function checks the adoption of signatures for different
    registries.
    '''

    # Parse the arguments
    args = parser.parse_args()

    # Log start
    log.info('Starting...')
    log.info(f'Finished in {datetime.now() - start_time}.')

    # Call correct function
    # args.func(args)

    # Log end
    log.info('Done...')


if __name__ == '__main__':
    main()

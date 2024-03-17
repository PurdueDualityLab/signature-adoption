#!/usr/bin/env python3

'''
__main__.py: This script checks the adoption of signatures for different
registries.
'''

import logging
from datetime import datetime
from sigadopt import parser

# Global variables


def main():
    '''
    This function checks the adoption of signatures for different
    registries.
    '''

    # Start time
    log = logging.getLogger(__name__)
    start_time = datetime.now()

    # Parse the arguments
    args = parser.parse_args()

    # Manage logger if needed
    if args.log_level:
        logging.root.handlers[0].setLevel(args.log_level)
    if args.log:
        old_handler = logging.root.handlers[0]
        new_handler = logging.FileHandler(args.log)
        new_handler.setLevel(old_handler.level)
        new_handler.setFormatter(old_handler.formatter)
        logging.root.removeHandler(old_handler)
        logging.root.addHandler(new_handler)

    # Log start
    log.info('Starting.')

    # Call correct stage
    args.stage(args).run()

    # Log end
    log.info(f'Done. Finished in {datetime.now() - start_time}.')


if __name__ == '__main__':
    main()

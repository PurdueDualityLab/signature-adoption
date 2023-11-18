#!/usr/bin/env python

'''signature_parser.py: This provides a series of functions to parse different
signature types.
'''

# Imports
from enum import Enum

# Author information
__author__ = 'Taylor R. Schorlemmer'
__email__ = 'tschorle@purdue.edu'


# enum to represent signature status
SignatureStatus = Enum('SignatureStatus', ['GOOD', 'NONE', 'BAD'])


def parse_pgp(signature: str) -> str:
    '''
    This function parses a PGP signature and returns a status.

    signature: the signature to parse.

    returns: the status of the signature.
    '''

    return str(SignatureStatus.NONE)


def parse_gcs(signature: str) -> str:
    '''
    This function parses a Git Commit Signature and returns a status.

    signature: the signature to parse.

    returns: the status of the signature.
    '''

    return str(SignatureStatus.NONE)

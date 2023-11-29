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
class SignatureStatus(Enum):
    '''
    This is an enum to represent the status of a PGP signature.
    '''
    GOOD = 1
    NO_SIG = 2
    BAD_SIG = 3
    EXP_SIG = 4
    EXP_PUB = 5
    NO_PUB = 6
    REV_PUB = 7
    BAD_PUB = 8
    OTHER = 9


def parse_pgp(signature: str) -> str:
    '''
    This function parses a PGP signature and returns a status.

    signature: the signature to parse.

    returns: the status of the signature.
    '''

    if signature is None:
        return SignatureStatus.NO_SIG.name

    signature = signature.lower()
    if 'revoked' in signature:
        return SignatureStatus.REV_PUB.name
    if 'invalid public key algorithm' in signature:
        return SignatureStatus.BAD_PUB.name
    if 'key expired' in signature or 'keyexpired' in signature or 'key has expired' in signature:
        return SignatureStatus.EXP_PUB.name
    if 'no public key' in signature or 'no_pubkey' in signature:
        return SignatureStatus.NO_PUB.name
    if 'bad signature' in signature or 'errsig' in signature or 'ambiguous' in signature:
        return SignatureStatus.BAD_SIG.name
    if 'not a detached signature' in signature:
        return SignatureStatus.BAD_SIG.name
    if 'expired signature' in signature:
        return SignatureStatus.EXP_SIG.name
    if 'wrong key usage' in signature:
        return SignatureStatus.BAD_PUB.name
    if 'good signature' in signature or 'goodsig' in signature:
        return SignatureStatus.GOOD.name
    if 'no signature' in signature or 'no such file or directory' in signature or '' == signature:
        return SignatureStatus.NO_SIG.name
    print(signature)
    return SignatureStatus.OTHER.name


def parse_gcs(signature: str) -> str:
    '''
    This function parses a Git Commit Signature and returns a status.

    signature: the signature to parse.

    returns: the status of the signature.
    '''

    return SignatureStatus.NONE.name

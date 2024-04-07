'''
pgp.py: This file contains functions to interact with pgp keys and signatures.
'''

import subprocess
import logging
import re
from sigadopt.util.database import SignatureStatus

# Create a logger
log = logging.getLogger(__name__)

# List of keyservers to try
keyservers = [
    'keyserver.ubuntu.com',
    'keys.openpgp.org',
    'keyring.debian.org',
    'pgp.surf.nl',
]


def parse_verify(output):
    '''
    This function parses the output of the gpg verify command and returns the
    signature status.

    output: The output of the gpg verify command.

    returns: The signature status.
    '''

    if output is None:
        return SignatureStatus.NO_SIG

    output = output.lower().strip()
    if 'revoked' in output:
        return SignatureStatus.REV_PUB
    if 'invalid public key algorithm' in output:
        return SignatureStatus.BAD_PUB
    if 'expired signature' in output:
        return SignatureStatus.EXP_SIG
    if 'key expired' in output \
            or 'keyexpired' in output \
            or 'key has expired' in output:
        return SignatureStatus.EXP_PUB
    if 'no public key' in output or 'no_pubkey' in output:
        return SignatureStatus.NO_PUB
    if 'bad signature' in output \
            or 'errsig' in output \
            or 'ambiguous' in output \
            or 'not a detached signature' in output \
            or 'general error' in output \
            or 'time conflict' in output \
            or 'bad mpi value' in output \
            or 'fatal error' in output \
            or 'segmentation fault' in output \
            or 'unknown system error' in output:
        return SignatureStatus.BAD_SIG
    if 'wrong key usage' in output:
        return SignatureStatus.BAD_PUB
    if 'good signature' in output or 'goodsig' in output:
        return SignatureStatus.GOOD
    if 'no signature' in output \
            or 'no such file or directory' in output \
            or '' == output:
        return SignatureStatus.NO_SIG

    log.warning(f'Unknown signature status: {output}')
    return SignatureStatus.OTHER


def verify(artifact_path, signature_path):
    '''
    This function verifies a signature.

    artifact_path: The path to the artifact file.
    signature_path: The path to the signature file.

    returns: The output of the gpg command.
    '''
    output = subprocess.run(
        [
            "gpg",
            "--verify",
            "--verbose",
            signature_path,
            artifact_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout.decode("utf-8")

    return output


def list_packets(signature_path):
    '''
    This function lists the packets in a signature.

    signature_path: The path to the signature file.

    returns: (algo, digest_algo, data, key_id, created, expires, raw)
    '''

    # Run the gpg list_packets command
    raw = subprocess.run(
        [
            'gpg',
            '--list-packets',
            signature_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout.decode("utf-8")

    # Create regex objects
    algo_regex = re.compile(r'algo (\d+)')
    created_regex = re.compile(r'created (\d+)')
    digest_regex = re.compile(r'digest algo (\d+)')
    data_regex = re.compile(r'data: \[(\d+) bits\]')
    keyid_regex = re.compile(r'keyid (\w+)')
    exp_regex = re.compile(r'sig expires')

    # Find matches in the string
    algo_match = algo_regex.search(raw)
    created_match = created_regex.search(raw)
    digest_match = digest_regex.search(raw)
    data_match = data_regex.search(raw)
    keyid_match = keyid_regex.search(raw)
    exp_match = exp_regex.search(raw)

    # Extract the matched groups
    algo = algo_match.group(1) if algo_match else None
    created = created_match.group(1) if created_match else None
    digest_algo = digest_match.group(1) if digest_match else None
    data = data_match.group(1) if data_match else None
    keyid = keyid_match.group(1) if keyid_match else None
    expires = 1 if exp_match else 0

    return (algo, digest_algo, data, keyid, created, expires, raw)


def get_key(key_id):
    '''
    This function gets a key from a keyserver.

    key_id: The key id to get.

    returns: (keyserver, output) or (None, output) if the key is not found.
    '''

    # Check if we already have the key
    output = subprocess.run(
        [
            'gpg',
            '--list-keys',
            key_id,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout.decode("utf-8")

    # Check if the key is already in the keyring
    if 'No public key' not in output:
        return 'local', output

    # Try each keyserver
    total_output = output
    for server in keyservers:
        output = subprocess.run(
            [
                'gpg',
                '--keyserver',
                server,
                '--verbose',
                '--recv-keys',
                key_id,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ).stdout.decode("utf-8")

        total_output += '\n' + output

        if 'Total number processed: 1' in output:
            return server, output

    return None, total_output

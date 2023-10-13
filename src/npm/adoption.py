#!/usr/bin/env python

'''
adoption.py: This script checks the adoption of signatures for packages from
NPM.
'''

# Imports
import json
import os
import subprocess
import requests
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import logging as log


# Author information
__author__ = 'Taylor R. Schorlemmer and Luke Chigges'
__email__ = 'tschorle@purdue.edu'


def download_file(remote_file_url, local_file_path):
    """
    This function downloads a file to a local path.

    remote_file_url: url of file to download.

    local_file_path: path to save file to.

    returns: True if file is downloaded, False otherwise.
    """

    response = requests.get(remote_file_url)

    if not response:
        log.warning(f'Could not download file {remote_file_url}.')
        return False
    if response.status_code != 200:
        log.warning(f'Could not download file {remote_file_url}. '
                    f'Code: {response.status_code}')
        return False

    # Write the file
    with open(local_file_path, "wb") as local_file:
        local_file.write(response.content)
    local_file.close()

    # Return True if file is downloaded
    return True


def check_ecdsa(package_name_version,
                signatures,
                integrity,
                ecdsa_public_keys):
    '''
    This function checks the ECDSA signatures for a version of a package.

    package_name_version: the name and version of the package.

    signatures: the ecdsa signatures for the package.

    integrity: the integrity value for the package.

    ecdsa_public_keys: the public ECDSA keys from NPM.

    returns: True if the signature is valid, False otherwise.
    '''

    log.info('Checking ECDSA signature for '
             f'{package_name_version}')

    # Create the data that is signed
    data = f'{package_name_version}:{integrity}'.encode('utf-8')

    # Get the public key and load it in
    public_key = base64.b64decode(ecdsa_public_keys['key'])
    public_key = serialization.load_der_public_key(
        public_key, backend=default_backend())

    # Get the signature and decode it
    data_signature = base64.b64decode(signatures[0]['sig'])

    # Verify the signature: if we have an exception, the signature is invalid
    result = True
    try:
        public_key.verify(data_signature, data,
                          ec.ECDSA(hashes.SHA256()))
    except Exception:
        result = False

    # Return result
    return result


def check_gpg(package_name_version,
              signature,
              integrity,
              download_path):
    '''
    This function checks the GPG signature for a file.

    package_name_version: the name and version of the package. Used as the base
    name of the signature and integrity files.

    signature: the PGP signature for the package.

    integrity: the integrity value for the package.

    download_path: the path to the directory to save files to.

    returns: The output of the GPG command.
    '''
    log.info('Checking PGP signature for '
             f'{package_name_version}')

    # Save signature and integrity to files
    log.debug('Saving signature and integrity to file for '
              f'{package_name_version}')
    clean_name = package_name_version.replace('/', '_')
    signature_path = os.path.join(download_path,
                                  f'{clean_name}.sig')
    integrity_path = os.path.join(download_path,
                                  f'{clean_name}')

    with open(signature_path, 'w') as signature_file:
        signature_file.write(signature)
    with open(integrity_path, 'w') as integrity_file:
        integrity_file.write(f'{package_name_version}:{integrity}')

    # Check signature
    result = subprocess.run(['gpg',
                             '--verify',
                             '--verbose',
                             signature_path,
                             integrity_path],
                            capture_output=True)

    # Remove files
    log.debug('Removing signature and integrity files for '
              f'{package_name_version}')
    os.remove(signature_path)
    os.remove(integrity_path)

    # Return output
    return {'stdout': result.stdout.decode('utf-8'),
            'stderr': result.stderr.decode('utf-8')}


def get_package_metadata(package_name):
    '''
    This function uses the NPM API to get metadata for a package.

    package_name: the name of the package to get metadata for.

    returns: the metadata for the package.
    '''

    # Fetch the package's signature and integrity value
    url = f"https://registry.npmjs.org/{package_name}"
    response = requests.get(url)

    # Check to see if we got a response
    if not response:
        log.warning(f'Could not get metadata for package {package_name}.')
        return None

    # Check for error codes
    if response.status_code != 200:
        log.warning(f'Could not get metadata for package {package_name}. '
                    f'Code: {response.status_code}')
        return None

    # Return the metadata
    return response.json()


def public_ecdsa_keys():
    '''
    This function gets the public ECDSA keys from NPM.

    returns: the public keys from NPM.
    '''

    log.info('Getting public ECDSA keys from NPM.')
    url = "https://registry.npmjs.org/-/npm/v1/keys"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["keys"]


def public_gpg_keys(download_dir):
    '''
    This function gets the public GPG keys from NPM and adds them to the
    keyring.

    download_dir: the directory to download the pub key to.

    returns: None.
    '''
    key_url = "https://keybase.io/npmregistry/pgp_keys.asc"

    key_path = os.path.join(download_dir, "npm_pub_key.asc")

    # Fetch the key
    downloaded = download_file(key_url, key_path)
    if not downloaded:
        log.error('Could not download the public key from NPM.')
        return

    # Add the key to the keyring
    result = subprocess.run(['gpg', '--import', key_path], capture_output=True)

    log.info('Added public key from NPM to keyring.')
    log.debug(f'stdout: {result.stdout.decode("utf-8")}')
    log.debug(f'stderr: {result.stderr.decode("utf-8")}')


def check_signatures(package, download_path, ecdsa_public_key):
    '''
    This function gets the signatures for a package from NPM.

    package: the package to get the signatures for.

    download_path: the path to the directory to download files to.

    ecdsa_public_key: the public ECDSA keys from NPM.

    returns: the package with the signatures added. None if there is an issue
    getting the metadata.
    '''

    # Get metadata
    metadata = get_package_metadata(package['name'])

    # Check for valid metadata
    if metadata is None:
        return None

    # Iterate through versions
    for version in package['versions']:
        version_number = version['number']

        # Placeholder for signature data
        pgp = None
        ecdsa = None
        integrity = None

        # Check for valid version metadata
        valid_info = version_number in metadata['versions']

        # Skip if no version metadata
        if not valid_info:
            log.warning(f'Could not get metadata for '
                        f'{package["name"]}@{version_number}.')
            continue

        # Get version metadata
        version_metadata = metadata['versions'][version_number]

        # Ensure dist is present with integrity
        valid_info = 'dist' in version_metadata
        valid_info = valid_info and 'integrity' in version_metadata['dist']

        # Skip if no dist or integrity
        if not valid_info:
            log.warning('Could not get integrity for '
                        f'{package["name"]}@{version_number}.')
            continue

        # Get integrity
        integrity = version_metadata['dist']['integrity']

        # Create name version string
        package_name_version = f'{package["name"]}@{version_number}'

        # Check for PGP signatures and verify
        if 'npm-signature' in version_metadata['dist']:
            signature = version_metadata['dist']['npm-signature']
            pgp = check_gpg(package_name_version,
                            signature,
                            integrity,
                            download_path)
        else:
            log.info('No PGP signature for '
                     f'{package["name"]}@{version_number}.')

        # Check for ECDSA signatures and verify
        if 'signatures' in version_metadata['dist']:
            signatures = version_metadata['dist']['signatures']
            ecdsa = check_ecdsa(package_name_version,
                                signatures,
                                integrity,
                                ecdsa_public_key)
        else:
            log.info('No ECDSA signatures for '
                     f'{package["name"]}@{version_number}.')

        # Add signatures to package and update dist
        version['signatures'] = {}
        version['signatures']['dist'] = version_metadata['dist']
        version['signatures']['pgp'] = pgp
        version['signatures']['ecdsa'] = ecdsa

    return package


def adoption(input_file_path,
             output_file_path,
             download_path,
             start=0,
             end=-1,
             min_downloads=20,
             min_versions=2):
    '''
    This function checks the adoption of signatures for packages from NPM.
    It takes a newline delimited JSON file and outputs a newline
    delimited JSON file with the signatures added.

    input_file_path: the path to the input file.

    output_file_path: the path to the output file.

    download_path: the path to the directory to download files to.

    start: the line to start on. Default is 0 (start of file).

    end: the line to end on. Default is -1 (end of file).

    min_downloads: the minimum number of downloads for a package to be
    considered. Default is 20.

    min_versions: the minimum number of versions for a package to be
    considered. Default is 2.

    returns: None.
    '''

    # Log start of script and open files
    log.info('Checking signature adoption for NPM packages.')
    log.info(f'Input file: {input_file_path}')
    log.info(f'Output file: {output_file_path}')
    log.info(f'Start: {start}')
    log.info(f'End: {end}')
    log.info(f'Min Downloads: {min_downloads}')
    log.info(f'Min Versions: {min_versions}')

    # Load public keys
    ecdsa_public_key = public_ecdsa_keys()[0]
    public_gpg_keys(download_path)

    with open(input_file_path, 'r') as input_file, \
            open(output_file_path, 'a') as output_file:

        # Read input file
        for indx, line in enumerate(input_file):

            # Skip lines and check for end
            if indx < start:
                continue
            if end != -1 and indx >= end:
                break

            # Parse line
            package = json.loads(line)

            # Check for minimum versions
            versions_count = package['versions_count']
            versions_count = 0 if versions_count is None else versions_count

            if versions_count < min_versions:
                log.debug(f'Skipping {package["name"]} - versions too low.')
                continue

            # Check for minimum downloads
            downloads = package['downloads']
            downloads = 0 if downloads is None else downloads

            if downloads < min_downloads:
                log.debug(f'Skipping {package["name"]} - downloads too low.')
                continue

            # Check signatures and write to file
            log.info(f'Processing package number {indx}: {package["name"]}')
            package_with_signatures = check_signatures(package,
                                                       download_path,
                                                       ecdsa_public_key)
            if package_with_signatures is None:
                log.warning(f'Skipping {package["name"]} - '
                            'could not get metadata.')
                continue

            # Write to file
            log.info(f'Writing package to {output_file_path}')
            json.dump(obj=package_with_signatures,
                      fp=output_file,
                      default=str)
            output_file.write('\n')
            output_file.flush()  # force write to disk

    log.info('Finished checking adoption of signatures for packages from NPM.')

'''
adoption.py: This script checks the adoption of signatures for packages from
PyPI.
'''

# Imports
import requests
import logging
from bs4 import BeautifulSoup
from sigadopt.util.files import download_file, remove_file
from sigadopt.util.database import SignatureStatus
from sigadopt.util.pgp import list_packets, get_key, verify, parse_verify

# Create a logger
log = logging.getLogger(__name__)


def url_construction(digest: str, filename: str) -> str:
    '''
    This function constructs the url for the package file.

    digest: The digest of the package file.

    filename: The name of the package file.

    return: The url for the package file.
    '''

    # Construct the url
    prefix = "https://files.pythonhosted.org/packages/"
    hash_section = f"{digest[0:2]}/{digest[2:4]}/{digest[4:]}/"
    url = prefix + hash_section + filename

    return url


def adoption(input_file_path, output_file_path, download_dir, start, stop,
             save_sigs, save_units, only_sigs):
    '''
    This function checks the adoption of signatures for packages from
    PyPI. It takes a newline delimited JSON file and outputs a newline
    delimited JSON file with the signatures added.

    input_file_path: the path to the input file.
    output_file_path: the path to the output file.
    download_dir: the directory to download the files to.
    start: the line number to start at.
    stop: the line number to stop at. If -1, go to the end of the file.
    save_sigs: whether to save the signatures.
    save_units: whether to save the units.
    only_sigs: whether to only get signatures.

    returns: None.
    '''

    # Log start of script and open files
    log.info('Checking adoption of signatures for packages from PyPI.')
    log.info(f'Input file: {input_file_path}')
    log.info(f'Output file: {output_file_path}')
    log.info(f'Download directory: {download_dir}')
    log.info(f'Start: {start}')
    log.info(f'Stop: {stop}')

    with open(input_file_path, 'r') as input_file, \
            open(output_file_path, 'w') as output_file:

        # Read input file
        for indx, line in enumerate(input_file):

            # Check if we are in the range
            if indx < start:
                continue
            if indx >= stop and stop != -1:
                break

            # Log progress
            if indx % 100 == 0:
                log.info(f'Processing package {indx}.')
            else:
                log.debug(f'Processing package {indx}.')

            # Parse line
            package = json.loads(line)

            # Iterate through versions
            for version_name, files in package['versions'].items():

                # Iterate through files
                for file in files.values():

                    # Add placeholder for signature adoption
                    file['signature'] = None

                    # Check if the package has a signature
                    if file['has_signature']:

                        # Create url and local file name
                        filename = file['filename']
                        local_file_path = os.path.join(download_dir, filename)
                        url = url_construction(
                            digest=file['blake2_256_digest'],
                            filename=filename
                        )

                        # Download the signature
                        dl_sign = download_file(
                            remote_file_url=url+'.asc',
                            local_file_path=local_file_path+'.asc'
                        )

                        # Check if the signature was downloaded
                        if not dl_sign:
                            log.warning(
                                f'Missing sig, skipping ver.: {version_name}'
                            )

                        # If we are only getting signatures, continue
                        if only_sigs:
                            continue

                        # Download the file
                        dl_file = download_file(
                            remote_file_url=url,
                            local_file_path=local_file_path
                        )

                        # Check if the file was downloaded
                        if not dl_file:
                            log.warning(
                                f'Missing file, skipping ver.: {version_name}'
                            )

                        # Verify the signature
                        stdout, stderr = gpg_verify(
                            file_path=local_file_path,
                            signature_path=local_file_path+'.asc'
                        )

                        # Add signature adoption to package
                        file['signature'] = {
                            'stdout': stdout,
                            'stderr': stderr
                        }

                        # Remove the files if not saving
                        if not save_units:
                            subprocess.run(['rm',
                                            '-r',
                                            local_file_path])
                        if not save_sigs:
                            subprocess.run(['rm',
                                            '-r',
                                            local_file_path+'.asc'])

            # Write package to output file
            log.debug(f'Writing package {indx} to file.')
            json.dump(package, output_file, default=str)
            output_file.write('\n')

    log.info('Finished checking adoption of signatures for packages from '
             'PyPI.')

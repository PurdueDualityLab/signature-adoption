'''
maven.py: This script checks the adoption of signatures for packages from
Maven Central.
'''

# Imports
import subprocess
import requests
import logging
from bs4 import BeautifulSoup

# Create a logger
log = logging.getLogger(__name__)


def download_file(remote_file_url, local_file_path):
    """
    This function downloads a file to a local path using wget.

    remote_file_url: url of file to download.
    local_file_path: path to save file to.

    returns: True if file is downloaded, False otherwise.
    """
    response = requests.get(remote_file_url)

    if not response:
        log.error(f'Could not download file {remote_file_url}.')
        return False
    if response.status_code != 200:
        log.error(f'Could not download file {remote_file_url}. '
                  f'Code: {response.status_code}')
        return False

    # Write the file
    with open(local_file_path, "wb") as local_file:
        local_file.write(response.content)
    local_file.close()

    # Return True if file is downloaded
    return True


def check_file(version_url, file_name, extensions, download_path,
               save_sigs, save_units, only_sigs):
    '''
    This function checks the adoption of signatures for a file from Maven
    Central.

    version_url: the URL for the package version.
    file_name: the name of the file to check.
    extensions: all of the extensions for the file.
    download_path: the path to the directory to download files to.
    save_sigs: whether to save the signatures.
    save_units: whether to save the units.
    only_sigs: whether to only get signatures.

    returns: The results of a GPG check.
    '''

    # Construct the url
    file_url = version_url + '/' + file_name
    log.debug(f'Checking file {file_url}.')

    # check for a signature file
    if '.asc' not in extensions:
        return None, None

    # Create the signature path
    signature_path = download_path + file_name + '.asc'
    log.debug(f'Signature path: {signature_path}')

    # Get the signature ensure file is downloaded
    if not download_file(file_url+'.asc', signature_path):
        log.warning(f'Could not download signature {file_url}.asc.')
        return None, None

    # If we are only getting signatures, return
    if only_sigs:
        return None, None

    # Create the file path
    file_path = download_path + file_name
    log.debug(f'File path: {file_path}')

    # Get the file ensure file is downloaded
    if not download_file(file_url, file_path):
        log.warning(f'Could not download file {file_url}.')
        return None, None

    # Run the gpg verify command
    output = subprocess.run(
        [
            "gpg",
            "--keyserver-options",
            "auto-key-retrieve",
            "--keyserver",
            "keyserver.ubuntu.com",
            "--verify",
            "--verbose",
            f"{signature_path}",
            f"{file_path}"
        ],
        capture_output=True)

    # Remove the files if we are not saving them
    if not save_units:
        subprocess.run(['rm', '-r', file_path])
    if not save_sigs:
        subprocess.run(['rm', '-r', signature_path])

    return output.stdout.decode('utf-8'), output.stderr.decode('utf-8')


def get_files(version_url):
    '''
    This function gets the files for a package from Maven Central.

    version_url: the URL for the package version.

    returns: the files for the package and corresponding extensions.
    '''

    # Get the html from the given url
    response = requests.get(version_url)

    # Check to see if we got a response
    if not response:
        return None

    files = []

    # Find all a tags - this is where the files are
    soup = BeautifulSoup(response.text, "html.parser")
    for a_tag in soup.find_all("a"):

        # if the href includes a forward slash the entry is another sub-dir
        href = a_tag.get("href")
        if '/' not in href:
            files.append(href)

    # Sort the files by length
    file_names = sorted(files, key=len)

    file_extensions = {}

    # Iterate through the files and get the extensions
    while len(file_names) > 0:
        temp = file_names.pop(0)
        extensions = [f for f in file_names if f.startswith(temp)]
        file_names = [f for f in file_names if f not in extensions]
        file_extensions[temp] = [f[len(temp):] for f in extensions]

    # Return the files and extensions
    return file_extensions


def check_signatures(package, download_dir, save_sigs, save_units, only_sigs):
    '''
    This function gets the signatures for a package from Maven Central.

    package: the package to get the signatures for.
    download_dir: the path to the directory to download files to.
    save_sigs: whether to save the signatures.
    save_units: whether to save the units.
    only_sigs: whether to only get signatures.

    returns: the package with the signatures added.
    '''

    # Maven Central URL
    maven_central_url = 'https://repo1.maven.org/maven2/'

    # Parse package name
    package_name = package['name']
    package_name = package_name.split(':')[0].replace('.', '/') + '/' + \
        package_name.split(':')[1]

    # Iterate through versions
    for version in package['versions']:
        version_number = version['number']

        # Construct the url and get the files
        version_url = maven_central_url + package_name + '/' + version_number
        files = get_files(version_url)

        version['files'] = []

        # Check for files
        if files is None:
            log.warning(f'Could not get files for {version_url}.')
            continue

        # Iterate through files
        for file_name, extensions in files.items():

            stdout, stderr = check_file(version_url,
                                        file_name,
                                        extensions,
                                        download_dir,
                                        save_sigs,
                                        save_units,
                                        only_sigs)
            version['files'].append({
                'name': file_name,
                'extensions': extensions,
                'has_signature': '.asc' in extensions,
                'stdout': stdout,
                'stderr': stderr
            })

    return package


def adoption(database, version):
    '''
    This function checks the adoption of signatures for packages from Maven
    Central for a single version.

    database: the database to use.
    version: the version to check. (package_id, package_name, version_id,
    version_name)
    '''

    # Get all artifacts for the version
    version_url = 'https://repo1.maven.org/maven2/' + \
        f'{version[1].split(":")[0].replace(".", "/")}/' + \
        f'{version[1].split(":")[1]}/' + \
        f'{version[3]}'
    files = get_files(version_url)

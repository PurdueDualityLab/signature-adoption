'''
maven.py: This script checks the adoption of signatures for packages from
Maven Central.
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


def insert_artifacts(database, artifacts):
    '''
    This function inserts an artifacts into the database.

    database: the database to use.
    artifacts: the artifacts to insert. Add the id to the end of each list.
    '''

    with database:
        # Create the cursor
        cursor = database.cursor()

        # Insert the artifact
        for a in artifacts:
            cursor.execute(
                '''
                INSERT INTO artifacts
                (version_id, name, type, has_sig, extensions)
                VALUES (?, ?, ?, ?, ?)
                ''',
                a
            )
            a.append(cursor.lastrowid)


def insert_signatures(database, artifacts):
    '''
    This function inserts signatures into the database.

    database: the database to use.
    artifacts: the artifacts to insert. Add the id to the end of each list.
    '''

    with database:
        # Create the cursor
        cursor = database.cursor()

        # Insert the signature
        for a in artifacts:
            if not a[3]:
                continue
            cursor.execute(
                '''
                INSERT INTO signatures
                (artifact_id, type, raw)
                VALUES (?, ?, ?)
                ''',
                [a[5], 'PGP', a[6]]
            )
            a.append(cursor.lastrowid)


def check_artifacts(artifacts, download_path, database):
    '''
    This function checks the adoption of signatures for a file from Maven
    Central.

    artifacts: the artifact to check.
    download_path: the path to the directory to download files to.
    database: the database to use.
    '''

    all_checks = []
    all_packets = []
    all_keys = {}

    # Iterate through the artifacts
    for artifact in artifacts:

        # Check if we have a signature
        if not artifact[3]:
            all_checks.append((artifact[5], SignatureStatus.NO_SIG, None))
            continue

        # list packets
        packets = list_packets(download_path / (artifact[1] + '.asc'))
        all_packets.append((artifact[7],) + packets)

        # Get the public key if we can find it
        keyserver, key_output = get_key(packets[3])
        if packets[3] not in all_keys:
            all_keys[packets[3]] = (keyserver, key_output)

        # Check if we have a key
        if not keyserver:
            all_checks.append((artifact[5], SignatureStatus.NO_PUB, None))
            continue

        # Check the signature
        verify_output = verify(
            download_path / artifact[1],
            download_path / (artifact[1] + '.asc')
        )

        # Parse the output
        status = parse_verify(verify_output)
        all_checks.append((artifact[5], status, verify_output))

    # Insert the things
    with database:
        cursor = database.cursor()

        # Insert the checks
        cursor.executemany(
            '''
            INSERT INTO sig_check
            (artifact_id, status, raw)
            VALUES (?, ?, ?)
            ''',
            all_checks
        )

        # Insert the packets
        cursor.executemany(
            '''
            INSERT INTO list_packets
            (signature_id, algo, digest_algo, data, key_id, created, expires,
            raw)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            all_packets
        )

        # Insert the keys
        cursor.executemany(
            '''
            INSERT OR IGNORE INTO pgp_keys
            (key_id, keyserver, raw)
            VALUES (?, ?, ?)
            ''',
            [(k, v[0], v[1]) for k, v in all_keys.items()]
        )


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


def already_artifacted(database, version_id):
    '''
    This function checks if we already have artifacts for a version.

    database: the database to use.
    version_id: the version id to check.

    returns: True if this version already has artifacts, False otherwise.
    '''

    # Assume we don't have artifacts
    artifacted = False

    with database:
        # Create the cursor
        cursor = database.cursor()

        # Execute the query
        cursor.execute(
            '''
            SELECT COUNT(*)
            FROM artifacts
            WHERE version_id = ?
            ''',
            (version_id,)
        )

        # Fetch the data
        count = cursor.fetchone()[0]

        # Return True if we have artifacts, False otherwise
        artifacted = count > 0

    return artifacted


def adoption(database, download_dir, version):
    '''
    This function checks the adoption of signatures for packages from Maven
    Central for a single version.

    database: the database to use.
    download_dir: the path to the directory to download files to.
    version: the version to check. (package_id, package_name, version_id,
    version_name)
    '''

    # Check if we have any artifacts already in the database for this version
    if already_artifacted(database, version[2]):
        log.debug(f'Already have artifacts for {version[1]} {version[3]}.')
        return

    # Get all artifacts for the version
    version_url = 'https://repo1.maven.org/maven2/' + \
        f'{version[1].split(":")[0].replace(".", "/")}/' + \
        f'{version[1].split(":")[1]}/' + \
        f'{version[3]}'
    files = get_files(version_url)

    # create the artifact list
    artifacts = [[version[2], file, 'file', 1 if '.asc' in extensions else 0,
                  ';'.join(extensions)] for file, extensions in files.items()]

    # Insert the artifacts into the database
    insert_artifacts(database, artifacts)

    # Download all file-signature pairs
    for artifact in artifacts:
        if not artifact[3]:
            continue
        download_file(
            version_url + '/' + artifact[1],
            download_dir / artifact[1]
        )
        sig_binary = download_file(
            version_url + '/' + artifact[1] + '.asc',
            download_dir / (artifact[1] + '.asc')
        )
        artifact.append(sig_binary)

    # Insert the signatures
    insert_signatures(database, artifacts)

    # Check signatures for each artifact
    check_artifacts(artifacts, download_dir, database)

    # Remove the files
    for artifact in artifacts:
        if not artifact[3]:
            continue
        remove_file(download_dir / artifact[1])
        remove_file(download_dir / (artifact[1] + '.asc'))

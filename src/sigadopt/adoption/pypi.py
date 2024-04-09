'''
adoption.py: This script checks the adoption of signatures for packages from
PyPI.
'''

# Imports
import logging
from sigadopt.util.files import download_file, remove_file
from sigadopt.util.database import SignatureStatus, Registry
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


def get_artifacts(database, start, stop):
    '''
    This function gets the artifacts for a version.

    database: the database to use.

    return: the artifacts for the version that have not been checked yet.
            id, version_id, name, type, has_sig, digest, date, extensions.
    '''

    # Get the artifacts for the version
    artifacts = None
    with database:
        cursor = database.cursor()

        # Ensure non-signed artifacts have a sig_check
        cursor.execute(
            '''
            INSERT OR IGNORE INTO sig_check
            (artifact_id, status, raw)
            SELECT a.id, ?, ?
            FROM artifacts a
            JOIN versions v ON a.version_id = v.id
            JOIN packages p ON v.package_id = p.id
            WHERE p.registry_id = ?
            AND a.has_sig = 0
            ''',
            (SignatureStatus.NO_SIG, None, Registry.PYPI)
        )

        # Find signed artifacts
        cursor.execute(
            '''
            SELECT a.*
            FROM artifacts a
            JOIN versions v ON a.version_id = v.id
            JOIN packages p ON v.package_id = p.id
            WHERE p.registry_id = ?
            AND a.has_sig = 1
            ''',
            (Registry.PYPI,)
        )
        artifacts = cursor.fetchall()

        # Log the number of artifacts
        log.debug(f'Found {len(artifacts)} artifacts with signatures for '
                  'PyPI.')

        # Subset
        artifacts = artifacts[start:stop]

    return artifacts


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
            if not a[4]:
                continue
            cursor.execute(
                '''
                INSERT INTO signatures
                (artifact_id, type, raw)
                VALUES (?, ?, ?)
                ''',
                [a[0], 'PGP', a[8]]
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
        if not artifact[4] or not artifact[8]:
            all_checks.append((artifact[0], SignatureStatus.NO_SIG, None))
            continue

        # list packets
        packets = list_packets(download_path / (artifact[2] + '.asc'))
        all_packets.append((artifact[9],) + packets)

        # Get the public key if we can find it
        keyserver, key_output = get_key(packets[3])
        if packets[3] not in all_keys:
            all_keys[packets[3]] = (keyserver, key_output)

        # Check if we have a key
        if not keyserver:
            all_checks.append((artifact[0], SignatureStatus.NO_PUB, None))
            continue

        # Check the signature
        verify_output = verify(
            download_path / artifact[2],
            download_path / (artifact[2] + '.asc')
        )

        # Parse the output
        status = parse_verify(verify_output)
        all_checks.append((artifact[0], status, verify_output))

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


def already_checked(database, artifact_id):
    '''
    This function checks if an artifact has already been checked.

    database: the database to use.
    artifact_id: the artifact to check.

    return: True if the artifact has already been checked, False otherwise.
    '''

    checked = False

    with database:
        cursor = database.cursor()

        cursor.execute(
            '''
            SELECT *
            FROM sig_check
            WHERE artifact_id = ?
            ''',
            (artifact_id,)
        )

        checked = cursor.fetchone() is not None

    return checked


def adoption(database, download_dir, start, stop, batch_size=25):
    '''
    This function checks the adoption of signatures for packages from PyPI.

    database: the database to use.
    download_dir: the path to the directory to download files to.
    start: the start artifact.
    stop: the stop artifact.
    batch_size: the number of artifacts to check at once.
    '''

    # Get artifacts for the version
    log.info('Getting artifacts for PyPI.')
    artifacts = get_artifacts(database, start, stop)
    num_selected = len(artifacts)
    log.info(f'Selected {num_selected} artifacts for the registry.')

    # Split the artifacts into batches
    batches = [
        artifacts[i:i+batch_size]
        for i in range(0, len(artifacts), batch_size)
    ]
    log.info(f'Split artifacts into {len(batches)} batches.')

    # Iterate through the batches
    for indx, batch in enumerate(batches):
        log.info(f'Checking batch {indx+1} of {len(batches)}.')

        batch = [list(a) for a in batch]
        collected = []

        # Download all file-signature pairs
        for artifact in batch:

            # Check if we have already checked this artifact
            if already_checked(database, artifact[0]):
                continue

            # Create url and local file name
            url = url_construction(
                digest=artifact[5],
                filename=artifact[2]
            )

            # Download the file and signature
            download_file(
                remote_file_url=url,
                local_file_path=download_dir / artifact[2]
            )
            sig_binary = download_file(
                remote_file_url=url+'.asc',
                local_file_path=download_dir / (artifact[2] + '.asc')
            )

            # Add the signature to the artifact
            artifact.append(sig_binary)
            collected.append(artifact)

        # Insert the signatures
        insert_signatures(database, collected)

        # Check signatures for each artifact
        check_artifacts(collected, download_dir, database)

        # Remove the files
        for artifact in collected:
            if not artifact[4]:
                continue
            remove_file(download_dir / artifact[2])
            remove_file(download_dir / (artifact[2] + '.asc'))

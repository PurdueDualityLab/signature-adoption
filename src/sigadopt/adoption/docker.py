'''
docker.py: This script checks the adoption of signatures for packages from
Docker Hub.
'''

# Imports
import json
import subprocess
import logging
from sigadopt.util.database import Registry, SignatureStatus

# Set up logging
log = logging.getLogger(__name__)


def get_signatures(package_name):
    '''
    This function gets the signatures for a package from Docker Hub.

    package_name: the name of the package.

    returns: the output of the docker trust inspect command.
    '''
    # Check to see if package has signatures
    output = subprocess.run(
        [
            "docker",
            "trust",
            "inspect",
            f"{package_name}",
        ],
        capture_output=True)

    return json.loads(output.stdout), output.stderr.decode("utf-8")

def get_versions(database, start, stop):
    '''
    This function gets a list of all versions in the start stop range for the
    selected registry.

    database: the database to use.
    start: the start index.
    stop: the stop index.

    returns: A list of all versions in the start stop range in the selected
    registry. (p.id, p.name, v.id, v.name)
    '''
    # Initialize the packages list
    versions = None

    # Create the cursor
    with database:
        curr = database.cursor()

        # Execute the query
        curr.execute(
            '''
            SELECT p.id, p.name, v.id, v.name
            FROM packages p
            JOIN versions v ON p.id = v.package_id
            WHERE registry_id = ?;
            ''',
            (Registry.DOCKER,)
        )

        # Fetch the data
        versions = curr.fetchall()
        log.debug(f'Found {len(versions)} versions for the registry.')

    # Subset packages in the start stop range
    versions = versions[start:stop]

    # Return the packages
    return versions


def adoption(database, start, stop, batch_size=50):
    '''
    This function checks the adoption of signatures for packages from Hugging
    Face.

    database: the database to use.
    start: the start index.
    stop: the stop index.
    batch_size: the number of packages to process at once.
    '''

    # Get the packages
    log.info('Getting versions from the database.')
    versions = get_versions(database, start, stop)
    log.info(f'Selected {len(versions)} versions.')

    # Create a dictionary for the packages
    packages = {}
    for version in versions:
        pid, pname, vid, vname = version
        if pid not in packages:
            packages[pid] = {
                'name': pname,
                'versions': []
            }
        packages[pid]['versions'].append((vid, vname))

    # Split the packages into batches
    pid_batches = [
        list(packages.keys())[i:i+batch_size]
        for i in range(0, len(packages), batch_size)
    ]
    log.info(f'Split packages into {len(pid_batches)} batches.')

    # Iterate over the batches
    for indx, batch in enumerate(pid_batches):

        log.info(f'Processing batch {indx+1}/{len(pid_batches)}.')

        artifacts = []

        # Iterate over the packages
        for pid in batch:

            # Get the DCT data
            json_data, _ = get_signatures(packages[pid]['name'])

            # Iterate over the versions and match the commits
            for vid, vname in packages[pid]['versions']:

                # Find the signature
                signature = None
                if json_data:
                    finder = (s for s in json_data[0]['SignedTags']
                              if s['SignedTag'] == vname)
                    signature = next(finder, None)

                status = SignatureStatus.GOOD if signature \
                    else SignatureStatus.NO_SIG
                raw = json.dumps(signature) if signature else None

                artifacts.append(
                    [
                        vid,
                        vname,
                        'tag',
                        status != SignatureStatus.NO_SIG,
                        status,
                        raw,
                    ]
                )

        # Insert the things
        with database:
            curr = database.cursor()

            for artifact in artifacts:
                curr.execute(
                    '''
                    INSERT INTO artifacts (version_id, name, type, has_sig)
                    VALUES (?, ?, ?, ?);
                    ''',
                    artifact[:4]
                )
                artifact_id = curr.lastrowid
                curr.execute(
                    '''
                    INSERT INTO sig_check (artifact_id, status, raw)
                    VALUES (?, ?, ?);
                    ''',
                    (artifact_id, artifact[4], artifact[5])
                )

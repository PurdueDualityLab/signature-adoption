'''
huggingface.py: This script checks the adoption of signatures for packages from
Hugging Face.
'''

# Import statements
import requests
import logging
from bs4 import BeautifulSoup
from sigadopt.util.database import SignatureStatus, Registry

# Create a logger
log = logging.getLogger(__name__)


def get_commits_page(name, page=0):
    '''
    Get the commits page for a package and page number.

    name: the name of the package.
    page: the page number.
    '''
    url = f'https://huggingface.co/{name}/commits/main?p={page}'
    r = requests.get(url)

    if not r:
        log.error(f'Failed to get commits for {name} page {page}.')
        return None
    if r.status_code != 200:
        log.error(f'Failed to get commits for {name} page {page}.')
        return None

    return r.text


def get_commit_data(name):
    '''
    Get the commit data for a package.

    name: the name of the package.

    returns: a dictionary of commit data.
    '''
    commit_data = {}
    page = 0

    while True:
        html = get_commits_page(name, page)
        page += 1
        if not html:
            break

        soup = BeautifulSoup(html, 'html.parser')
        commit_elements = soup.find_all('article')

        # Iterate over all commits on the page
        for commit_element in commit_elements:

            # Spans contain the hash and status
            spans = commit_element.h3.find_all('span')
            hash = spans[0].text.strip()

            # If theres only 1 span, there is no signature
            if len(spans) < 2:
                commit_data[hash] = SignatureStatus.NO_SIG
                continue

            # Get the status
            status_raw = spans[1].text.strip().lower()
            status = SignatureStatus.GOOD if status_raw == 'verified' \
                else SignatureStatus.BAD_SIG
            commit_data[hash] = status

        if len(commit_elements) < 50:
            break

    return commit_data


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
            (Registry.HUGGINGFACE,)
        )

        # Fetch the data
        versions = curr.fetchall()
        log.debug(f'Found {len(versions)} versions for the registry.')

    # Subset packages in the start stop range
    versions = versions[start:stop]

    # Return the packages
    return versions


def already_processed(database, pid):
    '''
    This function checks if a package has already been processed.

    database: the database to use.
    pid: the package id.

    returns: True if the package has already been processed, False otherwise.
    '''

    processed = False
    with database:
        curr = database.cursor()
        curr.execute(
            '''
            SELECT *
            FROM artifacts a
            JOIN versions v on a.version_id = v.id
            JOIN packages p on v.package_id = p.id
            WHERE p.registry_id = ?;
            ''',
            (Registry.HUGGINGFACE)
        )
        processed = curr.fetchone() is not None

    return processed


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

            # Check if the package is in the database
            if already_processed(database, pid):
                log.debug(f'Package {pid} already processed.')
                continue

            # Get commit data
            commit_data = get_commit_data(packages[pid]['name'])

            # Iterate over the versions and match the commits
            for vid, vname in packages[pid]['versions']:
                status = commit_data.get(vname[:7], SignatureStatus.NO_SIG)
                artifacts.append(
                    [
                        vid,
                        vname,
                        'GCS',
                        status != SignatureStatus.NO_SIG,
                        status,
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
                    INSERT INTO sig_check (artifact_id, status)
                    VALUES (?, ?);
                    ''',
                    (artifact_id, artifact[4])
                )

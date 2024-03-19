'''
huggingface.py: This script gets the repositories and associated metadata
from Hugging Face.
'''

# Import statements
import logging
from huggingface_hub.hf_api import list_repo_commits
from sigadopt.util.database import clean_db


def packages(output_conn, token_path=None, token=None, clean=False):
    '''
    This function gets the repositories and associated metadata from
    HuggingFace. The data is saved in the output_conn database.

    output_conn: The path to the output database.
    token_path: The path to the file containing the HuggingFace API token.
    token: The HuggingFace API token. If this is provided, token_path is
    ignored.
    clean: Whether to clear the versions table before adding the new data.

    returns: None
    '''

    # Log start of function
    log = logging.getLogger(__name__)
    log.info("Getting Hugging Face packages from local database.")

    # Read in token for huggingface api
    hf_token = token
    if hf_token is None and token_path:
        log.debug('Reading in token for Hugging Face API.')
        with open(token_path, 'r') as f:
            hf_token = f.read().strip()

    # Get list of all models on HuggingFace
    package_list = None
    with output_conn:
        # Create the cursor
        output_cursor = output_conn.cursor()

        # Create the query
        query = '''
            SELECT id, name
            FROM packages
            WHERE registry_id = 1;
        '''

        # Execute the query
        output_cursor.execute(query)

        # Fetch the data
        package_list = output_cursor.fetchall()

    # Clean the versions table
    if clean:
        # Clear the versions table
        log.info('Clearing versions for Hugging Face.')
        clean_db(output_conn, 1, 1)

    # Get commits for each package
    log.info('Getting commits from Hugging Face.')
    with output_conn:
        # Create the cursor
        output_cursor = output_conn.cursor()

        # Iterate through the packages
        for indx, package in enumerate(package_list):

            # Info from package
            package_id = package[0]
            model_id = package[1]

            # Get commits and iterate through
            commits = list_repo_commits(model_id, token=hf_token)
            for commit in commits:
                try:
                    output_cursor.execute(
                        '''
                            INSERT INTO versions (package_id, name, date)
                            VALUES (?, ?, ?);
                        ''',
                        (
                            package_id,              # package_id
                            commit.commit_id,            # name
                            commit.created_at.strftime('%Y-%m-%d %H:%M:%S')
                        )
                    )
                except Exception as e:
                    print(model_id)
                    print([c.commit_id for c in commits])
                    print(commit.commit_id)
                    exit(-1)

            # Update package with number of versions or delete if no versions
            if commits:
                output_cursor.execute(
                    '''
                        UPDATE packages
                        SET versions_count = ?
                        WHERE id = ?;
                    ''',
                    (len(commits), package_id)
                )
            else:
                output_cursor.execute(
                    '''
                        DELETE FROM packages
                        WHERE id = ?;
                    ''',
                    (package_id,)
                )

            # Log progress and make the occasional commit
            if indx % 100 == 0:
                log.debug(f'Processing package {indx}.')
                output_conn.commit()

'''
huggingface.py: This script gets the repositories and associated metadata
from Hugging Face.
'''

# Import statements
import logging
from huggingface_hub.hf_api import list_models, list_repo_commits
# from huggingface_hub import login as hf_login


def packages(output_conn, token_path=None, token=None):
    '''
    This function gets the repositories and associated metadata from
    HuggingFace. The data is saved in the output_conn database.

    output_conn: The path to the output database.
    token_path: The path to the file containing the HuggingFace API token.
    token: The HuggingFace API token. If this is provided, token_path is
    ignored.

    returns: None
    '''

    # Log start of function
    log = logging.getLogger(__name__)
    log.info("Getting packages from Hugging Face.")

    # Read in token for huggingface api
    hf_token = token
    if hf_token is None and token_path:
        log.debug('Reading in token for HuggingFace API.')
        with open(token_path, 'r') as f:
            hf_token = f.read().strip()

    # Login to Hugging Face
    # hf_login(token=hf_token, add_to_git_credential=True)

    # Get list of all models on HuggingFace
    model_list = list_models(full=True)  # , token=hf_token)

    # Insert packages into output database
    log.info('Adding packages to the output database.')
    with output_conn:

        # Create the cursor
        output_cursor = output_conn.cursor()

        # Create the query
        query = '''
            INSERT INTO packages (name, registry_id, latest_release_date,
                first_release_date, downloads, downloads_period,
                versions_count)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        '''

        # Count the number of gated, disabled, and private repos
        num_gated = 0
        num_disabled = 0
        num_private = 0

        # Insert the data
        for model in model_list:

            if model.gated:
                num_gated += 1
                continue
            if model.disabled:
                num_disabled += 1
                continue
            if model.private:
                num_private += 1
                continue

            # Find number of commits for each model
            # , token=hf_token))
            num_commits = len(list_repo_commits(model.id))

            # Put it in the database
            output_cursor.execute(
                query,
                (
                    model.id,              # name
                    1,                     # registry_id
                    model.last_modified,   # latest_release_date
                    model.created_at,      # first_release_date
                    model.downloads,       # downloads
                    'all_time',            # downloads_period
                    num_commits            # versions_count
                )
            )

        # Log the number of gated repos
        log.info(f'Skipped {num_gated} gated repos')
        log.info(f'Skipped {num_disabled} disabled repos.')
        log.info(f'Skipped {num_private} private repos.')

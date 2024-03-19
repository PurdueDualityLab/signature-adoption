'''
database.py: This module contains functions to interact with the databases.
'''


def clean_db(conn, registry_id, level=0):
    '''
    This function cleans the database for the selected registry.

    conn: The connection to the database.
    registry_id: The registry id.
    level: The level of cleaning to perform. 0 is the default and will
    remove all packages, versions, and artifacts for the selected registry.

    return: None
    '''
    with conn:
        curr = conn.cursor()
        if level <= 2:
            curr.execute(
                '''
                DELETE FROM artifacts
                WHERE version_id IN (
                    SELECT id FROM versions WHERE package_id IN (
                        SELECT id FROM packages WHERE registry_id = ?
                    )
                );
                ''',
                (registry_id,)
            )

        if level <= 1:
            curr.execute(
                '''
                DELETE FROM versions WHERE package_id IN (
                    SELECT id FROM packages WHERE registry_id = ?
                );
                ''',
                (registry_id,)
            )

        if level == 0:
            curr.execute(
                f'DELETE FROM packages WHERE registry_id = {registry_id};'
            )

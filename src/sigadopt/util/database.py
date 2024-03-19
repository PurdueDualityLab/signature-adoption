'''
database.py: This module contains functions to interact with the databases.
'''


def clean_db(conn, registry_id):
    '''
    This function cleans the database for the selected registry.

    conn: The connection to the database.
    registry_id: The registry id.

    return: None
    '''
    with conn:
        curr = conn.cursor()
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
        curr.execute(
            '''
            DELETE FROM versions WHERE package_id IN (
                SELECT id FROM packages WHERE registry_id = ?
            );
            ''',
            (registry_id,)
        )
        curr.execute(
            f'DELETE FROM packages WHERE registry_id = {registry_id};'
        )

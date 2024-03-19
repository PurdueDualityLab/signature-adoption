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
            DELETE FROM artifacts a
            JOIN versions v ON a.version_id = v.id
            JOIN packages p ON v.package_id = p.id
            WHERE p.registry_id = ?;
            ''',
            (registry_id,)
        )
        curr.execute(
            '''
            DELETE FROM versions v
            JOIN packages p ON v.package_id = p.id
            WHERE p.registry_id = ?;
            ''',
            (registry_id,)
        )
        curr.execute(
            f'DELETE FROM packages WHERE registry_id = {registry_id};'
        )

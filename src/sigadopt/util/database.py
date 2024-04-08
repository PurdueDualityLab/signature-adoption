'''
database.py: This module contains functions to interact with the databases.
'''

# Imports
import sqlite3
import logging
from enum import IntEnum

# Create a logger
log = logging.getLogger(__name__)


class Registry(IntEnum):
    '''
    This class contains the registry ids.
    '''
    HUGGINGFACE = 1
    DOCKER = 2
    MAVEN = 3
    PYPI = 4


class SignatureStatus(IntEnum):
    '''
    This is an enum to represent the status of a PGP signature.
    '''
    GOOD = 1
    NO_SIG = 2
    BAD_SIG = 3
    EXP_SIG = 4
    EXP_PUB = 5
    NO_PUB = 6
    REV_PUB = 7
    BAD_PUB = 8
    OTHER = 9


class CleanLevel(IntEnum):
    '''
    This is an enum to represent the level of cleaning to perform.
    '''
    PACKAGES = 0
    VERSIONS = 1
    ARTIFACTS = 2
    SIGNATURES = 3


def clean_db(conn, registry_id, level=0):
    '''
    This function cleans the database for the selected registry.

    conn: The connection to the database.
    registry_id: The registry id.
    level: The level of cleaning to perform. 0 is the default and will
    remove all packages, versions, and artifacts for the selected registry.

    return: None
    '''
    log.debug(f'Cleaning database for registry: {registry_id} level: {level}')
    with conn:
        curr = conn.cursor()
        if level <= CleanLevel.SIGNATURES:
            curr.execute(
                '''
                DELETE FROM list_packets
                WHERE signature_id IN (
                    SELECT id FROM signatures WHERE artifact_id IN (
                        SELECT id FROM artifacts WHERE version_id IN (
                            SELECT id FROM versions WHERE package_id IN (
                                SELECT id FROM packages WHERE registry_id = ?
                            )
                        )
                    )
                );
                ''',
                (registry_id,)
            )
            curr.execute(
                '''
                DELETE FROM signatures
                WHERE artifact_id IN (
                    SELECT id FROM artifacts WHERE version_id IN (
                        SELECT id FROM versions WHERE package_id IN (
                            SELECT id FROM packages WHERE registry_id = ?
                        )
                    )
                );
                ''',
                (registry_id,)
            )
            curr.execute(
                '''
                DELETE FROM sig_check
                WHERE artifact_id IN (
                    SELECT id FROM artifacts WHERE version_id IN (
                        SELECT id FROM versions WHERE package_id IN (
                            SELECT id FROM packages WHERE registry_id = ?
                        )
                    )
                );
                ''',
                (registry_id,)
            )

        if level <= CleanLevel.ARTIFACTS:
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

        if level <= CleanLevel.VERSIONS:
            curr.execute(
                '''
                DELETE FROM versions WHERE package_id IN (
                    SELECT id FROM packages WHERE registry_id = ?
                );
                ''',
                (registry_id,)
            )

        if level == CleanLevel.PACKAGES:
            curr.execute(
                f'DELETE FROM packages WHERE registry_id = {registry_id};'
            )


def connect_db(db_path):
    '''
    This function ensures the database is available and returns a connection
    to it.

    db_path: The path to the database.

    return: The connection to the database.
    '''

    log.debug('Ensuring database is available.')

    # Connect to the database
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=120)
    except sqlite3.Error as e:
        log.error(f'Error connecting to the database: {e}')
        exit(-1)

    # Check to see if the database is available
    if conn is None:
        log.error(f'Error connecting to the database: {db_path}')
        exit(-1)

    # Return the connection
    log.debug(f'Connected to database: {db_path}')
    return conn


def init_db(db_conn):
    '''
    This function initializes the database with the required tables.

    db_conn: The connection to the database.
    '''

    # Create registry table
    log.debug('Creating registry table if it does not exist.')
    with db_conn:
        db_conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS registries (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                UNIQUE (name)
            );
            '''
        )
        db_conn.executemany(
            '''
            INSERT OR IGNORE INTO registries (id, name)
            VALUES (?, ?);
            ''',
            [(reg, reg.name) for reg in Registry]
        )

    # Create sig_status table
    log.debug('Creating sig_status table if it does not exist.')
    with db_conn:
        db_conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS sig_status (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                UNIQUE (name)
            );
            '''
        )
        db_conn.executemany(
            '''
            INSERT OR IGNORE INTO sig_status (id, name)
            VALUES (?, ?);
            ''',
            [(status, status.name) for status in SignatureStatus]
        )

        # Create package table
    log.debug('Creating package table if it does not exist.')
    with db_conn:
        db_conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                registry_id INTEGER NOT NULL,
                versions_count INTEGER,
                latest_release_date TEXT,
                first_release_date TEXT,
                downloads INTEGER,
                downloads_period TEXT,
                UNIQUE (name, registry_id),
                FOREIGN KEY (registry_id) REFERENCES registries (id)
            );
            '''
        )

    # Create version table
    log.debug('Creating version table if it does not exist.')
    with db_conn:
        db_conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS versions (
                id INTEGER PRIMARY KEY,
                package_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                date TEXT,
                UNIQUE (package_id, name)
                FOREIGN KEY (package_id) REFERENCES packages (id)
            );
            '''
        )

    # Create artifact table
    log.debug('Creating artifact table if it does not exist.')
    with db_conn:
        db_conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY,
                version_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                has_sig INTEGER NOT NULL,
                digest TEXT,
                date TEXT,
                extensions TEXT,
                UNIQUE (version_id, name),
                FOREIGN KEY (version_id) REFERENCES versions (id)
            );
            '''
        )

    # Create signature table
    log.debug('Creating signature table if it does not exist.')
    with db_conn:
        db_conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS signatures (
                id INTEGER PRIMARY KEY,
                artifact_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                raw BLOB,
                UNIQUE (artifact_id),
                FOREIGN KEY (artifact_id) REFERENCES artifacts (id)
            );
            '''
        )

    # Create sig_check table
    log.debug('Creating sig_check table if it does not exist.')
    with db_conn:
        db_conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS sig_check (
                id INTEGER PRIMARY KEY,
                artifact_id INTEGER NOT NULL,
                status INTEGER NOT NULL,
                raw TEXT,
                UNIQUE (artifact_id),
                FOREIGN KEY (artifact_id) REFERENCES artifacts (id)
                FOREIGN KEY (status) REFERENCES sig_status (id)
            );
            '''
        )

    # Table to hold output from gpg list_packets
    log.debug('Creating list_packets table if it does not exist.')
    with db_conn:
        db_conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS list_packets (
                id INTEGER PRIMARY KEY,
                signature_id INTEGER NOT NULL,
                algo TEXT,
                digest_algo TEXT,
                data INTEGER,
                key_id TEXT,
                created INTEGER,
                expires INTEGER,
                raw TEXT,
                UNIQUE (signature_id),
                FOREIGN KEY (signature_id) REFERENCES signatures (id)
            );
            '''
        )

    # Table to hold list of keys
    log.debug('Creating pgp_keys table if it does not exist.')
    with db_conn:
        db_conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS pgp_keys (
                id INTEGER PRIMARY KEY,
                key_id TEXT NOT NULL,
                keyserver TEXT,
                raw TEXT,
                UNIQUE (key_id)
            );
            '''
        )

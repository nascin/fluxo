import os
import sqlite3
from fluxo.settings import Db


def _verify_if_db_exists(path_db: str = Db.PATH):
    '''
    Verifies if the database file exists at the specified path. If the file does not exist,
    it creates a new database using the `create_db` function.

    Parameters:
    - path_db (str): The path to the database file. Defaults to the path specified in the
      `settings_db.PATH` variable.

    Returns:
    None
    '''
    if not os.path.exists(path_db):
        create_db(path_db)


def create_db(path_db: str):
    '''
    Creates a SQLite database at the specified path with two tables: 'TB_Fluxo' and 'TB_Task'.
    If the tables do not exist, it creates them along with their respective columns.

    Parameters:
    - path_db (str): The path to the SQLite database file.

    Return:
    None
    '''
    # Database connection
    conn = sqlite3.connect(path_db)

    # Create TB_Fluxo table
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS TB_Fluxo (
                id INTEGER PRIMARY KEY,
                name TEXT,
                date_of_creation DATE,
                interval TEXT,
                active BOOLEAN
            )
        ''')
        print('++ TB_Fluxo table created successfully.')
    except Exception as err:
        print(f'++ Error creating TB_Fluxo table: {err}')

    # Create TB_Task table
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS TB_Task (
                id INTEGER PRIMARY KEY,
                name TEXT,
                execution_date DATE,
                fluxo_id INTEGER,
                start_time DATE,
                end_time DATE,
                error TEXT,
                FOREIGN KEY (fluxo_id) REFERENCES TB_Fluxo(id) ON DELETE CASCADE
            )
        ''')
        print('++ TB_Task table created successfully.')
    except Exception as err:
        print(f'++ Error creating TB_Task table: {err}')
    finally:
        # Committing the changes
        conn.commit()
        # Closing the database connection
        conn.close()

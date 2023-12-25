import os
import sqlite3
from fluxo.settings import Db
from fluxo.logging import logger


def _verify_if_db_exists(path_db: str = Db.PATH):
    '''
    Verifies if the database file exists at the specified path. If the file does not exist,
    it creates a new database using the `create_db` function.

    Parameters:
    - path_db (str): The path to the database file. Defaults to the path specified in the
      `Db.PATH` variable.

    Returns:
        None
    '''
    if not os.path.exists(path_db):
        create_db(path_db)


def create_db(path_db: str):
    '''
    Creates a SQLite database at the specified path. If the tables do not exist, 
    it creates them along with their respective columns.

    Parameters:
    - path_db (str): The path to the SQLite database file.

    Return:
    None
    '''
    try:
        # Database connection
        conn = sqlite3.connect(path_db)

        # Create TB_Flow table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS TB_Flow (
                id INTEGER PRIMARY KEY,
                name TEXT,
                date_of_creation DATE,
                interval TEXT,
                active BOOLEAN,
                list_names_tasks TEXT, -- Storing the list as a JSON string
                running BOOLEAN,
                running_process TEXT -- Storing the list as a JSON string
            )
        ''')
        logger.info('TB_Flow table created successfully')

        # Create TB_Task table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS TB_Task (
                id INTEGER PRIMARY KEY,
                name TEXT,
                execution_date DATE,
                flow_id INTEGER,
                start_time DATE,
                end_time DATE,
                error TEXT
            )
        ''')
        logger.info('TB_Task table created successfully')
        
        # Create TB_LogExecutionFlow table
        conn.execute('''
            CREATE TABLE TB_LogExecutionFlow (
                id INTEGER PRIMARY KEY,
                name TEXT,
                date_of_creation DATETIME,
                start_time DATETIME,
                end_time DATETIME,
                id_flow INTEGER,
                ids_task TEXT,  -- Storing the list as a JSON string
                ids_error_task TEXT  -- Storing the list as a JSON string
            )
        ''')
        logger.info('TB_LogExecutionFlow table created successfully')
        
        # Create TB_App table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS TB_App (
                id INTEGER PRIMARY KEY,
                active BOOLEAN,
                active_since DATE
            )
        ''')
        logger.info('TB_App table created successfully')

    
    except Exception as err:
        # Log the error
        logger.error(f'Error during database creation: {err}')

        # Close the connection if open
        if 'conn' in locals() and conn is not None:
            conn.close()

        # Delete the file if it exists
        if os.path.exists(path_db):
            os.remove(path_db)

        # Raise the exception to propagate the error
        raise err
    
    finally:
        # Committing the changes
        conn.commit()
        # Closing the database connection
        conn.close()

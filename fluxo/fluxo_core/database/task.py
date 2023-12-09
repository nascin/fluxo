import sqlite3
from datetime import datetime
from dataclasses import dataclass
from fluxo.settings import Db
from fluxo.uttils import current_time_formatted


@dataclass
class Task:
    '''
    Represents a 'Task' object with attributes corresponding to the columns
    in the 'TB_Task' table in the SQLite database.

    Attributes:
    - id (int): The unique identifier for the 'Task'.
    - name (str): The name of the 'Task'.
    - execution_date (datetime): The date and time when the 'Task' was executed.
    - fluxo_id (int): The ID of the 'Fluxo' associated with the 'Task'.
    - start_time (datetime): The start time of the 'Task'.
    - end_time (datetime): The end time of the 'Task'.
    - error (str): Any error message associated with the 'Task'.

    Methods:
    - save(): Saves the current 'Task' instance to the 'TB_Task' table in the database.
    - update(id, name, execution_date, fluxo_id, start_time, end_time, error): Updates the 'Task' with the specified ID
      with the provided information in the 'TB_Task' table.
    - get_all(): Retrieves all 'Task' instances from the 'TB_Task' table.
    - get_by_name(name): Retrieves a 'Task' instance by its name from the 'TB_Task' table.
    - get_by_id(id): Retrieves a 'Task' instance by its ID from the 'TB_Task' table.
    - get_all_by_fluxo_id(fluxo_id): Retrieves all 'Task' instances associated with the specified 'Fluxo' ID.
    - delete(id): Deletes the 'Task' with the specified ID from the 'TB_Task' table.
    - __repr__(): Returns a string representation of the 'Task' instance.
    '''
    id: int = None
    name: str = None
    execution_date: datetime = None
    fluxo_id: int = None
    start_time: datetime = None
    end_time: datetime = None
    error: str = None

    def save(self):
        '''
        Saves the current 'Task' instance to the 'TB_Task' table in the database.

        Returns:
        Task: The saved 'Task' instance.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO TB_Task (name, execution_date, fluxo_id, start_time, end_time, error)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.name, self.execution_date, self.fluxo_id, self.start_time, self.end_time, self.error))
        conn.commit()

        # Recuperar o ID da tarefa após a inserção
        cursor.execute('SELECT last_insert_rowid()')
        task_id = cursor.fetchone()[0]

        conn.close()

        return Task.get_by_id(task_id)

    @staticmethod
    def update(id, name, execution_date, fluxo_id, start_time, end_time, error):
        '''
        Updates the 'Task' with the specified ID with the provided information
        in the 'TB_Task' table.

        Parameters:
        - id (int): The ID of the 'Task' to be updated.
        - name (str): The new name for the 'Task'.
        - execution_date (datetime): The new execution date and time for the 'Task'.
        - fluxo_id (int): The new 'Fluxo' ID associated with the 'Task'.
        - start_time (datetime): The new start time for the 'Task'.
        - end_time (datetime): The new end time for the 'Task'.
        - error (str): The new error message for the 'Task'.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE TB_Task
            SET name=?, execution_date=?, fluxo_id=?, start_time=?, end_time=?, error=?
            WHERE id=?
        ''', (name, execution_date, fluxo_id, start_time, end_time, error, id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        '''
        Retrieves all 'Task' instances from the 'TB_Task' table.

        Returns:
        List[Task] or None: A list containing all 'Task' instances in the database, or None if no tasks are found.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_Task')
        data = cursor.fetchall()
        conn.close()
        if data:
            return [Task(*row) for row in data]
        else:
            return None

    @staticmethod
    def get_by_name(name):
        '''
        Retrieves a 'Task' instance by its name from the 'TB_Task' table.

        Parameters:
        - name (str): The name of the 'Task' to be retrieved.

        Returns:
        Task or None: The 'Task' instance if found, or None if not found.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_Task WHERE name=?', (name,))
        data = cursor.fetchone()
        conn.close()
        if data:
            return Task(*data)
        else:
            return None

    @staticmethod
    def get_by_id(id):
        '''
        Retrieves a 'Task' instance by its ID from the 'TB_Task' table.

        Parameters:
        - id (int): The ID of the 'Task' to be retrieved.

        Returns:
        Task or None: The 'Task' instance if found, or None if not found.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_Task WHERE id=?', (id,))
        data = cursor.fetchone()
        conn.close()
        if data:
            return Task(*data)
        else:
            return None

    @staticmethod
    def get_all_by_fluxo_id(fluxo_id):
        '''
        Retrieves all 'Task' instances associated with the specified 'Fluxo' ID from the 'TB_Task' table.

        Parameters:
        - fluxo_id (int): The ID of the 'Fluxo' for which tasks are to be retrieved.

        Returns:
        List[Task] or None: A list containing all 'Task' instances associated with the specified 'Fluxo' ID,
        or None if no tasks are found.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_Task WHERE fluxo_id=?', (fluxo_id,))
        data = cursor.fetchall()
        conn.close()
        if data:
            return [Task(*row) for row in data]
        else:
            return None

    @staticmethod
    def delete(id):
        '''
        Deletes the 'Task' with the specified ID from the 'TB_Task' table.

        Parameters:
        - id (int): The ID of the 'Task' to be deleted.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM TB_Task WHERE id=?', (id,))
        conn.commit()
        conn.close()

    def __repr__(self) -> str:
        '''
        Returns a string representation of the 'Task' instance.
        '''
        return f'''
            id:                     {self.id},
            name:                   {self.name},
            execution_date:         {self.execution_date},
            fluxo_id:               {self.fluxo_id},
            start_time:             {self.start_time},
            end_time:               {self.end_time},
            error:                  {self.error},
        '''

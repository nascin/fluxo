import sqlite3
import json
from datetime import datetime
from dataclasses import dataclass
from fluxo.settings import Db
from fluxo.uttils import current_time_formatted


@dataclass
class Fluxo:
    '''
    Represents a 'Fluxo' object with attributes corresponding to the columns
    in the 'TB_Fluxo' table in the SQLite database.

    Attributes:
    - id (int): The unique identifier for the 'Fluxo'.
    - name (str): The name of the 'Fluxo'.
    - date_of_creation (datetime): The date and time when the 'Fluxo' was created.
    - interval (dict): The interval information for the 'Fluxo'. Ex `{'minutes':1, 'at':':10'}`
    - active (bool): A flag indicating whether the 'Fluxo' is active or not.
    - list_names_tasks: (list): List of task names linked to the flow.

    Methods:
    - save(): Saves the current 'Fluxo' instance to the 'TB_Fluxo' table in the database.
    - update(id, name, date_of_creation, interval, active): Updates the 'Fluxo' with the specified ID
      with the provided information in the 'TB_Fluxo' table.
    - get_all(): Retrieves all 'Fluxo' instances from the 'TB_Fluxo' table.
    - get_by_name(name): Retrieves a 'Fluxo' instance by its name from the 'TB_Fluxo' table.
    - get_by_id(id): Retrieves a 'Fluxo' instance by its ID from the 'TB_Fluxo' table.
    - delete(id): Deletes the 'Fluxo' with the specified ID from the 'TB_Fluxo' table.
    - __repr__(): Returns a string representation of the 'Fluxo' instance.
    '''
    id: int = None
    name: str = None
    date_of_creation: datetime = None
    interval: dict = None
    active: bool = True
    list_names_tasks: list = None

    def save(self):
        '''
        Saves the current 'Fluxo' instance to the 'TB_Fluxo' table in the database.
        '''
        date_of_creation = current_time_formatted()
        interval = json.dumps(self.interval) if self.interval else None
        list_names_tasks = json.dumps(self.list_names_tasks) if self.list_names_tasks else None

        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO TB_Fluxo (name, date_of_creation, interval, active, list_names_tasks)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.name, date_of_creation, interval, self.active, list_names_tasks))
        conn.commit()
        conn.close()

    @staticmethod
    def update(id, name, date_of_creation, interval, active, list_names_tasks):
        '''
        Updates the 'Fluxo' with the specified ID with the provided information
        in the 'TB_Fluxo' table.

        Parameters:
        - id (int): The ID of the 'Fluxo' to be updated.
        - name (str): The new name for the 'Fluxo'.
        - date_of_creation (datetime): The new date and time of creation for the 'Fluxo'.
        - interval (dict): The new interval information for the 'Fluxo'.
        - active (bool): The new active status for the 'Fluxo'.
        - list_names_tasks: (list): The new List of task names linked to the flow.
        '''
        interval = json.dumps(interval) if interval else None
        list_names_tasks = json.dumps(list_names_tasks) if list_names_tasks else None

        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE TB_Fluxo
            SET name=?, date_of_creation=?, interval=?, active=?, list_names_tasks=?
            WHERE id=?
        ''', (name, date_of_creation, interval, active, list_names_tasks, id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        '''
        Retrieves all 'Fluxo' instances from the 'TB_Fluxo' table.

        Returns:
        List[Fluxo]: A list containing all 'Fluxo' instances in the database.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_Fluxo')
        data = cursor.fetchall()
        conn.close()

        fluxos = []
        for row in data:
            fluxo = Fluxo(*row)
            
            # Converter strings JSON from interval and list_names_tasks to lists
            fluxo.interval = json.loads(fluxo.interval) if fluxo.interval else None
            fluxo.list_names_tasks = json.loads(fluxo.list_names_tasks) if fluxo.list_names_tasks else None

            fluxos.append(fluxo)

        if fluxos:
            return fluxos
        else:
            return None

    @staticmethod
    def get_by_name(name):
        '''
        Retrieves a 'Fluxo' instance by its name from the 'TB_Fluxo' table.

        Parameters:
        - name (str): The name of the 'Fluxo' to be retrieved.

        Returns:
        Fluxo or None: The 'Fluxo' instance if found, or None if not found.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_Fluxo WHERE name=?', (name,))
        data = cursor.fetchone()
        conn.close()
        
        if data:
            fluxo = Fluxo(*data)

            # Converter strings JSON from interval and list_names_tasks to lists
            fluxo.interval = json.loads(fluxo.interval) if fluxo.interval else None
            fluxo.list_names_tasks = json.loads(fluxo.list_names_tasks) if fluxo.list_names_tasks else None

            return fluxo
        else:
            return None
        
    @staticmethod
    def get_by_id(id):
        '''
        Retrieves a 'Fluxo' instance by its ID from the 'TB_Fluxo' table.

        Parameters:
        - id (int): The ID of the 'Fluxo' to be retrieved.

        Returns:
        Task or None: The 'Fluxo' instance if found, or None if not found.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_Fluxo WHERE id=?', (id,))
        data = cursor.fetchone()
        conn.close()

        if data:
            fluxo = Fluxo(*data)

            # Converter strings JSON from interval and list_names_tasks to lists
            fluxo.interval = json.loads(fluxo.interval) if fluxo.interval else None
            fluxo.list_names_tasks = json.loads(fluxo.list_names_tasks) if fluxo.list_names_tasks else None

            return fluxo
        else:
            return None

    @staticmethod
    def delete(id):
        '''
        Deletes the 'Fluxo' with the specified ID from the 'TB_Fluxo' table.

        Parameters:
        - id (int): The ID of the 'Fluxo' to be deleted.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM TB_Fluxo WHERE id=?', (id,))
        conn.commit()
        conn.close()

    def __repr__(self) -> str:
        '''
        Returns a string representation of the 'Fluxo' instance.
        '''
        return f'''
            id:                     {self.id},
            name:                   {self.name},
            date_of_creation:       {self.date_of_creation},
            interval:               {self.interval},
            active:                 {self.active},
            list_names_tasks:       {self.list_names_tasks},
        '''

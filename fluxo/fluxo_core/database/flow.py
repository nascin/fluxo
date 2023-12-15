import sqlite3
import json
from datetime import datetime
from dataclasses import dataclass
from fluxo.settings import Db
from fluxo.uttils import current_time_formatted


@dataclass
class ModelFlow:
    '''
    Represents a 'Flow' object with attributes corresponding to the columns
    in the 'TB_Flow' table in the SQLite database.

    Attributes:
        - id (int): The unique identifier for the 'Fluxo'.
        - name (str): The name of the 'Fluxo'.
        - date_of_creation (datetime): The date and time when the 'Fluxo' was created.
        - interval (dict): The interval information for the 'Fluxo'. Ex `{'minutes':1, 'at':':10'}`
        - active (bool): A flag indicating whether the 'Fluxo' is active or not.
        - list_names_tasks: (list): List of task names linked to the flow.
        - running (bool): If the flow is running.
        - running_process (dict): What PID of the process the flow is running on.

    Methods:
        - save(): Saves the current 'Flow' instance to the 'TB_Flow' table in the database.
        - update(id, name, date_of_creation, interval, active): Updates the 'Flow' with the specified ID
                with the provided information in the 'TB_Flow' table.
        - get_all(): Retrieves all 'Flow' instances from the 'TB_Flow' table.
        - get_by_name(name): Retrieves a 'Flow' instance by its name from the 'TB_Flow' table.
        - get_by_id(id): Retrieves a 'Flow' instance by its ID from the 'TB_Flow' table.
        - delete(id): Deletes the 'Flow' with the specified ID from the 'TB_Flow' table.
    '''
    id: int = None
    name: str = None
    date_of_creation: datetime = None
    interval: dict = None
    active: bool = True
    list_names_tasks: list = None
    running: bool = None
    running_process: dict = None

    def save(self):
        '''
        Saves the current 'Fluxo' instance to the 'TB_Flow' table in the database.
        '''
        date_of_creation = current_time_formatted()
        interval = json.dumps(self.interval) if self.interval else None
        list_names_tasks = json.dumps(self.list_names_tasks) if self.list_names_tasks else None
        running_process = json.dumps(self.running_process) if self.running_process else None

        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO TB_Flow (name, date_of_creation, interval, active, list_names_tasks, running, running_process)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.name, date_of_creation, interval, self.active, list_names_tasks, self.running, running_process))
        conn.commit()

        # Retrieve fluxo ID after insertion
        cursor.execute('SELECT last_insert_rowid()')
        fluxo_id = cursor.fetchone()[0]

        conn.close()

        return ModelFlow.get_by_id(fluxo_id)

    @staticmethod
    def update(id, name, date_of_creation, interval, active, list_names_tasks, running, running_process):
        '''
        Updates the 'Flow' with the specified ID with the provided information
        in the 'TB_Flow' table.

        Parameters:
        - id (int): The ID of the 'Fluxo' to be updated.
        - name (str): The new name for the 'Flow'.
        - date_of_creation (datetime): The new date and time of creation for the 'Fluxo'.
        - interval (dict): The new interval information for the 'Fluxo'.
        - active (bool): The new active status for the 'Fluxo'.
        - list_names_tasks: (list): The new List of task names linked to the flow.
        - running (bool): If the flow is running.
        - running_process (dict): What PID of the process the flow is running on.
        '''
        interval = json.dumps(interval) if interval else None
        list_names_tasks = json.dumps(list_names_tasks) if list_names_tasks else None
        running_process = json.dumps(running_process) if running_process else None

        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE TB_Flow
            SET name=?, date_of_creation=?, interval=?, active=?, list_names_tasks=?, running=?, running_process=?
            WHERE id=?
        ''', (name, date_of_creation, interval, active, list_names_tasks, running, running_process, id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        '''
        Retrieves all 'Fluxo' instances from the 'TB_Flow' table.

        Returns:
        List[ModelFlow]: A list containing all 'Flow' instances in the database.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_Flow')
        data = cursor.fetchall()
        conn.close()

        flows = []
        for row in data:
            flow = ModelFlow(*row)
            
            # Converter strings JSON from interval, list_names_tasks and running_process to dicts
            flow.interval = json.loads(flow.interval) if flow.interval else None
            flow.list_names_tasks = json.loads(flow.list_names_tasks) if flow.list_names_tasks else None
            flow.running_process = json.loads(flow.running_process) if flow.running_process else None

            flows.append(flow)

        if flows:
            return flows
        else:
            return None

    @staticmethod
    def get_by_name(name):
        '''
        Retrieves a 'Flow' instance by its name from the 'TB_Flow' table.

        Parameters:
        - name (str): The name of the 'Flow' to be retrieved.

        Returns:
            Flow or None: The 'Flow' instance if found, or None if not found.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_Flow WHERE name=?', (name,))
        data = cursor.fetchone()
        conn.close()
        
        if data:
            flow = ModelFlow(*data)

            # Converter strings JSON from interval, list_names_tasks and running_process to dicts
            flow.interval = json.loads(flow.interval) if flow.interval else None
            flow.list_names_tasks = json.loads(flow.list_names_tasks) if flow.list_names_tasks else None
            flow.running_process = json.loads(flow.running_process) if flow.running_process else None

            return flow
        else:
            return None
        
    @staticmethod
    def get_by_id(id):
        '''
        Retrieves a 'Flow' instance by its ID from the 'TB_Flow' table.

        Parameters:
        - id (int): The ID of the 'Flow' to be retrieved.

        Returns:
            Flow or None: The 'Flow' instance if found, or None if not found.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_Flow WHERE id=?', (id,))
        data = cursor.fetchone()
        conn.close()

        if data:
            flow = ModelFlow(*data)

            # Converter strings JSON from interval, list_names_tasks and running_process to dicts
            flow.interval = json.loads(flow.interval) if flow.interval else None
            flow.list_names_tasks = json.loads(flow.list_names_tasks) if flow.list_names_tasks else None
            flow.running_process = json.loads(flow.running_process) if flow.running_process else None

            return flow
        else:
            return None

    @staticmethod
    def delete(id):
        '''
        Deletes the 'Flow' with the specified ID from the 'TB_Flow' table.

        Parameters:
            - id (int): The ID of the 'Flow' to be deleted.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM TB_Flow WHERE id=?', (id,))
        conn.commit()
        conn.close()

    def __repr__(self) -> str:
        '''
        Returns a string representation of the 'Flow' instance.
        '''
        return f'''
            id:                     {self.id},
            name:                   {self.name},
            date_of_creation:       {self.date_of_creation},
            interval:               {self.interval},
            active:                 {self.active},
            list_names_tasks:       {self.list_names_tasks},
            running:                {self.running},
            running_process:        {self.running_process},
        '''

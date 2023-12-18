import sqlite3
import json
from datetime import datetime
from dataclasses import dataclass
from fluxo.settings import Db
from fluxo.uttils import current_time_formatted


@dataclass
class ModelLogExecutionFlow:
    '''
    Represents the log of flow execution, storing information about tasks, errors, and execution times.

    Attributes:
        id (int, optional): The unique identifier for the log entry.
        name (str, optional): The name of the flow associated with the log entry.
        date_of_creation (datetime, optional): The date and time when the log entry was created.
        start_time (datetime, optional): The start time of the flow execution.
        end_time (datetime, optional): The end time of the fluxo execution.
        id_flow (int, optional): The identifier of the associated flow.
        ids_task (list, optional): A list of task IDs involved in the flow.
        ids_error_task (list, optional): A list of task IDs that encountered errors during execution.

    Methods:
        save(self): Save the log entry to the database and return the updated LogExecutionFluxo instance.
        update(cls, id, name, date_of_creation, start_time, end_time, id_fluxo, ids_task, ids_error_task):
            Update an existing log entry in the database and return the updated LogExecutionFluxo instance.
        get_all(cls): Retrieve all log entries from the database.
        get_by_name(cls, name): Retrieve a log entry by its associated fluxo name from the database.
        get_by_id(cls, id): Retrieve a log entry by its unique identifier from the database.
        get_by_idflow_and_endtime_is_none(cls, id_flow): Retrieve a log entry for a specific fluxo
            where the end time is not set.
        get_all_by_id_flow(cls, id_flow): Retrieve all log entries for a specific flow from the database.
        delete(cls, id): Delete a log entry by its unique identifier from the database.
    '''
    id: int = None
    name: str = None
    date_of_creation: datetime = None
    start_time: datetime = None
    end_time: datetime = None
    id_flow: int = None
    ids_task: list = None
    ids_error_task: list = None

    def save(self):
        date_of_creation = current_time_formatted()
        ids_task = json.dumps(self.ids_task) if self.ids_task else None
        ids_error_task = json.dumps(self.ids_error_task) if self.ids_error_task else None

        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO TB_LogExecutionFlow (name, date_of_creation, start_time, end_time, id_flow, ids_task, ids_error_task)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.name, date_of_creation, self.start_time, self.end_time, self.id_flow, ids_task, ids_error_task))
        conn.commit()

        cursor.execute('SELECT last_insert_rowid()')
        id_log_execution_flow = cursor.fetchone()[0]

        conn.close()

        return ModelLogExecutionFlow.get_by_id(id_log_execution_flow)

    @staticmethod
    def update(id, name, date_of_creation, start_time, end_time, id_flow, ids_task, ids_error_task):
        ids_task = json.dumps(ids_task) if ids_task else None
        ids_error_task = json.dumps(ids_error_task) if ids_error_task else None

        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE TB_LogExecutionFlow
            SET name=?, date_of_creation=?, start_time=?, end_time=?, id_flow=?, ids_task=?, ids_error_task=?
            WHERE id=?
        ''', (name, date_of_creation, start_time, end_time, id_flow, ids_task, ids_error_task, id))
        conn.commit()

        conn.close()

        return ModelLogExecutionFlow.get_by_id(id)

    @staticmethod
    def get_all():
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_LogExecutionFlow')
        data = cursor.fetchall()
        conn.close()

        log_flows = []
        for row in data:
            log_flow = ModelLogExecutionFlow(*row)
            
            # Converter strings JSON from ids_task and ids_error_task to lists
            log_flow.ids_task = json.loads(log_flow.ids_task) if log_flow.ids_task else None
            log_flow.ids_error_task = json.loads(log_flow.ids_error_task) if log_flow.ids_error_task else None

            log_flows.append(log_flow)

        if log_flows:
            return log_flows
        else:
            return None

    @staticmethod
    def get_by_name(name):
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_LogExecutionFlow WHERE name=?', (name,))
        data = cursor.fetchone()
        conn.close()

        if data:
            log_flow = ModelLogExecutionFlow(*data)

            # Converter strings JSON from ids_task and ids_error_task to lists
            log_flow.ids_task = json.loads(log_flow.ids_task) if log_flow.ids_task else None
            log_flow.ids_error_task = json.loads(log_flow.ids_error_task) if log_flow.ids_error_task else None

            return log_flow
        else:
            return None

    @staticmethod
    def get_by_id(id):
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_LogExecutionFlow WHERE id=?', (id,))
        data = cursor.fetchone()
        conn.close()

        if data:
            log_flow = ModelLogExecutionFlow(*data)

            # Converter strings JSON from ids_task and ids_error_task to lists
            log_flow.ids_task = json.loads(log_flow.ids_task) if log_flow.ids_task else None
            log_flow.ids_error_task = json.loads(log_flow.ids_error_task) if log_flow.ids_error_task else None

            return log_flow
        else:
            return None
        
    @staticmethod
    def get_by_idflow_and_endtime_is_none(id_flow):
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_LogExecutionFlow WHERE id_flow=? AND end_time IS NULL', (id_flow,))
        data = cursor.fetchone()
        conn.close()

        if data:
            log_flow = ModelLogExecutionFlow(*data)

            # Converter strings JSON from ids_task and ids_error_task to lists
            log_flow.ids_task = json.loads(log_flow.ids_task) if log_flow.ids_task else None
            log_flow.ids_error_task = json.loads(log_flow.ids_error_task) if log_flow.ids_error_task else None

            return log_flow
        else:
            return None

    @staticmethod
    def get_all_by_id_flow(id_flow):
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_LogExecutionFlow WHERE id_flow=?', (id_flow,))
        data = cursor.fetchall()
        conn.close()

        log_flows = []
        for row in data:
            log_flow = ModelLogExecutionFlow(*row)
            
            # Converter strings JSON from ids_task and ids_error_task to lists
            log_flow.ids_task = json.loads(log_flow.ids_task) if log_flow.ids_task else None
            log_flow.ids_error_task = json.loads(log_flow.ids_error_task) if log_flow.ids_error_task else None

            log_flows.append(log_flow)

        if log_flows:
            return log_flows
        else:
            return None

    @staticmethod
    def delete(id):
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM TB_LogExecutionFlow WHERE id=?', (id,))
        conn.commit()
        conn.close()

    def __repr__(self) -> str:
        '''
        Returns a string representation of the 'LogExecutionFlow' instance.
        '''
        return f'''
            id:                     {self.id},
            name:                   {self.name},
            date_of_creation:       {self.date_of_creation},
            start_time:             {self.start_time},
            end_time:               {self.end_time},
            id_flow:                {self.id_flow},
            ids_task:               {self.ids_task},
            ids_error_task:         {self.ids_error_task},
        '''

import sqlite3
import json
from datetime import datetime
from dataclasses import dataclass
from fluxo.settings import Db
from fluxo.uttils import current_time_formatted


@dataclass
class LogExecutionFluxo:
    '''
    Represents the log of fluxo execution, storing information about tasks, errors, and execution times.

    Attributes:
        id (int, optional): The unique identifier for the log entry.
        name (str, optional): The name of the fluxo associated with the log entry.
        date_of_creation (datetime, optional): The date and time when the log entry was created.
        start_time (datetime, optional): The start time of the fluxo execution.
        end_time (datetime, optional): The end time of the fluxo execution.
        id_fluxo (int, optional): The identifier of the associated fluxo.
        ids_task (list, optional): A list of task IDs involved in the fluxo.
        ids_error_task (list, optional): A list of task IDs that encountered errors during execution.

    Methods:
        save(self): Save the log entry to the database and return the updated LogExecutionFluxo instance.
        update(cls, id, name, date_of_creation, start_time, end_time, id_fluxo, ids_task, ids_error_task):
            Update an existing log entry in the database and return the updated LogExecutionFluxo instance.
        get_all(cls): Retrieve all log entries from the database.
        get_by_name(cls, name): Retrieve a log entry by its associated fluxo name from the database.
        get_by_id(cls, id): Retrieve a log entry by its unique identifier from the database.
        get_by_idfluxo_and_endtime_is_none(cls, id_fluxo): Retrieve a log entry for a specific fluxo
            where the end time is not set.
        get_all_by_id_fluxo(cls, id_fluxo): Retrieve all log entries for a specific fluxo from the database.
        delete(cls, id): Delete a log entry by its unique identifier from the database.

        __repr__(self): Returns a string representation of the 'LogExecutionFluxo' instance.
    '''
    id: int = None
    name: str = None
    date_of_creation: datetime = None
    start_time: datetime = None
    end_time: datetime = None
    id_fluxo: int = None
    ids_task: list = None
    ids_error_task: list = None

    def save(self):
        date_of_creation = current_time_formatted()
        ids_task = json.dumps(self.ids_task) if self.ids_task else None
        ids_error_task = json.dumps(self.ids_error_task) if self.ids_error_task else None

        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO TB_LogExecutionFluxo (name, date_of_creation, start_time, end_time, id_fluxo, ids_task, ids_error_task)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.name, date_of_creation, self.start_time, self.end_time, self.id_fluxo, ids_task, ids_error_task))
        conn.commit()

        cursor.execute('SELECT last_insert_rowid()')
        id_log_execution_fluxo = cursor.fetchone()[0]

        conn.close()

        return LogExecutionFluxo.get_by_id(id_log_execution_fluxo)

    @staticmethod
    def update(id, name, date_of_creation, start_time, end_time, id_fluxo, ids_task, ids_error_task):
        ids_task = json.dumps(ids_task) if ids_task else None
        ids_error_task = json.dumps(ids_error_task) if ids_error_task else None

        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE TB_LogExecutionFluxo
            SET name=?, date_of_creation=?, start_time=?, end_time=?, id_fluxo=?, ids_task=?, ids_error_task=?
            WHERE id=?
        ''', (name, date_of_creation, start_time, end_time, id_fluxo, ids_task, ids_error_task, id))
        conn.commit()

        conn.close()

        return LogExecutionFluxo.get_by_id(id)

    @staticmethod
    def get_all():
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_LogExecutionFluxo')
        data = cursor.fetchall()
        conn.close()

        log_fluxos = []
        for row in data:
            log_fluxo = LogExecutionFluxo(*row)
            
            # Converter strings JSON from ids_task and ids_error_task to lists
            log_fluxo.ids_task = json.loads(log_fluxo.ids_task) if log_fluxo.ids_task else None
            log_fluxo.ids_error_task = json.loads(log_fluxo.ids_error_task) if log_fluxo.ids_error_task else None

            log_fluxos.append(log_fluxo)

        if log_fluxos:
            return log_fluxos
        else:
            return None

    @staticmethod
    def get_by_name(name):
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_LogExecutionFluxo WHERE name=?', (name,))
        data = cursor.fetchone()
        conn.close()
        if data:
            data_list = []
            for value in data:
                data_list.append(value)
            data_list[6] = json.loads(data_list[6]) # attribute ids_task
            data_list[7] = json.loads(data_list[7]) # attribute ids_error_task
            return LogExecutionFluxo(*data_list)
        else:
            return None

    @staticmethod
    def get_by_id(id):
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_LogExecutionFluxo WHERE id=?', (id,))
        data = cursor.fetchone()
        conn.close()

        if data:
            log_fluxo = LogExecutionFluxo(*data)

            # Converter strings JSON from ids_task and ids_error_task to lists
            log_fluxo.ids_task = json.loads(log_fluxo.ids_task) if log_fluxo.ids_task else None
            log_fluxo.ids_error_task = json.loads(log_fluxo.ids_error_task) if log_fluxo.ids_error_task else None

            return log_fluxo
        else:
            return None
        
    @staticmethod
    def get_by_idfluxo_and_endtime_is_none(id_fluxo):
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_LogExecutionFluxo WHERE id_fluxo=? AND end_time IS NULL', (id_fluxo,))
        data = cursor.fetchone()
        conn.close()

        if data:
            log_fluxo = LogExecutionFluxo(*data)

            # Converter strings JSON from ids_task and ids_error_task to lists
            log_fluxo.ids_task = json.loads(log_fluxo.ids_task) if log_fluxo.ids_task else None
            log_fluxo.ids_error_task = json.loads(log_fluxo.ids_error_task) if log_fluxo.ids_error_task else None

            return log_fluxo
        else:
            return None

    @staticmethod
    def get_all_by_id_fluxo(id_fluxo):
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_LogExecutionFluxo WHERE id_fluxo=?', (id_fluxo,))
        data = cursor.fetchall()
        conn.close()

        log_fluxos = []
        for row in data:
            log_fluxo = LogExecutionFluxo(*row)
            
            # Converter strings JSON from ids_task and ids_error_task to lists
            log_fluxo.ids_task = json.loads(log_fluxo.ids_task) if log_fluxo.ids_task else None
            log_fluxo.ids_error_task = json.loads(log_fluxo.ids_error_task) if log_fluxo.ids_error_task else None

            log_fluxos.append(log_fluxo)

        if log_fluxos:
            return log_fluxos
        else:
            return None

    @staticmethod
    def delete(id):
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM TB_LogExecutionFluxo WHERE id=?', (id,))
        conn.commit()
        conn.close()

    def __repr__(self) -> str:
        '''
        Returns a string representation of the 'LogExecutionFluxo' instance.
        '''
        return f'''
            id:                     {self.id},
            name:                   {self.name},
            date_of_creation:       {self.date_of_creation},
            start_time:             {self.start_time},
            end_time:               {self.end_time},
            id_fluxo:               {self.id_fluxo},
            ids_task:               {self.ids_task},
            ids_error_task:         {self.ids_error_task},
        '''

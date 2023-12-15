import sqlite3
from datetime import datetime
from dataclasses import dataclass
from fluxo.settings import Db
from fluxo.uttils import current_time_formatted


@dataclass
class ModelApp:
    '''
    Represents an application status in database

    Attributes:
        id (int): The unique identifier for the application.
        active (bool): Indicates whether the application is currently active.
        active_since (datetime): The datetime when the application was last activated.

    Methods:
        save(self): Saves the current state of the application to the database.
        update(cls, id: int, active: bool): Updates the activation status of the application in the database.
        get(cls, id: int = 1): Retrieves an application instance based on the provided ID from the database.
        __repr__(self): Returns a string representation of the 'App' instance.
    '''
    id: int = None
    active: bool = None
    active_since: datetime = None

    def save(self):
        '''
        Saves the current state of the application to the database.

        Returns:
            App: An instance of the 'App' class.
        '''
        if self.active:
            self.active_since = current_time_formatted()
        else:
            self.active_since = None
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO TB_App (active, active_since)
            VALUES (?, ?)
        ''', (self.active, self.active_since))
        conn.commit()

        cursor.execute('SELECT last_insert_rowid()')
        task_id = cursor.fetchone()[0]

        conn.close()

        return ModelApp.get()

    @staticmethod
    def update(id: int, active: bool):
        '''
        Updates the activation status of the application in the database.

        Args:
            id (int): The unique identifier of the application to be updated.
            active (bool): The new activation status for the application.
        '''
        active_since: datetime
        if active:
            active_since = current_time_formatted()
        else:
            active_since = None
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE TB_App
            SET active=?, active_since=?
            WHERE id=?
        ''', (active, active_since, id))
        conn.commit()
        conn.close()

        return ModelApp.get()

    @staticmethod
    def get(id: int = 1):
        '''
        Retrieves an application instance based on the provided ID from the database.

        Args:
            id (int): The unique identifier of the application to be retrieved.

        Returns:
            App or None: An instance of the 'App' class if found, else None.
        '''
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_App WHERE id=?', (id,))
        data = cursor.fetchone()
        conn.close()
        if data:
            return ModelApp(*data)
        else:
            return None


    def __repr__(self) -> str:
        '''
        Returns a string representation of the 'ModelApp' instance.
        '''
        return f'''
            id:                   {self.id},
            active:               {self.active},
            active_since:         {self.active_since},
        '''

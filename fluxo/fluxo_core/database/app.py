import sqlite3
from datetime import datetime
from dataclasses import dataclass
from fluxo.settings import Db
from fluxo.uttils import current_time_formatted


@dataclass
class App:
    id: int = None
    active: bool = None
    active_since: datetime = None

    def save(self):
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

        return App.get()

    @staticmethod
    def update(id: int, active: bool):
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

        return App.get()

    @staticmethod
    def get(id: int = 1):
        conn = sqlite3.connect(Db.PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TB_App WHERE id=?', (id,))
        data = cursor.fetchone()
        conn.close()
        if data:
            return App(*data)
        else:
            return None


    def __repr__(self) -> str:
        '''
        Returns a string representation of the 'Task' instance.
        '''
        return f'''
            id:                   {self.id},
            active:               {self.active},
            active_since:         {self.active_since},
        '''

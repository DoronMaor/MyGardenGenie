import os
import pickle
import sqlite3
import uuid


def generate_uid():
    """Generate a unique ID"""
    uid = uuid.uuid4()
    return uid.hex


class SQLUserManager:
    def __init__(self, db_path=None, file_name="users.db"):
        """
        Initializes the class
        """
        if not db_path:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_name = file_name
            self.db_path = os.path.join(base_dir, file_name)
        else:
            self.db_path = db_path + file_name
        self.table_name = file_name[:-3]
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def sign_up(self, username, password):
        query = 'INSERT INTO users (id, username, password, plants) VALUES (?, ?, ?, ?)'
        self.cursor.execute(query, (generate_uid(), username, password, pickle.dumps([])))
        self.conn.commit()

    def login(self, username, password):
        query = "SELECT * FROM users WHERE username=? AND password=?"
        self.cursor.execute(query, (username, password))
        result = self.cursor.fetchone()

        if result is not None:
            # result is a tuple, so we can access its elements by index
            last_element = result[-1]
            if isinstance(last_element, bytes):
                # last_element is a pickled object, so we need to unpickle it
                last_element = pickle.loads(last_element)
            # Replace the last element of the tuple with the unpickled object
            result = result[:-1] + (last_element,)

        return result

    def add_plant(self, idnum, plant):

        plant[0] = generate_uid()
        query = 'SELECT * FROM users WHERE id = ?'
        self.cursor.execute(query, (id,))
        result = self.cursor.fetchone()

        if result is not None:
            # result is a tuple, so we can access its elements by index
            plant_lst = result[-1]
            if isinstance(plant_lst, bytes):
                # last_element is a pickled object, so we need to unpickle it
                plant_lst = pickle.loads(plant_lst) + [plant]

            self.update_user(idnum, plant_lst)

    def get_user(self, id):
        query = 'SELECT * FROM users WHERE id = ?'
        self.cursor.execute(query, (id,))
        result = self.cursor.fetchone()

        if result is not None:
            # result is a tuple, so we can access its elements by index
            plant_lst = result[-1]
            if isinstance(plant_lst, bytes):
                # last_element is a pickled object, so we need to unpickle it
                plant_lst = pickle.loads(plant_lst)
            # Replace the last element of the tuple with the unpickled object
            result = result[:-1] + (plant_lst,)

        return result

    def update_user(self, id, plants):
        query = 'UPDATE users SET plants = ? WHERE id = ?'
        self.cursor.execute(query, (pickle.dumps(plants), id))
        self.conn.commit()

    def delete_user(self, id):
        query = 'DELETE FROM users WHERE id = ?'
        self.cursor.execute(query, (id,))
        self.conn.commit()

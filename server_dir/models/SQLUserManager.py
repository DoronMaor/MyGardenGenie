import os
import pickle
import sqlite3
import uuid


def generate_uid():
    """Generate a unique ID"""
    return uuid.uuid4().hex[:-1]

def normalize_input(input):
    lower_input = input.lower()
    new_input = ""
    for let in lower_input:
        new_input += let

    return new_input



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

    def sign_up(self, username, password, code=None):
        if code is not None:
            idn = self.get_id_by_code(code)
            if idn is None:
                print("ERORR, idn is NONE!")
                return None
            idn = idn[:-1] + "B"
        else:
            idn = generate_uid() + "A"

        query = 'INSERT INTO users (id, username, password, plants) VALUES (?, ?, ?, ?)'
        self.cursor.execute(query, (idn, username, password, pickle.dumps([])))
        self.conn.commit()
        return True

    def login(self, username, password):
        username = normalize_input(username)
        password = normalize_input(password)
        print("LOGIN:", username, password)
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

    def add_plant(self, id_num, plant_dict):
        # plants : (dict1, dict2)

        query = 'SELECT * FROM users WHERE id = ?'
        self.cursor.execute(query, (id_num,))
        pickled_result = self.cursor.fetchone()[3]
        results = pickle.loads(pickled_result)
        plants = []
        if not results:
            plants = [plant_dict, None]
        else:
            for idx, result in enumerate(results):
                try:
                    if not result:
                        plants[idx] = plant_dict
                        break
                except:
                    plants.append(plant_dict)

        self.update_user(id_num, pickle.dumps(plants))

    def get_id_by_code(self, code):
        try:
            query = "SELECT id FROM users WHERE id LIKE ?"
            self.cursor.execute(query, (code + '%',))
            result = self.cursor.fetchone()
            if result is not None:
                return result[0]
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        return None

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

    def update_user(self, id_num, pickled_plants):
        query = 'UPDATE users SET plants = ? WHERE id LIKE ?'
        self.cursor.execute(query, (pickled_plants, id_num[:7] + '%'))
        self.conn.commit()

    def delete_user(self, id):
        query = 'DELETE FROM users WHERE id = ?'
        self.cursor.execute(query, (id,))
        self.conn.commit()

import os
import pickle
import sqlite3
import uuid


def generate_uid():
    """Generate a unique ID"""
    return uuid.uuid4().hex[:-1]


def normalize_input(str_input):
    lower_input = str_input.lower()
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

    def sign_up(self, username, password, email, code=None):
        if code != "" and code is not None and len(code) >= 4:
            print("code", code)
            idn = self.get_id_by_code(code)
            if idn is None:
                print("Error, no code found")
                return None
            idn = idn[:-1] + "B"
        else:
            idn = generate_uid() + "A"

        query = 'INSERT INTO users (id, username, password, plants, email, admin) VALUES (?, ?, ?, ?, ?, ?)'
        self.cursor.execute(query, (idn, username, password, pickle.dumps([]), email, "False"))
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
        query = 'SELECT * FROM users WHERE id = ?'
        self.cursor.execute(query, (id_num,))
        pickled_result = self.cursor.fetchone()[3]
        results = pickle.loads(pickled_result)
        plants = results
        changed = False

        if not plants:
            plants = [None, None]

        if plants[0] == plants[1]:
            plants[1] = None

        # Look for a free spot in the results
        for i, plant in enumerate(results):
            if plant is None:
                # Put the new plant in the results where it belongs
                results[i] = plant_dict
                plants = results
                changed = True
                break

        # Look for the same PLANT_TYPE as the plant_dict
        for i, plant in enumerate(results):
            if plant and plant['PLANT_TYPE'] == plant_dict['PLANT_TYPE']:
                # Replace the old plant with the new one
                results[i] = plant_dict
                plants = results
                changed = True

        if not changed:
            plants = [None, None]
            for i, plant in enumerate(results):
                if plant is None:
                    # Put the new plant in the results where it belongs
                    results[i] = plant_dict
                    plants = results
                    break

        self.update_user(id_num, pickle.dumps(plants))
    def remove_plant(self, id_num, plant_name):
        id_num_base = id_num[:-1]
        lets = ["A", "B", "C"]
        for let in lets:
            curr_id_num = id_num_base + let
            query = 'SELECT * FROM users WHERE id = ?'
            self.cursor.execute(query, (curr_id_num,))
            pickled_result = self.cursor.fetchone()[3]
            results = pickle.loads(pickled_result)
            plants = results

            if not plants:
                plants = [None, None]

            # Look for the plant with the matching PLANT_NAME
            for i, plant in enumerate(results):
                if plant and plant['PLANT_NAME'] == plant_name:
                    # Remove the plant from the results
                    results[i] = None
                    plants = results

            self.update_user(curr_id_num, pickle.dumps(plants))
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
    def get_user_by_id(self, id_num):
        query = 'SELECT * FROM users WHERE id = ?'
        self.cursor.execute(query, (id_num,))
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

    def get_plants_by_similar_id(self, id_num, as_plant_dict=False):

        # Remove the last character from the id
        id_prefix = id_num[:-1]
        # Query the database for all users with an id that starts with the modified id
        query = 'SELECT * FROM users WHERE id LIKE ?'
        self.cursor.execute(query, (f"{id_prefix}%",))
        results = self.cursor.fetchall()

        plants = []
        for result in results:
            plant_lst = result[3]
            if isinstance(plant_lst, bytes):
                plant_lst = pickle.loads(plant_lst)
            plants += plant_lst

        if not as_plant_dict:
            return plants

        let = "A"
        dict_plants = {}
        for plant in plants:
            dict_plants[let] = plant
            let = chr(ord(let) + 1)

        return dict_plants

    def update_user(self, id_num, pickled_plants):
        query = 'UPDATE users SET plants = ? WHERE id LIKE ?'
        self.cursor.execute(query, (pickled_plants, id_num[:7] + '%'))
        self.conn.commit()
    def update_full_user(self, new_name, new_email, new_password_hashed, user_id):
        self.cursor.execute("""
                UPDATE users
                SET username = ?, password = ?, email = ?
                WHERE id = ?
            """, (normalize_input(new_name), normalize_input(new_password_hashed), new_email, user_id))
        self.conn.commit()

    def delete_user(self, user_id):
        query = 'DELETE FROM users WHERE id = ?'
        self.cursor.execute(query, (user_id,))
        self.conn.commit()
    def is_admin(self, user_id):
        usr = self.get_user_by_id(user_id)

        if usr[-1] == "True":
            return True

        return False
    def get_username_by_id(self, user_id):
        if user_id[-1] != "A" and user_id[-1] != "B":
            user_id = user_id + "A"
        usr = self.get_user_by_id(user_id)
        return usr[1]

    import sqlite3

    def get_unique_user_ids(self):
        # execute a query to get all the user ids
        query = "SELECT id FROM users"
        self.cursor.execute(query)

        # fetch all the user ids and convert them to a list
        rows = self.cursor.fetchall()
        user_ids = [row[0] for row in rows]

        # remove the last character from each user id
        user_ids = [uid[:-1] for uid in user_ids]

        # remove duplicates from the list
        unique_user_ids = list(set(user_ids))


        return unique_user_ids



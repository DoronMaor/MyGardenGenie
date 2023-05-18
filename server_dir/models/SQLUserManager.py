import os
import pickle
import sqlite3
import uuid


def generate_uid():
    """Generate a unique ID"""
    return uuid.uuid4().hex[:-1]


def normalize_input(str_input):
    """Normalize input string by converting it to lowercase"""
    lower_input = str_input.lower()
    new_input = ""
    for let in lower_input:
        new_input += let

    return new_input


class SQLUserManager:
    def __init__(self, db_path=None, file_name="users.db"):
        """
        Initializes the SQLUserManager class.

        Args:
            db_path (str, optional): Path to the database file. Defaults to None.
            file_name (str, optional): Name of the database file. Defaults to "users.db".
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
        """
        Create a new user account.

        Args:
            username (str): Username of the user.
            password (str): Password of the user.
            email (str): Email address of the user.
            code (str, optional): Code for special access. Defaults to None.

        Returns:
            bool: True if the user account is successfully created, False otherwise.
        """
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
        """
        Log in a user.

        Args:
            username (str): Username of the user.
            password (str): Password of the user.

        Returns:
            tuple: User information as a tuple if login is successful, None otherwise.
        """
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
        """
        Add a plant to a user's list of plants.

        Args:
            id_num (str): ID of the user.
            plant_dict (dict): Dictionary containing plant information.

        Returns:
            None
        """
        query = 'SELECT * FROM users WHERE id = ?'
        self.cursor.execute(query, (id_num,))
        pickled_result = self.cursor.fetchone()[3]

        if pickled_result:
            results = pickle.loads(pickled_result)
            if not results:
                results = [None, None]
        else:
            results = [None, None]

        changed = False

        for i, plant in enumerate(results):
            if plant is None or plant['PLANT_TYPE'] == plant_dict['PLANT_TYPE']:
                results[i] = plant_dict
                changed = True
                break

        if not changed:
            results[0] = plant_dict

        self.update_user(id_num, pickle.dumps(results))

    def remove_plant(self, id_num, plant_name):
        """
        Remove a plant from a user's list of plants.

        Args:
            id_num (str): ID of the user.
            plant_name (str): Name of the plant to remove.

        Returns:
            None
        """
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
        """
        Get user ID based on a given code.

        Args:
            code (str): Code for user identification.

        Returns:
            str: User ID if found, None otherwise.
        """
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
        """
        Get user information based on user ID.

        Args:
            id_num (str): ID of the user.

        Returns:
            tuple: User information as a tuple if user is found, None otherwise.
        """
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
        """
        Get plants from users with similar IDs.

        Args:
            id_num (str): ID of the user.
            as_plant_dict (bool, optional): Whether to return plants as a dictionary. Defaults to False.

        Returns:
            list or dict: List of plants if as_plant_dict is False, otherwise a dictionary of plants.
        """
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
        """
        Update user's plant information.

        Args:
            id_num (str): ID of the user.
            pickled_plants (bytes): Pickled plant information.

        Returns:
            None
        """
        query = 'UPDATE users SET plants = ? WHERE id LIKE ?'
        self.cursor.execute(query, (pickled_plants, id_num[:7] + '%'))
        self.conn.commit()

    def update_full_user(self, new_name, new_email, new_password_hashed, user_id):
        """
        Update the information of a user.

        Args:
            new_name (str): New username.
            new_email (str): New email address.
            new_password_hashed (str): New hashed password.
            user_id (str): ID of the user.

        Returns:
            None
        """
        self.cursor.execute("""
                UPDATE users
                SET username = ?, password = ?, email = ?
                WHERE id = ?
            """, (normalize_input(new_name), normalize_input(new_password_hashed), new_email, user_id))
        self.conn.commit()

    def delete_user(self, user_id):
        """
        Delete a user.

        Args:
            user_id (str): ID of the user.

        Returns:
            None
        """
        query = 'DELETE FROM users WHERE id = ?'
        self.cursor.execute(query, (user_id,))
        self.conn.commit()

    def is_admin(self, user_id):
        """
        Check if a user is an admin.

        Args:
            user_id (str): ID of the user.

        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        usr = self.get_user_by_id(user_id)

        if usr[-1] == "True":
            return True

        return False

    def get_username_by_id(self, user_id):
        """
        Get username based on user ID.

        Args:
            user_id (str): ID of the user.

        Returns:
            str: Username if user is found, None otherwise.
        """
        if user_id[-1] != "A" and user_id[-1] != "B":
            user_id = user_id + "A"
        usr = self.get_user_by_id(user_id)
        return usr[1]

    def get_unique_user_ids(self):
        """
        Get unique user IDs from the database.

        Returns:
            list: List of unique user IDs.
        """
        # execute a query to get all the user ids
        query = "SELECT id FROM users"
        self.cursor.execute(query)

        # fetch all the user ids and convert them to a list
        rows = self.cursor.fetchall()
        user_ids = [row[0] for row in rows]

        # remove duplicate user ids and return the unique user ids
        unique_user_ids = list(set(user_ids))
        return unique_user_ids

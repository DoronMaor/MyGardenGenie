import re
import sqlite3 as lite
import os
import pickle
import time


def format_plants_for_html(plants):
    """
    Formats the plant data for HTML representation.

    Args:
        plants (list): List of plants data.

    Returns:
        list: Formatted plant data.
    """
    formatted_plants = []
    for plant in plants:
        formatted_plant = {}
        if -1 in plant or "-1" in plant:
            formatted_plant['missing'] = True
        else:
            formatted_plant['missing'] = False

        formatted_plant['type'] = plant[0]
        formatted_plant['light'] = plant[1]
        formatted_plant['light_hours'] = plant[2]
        formatted_plant['moisture'] = plant[3].strip()
        formatted_plants.append(formatted_plant)
    return formatted_plants


class PlantManagerDB:
    """
    A class that handles SQL connection to the plant database.
    """

    def __init__(self, db_path=None, file_name="plants_conditions.db"):
        """
        Initializes the PlantManagerDB class.

        Args:
            db_path (str): Path to the database file.
            file_name (str): Name of the database file.
        """
        if not db_path:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_name = file_name
            self.db_path = os.path.join(base_dir, file_name)
        else:
            self.db_path = db_path + file_name
        self.table_name = file_name[:-3]
        self.conn = lite.connect(self.db_path)
        self.cur = self.conn.cursor()

    def disconnect(self):
        """
        Disconnects from the database.
        """
        self.conn.close()

    def db_query(self, query):
        """
        Executes a database query.

        Args:
            query (str): SQL query to execute.

        Returns:
            list: Query results.
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def add_plant(self, plant_type, light, light_hours, moisture):
        """
        Adds a new plant to the database.

        Args:
            plant_type (str): Type of the plant.
            light (int): Light level required by the plant.
            light_hours (int): Number of light hours required by the plant.
            moisture (int): Moisture level required by the plant.
        """
        self.cur.execute(
            '''
            INSERT INTO plants_conditions (type, light, light_hours, moisture)
            VALUES (?, ?, ?, ?)
            ''',
            (self.format_plant_type(plant_type), light, light_hours, moisture)
        )

    def add_plant_from_form(self, data):
        """
        Adds a new plant to the database from form data.

        Args:
            data (dict): Form data containing plant information.
        """
        self.add_plant(self.format_plant_type(data["type"]), data["light"], data["light_hours"], data["moisture"])

    def update_plant(self, plant_type, light, light_hours, moisture):
        """
        Updates an existing plant in the database.

        Args:
            plant_type (str): Type of the plant.
            light (int): Light level required by the plant.
            light_hours (int): Number of light hours required by the plant.
            moisture (int): Moisture level required by the plant.
        """
        self.cur.execute(
            '''
            UPDATE plants_conditions
            SET type = ?, light = ?, light_hours = ?, moisture = ?
            WHERE type = ?
            ''',
            (plant_type, light, light_hours, moisture, self.format_plant_type(plant_type))
        )

    def format_plant_type(self, plant_type):
        """
        Formats the plant type.

        Args:
            plant_type (str): Type of the plant.

        Returns:
            str: Formatted plant type.
        """
        # Convert to title case
        plant_type = plant_type.lower()
        plant_type = plant_type.title()

        # Remove leading/trailing spaces
        plant_type = plant_type.strip()

        # Remove multiple spaces
        plant_type = re.sub(r'\s+', ' ', plant_type)

        return plant_type

    def update_plant_types(self):
        """
        Updates the plant types in the database.
        """
        self.cur.execute('SELECT type FROM plants_conditions')
        rows = self.cur.fetchall()

        for row in rows:
            plant_type = row[0]
            formatted_type = self.format_plant_type(plant_type)

            if formatted_type != plant_type:
                self.cur.execute(
                    '''
                    UPDATE plants_conditions
                    SET type = ?
                    WHERE type = ?
                    ''',
                    (formatted_type, plant_type)
                )
                self.conn.commit()

    def update_db(self, data):
        """
        Updates the database based on form data.

        Args:
            data (dict): Form data containing plant information.
        """
        for plant, value in list(data.items())[:-4]:
            try:
                split_plant = plant.strip().split('/')
                plant_type = self.format_plant_type(split_plant[0].strip())
                plant_attr = split_plant[1]
            except:
                if plant == 'delete':
                    self.cur.execute(
                        'DELETE FROM plants_conditions WHERE type = ?',
                        (value,)
                    )
                continue
            if plant_attr == 'light':
                self.cur.execute(
                    'UPDATE plants_conditions SET light = ? WHERE type = ?',
                    (value, plant_type)
                )
            elif plant_attr == 'light_hours':
                self.cur.execute(
                    'UPDATE plants_conditions SET light_hours = ? WHERE type = ?',
                    (value, plant_type)
                )
            elif plant_attr == 'moisture':
                self.cur.execute(
                    'UPDATE plants_conditions SET moisture = ? WHERE type = ?',
                    (value, plant_type)
                )
            elif plant_attr == 'delete' and value == plant_type:
                self.cur.execute(
                    'DELETE FROM plants_conditions WHERE type = ?',
                    (plant_type,)
                )

        self.update_plant_types()

        self.conn.commit()

    def delete_plant(self, plant_type):
        """
        Deletes a plant from the database.

        Args:
            plant_type (str): Type of the plant.
        """
        self.cur.execute(
            '''
            DELETE FROM plants_conditions
            WHERE type = ?
            ''',
            (self.format_plant_type(plant_type),)
        )
        self.conn.commit()

    def get_plant(self, plant_type, add_new=True):
        results=None
        while results is None:
            self.cur.execute(
                '''
                SELECT * FROM plants_conditions
                WHERE type = ?
                ''',
                (self.format_plant_type(plant_type),)
            )
            results = self.cur.fetchone()
            self.conn.commit()

            if results is None and add_new:
                self.add_plant(plant_type=plant_type, light=-1, light_hours=-1, moisture=-1)
                time.sleep(0.2)
            else:
                return results

    def get_all_plants(self):
        """
        Retrieves all plants from the database.

        Returns:
            list: All plants data.
        """
        self.cur.execute(
            '''
            SELECT * FROM plants_conditions
            '''
        )
        return self.cur.fetchall()

    def get_all_plants_dict(self):
        """
        Retrieves all plants from the database as a dictionary.

        Returns:
            list: All plants data as a dictionary.
        """
        plants = self.get_all_plants()
        return format_plants_for_html(plants)

    def search_plant_from_list(self, plant_list):
        """
        Searches for a plant from a list of plant types.

        Args:
            plant_list (list): List of plant types.

        Returns:
            dict: Plant information if found, None otherwise.
        """
        results = []
        for plant in plant_list:
            result = self.get_plant(plant, add_new=False)
            if result:
                results = result
                break
        if not results:
            results = self.get_plant(plant_list[0], add_new=True)
        results_dict = {
            "PLANT_TYPE": results[0],
            "LIGHT_LVL": results[1],
            "LIGHT_HOURS": results[2],
            "MOISTURE_LVL": results[3],
        }
        results_dict["OKAY_VALUES"] = False if -1 in results_dict.values() else True

        return results_dict


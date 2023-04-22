import sqlite3 as lite
import os
import pickle


def format_plants_for_html(plants):
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
    A class that handles sql connection to users data base.
    Database contains:
        "type"	TEXT,
        "light"	INTEGER,
        "light_hours"	INTEGER,
        "moisture"	INTEGER
    """

    def __init__(self, db_path=None, file_name="plants_conditions.db"):
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
        self.conn = lite.connect(self.db_path)
        self.cur = self.conn.cursor()

    def disconnect(self):
        """
        Disconnects from the database
        """
        self.conn.close()

    def db_query(self, query):
        """
        Executes a query
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def add_plant(self, plant_type, light, light_hours, moisture):
        self.cur.execute(
            '''
            INSERT INTO plants_conditions (type, light, light_hours, moisture)
            VALUES (?, ?, ?, ?)
            ''',
            (plant_type, light, light_hours, moisture)
        )
        self.conn.commit()

    def add_plant_from_form(self, data):
        self.add_plant(data["type"], data["light"], data["light_hours"], data["moisture"])

    def update_plant(self, plant_type, light, light_hours, moisture):
        self.cur.execute(
            '''
            UPDATE plants_conditions
            SET type = ?, light = ?, light_hours = ?, moisture = ?
            WHERE type = ?
            ''',
            (plant_type, light, light_hours, moisture, plant_type)
        )

    def update_db(self, data):

        # Loop through each plant in the form data
        for plant, value in list(data.items())[:-4]:
            # Split the plant name into its type and attribute
            try:
                split_plant = plant.strip().split('/')
                plant_type = split_plant[0].strip()
                plant_attr = split_plant[1]
            except:
                print( plant, value)
                if plant == 'delete':
                    self.cur.execute(
                        'DELETE FROM plants_conditions WHERE type = ?',
                        (value,)
                    )
                continue
            # Handle update requests
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

            # Handle delete requests
            elif plant_attr == 'delete' and value == plant_type:
                self.cur.execute(
                    'DELETE FROM plants_conditions WHERE type = ?',
                    (plant_type,)
                )

        # Commit changes and close connection
        self.conn.commit()

    def delete_plant(self, plant_type):
        self.cur.execute(
            '''
            DELETE FROM plants_conditions
            WHERE type = ?
            ''',
            (plant_type,)
        )

    def get_plant(self, plant_type, add_new=True):
        self.cur.execute(
            '''
            SELECT * FROM plants_conditions
            WHERE LOWER(type) = ?
            ''',
            (plant_type,)
        )
        results = self.cur.fetchone()
        if results is None and add_new:
            self.add_plant(plant_type=plant_type, light=-1, light_hours=-1, moisture=-1)
            return self.get_plant(plant_type)
        return results

    def get_all_plants(self):
        self.cur.execute(
            '''
            SELECT * FROM plants_conditions
            '''
        )
        return self.cur.fetchall()

    def get_all_plants_dict(self):
        plants = self.get_all_plants()
        return format_plants_for_html(plants)

    def search_plant_from_list(self, plant_list):
        results = []
        for plant in plant_list:
            result = self.get_plant(plant, add_new=False)
            if result:
                results = result
                break
        if not results:
            results = self.get_plant(plant_list[0], add_new=True)
        print(results)
        results_dict = {
            "PLANT_TYPE": results[0],
            "LIGHT_LVL": results[1],
            "LIGHT_HOURS": results[2],
            "MOISTURE_LVL": results[3],
        }
        results_dict["OKAY_VALUES"] = False if -1 in results_dict.values() else True

        return results_dict

import os
import sqlite3

class PlantStatLocator:
    def __init__(self, db_path=None, file_name="../dbs/plants_conditions.db"):
        """
        Initializes the PlantStatLocator class.

        Args:
            db_path (str): Optional. Path to the database file. If not provided, the default file path will be used.
            file_name (str): Optional. Name of the database file. Defaults to "../dbs/plants_conditions.db".
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

    def search_plants(self, plant_list):
        """
        Searches for plant conditions in the database for the given list of plants.

        Args:
            plant_list (list): List of plant names to search for.

        Returns:
            dict: A dictionary containing the plant conditions. If a plant is found, the dictionary will include the
                  plant type, light level, light hours, and moisture level. If no plant is found, the dictionary will
                  contain default values with the "FOUND" key set to "FALSE".
        """
        results = []
        for plant in plant_list:
            print(plant)
            self.cursor.execute("SELECT * FROM plants_conditions WHERE LOWER(type) = ?", (plant,))
            result = self.cursor.fetchone()
            if result:
                results.append(result)
                break
        if not results:
            results_dict = {
                "FOUND": "FALSE",
                "PLANT_TYPE": -1,
                "LIGHT_LVL": -1,
                "LIGHT_HOURS": -1,
                "MOISTURE_LVL": -1,
            }
            return results_dict
        print(results)
        results_dict = {
            "PLANT_TYPE": results[0][0],
            "LIGHT_LVL": results[0][1],
            "LIGHT_HOURS": results[0][2],
            "MOISTURE_LVL": results[0][3],
        }
        results_dict["OKAY_VALUES"] = False if -1 in results_dict.values() else True

        return results_dict

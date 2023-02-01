import os
import sqlite3


class PlantStatLocator:
    def __init__(self, db_path=None, file_name="../dbs/plants_conditions.db"):
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

    def search_plants(self, plant_list):
        results = []
        for plant in plant_list:
            print(plant)
            self.cursor.execute("SELECT * FROM plants_conditions WHERE LOWER(type) = ?", (plant,))
            result = self.cursor.fetchone()
            if result:
                results.append(result)
                break
        if results == []:
            results_dict = {
                "PLANT_TYPE": "DEFAULT",
                "LIGHT_LVL": "HIGH",
                "LIGHT_HOURS": "14",
                "MOISTURE_LVL": "MOIST",
            }
            return results_dict
        print(results)
        results_dict = {
            "PLANT_TYPE": results[0][0],
            "LIGHT_LVL": results[0][1],
            "LIGHT_HOURS": results[0][2],
            "MOISTURE_LVL": results[0][3],
        }
        return results_dict
    
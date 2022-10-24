import random
import datetime as dt


class Plant:
    """
    name: str
    plant_type: str
    plant_id: str
    key: str
    values: dictionary [{"light_lvl": int, "moisture_lvl": int, "light_time": int, "last_time_of_light": time}]
    optimal_values: dictionary [{"light_lvl":int, "moisture_lvl": int, "light_time": int}]
    mode: int [0 = automatic, 1 = manual]
    """

    def __init__(self, name: str, plant_type: str, plant_id=None, key=None, values=None, optimal_values=None, mode=0):
        self.name = name
        self.plant_type = plant_type
        self.plant_id = plant_id
        self.key = key
        self.values = values
        self.optimal_values = optimal_values
        self.mode = mode

    def get_optimal_values(self):
        ######### use type from server csv
        #########
        #########
        return {"light_lvl": 6, "moisture_lvl": 50, "light_time": 14}

    def fix_values(self):
        if self.plant_id is None:
            self.plant_id = str(random.randint(100, 999999))

        if self.key is None:
            self.key = str(random.randint(100, 999999))

        if self.values is None:
            self.values = {"light_lvl": -1, "moisture_lvl": -1, "light_time": -1, "last_time_of_light":  dt.datetime.now()}

        if self.optimal_values is None:
            self.optimal_values = self.get_optimal_values()

    def add_water(self, mm: int):
        print("Added %d water" % mm)

    def set_light(self, on: bool):
        if on:
            print("Light has turned on")
        else:
            print("Light has turned off")

    def update_light_lvl(self):
        l_lvl = -1
        print("Light level is: %d" % l_lvl)
        self.values["light_lvl"] = l_lvl

    def update_moisture_lvl(self):
        m_lvl = -1
        print("Moisture level is: %d" % m_lvl)
        self.values["moisture_lvl"] = m_lvl

    def update_light_time(self, time):
        l_time = self.values["light_time"] + time
        print("Light time is: %d" % l_time)
        self.values["light_time"] = l_time

    def update_last_time_of_light(self):
        l_time = dt.datetime.now() - self.values["last_time_of_light"]
        print("Last light time is: %d" % l_time)
        self.values["last_time_of_light"] = l_time



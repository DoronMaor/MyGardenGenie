import random
import string


class Plant:
    """
    id_num: str
    name: str
    plant_type: str
    owner_id: str
    """

    def __init__(self, id_num: str, name: str, plant_type: str, owner_id: str, new=False):
        self.name = name
        if new:
            self.id_num = self.key_generator(5)
        else:
            self.id_num = id_num
        self.plant_type = plant_type
        self.owner_id = owner_id

    def __str__(self):
        attrs = vars(self)
        return ', '.join("%s: %s" % item for item in attrs.items())

    def key_generator(self, n: int):
        return self.name + "_" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))


    def set_LCD(self, txt: str):
        self.arduino.set_text_display(txt)

    def get_optimal_values(self):
        ######### use type from server csv
        #########
        #########
        return {"light_lvl": 30, "light_hours": 16, "moisture_lvl": 25}


    def get_values(self):
        return self.values


    def fix_values(self):
        if self.plant_id is None:
            self.plant_id = random.randint(0, 9999999)

        if self.key is None:
            self.key = self.key_generator(4)

        if self.values is None:
            self.values = {"light_lvl": 0, "light_hours": (0, 0), "moisture_lvl": 0}
            self.update_all()

        if self.optimal_values is None:
            self.optimal_values = self.get_optimal_values()

    def add_water(self, dur: int):
        self.arduino.add_water(dur)
        print("Added %d watering time" % dur)
        self.update_moisture_lvl()

    def set_light(self, on: bool, dur: int, auto=False):
        self.arduino.set_light(on, dur)
        if not auto:
            if on:
                print("Light has turned on")
            else:
                print("Light has turned off")
        if auto:
            # check with board light situation, do the opposite.
            c = self.arduino.get_led_mode()
            self.arduino.set_light(not c, 0)
        self.update_light_lvl()

    def update_light_lvl(self):
        l_lvl = self.arduino.get_light_level()
        print("Light level is: %d" % l_lvl)
        self.values["light_lvl"] = l_lvl

    def update_moisture_lvl(self):
        m_lvl = self.arduino.get_moisture_level()
        print("Moisture level is: %d" % m_lvl)
        self.values["moisture_lvl"] = m_lvl

    def update_light_hours(self, time, ptype):
        nl_time = self.values["light_hours"][0]
        ll_time = self.values["light_hours"][0]

        if ptype == "natural":
            nl_time = self.values["light_hours"][0] + time
        else:
            ll_time = self.values["light_hours"][0] + time

        print("Light time:", (nl_time, ll_time))
        self.values["light_hours"] = (nl_time, ll_time)

    def update_all(self, time=0, ptype="natural"):
        self.update_light_lvl()
        self.update_moisture_lvl()
        if time > 0:
            self.update_light_hours(time, ptype)

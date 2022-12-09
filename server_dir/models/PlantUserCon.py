class PlantUserCon:

    def __init__(self, c_type: str, id_num: int , sock):
        self.plant = None
        self.user = None
        self.id_num = id_num

        if c_type == "plant":
            self.plant = sock
        elif c_type == "user":
            self.plant = sock

    def set_plant(self, sock):
        self.plant = sock

    def set_user(self, sock):
        self.user = sock

    def auto_set(self, c_type, sock):
        if c_type == "plant":
            self.plant = sock
        elif c_type == "user":
            self.plant = sock

    def get_id(self):
        return self.id_num

    def get_user_sock(self):
        return self.user

    def get_plant_sock(self):
        return self.plant
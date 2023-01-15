class PlantUserCon:

    def __init__(self, c_type: str, full_id: str, sock):
        self.plant = None
        self.users = ["A", "B"]
        self.id_num = full_id[:-1]

        if c_type == "plant":
            self.set_plant(sock)
        elif c_type == "user":
            self.set_user(sock, full_id[-1])

    def set_plant(self, sock):
        self.plant = sock

    def set_user(self, sock, letter):
        self.users[0 if letter == 'A' else 1] = sock
        print("users", self.users)

    def auto_set(self, c_type, sock, full_id):
        if c_type == "plant":
            self.set_plant(sock)
        elif c_type == "user":
            self.set_user(sock, full_id[-1])

    def get_id(self):
        return self.id_num

    def get_user_sock(self, letter):
        print("users", self.users)
        return self.users[0 if letter == 'A' else 1]

    def get_plant_sock(self):
        return self.plant

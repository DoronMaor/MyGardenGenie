class User:
    def __init__(self, user_id, username, password, plants, admin=False):
        self.id = user_id
        self.username = username
        self.password = password
        self.admin = admin
        self.plants = plants  # [[plant_id, plant_type], ...]

    @classmethod
    def from_tuple(cls, user_id, username, password, plants):
        cls(user_id, username, password, plants)

    def __str__(self):
        return f"User ID: {self.id}\nUsername: {self.username}\nPassword: {self.password}\nPlants: {self.plants}"




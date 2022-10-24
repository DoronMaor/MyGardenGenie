

class User:
    """
    username : str
    password: str
    is_admin: bool
    email: str
    plant_id: str
    plant_key: str

    """

    def __init__(self, username: str, password: str, is_admin: bool, email: str, plant_id=None, plant_key=None):
        self.username = username
        self.password = password
        self.is_admin = is_admin
        self.email = email
        self.plant_id = plant_id
        self.plant_key = plant_key

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_plant_id(self):
        return self.plant_id

    def get_plant_key(self):
        return self.plant_key

    def set_plant_id(self, p_id):
        self.plant_id = p_id

    def set_plant_key(self, p_key):
        self.plant_key = p_key

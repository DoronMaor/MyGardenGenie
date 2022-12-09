import random


class User:
    """
    - id_num : str
    - name : str
    - password : str
    - email : str
    - is_admin : bool
    - plants_id [] : lst
    """

    def __init__(self, id_num: str, name: str, password: str, email: str, is_admin: str, plants_id: list, new=False):
        if new:
            id_num = str(random.randint(0, 99999999))
        self.id_num = id_num
        self.name = name
        self.password = password
        self.email = email
        self.is_admin = is_admin
        self.plants_id = plants_id

    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )


    def get_name(self):
        return self.name

    def get_password(self):
        return self.password

    def get_plant_id(self):
        return self.plants_id

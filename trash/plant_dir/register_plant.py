from models.Plant import Plant


def create_plant():
    name = input("Name of plant: ")
    ptype = input("Type of plant: ")

    plant = Plant(name, ptype)

    print(plant)


create_plant()
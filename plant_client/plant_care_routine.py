def routine(plant: str):
    print("- Done routine for plant %s - " % plant)


def full_routine_checkup(plantA_state:str, plantB_state:str):
    if plantA_state == "AUTOMATIC":
        routine("A")

    if plantB_state == "AUTOMATIC":
        routine("B")

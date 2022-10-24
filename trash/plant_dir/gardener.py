from models.Plant import Plant
import time


def set_LCD(txt: str):
    dummy = Plant("dummy", "dummy")
    dummy.set_LCD(txt)


####

def actual_time(ltime: tuple):
    """
    In order to maximize plant growth, there should be a certain amount of time exposure for the plant.
    The problem is that 1 hour of natural light DOES NOT EQUAL to 1 hour of LED lights.
    Therefore, a calculation is needed.
    """
    ntime = ltime[0]
    ledtime = ltime[1]
    return ntime + ledtime * 0.75


def moisture_analyzer(plant: Plant):
    """
    Analyzes the current plant water situation and decides if it should be watered or not.
    """
    curr = plant.get_values()["moisture_lvl"]
    optimal = plant.get_optimal_values()["moisture_lvl"]
    if curr < optimal:
        return True
    else:
        return False


def light_analyzer(plant: Plant):
    """
    Analyzes the current plant light situation and decides if LEDs should be turned on or not.
    """
    curr_light = plant.get_values()["light_lvl"]
    optimal_light = plant.get_optimal_values()["light_lvl"]
    curr_time = actual_time(plant.get_values()["light_hours"])
    optimal_time = plant.get_optimal_values()["light_hours"]

    if curr_light < optimal_light and curr_time < optimal_time:
        return True
    else:
        return False


def watering_process(plant: Plant):
    optimal = plant.get_optimal_values()["moisture_lvl"]
    while plant.get_values()["moisture_lvl"] < optimal:
        plant.add_water(1)
        break ############

    print("Done watering")


def turn_light_on(plant: Plant, dur: int):
    plant.set_light(True, dur)


def add_water(plant: Plant, dur: int):
    plant.add_water(dur)


def turn_light(plant: Plant):
    plant.set_light(True, 1, True)


def gardener(plant: Plant):
    # water
    if plant.mode == 0:
        if moisture_analyzer(plant):
            watering_process(plant)

        if light_analyzer(plant):
            turn_light_on(plant, 1)


def gardener_loop(plant: Plant, inter: int):
    while True:
        gardener(plant)
        print("Gardened")
        time.sleep(inter)

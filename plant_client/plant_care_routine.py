import time
import mgg_functions as mgf


def hysteresis_water_handling(plant: str, low_threshold: int, high_threshold: int, gardener):
    def watering_process():
        while gardener.get_moisture() < high_threshold:
            gardener.add_water(plant, 0.5)
            time.sleep(0.2)

    if gardener.get_moisture(plant) <= low_threshold:
        watering_process()


def hysteresis_lighting_handling(plant: str, low_threshold: int, gardener):
    if gardener.get_light_level(plant) < low_threshold:
        gardener.set_led_ring(plant, True)
    else:
        gardener.set_led_ring(plant, False)
        if gardener.get_light_level(plant) < low_threshold:
            gardener.set_led_ring(plant, True)


def routine(plant: str, gardener):
    moisture_values = {"DRY": (40, 50), "MOIST": (80, 100), "WET": (130, 150)}
    light_values = {"LOW": 10, "MEDIUM": 30, "HIGH": 60}

    p_water_low_threshold, p_water_high_threshold = moisture_values[mgf.get_plant_dict(plant)["MOISTURE_LVL"]]
    p_light_low_threshold = light_values[mgf.get_plant_dict(plant)["LIGHT_LVL"]]

    hysteresis_water_handling(plant, p_water_low_threshold, p_water_high_threshold, gardener)
    hysteresis_lighting_handling(plant, p_light_low_threshold, gardener)

    print("- Done routine for plant %s - " % plant)


def full_routine_checkup(plantA_state: str, plantB_state: str, gardener):
    if plantA_state == "AUTOMATIC":
        routine("A", gardener)

    if plantB_state == "AUTOMATIC":
        routine("B", gardener)

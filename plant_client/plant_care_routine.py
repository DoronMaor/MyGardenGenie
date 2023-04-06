import time
import mgg_functions as mgf


def hysteresis_water_handling(plant: str, low_threshold: int, high_threshold: int, gardener, event_logger):
    def watering_process():
        while gardener.get_moisture(plant) < high_threshold:
            gardener.add_water(plant, 1)
            time.sleep(0.2)

    if gardener.get_moisture(plant) <= low_threshold:
        watering_process()
        event_logger.automatic_event_logger(user_id=mgf.get_id(), action_data=("watering", plant), send_now=True)


def hysteresis_lighting_handling(plant: str, low_threshold: int, gardener, event_logger):
    if gardener.get_light_level(plant) < low_threshold:
        gardener.set_led_ring(plant, True)
        event_logger.automatic_event_logger(user_id=mgf.get_id(), action_data=("Turned on LED", plant), send_now=True)

    else:
        gardener.set_led_ring(plant, False)
        if gardener.get_light_level(plant) < low_threshold:
            gardener.set_led_ring(plant, True)
            event_logger.automatic_event_logger(user_id=mgf.get_id(), action_data=("Turned on LED", plant),
                                                send_now=True)
        else:
            event_logger.automatic_event_logger(user_id=mgf.get_id(), action_data=("Turned off LED", plant),
                                                send_now=True)


def routine(plant: str, gardener, event_logger):
    moisture_values = {"DRY": (40, 50), "MOIST": (80, 100), "WET": (130, 150)}
    light_values = {"LOW": 10, "MEDIUM": 30, "HIGH": 60}

    p_water_low_threshold, p_water_high_threshold = moisture_values[mgf.get_plant_dict(plant)["MOISTURE_LVL"]]
    p_light_low_threshold = light_values[mgf.get_plant_dict(plant)["LIGHT_LVL"]]

    hysteresis_water_handling(plant, p_water_low_threshold, p_water_high_threshold, gardener, event_logger)
    hysteresis_lighting_handling(plant, p_light_low_threshold, gardener, event_logger)

    print("- Done routine for plant %s - " % plant)


def full_routine_checkup(plantA_state: str, plantB_state: str, gardener, event_logger):
    return
    if plantA_state == "AUTOMATIC":
        routine("A", gardener, event_logger)

    if plantB_state == "AUTOMATIC":
        routine("B", gardener, event_logger)

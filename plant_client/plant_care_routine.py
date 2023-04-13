import time
import mgg_functions as mgf


def hysteresis_water_handling(plant: str, low_threshold: int, high_threshold: int, gardener, event_logger):
    def watering_process():
        start_time = time.monotonic()
        while gardener.get_moisture(plant) < high_threshold:
            gardener.add_water(plant, 1)
            time.sleep(0.2)
            elapsed_time = time.monotonic() - start_time
            if elapsed_time > 60:
                # Timeout after 60 seconds
                break

    if gardener.get_moisture(plant) <= low_threshold:
        watering_process()
        event_logger.automatic_event_logger(user_id=mgf.get_id(), action_data=("watering", plant), send_now=True)



def hysteresis_lighting_handling(plant: str, low_threshold: int, gardener, event_logger):
    light_level = gardener.get_light_level(plant)
    if light_level < low_threshold and not gardener.get_led_ring(plant):
        gardener.set_led_ring(plant, True)
        event_logger.automatic_event_logger(user_id=mgf.get_id(), action_data=("Turned on LED", plant), send_now=True)

    elif light_level >= low_threshold and gardener.get_led_ring(plant):
        gardener.set_led_ring(plant, False)
        event_logger.automatic_event_logger(user_id=mgf.get_id(), action_data=("Turned off LED", plant), send_now=True)


def routine(plant: str, gardener, event_logger):

    p_water_low_threshold, p_water_high_threshold =mgf.get_plant_dict(plant)["MOISTURE_LVL"]
    p_light_low_threshold = mgf.get_plant_dict(plant)["LIGHT_LVL"]

    hysteresis_lighting_handling(plant, p_light_low_threshold, gardener, event_logger)
    hysteresis_water_handling(plant, p_water_low_threshold, p_water_high_threshold, gardener, event_logger)

    print("- Done routine for plant %s - " % plant)


def full_routine_checkup(plantA_state: str, plantB_state: str, gardener, event_logger, testing=False):
    if not testing:
        if plantA_state == "AUTOMATIC":
            routine("A", gardener, event_logger)

        if plantB_state == "AUTOMATIC":
            routine("B", gardener, event_logger)

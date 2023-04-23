import time
import mgg_functions as mgf


def hysteresis_water_handling(plant: str, low_threshold: int, high_threshold: int, gardener, event_logger):
    """
    Check the moisture level of the plant and add water to it if it falls below the low threshold. Stop adding water when
    it reaches the high threshold or after 60 seconds of adding water.

    Args:
        plant (str): The name of the plant to check moisture level for.
        low_threshold (int): The minimum moisture level at which water should be added to the plant.
        high_threshold (int): The maximum moisture level at which watering should be stopped.
        gardener (Gardener): An object representing the gardener.
        event_logger (EventLogger): An object for logging events.

    Returns:
        None
    """
    if high_threshold == -1:
        mgf.set_mode("plant%s.mgg" % plant, new_mode="MANUAL")
        return

    start_time = time.monotonic()
    while gardener.get_moisture(plant) > high_threshold:
        gardener.add_water(plant, 1)
        time.sleep(1.5)
        elapsed_time = time.monotonic() - start_time
        if elapsed_time > 60:
            # Timeout after 60 seconds
            break

    # Log watering event
    event_logger.automatic_event_logger(user_id=mgf.get_id(), action_data=("watering", plant), send_now=True)




def hysteresis_lighting_handling(plant: str, low_threshold: int, gardener, event_logger):
    """
    Check the light level of the plant and turn on/off the LED ring depending on whether it falls below the low threshold.

    Args:
        plant (str): The name of the plant to check light level for.
        low_threshold (int): The minimum light level at which the LED ring should be turned on.
        gardener (Gardener): An object representing the gardener.
        event_logger (EventLogger): An object for logging events.

    Returns:
        None
    """
    if low_threshold == -1:
        mgf.set_mode("plant%s.mgg" % plant, new_mode="MANUAL")
        return
    light_level = gardener.get_light_level(plant)
    if light_level < low_threshold and not gardener.get_led_ring(plant):
        gardener.set_led_ring(plant, True)
        event_logger.automatic_event_logger(user_id=mgf.get_id(), action_data=("Turned on LED", plant), send_now=True)
    elif light_level >= low_threshold and gardener.get_led_ring(plant):
        gardener.set_led_ring(plant, False)
        event_logger.automatic_event_logger(user_id=mgf.get_id(), action_data=("Turned off LED", plant), send_now=True)


def routine(plant: str, gardener, event_logger):
    """Performs a routine checkup for the specified plant, including hysteresis lighting handling and hysteresis water handling."""

    p_water_low_threshold, p_water_high_threshold = int(mgf.get_plant_dict(plant)["MOISTURE_LVL"])-100, int(mgf.get_plant_dict(plant)["MOISTURE_LVL"])
    p_light_low_threshold = int(mgf.get_plant_dict(plant)["LIGHT_LVL"])

    hysteresis_lighting_handling(plant, p_light_low_threshold, gardener, event_logger)
    hysteresis_water_handling(plant, p_water_low_threshold, p_water_high_threshold, gardener, event_logger)

    print(f"- Done routine for plant {plant} -")


def full_routine_checkup(plantA_state: str, plantB_state: str, gardener, event_logger, testing=False):
    """Checks the specified plants for any necessary routine maintenance, based on their current state."""

    if not testing:
        return
        if plantA_state == "AUTOMATIC":
            routine("A", gardener, event_logger)

        if plantB_state == "AUTOMATIC":
            routine("B", gardener, event_logger)

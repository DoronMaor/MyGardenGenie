"""
In order to have a fixed and known range of values, a transformer is needed.
Every function receives the raw data from the arduino, transforms it into
the acceptable range (0-100) and returns it.
"""


def raw_moisture_to_scale(m_lvl: int):
    return m_lvl


def raw_light_to_scale(l_lvl: int):
    return l_lvl
def A201_resistance(
        vin: float,
        vout: float,
        rf: float,
):
    """
    convert from voltages and sensitivity resistance to A201 sensor resistance
    :param vin:
    :param vout:
    :param rf: calibration resistor resistance
    :return: resistance of sensor in units of rf
    """
    try:
        rs = rf/((vout/vin) - 1)
    except ZeroDivisionError:
        rs = 0

    return rs
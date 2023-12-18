from system.initialize import load_state, init_system, save_state
from adc.ads1115 import read_ads1115


# might need to be careful with states of state and init params
STATE = load_state()
INIT_PARAMS = init_system()  # TODO this should be components?


def find_full_ring_rotation_steps():
    # TODO
    # funcs needed
    # continuous sampling for adc
    # continuous stepper motor rotation

    # if previous direction or last triggered stop or currently triggered stop? - store in json and load globals?
    # go in that dir or towards end stop
    # if not go cw - from front of unit
    # go slow until one end stop is reached
    # verify stop is reached by tapping? - maybe different protocol

    return


def read_endstop_state(
        sample1: float,
        sample2: float,
        trigger_threshold: float,
        trigger_above_threshold: bool,
):
    """
    sample an end stop to determine if triggered
    endstop switch could be an object also but probably not necessary
    return bool
    :param channels: must be of length 2? list of strings
    :return:
    """

    print(f'{abs(sample1 - sample2)}')

    # TODO need to set state in here? - no outside since we need to know the direction
    # the motor is going to know which endstop state to set
    triggered = endstop_is_triggered(
        sample1=sample1,
        sample2=sample2,
        trigger_threshold=trigger_threshold,
        trigger_above_threshold=trigger_above_threshold
    )

    return triggered


def endstop_is_triggered(
        sample1: float,
        sample2: float,
        trigger_threshold: float,
        trigger_above_threshold: bool
):
    if abs(sample1 - sample2) > trigger_threshold:
        if trigger_above_threshold == True:
            return True
        else:
            return False

    if abs(sample1 - sample2) <= trigger_threshold:
        if trigger_above_threshold == True:
            return False
        else:
            return True


def read_endstops_states(
        adc,
        adc_channels: list,
        channel1: list,
        channel2: list,
        trigger_thresholds: list,
        trigger_above_thresholds: list,
        trigger_event=False
):
    """
    sample both camera ring endstops until one is triggered
    return the one that was triggered
    break function when end stop triggered?
    :return:
    """

    adc_samples = read_ads1115(adc, adc_channels)

    for i in range(0, len(channel1)):
        endstop_state = read_endstop_state(
            sample1=adc_samples[channel1[i]],
            sample2=adc_samples[channel2[i]],
            trigger_threshold=trigger_thresholds[i],
            trigger_above_threshold=trigger_above_thresholds[i],
        )
        if endstop_state == True:
            trigger_event = True

    pass


def full_ring_rotation():
    """
    trigger end stop if not triggered
    multiprocess stepper move and endstop samples
    :return:
    """
    return
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
        adc,
        channel1: str,
        channel2: str,
        trigger_threshold: float,
        trigger_above_threshold: bool,
        trigger_event: bool=False,
):
    """
    sample an end stop to determine if triggered
    endstop switch could be an object also but probably not necessary
    return bool
    :param channels: must be of length 2? list of strings
    :return:
    """
    channels = [channel1, channel1]
    channel_samples = read_ads1115(adc=adc, channels=channels)

    sample1 = channel_samples[channel1]
    sample2 = channel_samples[channel2]

    print(f'{abs(sample1 - sample2)}')

    # TODO need to set state in here? - no outside since we need to know the direction
    # the motor is going to know which endstop state to set
    if abs(sample1 - sample2) > trigger_threshold:
        if trigger_above_threshold == True:
            trigger_event = True
        else:
            trigger_event = False

    if abs(sample1 - sample2) <= trigger_threshold:
        if trigger_above_threshold == True:
            trigger_event = False
        else:
            trigger_event = True

    pass


def read_endstops_states_continuous():
    """
    sample both camera ring endstops until one is triggered
    return the one that was triggered
    break function when end stop triggered?
    :return:
    """

    return


def full_ring_rotation():
    """
    trigger end stop if not triggered
    multiprocess stepper move and endstop samples
    :return:
    """
    return
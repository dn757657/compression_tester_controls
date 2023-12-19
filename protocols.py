# anything in this file should be able to run in a thread
import threading

from system.initialize import load_state, init_system, save_state, init_components
from adc.ads1115 import read_ads1115


# might need to be careful with states of state and init params
STATE = load_state()
INIT_PARAMS = init_system()
COMPS = init_components(INIT_PARAMS)


def rotate_camera_position_onto_endstop():
    """
    check if endstop is triggered
    if not move in last known direction
    if yes then need to verify which stop its on
    move until endstop triggered
    :return:
    """

    # check if endstops triggered
    adc = COMPS.get('camera_endstops_adc')
    camera_stepper = COMPS.get('camera_stepper')

    adc.read()  # update adc
    endstop_params = COMPS.get('end_stop1')
    end1_state = read_endstop_state(
        sample1=adc.channel_states[endstop_params.get('channel1')],
        sample2=adc.channel_states[endstop_params.get('channel2')],
        trigger_threshold=adc.channel_states[endstop_params.get('trigger_threshold')],
        trigger_above_threshold=adc.channel_states[endstop_params.get('trigger_above_threshold')]
    )


    trigger_event = threading.Event()  # create event for triggering

    camera_stepper_thread = threading.Thread(
        target=camera_stepper.rotate,
        args=(
            'cw',  # direction
            50,  # duty cycle
            500,  # frequency
            trigger_event
        )
    )

    # camera_stepper_thread.start()

    endstops_thread = threading.Thread(
        target=read_endstops_states,
        args=(adc,
              ["A0", "A1", "A2"],
              ["A0", "A1"],
              ["A2", "A2"],
              [2, 2],
              [False, False],
              trigger_event
              )
    )

    endstops_thread.start()
    camera_stepper_thread.start()
    endstops_thread.join()  # wait for endstop thread

    # set state of last camera stepper direction

    pass


def rotate_camera_position_off_endstop():
    """
    move camera until off of endstop, or endstop is un-triggered
    :return:
    """

    return


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


# def read_endstop_state(
#         sample1: float,
#         sample2: float,
#         trigger_threshold: float,
#         trigger_above_threshold: bool,
# ):
#     """
#     sample an end stop to determine if triggered
#     endstop switch could be an object also but probably not necessary
#     return bool
#     :param channels: must be of length 2? list of strings
#     :return:
#     """
#
#     print(f'{abs(sample1 - sample2)}')
#
#     # TODO need to set state in here? - no outside since we need to know the direction
#     # the motor is going to know which endstop state to set
#     triggered = endstop_is_triggered(
#         sample1=sample1,
#         sample2=sample2,
#         trigger_threshold=trigger_threshold,
#         trigger_above_threshold=trigger_above_threshold
#     )
#
#     return triggered
#
#
# def endstop_is_triggered(
#         sample1: float,
#         sample2: float,
#         trigger_threshold: float,
#         trigger_above_threshold: bool
# ):
#     if abs(sample1 - sample2) > trigger_threshold:
#         if trigger_above_threshold == True:
#             return True
#         else:
#             return False
#
#     if abs(sample1 - sample2) <= trigger_threshold:
#         if trigger_above_threshold == True:
#             return False
#         else:
#             return True


def detect_switches_triggers(
        switch_adc,
        switches: list,
        trigger_event
):
    """
    sample both camera ring endstops until one is triggered
    return the one that was triggered
    break function when end stop triggered?
    :return:
    """

    switch_adc.read()
    while not trigger_event.is_set():

        for switch in switches:
            switch.read()
            if switch.state == True:

                trigger_event.set()

    pass


def detect_switches_untriggers(
        switch_adc,
        switches: list,
        trigger_event
):
    """
    sample switches and return trigger event when no switch is triggered
    :return:
    """

    switch_adc.read()
    while not trigger_event.is_set():
        for switch in switches:
            switch.read()
            if switch.state == True:  # if either is true then break
                break
        trigger_event.set()  # if neither triggered then trigger event

    pass

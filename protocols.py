# anything in this file should be able to run in a thread
import threading
import logging
import timeit

from typing import List

from motors.stepper_controls import StepperMotorDriver
from system.setup import load_state, load_init_vars, save_state, init_components
from camera.canon_eosr50 import eosr50_continuous_capture_and_save

# might need to be careful with states of state and init params
# STATE = load_state()
INIT_PARAMS = load_init_vars()
COMPS = init_components(INIT_PARAMS)

logging.getLogger().setLevel(logging.INFO)


def rotate_motor_until_switch_state(
        stepper_motor: StepperMotorDriver,
        switch_adcs: list,
        switches: list,
        stepper_duty_cycle: float,
        stepper_frequency: float,
        stepper_dir: str,
        trigger_event: threading.Event,
        switch_trigger_state: List[bool],
):
    """
    check if switch state is switch trigger state
    if not move in last known direction - may need to dial in state updating
    move until switch state reached

    :param stepper_motor:
    :param switch_adcs:
    :param switches:
    :param stepper_duty_cycle:
    :param stepper_frequency:
    :param stepper_dir:
    :param trigger_event:
    :param switch_trigger_state:
    :return:
    """

    # input checks
    if len(switch_trigger_state) != len(switches):
        logging.info(f'Number of target switch states: {len(switch_trigger_state)},'
                     f' not matching number of switches: {len(switches)}.')

    # TODO add names for components for logging/reporting intent to console
    logging.info(f'Moving stepper {stepper_dir} @ {stepper_frequency} [Hz]:\n'
                 f'Seeking switch state {switch_trigger_state}...')

    initial_switch_states = get_switch_states(switch_adcs=switch_adcs, switches=switches)
    if set(initial_switch_states) == set(switch_trigger_state):
        logging.info(f'Switch state, {switch_trigger_state}, reached.')
        return

    stepper_thread = threading.Thread(
        target=stepper_motor.rotate,
        args=(
            stepper_dir,  # direction
            stepper_duty_cycle,  # duty cycle
            stepper_frequency,  # frequency
            trigger_event
        )
    )

    switch_thread = threading.Thread(
        target=monitor_switches_until_state_reached,
        args=(switch_adcs,
              switches,
              trigger_event,
              switch_trigger_state
              )
    )

    switch_thread.start()
    stepper_thread.start()
    switch_thread.join()  # wait for endstop thread to trigger

    logging.info(f'Switch state, {switch_trigger_state}, reached.')

    pass


def rotate_motor_until_switch_state_or_steps_reached(
        stepper_motor: StepperMotorDriver,
        switch_adcs: list,
        switches: list,
        stepper_duty_cycle: float,
        stepper_frequency: float,
        stepper_dir: str,
        steps: int,
        trigger_event: threading.Event,
        switch_trigger_state: List[bool],
):
    """
    check if switch state is switch trigger state
    if not move in last known direction - may need to dial in state updating
    move until switch state reached

    :param stepper_motor:
    :param switch_adcs:
    :param switches:
    :param stepper_duty_cycle:
    :param stepper_frequency:
    :param stepper_dir:
    :param trigger_event:
    :param switch_trigger_state:
    :return:
    """

    # input checks
    if len(switch_trigger_state) != len(switches):
        logging.info(f'Number of target switch states: {len(switch_trigger_state)},'
                     f' not matching number of switches: {len(switches)}.')

    # TODO add names for components for logging/reporting intent to console
    logging.info(f'Moving stepper {stepper_dir} @ {stepper_frequency} [Hz]:\n'
                 f'Seeking switch state {switch_trigger_state}...')

    initial_switch_states = get_switch_states(switch_adcs=switch_adcs, switches=switches)
    if set(initial_switch_states) == set(switch_trigger_state):
        logging.info(f'Switch state, {switch_trigger_state}, reached.')
        return

    stepper_thread = threading.Thread(
        target=stepper_motor.rotate_steps,
        args=(
            stepper_dir,  # direction
            stepper_duty_cycle,  # duty cycle
            stepper_frequency,  # frequency
            steps,
            trigger_event
        )
    )

    switch_thread = threading.Thread(
        target=monitor_switches_until_state_reached,
        args=(switch_adcs,
              switches,
              trigger_event,
              switch_trigger_state
              )
    )

    switch_thread.start()
    stepper_thread.start()
    switch_thread.join()  # wait for endstop thread to trigger

    logging.info(f'Switch state, {switch_trigger_state}, reached.')

    pass


def rotate_camera_position_onto_endstop(
        stepper_dir: str,
        trigger_event: threading.Event,
        stepper_motor: StepperMotorDriver = COMPS.get('camera_stepper'),
        endstop_adcs: list = [COMPS.get('camera_endstops_adc')],
        endstops: list = [COMPS.get('endstop1'), COMPS.get('endstop2')],
        stepper_duty_cycle: float = None,
        stepper_frequency: float = None,
):
    """
    check if endstop is triggered
    if not move in last known direction
    if yes then need to verify which stop its on
    move until endstop triggered
    :return:
    """

    # set some defaults
    if not stepper_duty_cycle:
        stepper_duty_cycle = stepper_motor.default_duty_cycle

    if not stepper_frequency:
        stepper_frequency = stepper_motor.default_frequency

    logging.info(f'Rotating camera stepper until end-stop triggered...')

    rotate_motor_until_switch_state(
        stepper_motor=stepper_motor,
        switch_adcs=endstop_adcs,
        switches=endstops,
        stepper_duty_cycle=stepper_duty_cycle,
        stepper_frequency=stepper_frequency,
        stepper_dir=stepper_dir,
        trigger_event=trigger_event,
        switch_trigger_state=[True, False]  # just one of the endstops needs to be triggered
    )

    return


def rotate_camera_position_onto_endstop_with_cameras(
        stepper_dir: str,
        trigger_event: threading.Event,
        camera_ports: list,
        photo_base_filename: str = 'test_capture',
        stepper_motor: StepperMotorDriver = COMPS.get('camera_stepper'),
        endstop_adcs: list = [COMPS.get('camera_endstops_adc')],
        endstops: list = [COMPS.get('endstop1'), COMPS.get('endstop2')],
        stepper_duty_cycle: float = None,
        stepper_frequency: float = None,
):
    """
    check if endstop is triggered
    if not move in last known direction
    if yes then need to verify which stop its on
    move until endstop triggered
    :return:
    """

    # set some defaults
    if not stepper_duty_cycle:
        stepper_duty_cycle = stepper_motor.default_duty_cycle

    if not stepper_frequency:
        stepper_frequency = stepper_motor.default_frequency

    logging.info(f'Rotating and activating camera until end-stop triggered...')

    camera_threads = list()
    for port in camera_ports:
        camera_thread = threading.Thread(
            target=eosr50_continuous_capture_and_save,
            args=(
                port,
                photo_base_filename,
                trigger_event
            )
        )
        camera_threads.append(camera_thread)

    for t in camera_threads:
        t.start()

    rotate_motor_until_switch_state(
        stepper_motor=stepper_motor,
        switch_adcs=endstop_adcs,
        switches=endstops,
        stepper_duty_cycle=stepper_duty_cycle,
        stepper_frequency=stepper_frequency,
        stepper_dir=stepper_dir,
        trigger_event=trigger_event,
        switch_trigger_state=[True, False]  # just one of the endstops needs to be triggered
    )

    return


#         trigger_event=trigger_event,
#         switch_trigger_state=[True, False]
#     )
#     trigger_event = threading.Event()    
#     stepper_dir = [d for d in stepper_motor.motor_directions if d != stepper_dir][0]

#     rotate_motor_until_switch_state_or_steps_reached(
#         stepper_motor=stepper_motor,
#         switch_adcs=endstop_adcs,
#         switches=endstops,
#         stepper_duty_cycle=stepper_duty_cycle,
#         stepper_frequency=stepper_frequency,
#         stepper_dir=stepper_dir,
#         steps=200,
#         trigger_event=trigger_event,
#         switch_trigger_state=[True, False]
#     )

#     pass


def reset_camera_position(
        state,
        trigger_event: threading.Event,
        verification_cycles: int,
        stepper_motor: StepperMotorDriver = COMPS.get('camera_stepper'),
        endstop_adcs: list = [COMPS.get('camera_endstops_adc')],
        endstops: list = [COMPS.get('endstop1'), COMPS.get('endstop2')],
        stepper_duty_cycle: float = None,
        stepper_frequency: float = None,
):
    """

    :param stepper_dir:
    :param trigger_event:
    :param verification_cycles:
    :param stepper_motor:
    :param endstop_adcs:
    :param endstops:
    :param stepper_duty_cycle:
    :param stepper_frequency:
    :return:
    """
    logging.info(f'Resetting camera stepper position...')

    # set some defaults
    if not stepper_duty_cycle:
        stepper_duty_cycle = stepper_motor.default_duty_cycle

    if not stepper_frequency:
        stepper_frequency = stepper_motor.default_frequency

    switch_states = get_switch_states(switch_adcs=endstop_adcs, switches=endstops)

    # if endstop is triggered already, go opposite direction to confirm
    stepper_dir = state.get('camera_stepper_last_dir')
    if True in switch_states:  # switch is triggered, resting on endstop, go opposite dir
        stepper_dir = [d for d in stepper_motor.motor_directions if d != stepper_dir][0]  # swap dir

    switch_states_to_seek = list()
    for i in range(0, verification_cycles):
        if True in switch_states:
            [switch_states_to_seek.append(False) for state in switch_states]
        else:
            [switch_states_to_seek.append(False) for s in range(0, len(switch_states) - 1)]
            switch_states_to_seek.append(True)  # one true

        # first seek to trigger an endstop
        rotate_motor_until_switch_state(
            stepper_motor=stepper_motor,
            switch_adcs=endstop_adcs,
            switches=endstops,
            stepper_duty_cycle=stepper_duty_cycle,
            stepper_frequency=stepper_frequency,
            stepper_dir=stepper_dir,
            trigger_event=trigger_event,
            switch_trigger_state=switch_states_to_seek
        )
        trigger_event = threading.Event()  # reset trigger 
        stepper_dir = [d for d in stepper_motor.motor_directions if d != stepper_dir][0]
        switch_states = switch_states_to_seek  # assume swithc state is the sought state if gets here
        switch_states_to_seek = list()  # reset seeking state

    # ensure off trigger - loop may not end off trigger
    if True in switch_states:  # this is on trigger
        # move off trigger - direction should already be swapped from loop
        rotate_motor_until_switch_state(
                stepper_motor=stepper_motor,
                switch_adcs=endstop_adcs,
                switches=endstops,
                stepper_duty_cycle=stepper_duty_cycle,
                stepper_frequency=stepper_frequency,
                stepper_dir=stepper_dir,
                trigger_event=trigger_event,
                switch_trigger_state=[False, False]
            )
    else:  # loop ended offf trigger but swapped direction back towards trigger
        # swap direction away from trigger as last known dir
        stepper_dir = [d for d in stepper_motor.motor_directions if d != stepper_dir][0]

    state['camera_stepper_last_dir'] = stepper_dir

    logging.info(f'Camera position reset.')
    return state


def find_full_camera_rotation_steps(
        stepper_dir: str,
        stepper_frequency: float = 500,
):

    logging.info(f'Finding full camera rotation steps...')

    stepper_dir = reset_camera_position(
        stepper_dir=stepper_dir,
        trigger_event=threading.Event(),
        verification_cycles=1,
        stepper_frequency=stepper_frequency
    )

    start = timeit.default_timer()
    rotate_camera_position_onto_endstop(
        stepper_dir=stepper_dir,
        trigger_event=threading.Event(),
        stepper_frequency=stepper_frequency
    )
    end = timeit.default_timer()

    total_time = end - start
    total_steps = stepper_frequency * total_time
    total_whole_steps = round(total_steps, ndigits=None)

    return total_whole_steps


def get_switch_states(
        switch_adcs: list,
        switches: list,
) -> list:
    states = []

    for adc in switch_adcs:
        adc.read()
    for switch in switches:
        switch.read()
        states.append(switch.state)

    return states


def monitor_switches_until_state_reached(
        switch_adcs: list,
        switches: list,
        trigger_event,
        trigger_state,
):
    while not trigger_event.is_set():
        states = get_switch_states(switch_adcs=switch_adcs, switches=switches)

        if set(states) == set(trigger_state):  # not order specific
            trigger_event.set()

    pass

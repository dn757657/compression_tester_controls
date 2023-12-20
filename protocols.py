# anything in this file should be able to run in a thread
import threading
import logging

from motors.stepper_controls import StepperMotorDriver


def rotate_camera_position_onto_endstop(
        stepper_motor: StepperMotorDriver,
        switch_adcs: list,
        endstops: list,  # should only ever be two tbh
        stepper_duty_cycle: float,
        stepper_frequency: float,
        stepper_dir: str,
        trigger_event: threading.Event = threading.Event()
):
    """
    check if endstop is triggered
    if not move in last known direction
    if yes then need to verify which stop its on
    move until endstop triggered
    :return:
    """

    # update adcs for switches
    for adc in switch_adcs:
        adc.read()

    # if any endstop is triggered than do nothing
    for endstop in endstops:
        if endstop.state:
            logging.info("An endstop switch is triggered, must reset position!")
            return

    camera_stepper_thread = threading.Thread(
        target=stepper_motor.rotate,
        args=(
            stepper_dir,  # direction
            stepper_frequency,  # duty cycle
            stepper_duty_cycle,  # frequency
            trigger_event
        )
    )

    # camera_stepper_thread.start()

    endstops_thread = threading.Thread(
        target=detect_switches_triggers,
        args=(switch_adcs,
              endstops,
              trigger_event
              )
    )

    endstops_thread.start()
    camera_stepper_thread.start()
    endstops_thread.join()  # wait for endstop thread to trigger

    pass


def reset_camera_position(
        stepper_motor: StepperMotorDriver,
        switch_adcs: list,
        endstops: list,  # should only ever be two tbh
        stepper_duty_cycle: float,
        stepper_frequency: float,
        stepper_dir: str,
        steps_to_untrigger: int,
        bumps: int = 2,
    ):
    """
    move camera until off of endstop, or endstop is un-triggered
    :return:
    """

    # update adcs for switches
    for adc in switch_adcs:
        adc.read()

    # at least on endstop must be triggered for this function to make sense
    triggered = False
    for endstop in endstops:
        if endstop.state:
            triggered = True

    if not triggered:
        logging.info("No endstop switch is triggered, no need to reset position!")
        return

    # TODO ideally we have a function to find the number of steps required to back off
    # an endstop switch but for now we just set it manually

    # last known dir is stepper dir - get opposite dir to back off switch
    stepper_dir = [d for d in stepper_motor.motor_directions if d != stepper_dir][0]

    stepper_motor.rotate_steps(
        direction=stepper_dir,
        duty_cyle=stepper_duty_cycle,
        freq=stepper_frequency,
        steps=steps_to_untrigger
    )

    triggered = False
    for endstop in endstops:
        if endstop.state:
            triggered = True

    if not triggered:
        logging.info('Successfully reset camera position, confirming...')

    # bump the stop a few times to confirm
    for i in range(0, bumps):
        # swap dir
        stepper_dir = [d for d in stepper_motor.motor_directions if d != stepper_dir][0]

        stepper_motor.rotate_steps(
            direction=stepper_dir,
            duty_cyle=stepper_motor.default_duty_cycle,
            freq=stepper_motor.default_frequency,
            steps=steps_to_untrigger
        )

        triggered = False
        for endstop in endstops:
            if endstop.state:
                triggered = True

        # if no stop is triggered bump has failed
        if not triggered:
            logging.info("Failed to confirm camera position status")
            return

        # swap dir
        stepper_dir = [d for d in stepper_motor.motor_directions if d != stepper_dir][0]

        stepper_motor.rotate_steps(
            direction=stepper_dir,
            duty_cyle=stepper_motor.default_duty_cycle,
            freq=stepper_motor.default_frequency,
            steps=steps_to_untrigger
        )

        triggered = False
        for endstop in endstops:
            if endstop.state:
                triggered = True

        # if no stop is triggered bump has succeeded
        if not triggered:
            logging.info(f"Confirmed stepper position: bump {i}")
            # stepper dir should be set to pointing away from the endstop switch
        else:
            logging.info("Failed to confirm camera position status")
            return

    return stepper_dir  # return just in case, although should be mutated by stepper_dir arg


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
        switch_adcs: list,
        switches: list,
        trigger_event
):
    """
    sample both camera ring endstops until one is triggered
    return the one that was triggered
    break function when end stop triggered?
    :return:
    """

    for adc in switch_adcs:
        adc.read()

    while not trigger_event.is_set():

        for switch in switches:
            switch.read()
            if switch.state == True:

                trigger_event.set()

    pass


def detect_switches_untriggers(
        switch_adcs: list,
        switches: list,
        trigger_event
):
    """
    sample switches and return trigger event when no switch is triggered
    :return:
    """

    for adc in switch_adcs:
        adc.read()

    while not trigger_event.is_set():
        for switch in switches:
            switch.read()
            if switch.state == True:  # if either is true then break
                break
        trigger_event.set()  # if neither triggered then trigger event

    pass

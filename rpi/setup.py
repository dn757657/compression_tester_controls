import RPi.GPIO as GPIO

from typing import List


def init_pi_pins(
        channel_list: List[int],
        pin_mode: str,
):

    pin_modes = ['BCM', 'BOARD']
    if pin_mode in pin_modes:
        if pin_mode == 'BCM':
            pin_mode = GPIO.BCM
        else:
            pin_mode = GPIO.BOARD
    else:
        print(f"{pin_mode} must be one of {pin_modes}")
        return
    print(f'{channel_list}')
    # Set up GPIO pins - all gpio config is done here, easier to cleanup (less fancy)
    GPIO.setmode(pin_mode)
    GPIO.setup(channel_list, GPIO.OUT)  # may need to accomodate IN pins also?

    pass

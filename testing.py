import threading
import subprocess

from system.setup import load_state, load_init_vars, save_state, init_components
from protocols import rotate_stepper_until_force_applied
from camera.canon_eosr50 import eosr50_init, gphoto2_get_active_ports, gpohoto2_get_camera_settings

# might need to be careful with states of state and init params
STATE = load_state()
INIT_PARAMS = load_init_vars()
COMPS = init_components(INIT_PARAMS)


def move_crusher(direction: str, steps: int):
    stepper = COMPS.get('crushing_stepper')
    stepper.rotate_steps(
        direction=direction,
        duty_cyle=stepper.default_duty_cycle,
        freq=stepper.default_frequency,
        steps=steps,
        stop_event=threading.Event()
    )


def test():
    rotate_stepper_until_force_applied(
        state=STATE,
        sensor_adc=COMPS.get('force_sensor_adc'),
        stepper_motor=COMPS.get('crushing_stepper'),
        stepper_dir='cw',
        trigger_event=threading.Event(),
    )


def main():

    move_crusher(direction='cw', steps=100)
    # test()
    
    pass


if __name__ == '__main__':
    main()

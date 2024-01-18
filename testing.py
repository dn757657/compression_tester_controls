import threading
import subprocess

from system.setup import load_state, load_init_vars, save_state, init_components
from protocols import rotate_stepper_until_force_applied, sample_a201_until_force_applied, establish_A201_noise_limits
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


def test_force_sensitivity():
    rf = 50000
    noise_floor, noise_ceiling = establish_A201_noise_limits(
        sensor_adc=COMPS.get('force_sensor_adc'),
        rf=50000

    )

    sample_a201_until_force_applied(
        sensor_adc=COMPS.get('force_sensor_adc'),
        noise_floor=noise_floor,
        noise_ceiling=noise_ceiling,
        trigger_event=threading.Event(),
        rf=rf,
    )


def main():

    #move_crusher(direction='ccw', steps=1000)
    # test()
    test_force_sensitivity()

    pass


if __name__ == '__main__':
    main()

import threading
import subprocess

from system.setup import load_state, load_init_vars, save_state, init_components
from protocols import rotate_stepper_until_force_applied, sample_a201_until_force_applied, establish_A201_noise_std
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
        stepper_dir='ccw',
        trigger_event=threading.Event(),
        rf=50000,
        sample_avg_len=100,
        cusum_limit=0.5
    )


def test_force_sensitivity():
    # std, pre_samples = establish_A201_noise_std(
    #     sensor_adc=COMPS.get('force_sensor_adc'),
    #     rf=50000,
    #     noise_count=100
    # )

    sample_a201_until_force_applied(
        sensor_adc=COMPS.get('force_sensor_adc'),
        trigger_event=threading.Event(),
        rf=50000,
        h=5,
        k=.01
    )


# def a201_cusum():
#     import numpy as np
#     from protocols import sample_A201_Rs
#
#     sensor_adc = COMPS.get('force_sensor_adc')
#     rf = 50000
#     cusum = 0
#
#     samples = np.array([])
#     while True:
#         sample = sample_A201_Rs(sensor_adc=sensor_adc, rf=rf)
#         samples = np.append(samples, [sample])
#
#         if len(samples) > 100:
#             idx = max(-100, -len(samples))
#             samples = samples[idx:]
#
#             avg = np.average(samples)
#             diff = sample - avg
#             cusum += diff/avg
#
#         if abs(cusum) > 0.5:
#             break
#         print(f"cusum: {cusum}")


def main():

    # move_crusher(direction='cw', steps=2000)
    # test()
    test_force_sensitivity()

    pass


if __name__ == '__main__':
    main()

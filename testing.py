import threading
import subprocess

from system.setup import load_state, load_init_vars, save_state, init_components
from protocols import sample_A201_Rs, establish_A201_noise_limits
from camera.canon_eosr50 import eosr50_init, gphoto2_get_active_ports, gpohoto2_get_camera_settings

# might need to be careful with states of state and init params
STATE = load_state()
INIT_PARAMS = load_init_vars()
COMPS = init_components(INIT_PARAMS)


def main():

    noise_floor, noise_ceiling = establish_A201_noise_limits(
        sensor_adc=COMPS.get('force_sensor_adc'),
        num_samples=1000,
    )

    print(f"NOISE FLOOR  : {noise_floor}\n"
          f"NOISE CEILING: {noise_ceiling}\n")

    pass


if __name__ == '__main__':
    main()

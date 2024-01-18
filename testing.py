import threading
import subprocess

from system.setup import load_state, load_init_vars, save_state, init_components
from protocols import sample_A201_Rs, establish_A201_noise_limits, sample_a201_until_force_applied
from camera.canon_eosr50 import eosr50_init, gphoto2_get_active_ports, gpohoto2_get_camera_settings

# might need to be careful with states of state and init params
STATE = load_state()
INIT_PARAMS = load_init_vars()
COMPS = init_components(INIT_PARAMS)


def main():

    sample_a201_until_force_applied(
        sensor_adc=COMPS.get('force_sensor_adc'),
        num_samples=100,
        rf=50000,
        offset_stds=3,
        trigger_event=threading.Event()
    )

    pass


if __name__ == '__main__':
    main()

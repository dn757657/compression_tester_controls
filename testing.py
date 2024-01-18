import threading
import subprocess

from system.setup import load_state, load_init_vars, save_state, init_components
from protocols import sample_A201_Rs
from camera.canon_eosr50 import eosr50_init, gphoto2_get_active_ports, gpohoto2_get_camera_settings

# might need to be careful with states of state and init params
STATE = load_state()
INIT_PARAMS = load_init_vars()
COMPS = init_components(INIT_PARAMS)


def main():

    while True:
        rs = sample_A201_Rs(sensor_adc=COMPS.get('force_sensor_adc'))
        print(f"rs = {rs}")

    pass


if __name__ == '__main__':
    main()

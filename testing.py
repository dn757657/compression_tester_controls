import threading
import subprocess

from system.setup import load_state, load_init_vars, save_state, init_components
from protocols import rotate_camera_position_onto_endstop, reset_camera_position, \
    find_full_camera_rotation_steps, rotate_camera_position_onto_endstop_with_cameras
from camera.canon_eosr50 import eosr50_init, gphoto2_get_active_ports, gpohoto2_get_camera_settings

# might need to be careful with states of state and init params
STATE = load_state()
INIT_PARAMS = load_init_vars()
COMPS = init_components(INIT_PARAMS)


def main():

    cam_ports = gphoto2_get_active_ports()
    for port in cam_ports:
        eosr50_init(port)
        cam_settings = gpohoto2_get_camera_settings(port)
        for setting, value in cam_settings.items():
            print(setting, ':', value)
    
    pass


if __name__ == '__main__':
    main()

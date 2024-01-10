import threading
import subprocess

from system.setup import load_state, load_init_vars, save_state, init_components
from protocols import rotate_camera_position_onto_endstop, reset_camera_position, \
    find_full_camera_rotation_steps, rotate_camera_position_onto_endstop_with_cameras
from camera.canon_eosr50 import eosr50_init, gphoto2_get_active_ports

# might need to be careful with states of state and init params
STATE = load_state()
INIT_PARAMS = load_init_vars()
COMPS = init_components(INIT_PARAMS)


def get_camera_settings(port):
    # List all configuration options
    list_command = ['sudo', 'gphoto2', f'--port {port}', '--list-config']
    list_result = subprocess.run(list_command, capture_output=True, text=True)
    config_options = list_result.stdout.splitlines()

    # Retrieve current settings
    settings = {}
    for option in config_options:
        get_command = ['sudo', 'gphoto2', f'--port {port}', '--get-config', option]
        get_result = subprocess.run(get_command, capture_output=True, text=True)
        settings[option] = get_result.stdout

    return settings


def main():

    cam_ports = gphoto2_get_active_ports()
    for port in cam_ports:
        eosr50_init(port)

    cam_settings = get_camera_settings(cam_ports[0])
    print(cam_settings)
    
    pass


if __name__ == '__main__':
    main()

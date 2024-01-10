import threading

from system.setup import load_state, load_init_vars, save_state, init_components
from protocols import reset_camera_position, rotate_camera_position_onto_endstop_with_cameras
from camera.canon_eosr50 import eosr50_init, gphoto2_get_active_ports

# might need to be careful with states of state and init params
STATE = load_state()
INIT_PARAMS = load_init_vars()
COMPS = init_components(INIT_PARAMS)


def trial_step():

    reset_camera_position(
        state=STATE,
        trigger_event=threading.Event(),
        verification_cycles=3
    )

    cam_ports = gphoto2_get_active_ports()
    for port in cam_ports:
        eosr50_init(port)

    # use last known dir
    stepper_dir = STATE.get('camera_stepper_last_dir')
    rotate_camera_position_onto_endstop_with_cameras(
        state=STATE,
        stepper_dir=stepper_dir,
        camera_ports=cam_ports,
        trigger_event=threading.Event()
    )
    save_state(state=STATE)

    pass


def main():
    trial_step()

    pass


if __name__ == '__main__':
    main()

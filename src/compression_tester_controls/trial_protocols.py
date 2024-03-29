import threading

from src.compression_tester_controls.system.setup import load_state, load_init_vars, save_state, init_components
from src.compression_tester_controls.protocols import reset_camera_position, rotate_camera_position_onto_endstop_with_cameras
from src.compression_tester_controls.camera import eosr50_init, gphoto2_get_active_ports

# might need to be careful with states of state and init params
STATE = load_state()
INIT_PARAMS = load_init_vars()
COMPS = init_components(INIT_PARAMS)

# TODO start all observers in the setup bit - reconfigure any observers that arent currently


def trial_step(num_photos: int = None, **kwargs):

    reset_camera_position(
        state=STATE,
        trigger_event=threading.Event(),
        verification_cycles=3
    )

    # TODO add force limit monitoring for motor move
    # TODO add strain limit monitoring for motor move
    #  make is flexible in case it goes a little over, or define the steps,
    #  then check if the machine is within a certain distance of the step?
    #  using cam or encoder etc

    cam_ports = gphoto2_get_active_ports()
    for port in cam_ports:
        eosr50_init(port)

    # use last known dir
    stepper_dir = STATE.get('camera_stepper_last_dir')
    rotate_camera_position_onto_endstop_with_cameras(
        state=STATE,
        stepper_dir=stepper_dir,
        camera_ports=cam_ports,
        trigger_event=threading.Event(),
        num_photos=num_photos,
        **kwargs
    )
    save_state(state=STATE)

    pass


def main():
    trial_step()

    pass


if __name__ == '__main__':
    main()

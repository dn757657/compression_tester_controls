import threading

from system.setup import load_state, load_init_vars, save_state, init_components
from protocols import rotate_camera_position_onto_endstop, reset_camera_position, \
    find_full_camera_rotation_steps, rotate_camera_position_onto_endstop_with_cameras
from camera.canon_eosr50 import eosr50_init, gphoto2_get_active_ports

# might need to be careful with states of state and init params
STATE = load_state()
INIT_PARAMS = load_init_vars()
COMPS = init_components(INIT_PARAMS)

# # Define pin connections
# CRUSHING_STEP_PIN = 13
# CRUSHING_DIR_PIN = 27
# CRUSHING_ENA_PIN = 22  # not currently implemented since using estop instead
#
# # Define pin connections
# CAMERA_STEP_PIN = 12
# CAMERA_DIR_PIN = 17
# CAMERA_ENA_PIN = 26  # not currently implemented since using estop instead
#
# chan_list = [
#     CRUSHING_STEP_PIN,
#     CRUSHING_DIR_PIN,
#     CRUSHING_ENA_PIN,
#     CAMERA_STEP_PIN,
#     CAMERA_DIR_PIN,
#     CAMERA_ENA_PIN
# ]
#
# # Set up GPIO pins - all gpio config is done here, easier to cleanup (less fancy)
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(chan_list, GPIO.OUT)


def camera_step():

    # reset_camera_position(
    #     state=STATE,
    #     trigger_event=threading.Event(),
    #     verification_cycles=3
    # )

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

    # reset_camera_position(
    #     state=STATE,
    #     trigger_event=threading.Event(),
    #     verification_cycles=3
    # )

    save_state(state=STATE)

    pass


def main():
    camera_step()
    # print(f"initial last known dir: {STATE.get('camera_stepper_last_dir')}")
    
    # reset_camera_position(
    #     state=STATE,
    #     trigger_event=threading.Event(),
    #     verification_cycles=3
    # )

    # print(f"final last knwon dirL {STATE.get('camera_stepper_last_dir')}")
    
    pass



if __name__ == '__main__':
    main()

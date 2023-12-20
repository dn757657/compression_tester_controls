from system.setup import load_state, load_init_vars, save_state, init_components
from protocols import rotate_camera_position_onto_endstop, reset_camera_position

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


def main():

    stepper_dir = STATE.get('camera_stepper_last_dir')
    camera_stepper_steps_to_untrigger_endstop = STATE.get('camera_stepper_steps_to_untrigger_endstop')
    while True:
        es1 = COMPS.get('endstop1')
        es2 = COMPS.get('endstop2')
        print(f'es1: {es1.state}\nes2: {es2.state}')

        adc = COMPS.get('camera_endstops_adc')
        print(f'{adc.channel_states}')

    # print(f'{stepper_dir}')
    # camera_stepper = COMPS.get('camera_stepper')
    # rotate_camera_position_onto_endstop(
    #     stepper_motor=camera_stepper,
    #     switch_adcs=[COMPS.get('camera_endstops_adc')],
    #     endstops=[COMPS.get('endstop1'), COMPS.get('endstop2')],
    #     stepper_duty_cycle=camera_stepper.default_duty_cycle,
    #     stepper_frequency=camera_stepper.default_frequency,
    #     stepper_dir=stepper_dir
    # )
    #
    # stepper_dir = reset_camera_position(
    #     stepper_motor=camera_stepper,
    #     switch_adcs=[COMPS.get('camera_endstops_adc')],
    #     endstops=[COMPS.get('endstop1'), COMPS.get('endstop2')],
    #     stepper_duty_cycle=camera_stepper.default_duty_cycle,
    #     stepper_frequency=camera_stepper.default_frequency,
    #     stepper_dir=stepper_dir,
    #     steps_to_untrigger=camera_stepper_steps_to_untrigger_endstop
    # )


if __name__ == '__main__':
    main()

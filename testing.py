import RPi.GPIO as GPIO

from motors.stepper_controls import StepperMotorDriver

# Define pin connections
CRUSHING_STEP_PIN = 13
CRUSHING_DIR_PIN = 27
CRUSHING_ENA_PIN = 22

# Define pin connections
CAMERA_STEP_PIN = 19
CAMERA_DIR_PIN = 4
CAMERA_ENA_PIN = 17

chan_list = [
    CRUSHING_STEP_PIN,
    CRUSHING_DIR_PIN,
    CRUSHING_ENA_PIN,
    CAMERA_STEP_PIN,
    CAMERA_DIR_PIN,
    CAMERA_ENA_PIN
]

# Set up GPIO pins - all gpio config is done here, easier to cleanup (less fancy)
GPIO.setmode(GPIO.BCM)
GPIO.setup(chan_list, GPIO.OUT)

# crushing stepper motor configuration
CRUSHING_STEPPER_PROPERTIES = {
    'dir_pin': CRUSHING_DIR_PIN,
    'dsbl_pin': CRUSHING_ENA_PIN,
    'step_pin': CRUSHING_STEP_PIN,
    'cw_pin_high': False,
    'disable_high': False,  # subject to change with new relay setup?
    'step_on_rising_edge': False
}

CAMERA_STEPPER_PROPERTIES = {
    'dir_pin': CAMERA_DIR_PIN,
    'dsbl_pin': CAMERA_ENA_PIN,
    'step_pin': CAMERA_STEP_PIN,
    'cw_pin_high': False,
    'disable_high': False,  # subject to change with new relay setup?
    'step_on_rising_edge': True
}


def main():
    crushing_stepper = StepperMotorDriver(**CRUSHING_STEPPER_PROPERTIES)
    crushing_stepper.move_steps(steps=100, duty_cyle=(3/3.5)*100, direction='cw', freq=100)

    camera_stepper = StepperMotorDriver(**CAMERA_STEPPER_PROPERTIES)
    camera_stepper.move_steps(steps=100, duty_cyle=50, direction='cw', freq=5000)
    camera_stepper.move_steps(steps=100, duty_cyle=50, direction='ccw', freq=5000)

    GPIO.cleanup()


if __name__ == '__main__':
    main()
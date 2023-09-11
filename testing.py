import RPi.GPIO as GPIO

from stepper_controls.motion import move_pwm, enable_driver, set_dir

# Define pin connections
STEP_PIN = 18  # GPIO 18 is capable of hardware PWM
DIR_PIN = 27
ENA_PIN = 22

# Set up GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(ENA_PIN, GPIO.OUT)


def main():
    enable_driver(ENA_PIN)
    set_dir(DIR_PIN, dir='cw')
    move_pwm(pin=STEP_PIN, freq=1000, run_time=1, duty_cycle=50)

    GPIO.cleanup()


if __name__ == '__main__':
    main()
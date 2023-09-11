import RPi.GPIO as GPIO
import time
import logging

# Define pin connections
STEP_PIN = 18  # GPIO 18 is capable of hardware PWM
DIR_PIN = 27
ENA_PIN = 22

# Set up GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(ENA_PIN, GPIO.OUT)


def set_dir(
        pin: int,
        dir: str='cww'
):
    if dir not in ['cw', 'ccw']:
        logging.info(f'{dir}: not in possible directions')

    if dir == 'cw':
        GPIO.output(pin, GPIO.HIGH)
    elif dir == 'ccw':
        GPIO.output(pin, GPIO.LOW)
    pass


def enable_driver(
        pin: int,
):
    GPIO.output(pin, GPIO.LOW)
    pass


def disable_driver(
        pin: int,
):
    GPIO.output(pin, GPIO.HIGH)
    pass


def move_pwm(
        pin: int,
        freq: int,
        run_time: int,
        duty_cycle: int=50,
):
    pwm = GPIO.PWM(pin, freq)
    pwm.start(duty_cycle)
    time.sleep(run_time)
    pwm.stop()

# Cleanup GPIO
GPIO.cleanup()

import RPi.GPIO as GPIO
import pigpio
import time
import logging


def set_dir(
        pin: int,
        dir: str='ccw'
):
    """
    maybe alter such that ccw and cs being high or low can be set in the args for
    different motors
    :param pin:
    :param dir:
    :return:
    """
    if dir not in ['cw', 'ccw']:
        logging.info(f'{dir}: not in possible directions')

    if dir == 'ccw':
        GPIO.output(pin, GPIO.HIGH)
    elif dir == 'cw':
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


def move_pwm_rpigpio(
        pin: int,
        freq: int,
        run_time: int,
        duty_cycle: int=50,
):
    pwm = GPIO.PWM(pin, freq)
    pwm.start(duty_cycle)
    time.sleep(run_time)
    pwm.stop()


def move_pwm_pigpio(
        pin,
        pulse_timings,
):
    # Initialize pigpio
    pi = pigpio.pi()

    # Set the mode of the pin
    pi.set_mode(pin, pigpio.OUTPUT)

    # Create a waveform using the specified timings
    waves = []
    for high, low in pulse_timings:
        waves.append(pigpio.pulse(1 << pin, 0, int(high * 1000)))
        waves.append(pigpio.pulse(0, 1 << pin, int(low * 1000)))

    # Create a wave from the pulses
    pi.wave_add_generic(waves)

    # Create a wave ID for the waveform
    wave_id = pi.wave_create()

    # Send the waveform (this will repeat the waveform indefinitely)
    pi.wave_send_repeat(wave_id)

    try:
        # Keep the script running to allow the PWM signal to be generated
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop the waveform and clean up on Ctrl+C
        pi.wave_tx_stop()
        pi.wave_delete(wave_id)
        pi.stop()

    pass

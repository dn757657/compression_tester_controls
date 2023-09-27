import RPi.GPIO as GPIO
import pigpio
import time
import logging


class StepperMotor:
    def init(
            self,
            steps_per_rev,

    ):
        """
        could maybe use this to manage limits and all that jazz?
        :return:
        """
        pass


class StepperMotorDriver:
    def __init__(
            self,
            dir_pin: int,
            dsbl_pin: int,
            step_pin: int,
            cw_pin_high: bool,
            disable_high: bool,
            step_on_rising_edge: bool,
    ):
        # define pins
        self.dir_pin = dir_pin
        self.dsbl_pin = dsbl_pin
        self.step_pin = step_pin

        # set directionality, is pin high clockwise
        self.cw_pin_high = cw_pin_high

        # set if disable on disable pin is high or low signal
        self.disable_high = disable_high

        # set if pulse is defined by rising or falling edge
        if step_on_rising_edge:
            self.step_edge = 'rising'
        else:
            self.step_edge = 'falling'

        return

    def set_dir(
            self,
            direction: str='ccw'
    ):
        """
        maybe alter such that ccw and cs being high or low can be set in the args for
        different motors
        :param pin:
        :param dir:
        :return:
        """
        if direction not in ['cw', 'ccw']:
            logging.info(f'{dir}: not in possible directions')


        if direction == 'ccw':
            if self.cw_pin_high is True:
                GPIO.output(self.dir_pin, GPIO.LOW)
            elif self.cw_pin_high is False:
                GPIO.output(self.dir_pin, GPIO.HIGH)
        elif direction == 'cw':
            if self.cw_pin_high is True:
                GPIO.output(self.dir_pin, GPIO.HIGH)
            elif self.cw_pin_high is False:
                GPIO.output(self.dir_pin, GPIO.LOW)

        pass

    def enable_driver(
            self,
    ):
        if self.disable_high:
            GPIO.output(self.dsbl_pin, GPIO.LOW)
        pass

    def disable_driver(
            self,
    ):
        if self.disable_high:
            GPIO.output(self.dsbl_pin, GPIO.HIGH)
        pass

    # TODO test limits of both motors frequency?
    # TODO the limits of duty cycle are implied
    def move_steps(
            self,
            direction: str,
            steps: int,
            duty_cyle: float,
            freq: float
    ):
        """

        :param direction:
        :param steps:
        :param duty_cyle: percentage of time signal is high/ON
        :param freq:
        :return:
        """
        self.enable_driver()
        self.set_dir(direction=direction)

        for step in range(0, steps):
            self.step(duty_cycle=duty_cyle, freq=freq)

        return

    def step(
            self,
            duty_cycle,
            freq,
    ):
        """
        need to
        :param duty_cycle:
        :return:
        """
        # need to check the status of a pin, as just setting the pin could be
        # interpreted as a step in the wrong scenario
        step_pin_status = GPIO.input(self.step_pin)

        # calculate high time and low time form duty cycle
        period = 1/freq
        on_time = period * (duty_cycle / 100)
        off_time = period - on_time

        if step_pin_status:
            # step will trigger on rising edge, if status is true pin is high
            # need to go low and high again
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(off_time)
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(on_time)
        elif not step_pin_status:
            # pin is LOW and will trigger step on rising edge
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(on_time)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(off_time)

        return


# def move_pwm_rpigpio(
#         pin: int,
#         freq: int,
#         run_time: int,
#         duty_cycle: int=50,
# ):
#     pwm = GPIO.PWM(pin, freq)
#     pwm.start(duty_cycle)
#     time.sleep(run_time)
#     pwm.stop()
#
# # TODO new motion func
# # set duty cycle
# # set frequency
# # might instead need to make composite funcs for moving while checking something
#
# def move_pwm_pigpio(
#         pin,
#         pulse_timings,
# ):
#     # Initialize pigpio
#     pi = pigpio.pi()
#
#     # Set the mode of the pin
#     pi.set_mode(pin, pigpio.OUTPUT)
#
#     # Create a waveform using the specified timings
#     waves = []
#     for high, low in pulse_timings:
#         waves.append(pigpio.pulse(1 << pin, 0, int(high * 1000)))
#         waves.append(pigpio.pulse(0, 1 << pin, int(low * 1000)))
#
#     # Create a wave from the pulses
#     pi.wave_add_generic(waves)
#
#     # Create a wave ID for the waveform
#     wave_id = pi.wave_create()
#
#     # Send the waveform (this will repeat the waveform indefinitely)
#     pi.wave_send_repeat(wave_id)
#
#     try:
#         # Keep the script running to allow the PWM signal to be generated
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         # Stop the waveform and clean up on Ctrl+C
#         pi.wave_tx_stop()
#         pi.wave_delete(wave_id)
#         pi.stop()
#
#     pass

import logging

import RPi.GPIO as GPIO


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
MOTOR_DIRECTIONS = ['cw', 'ccw']


class StepperMotorDriver:
    def __init__(
            self,
            dir_pin: int,
            dsbl_pin: int,
            step_pin: int,
            cw_pin_high: bool,
            disable_high: bool,
            name: str = 'motor',
            **kawrgs
    ):
        self.name = name

        # config pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(dir_pin, GPIO.OUT)
        GPIO.setup(dsbl_pin, GPIO.OUT)
        GPIO.setup(step_pin, GPIO.OUT)

        self.direction = None
        self.frequency = None

        self.dir_pin = dir_pin
        self.dsbl_pin = dsbl_pin
        self.step_pin = step_pin

        self.pwd_chan = None

        # set directionality, is pin high clockwise
        self.cw_pin_high = cw_pin_high

        # set if disable on disable pin is high or low signal
        self.disable_high = disable_high

        logging.info(f"{self.name}: initialized")
        return

    def set_dir(
            self,
            direction: str
    ):
        """
        maybe alter such that ccw and cs being high or low can be set in the args for
        different motors
        :param direction:
        :return:
        """
        if direction not in MOTOR_DIRECTIONS:
            logging.info(f'{self.name}: {direction} not in {MOTOR_DIRECTIONS}')

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

        self.direction = direction
        logging.info(f"{self.name}: direction set to {direction}")
        pass

    def enable_driver(
            self,
    ):
        if self.disable_high:
            GPIO.output(self.dsbl_pin, GPIO.LOW)

        logging.info(f"{self.name}: enabled")
        pass

    def disable_driver(
            self,
    ):
        if self.disable_high:
            GPIO.output(self.dsbl_pin, GPIO.HIGH)

        logging.info(f"{self.name}: disabled")
        pass

    def set_frequency(self, freq: float):
        if freq < 0:  # swap direction if frequency negative
            #direction = [x for x in MOTOR_DIRECTIONS != direction][0]
            self.set_dir(direction='cw')
            self.frequency = abs(freq)
        elif freq > 0:
            self.set_dir(direction='ccw')
            self.frequency = freq
        elif freq == 0:
            #self.stop()
            return
        
        pass

    def reverse_direction(self):
        print(F"MOTOR DIR: {self.direction}")
        self.direction = list([set(MOTOR_DIRECTIONS) - {self.direction}][0])[0]
        print(F"REVSERSE MOTOR DIR: {self.direction}")
        pass

    def rotate(
            self,
            duty_cycle: float,
            freq: float,
    ):
        """

        :param direction:
        :param duty_cycle: should be between zero and 100
        :param freq: operational frequency in 1/s
        :return:
        """

        self.set_frequency(freq=freq)  # also sets direction
        
        logging.info(f"{self.name}: rotating: \n"
                     f"\tduty-cycle: {duty_cycle}\n"
                     f"\tfrequency : {self.frequency}\n"
                     f"\tdirection : {self.direction}")

        if not self.pwd_chan:
            self.enable_driver()
            self.pwd_chan = GPIO.PWM(self.step_pin, self.frequency)  # pin, freq
            self.pwd_chan.start(duty_cycle)
        else:
            self.pwd_chan.ChangeFrequency(self.frequency)
            self.pwd_chan.ChangeDutyCycle(duty_cycle)

        pass
    
    def stop(self):
        if self.pwd_chan:
            self.pwd_chan.stop()
            self.pwd_chan = None
            logging.info(f"{self.name}: stopped")
        pass



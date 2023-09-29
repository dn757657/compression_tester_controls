import RPi.GPIO as GPIO
import time

from motors.stepper_controls import StepperMotorDriver
from adc.ads1115 import ads1115_read_channels, init_ads1115, ads1115_bits_to_volts
from camera.canon_eosr50 import eosr50_init, eosr50_capture_and_save, gphoto2_get_active_ports

# Define pin connections
CRUSHING_STEP_PIN = 13
CRUSHING_DIR_PIN = 27
CRUSHING_ENA_PIN = 22

# Define pin connections
CAMERA_STEP_PIN = 19
CAMERA_DIR_PIN = 17
CAMERA_ENA_PIN = 26

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


# setup funcs
def check_big_stepper():
    crushing_stepper = StepperMotorDriver(**CRUSHING_STEPPER_PROPERTIES)
    crushing_stepper.move_steps(steps=1000, duty_cyle=(3/3.5)*100, direction='cw', freq=1000)
    crushing_stepper.move_steps(steps=1000, duty_cyle=(3/3.5)*100, direction='ccw', freq=1000)
    pass


def check_small_stepper():
    camera_stepper = StepperMotorDriver(**CAMERA_STEPPER_PROPERTIES)
    camera_stepper.move_steps(steps=1000, duty_cyle=50, direction='cw', freq=5000)
    camera_stepper.move_steps(steps=1000, duty_cyle=50, direction='ccw', freq=5000)
    pass


def A201_resistance(
        vin: float,
        vout: float,
        rf: float,
):
    """
    convert from voltages and sensitivity resistance to A201 sensor resistance
    :param vin:
    :param vout:
    :param rf:
    :return: resistance of sensor in units of rf
    """
    try:
        rs = rf/((vout/vin) - 1)
    except ZeroDivisionError:
        rs = 0

    return rs


def main():
    # # ADC testing
    # while True:
    #     adc = init_ads1115(gain=2/3, address=0x48)
    #
    #     bits_samples = ads1115_read_channels(req_channels=['A0', 'A1', 'A2', 'A3'], adc=adc)
    #
    #     volts_samples = {}
    #     for k, v in bits_samples.items():
    #         volts_samples[k] = ads1115_bits_to_volts(adc=adc, bits_val=v)
    #
    #     for k, v in volts_samples.items():
    #         vin = volts_samples['A3'] - volts_samples['A2']
    #         vout = volts_samples['A1'] - volts_samples['A0']
    #
    #         rs = A201_resistance(
    #             vin=vin,
    #             vout=vout,
    #             rf=13430
    #         )
    #         print(f'{vin}, {vout}')
    #         print(f'{rs}')
    #         # print(f'{k}: {v}')
    #
    #     time.sleep(0.5)

    # camera testign
    # active_ports = gphoto2_get_active_ports()
    # eosr50_init(port=active_ports[0])

    freq = 10
    for i in range(0, 10):
        eosr50_capture_and_save(port='usb:001,012', filename=f'test{i}.jpg')
        time.sleep(1/freq)


if __name__ == '__main__':
    main()
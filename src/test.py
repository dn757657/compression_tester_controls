# import Encoder
import time
import serial

from simple_pid import PID
from compression_tester_controls.protocols_dev import load_configs, inst_components


def init():
    configs = load_configs()
    components = inst_components(component_configs=configs)
    return components


def test():

    configs = load_configs()
    components = inst_components(component_configs=configs)
    adc = components.get('force_sensor_adc')
    a201 = components.get('A201')
    # adc_observer(adc)
    try:
        while True:
            state_sma = adc.get_state_SMA(n=100, unit='volts')
            vout = state_sma.get('a1') - state_sma.get('a0')
            vref = state_sma.get('a3') - state_sma.get('a2')
            load = a201.get_load(vout=vout, vref=vref)

            print(f"{state_sma}")
            print(f"a201 load: {load}")
    except KeyboardInterrupt:
        print("Stopping...")
        for channel in adc.channels:
            channel.stop_running()


from .compression_tester_controls.protocols import sample_a201_until_force_applied
def platon_sensing_test():
    components = init()
    adc = components.get('force_sensor_adc')
    a201 = components.get('A201')
    big_stepper = components.get('big_stepper')

    sample_a201_until_force_applied(
        force_sensor_adc=adc,
        force_sensor=a201,
        big_stepper=big_stepper
    )



if __name__ == '__main__':
    platon_sensing_test()
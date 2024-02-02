# import Encoder
import time
import serial

from simple_pid import PID
from compression_tester_controls.protocols_dev import load_configs, inst_components



def main():

    configs = load_configs()
    components = inst_components(component_configs=configs)
    adc = components.get('force_sensor_adc')
    a201 = components.get('A201')
    # adc_observer(adc)

    while True:
        state_sma = adc.get_state_SMA(n=100, unit='volts')
        vout = state_sma.get('a1') - state_sma.get('a0')
        vref = state_sma.get('a3') - state_sma.get('a2')
        load = a201.get_load(vout=vout, vref=vref)

        print(f"{state_sma}")
        print(f"a201 load: {load}")

# def adc_observer(adc):

#     for channel in adc.channels:
#         if not channel.running:
#             channel.start()

#     try:
#         while True:
#             for channel in adc.channels:
#                 print(f"{channel.name}: {adc.bits_to_volts(channel.sample())}")
#             time.sleep(0.1)  # Adjust the sampling interval as needed
#     except KeyboardInterrupt:
#         print("Stopping...")
#         for channel in adc.channels:
#             channel.stop_running()


if __name__ == '__main__':
    main()
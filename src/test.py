# import Encoder
import time
import serial

from simple_pid import PID
from compression_tester_controls.protocols_dev import load_configs, inst_components

def main():

    configs = load_configs()
    components = inst_components(component_configs=configs)
    adc = components.get('force_sensor_adc')
    adc_observer(adc)

def adc_observer(adc):

    for channel in adc.channels:
        if not channel.running:
            channel.start()

    try:
        while True:
            for channel in adc.channels:
                print(f"{channel.name}: {adc.bits_to_volts(channel.sample())}")
            time.sleep(0.1)  # Adjust the sampling interval as needed
    except KeyboardInterrupt:
        print("Stopping...")
        for channel in adc.channels:
            channel.stop_running()


if __name__ == '__main__':
    main()
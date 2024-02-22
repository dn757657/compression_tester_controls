
# import Encoder
import time
import serial
import threading

from simple_pid import PID
from compression_tester_controls.sys_functions import load_configs, inst_components
from compression_tester_controls.sys_protocols import platon_setup, camera_system_setup, test_frame_speed
from compression_tester_controls.components.canon_eosr50 import gphoto2_get_active_ports, eosr50_init, eosr50_continuous_capture_and_save
from compression_tester_controls.sys_functions import detect_force_anomoly, sample_force_sensor
from compression_tester_controls.utils import generate_s_curve_velocity_profile, adjust_pwm_based_on_position, scale_velocity_profile


def sys_init():
    configs = load_configs()
    components = inst_components(component_configs=configs)
    return components


# def test():

#     configs = load_configs()
#     components = inst_components(component_configs=configs)
#     adc = components.get('force_sensor_adc')
#     a201 = components.get('A201')
#     # adc_observer(adc)
#     try:
#         while True:
#             state_sma = adc.get_state_SMA(n=100, unit='volts')
#             vout = state_sma.get('a1') - state_sma.get('a0')
#             vref = state_sma.get('a3') - state_sma.get('a2')
#             load = a201.get_load(vout=vout, vref=vref)

#             print(f"{state_sma}")
#             print(f"a201 load: {load}")
#     except KeyboardInterrupt:
#         print("Stopping...")
#         for channel in adc.channels:
#             channel.stop_running()


# from compression_tester_controls.sys_functions import detect_force_anomoly
# def platon_sensing_test():
#     components = sys_init()
#     adc = components.get('force_sensor_adc')
#     a201 = components.get('A201')

#     detect_force_anomoly(
#         force_sensor_adc=adc,
#         force_sensor=a201,
#     )
import logging
import uuid
import subprocess

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

def test_canon_speed():
    cam_ports = gphoto2_get_active_ports()
    port = cam_ports[0]
    eosr50_init(port=port)
    filenames = list()

    start = time.time()
    while True:
        id = uuid.uuid4()
        filename = f"{id}.%C"  # %C uses extension assigned by cam
        try:
            subprocess.run([
                'sudo',
                'gphoto2',
                '--port', port,
                '--capture-image-and-download',
                '--filename', filename,
                '--keep'
            ],
                check=True
            )
            filenames.append(id)
            logging.info(f"Image {filename} Captured")
            i += 1  # only increment if captured

        except subprocess.CalledProcessError:
            logging.info(f"Failed to capture @ {port}.")

        if time.time() - start > 10:
            print(f"{len(filenames)} photos taken in {time.time() - start} seconds: {len(filenames) / (time.time() - start)} [photos/sec]")
            break


def test_force_sensor():
    components = sys_init()
    while True:
        time.sleep(1)
        sample_force_sensor(n_samples=10, components=components)


if __name__ == '__main__':
    test_frame_speed(runtime=10)

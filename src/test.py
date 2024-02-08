# import Encoder
import time
import serial

from simple_pid import PID
from compression_tester_controls.sys_functions import load_configs, inst_components
from compression_tester_controls.sys_protocols import platon_setup, camera_system_setup
from compression_tester_controls.components.canon_eosr50 import gphoto2_get_active_ports, gpohoto2_get_camera_settings
from compression_tester_controls.components.qsbd import send_command
# def sys_init():
#     configs = load_configs()
#     components = inst_components(component_configs=configs)
#     return components


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

def test_qsbd():
    enc_pos = send_command("RP")
    print(f"encoder pos = {enc_pos}")
    return


if __name__ == '__main__':
    test_qsbd()
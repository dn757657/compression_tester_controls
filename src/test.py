# import Encoder
import time
import serial

from simple_pid import PID
from compression_tester_controls.sys_functions import load_configs, inst_components
from compression_tester_controls.sys_protocols import platon_setup, camera_system_setup
from compression_tester_controls.components.canon_eosr50 import gphoto2_get_active_ports, gpohoto2_get_camera_settings
from compression_tester_controls.sys_functions import detect_force_anomoly

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

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

# def test_qsbd():
#     components = sys_init()
#     big_stepper_enc = components.get('e5')
#     a201 = components.get('A201')
#     force_sensor_adc = components.get('force_sensor_adc')
#     big_stepper = components.get('big_stepper')
#     big_stepper_pid = components.get('big_stepper_PID')

#     force_sensor_adc_sma_window: int = 100

#     while True:

#         while True:
#             state_n = force_sensor_adc.get_state_n(n=force_sensor_adc_sma_window, unit='volts')
#             states = [x.size for x in state_n.values()]
#             x = list()
#             for state in states:
#                 if state >= force_sensor_adc_sma_window:
#                     x.append(True)
#                 else:
#                     x.append(False)

#             if False in x:
#                 logging.info(f"Insufficient samples: {force_sensor_adc.name}. Retrying...")
#                 time.sleep(0.5)
#             else:
#                 break

#         print(f"position is: {big_stepper_enc.read()}")
#         big_stepper.rotate(freq=300, duty_cycle=80)

#         while True:
#             if detect_force_anomoly(
#                 force_sensor_adc=force_sensor_adc,
#                 force_sensor=a201,
#             ):
#                 big_stepper.stop()
#                 break

#         error = 5

#         print(f"found sample, position is: {big_stepper_enc.read()}")
#         # setpoint = input("Enter Desired Position: ")
#         setpoint = 100
#         big_stepper_pid.setpoint = setpoint
            
#         while True:
#             freq = big_stepper_pid(big_stepper_enc.read())

#             big_stepper.rotate(freq=freq, duty_cycle=80)

#             if (setpoint - error) < big_stepper_enc.read() < (setpoint + error):
#                 break

#     return


if __name__ == '__main__':
    platon_setup(components=sys_init())
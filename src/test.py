
# import Encoder
import time
import serial

from simple_pid import PID
from compression_tester_controls.sys_functions import load_configs, inst_components
from compression_tester_controls.sys_protocols import platon_setup, camera_system_setup
from compression_tester_controls.components.canon_eosr50 import gphoto2_get_active_ports, gpohoto2_get_camera_settings
from compression_tester_controls.sys_functions import detect_force_anomoly, sample_force_sensor
from compression_tester_controls.utils import generate_s_curve_velocity_profile, adjust_pwm_based_on_position


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

def test_qsbd():
    components = sys_init()
    big_stepper_enc = components.get('e5')
    a201 = components.get('A201')
    force_sensor_adc = components.get('force_sensor_adc')
    big_stepper = components.get('big_stepper')
    big_stepper_pid = components.get('big_stepper_PID')

    force_sensor_adc_sma_window: int = 100
    enc_init = big_stepper_enc.read()
    
    # freq = 500
    while True:

        error = 5

        setpoint = int(input("Enter Desired Position: "))
        start_pos = big_stepper_enc.read()
        total_pulses = setpoint - start_pos
        if total_pulses < 0:
            total_pulses = abs(total_pulses)
            freq_multi = -1
        else:
            freq_multi = 1 

        pos, vel = generate_s_curve_velocity_profile(total_pulses=total_pulses, steps=total_pulses)

        print(f"current pos: {big_stepper_enc.read()}, target: {setpoint}")
        while True:
            # freq = big_stepper_pid(sample_force_sensor(n_sample=100, components=components))
            enc_pos = big_stepper_enc.read()
            
            if (setpoint - error) < enc_pos < (setpoint + error):
                big_stepper.stop()
                print(f"position reached: {big_stepper_enc.read()} = {setpoint}")
                break
            
            enc_pos = big_stepper_enc.read() - start_pos
            new_freq = adjust_pwm_based_on_position(
                current_position=enc_pos,
                positions=pos,
                velocities=vel,
                max_pwm_frequency=400,
                min_pwm_frequency=50
            )
            big_stepper.rotate(freq=new_freq * freq_multi, duty_cycle=85)

    return


if __name__ == '__main__':
    test_qsbd()

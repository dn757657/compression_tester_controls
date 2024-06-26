import json
import logging
import os
import time
import threading

import numpy as np

from collections import OrderedDict
from importlib import resources, util
from pathlib import Path

from .components.factory import HardwareFactory
from .components.ads1115 import ADS1115
from .components.stepper import StepperMotorDriver
from .components.A201 import A201
from .utils import generate_scaled_s_curve, scale_velocity_profile, adjust_pwm_based_on_position


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
REQUIRED_CONFIG_ATTRS = ['name', 'type']


def load_configs(
        package: str = "compression_tester_controls.components.configs",
        directory: str = "configs",
        config_file_ext: str = 'json'
) -> dict():

    component_configs = dict()

    # Use importlib.resources to list all entries within the given directory of the package
    # if resources.is_resource(package, directory):
        # with resources.path(package, directory) as pkg_dir:
            # List all resources in the given directory
    for entry in resources.contents(package):
        config_dir = Path(f"{util.find_spec(package).origin}")
        config_dir = config_dir.parent
        entry_path = config_dir / Path(f"{entry}")
        if entry_path.is_file() and entry.endswith(f".{config_file_ext}"):
            # Open and load the JSON file
            with open(entry_path, "r") as f:
                d = json.load(f)
                all_reqd_attrs = True
                for attr in REQUIRED_CONFIG_ATTRS:
                    if attr not in d.keys():
                        logging.error(f"Config {entry} missing attribute: {attr}")
                        all_reqd_attrs = False
                        break
                if all_reqd_attrs:
                    component_configs[entry.split(".")[0]] = d

    return component_configs


def inst_components(
        component_configs: dict
):
    components = dict()
    sort_key = "init_priority"
    if all(sort_key in inner_dict for inner_dict in component_configs.values()):
        # Sort the dictionary of dictionaries by the specified key in the inner dictionaries
        sorted_tuples = sorted(component_configs.items(), key=lambda x: x[1][sort_key])
        # Convert the sorted list of tuples back into an OrderedDict to maintain the sorted order
        component_configs = OrderedDict(sorted_tuples)
    else:
        # Not all inner dictionaries contain the key, handle this case as needed
        raise ValueError(f"Not all component configs have the key '{sort_key}'")

    for config_name, config in component_configs.items():
        name = config.get('name')
        for k in config.keys():
            ref_tag = '_ref'
            new_config = None
            if ref_tag.lower() in k.lower():
                obj_ref = config.get(k)
                # print(f"assigning {k} object reference")
                # config.pop(k)  # drop old

                s = obj_ref.split(".")
                if len(s) > 2:
                    logging.info(f"Cannot configure {name}: incorrect object refernce")
                    continue
                ref_obj_name = s[0]
                ref_obj_attr = s[1]
                comp = components.get(ref_obj_name)
                if not comp:
                    logging.info(f"No component named: {ref_obj_name}, referenced in config: {name}")
                    continue
                try:
                    if not new_config:
                        new_config = dict()
                    new_config[k.rsplit('_', 1)[0]] = getattr(comp, ref_obj_attr)
                except ValueError:
                    logging.info(f"Component: {ref_obj_name} does not have attribute: {ref_obj_attr} - referenced in config: {name}")
                    continue
            if new_config:
                config = config | new_config

        # config_objects = [x for x in config.values() if "." in x]
        # for ob in config_objects:
        #     s = ob.split(".")
        #     if len(s) > 2:
        #         logging.info(f"Cannot configure {name}: incorrect object refernce")
        #         continue
        #     else:
        #         ref_obj_name = s[0]
        #         ref_obj_attr = s[1]
        #         comp = components.get(ref_obj_name)
        #         config[ob] = comp.ref_obj_attr

        components[name] = HardwareFactory().create_component(config=config)

    i2c_lock = threading.Lock()
    for component in components.values():
        attrs = dir(component)
        if 'i2c_lock'.lower() in attrs:
          component.i2c_lock = i2c_lock

    return components


def detect_force_anomoly(
        components,
        cusum_h: float = 4,
        cusum_k: float = 0.1,
        sma_window: int = 100,
):

    # while True:
    #     state_n = force_sensor_adc.get_state_n(n=sma_window, unit='volts')
    #     try:
    #         vouts = state_n.get('a1') - state_n.get('a0')
    #     except ValueError:
    #         vouts = np.array([])
    #     try:
    #         vrefs = state_n.get('a3') - state_n.get('a2')
    #     except ValueError:
    #         vrefs = np.array([])

    #     if vrefs.size >= sma_window:
    #         break
    #     if vouts.size >= sma_window:
    #         break
    #     else:
    #         logging.info(f"Insufficient samples: {force_sensor_adc.name}. Retrying...")
    #         time.sleep(0.5)

    rs = sample_force_sensor(n_samples=sma_window, components=components)

    # TODO convert to force instead?
    if detect_anomoly_rolling_cusum(samples=rs, h=cusum_h, k=cusum_k):
        return True
    else:
        return False


def detect_anomoly_rolling_cusum(samples, h, k):

    avg = np.mean(samples)
    std = np.std(samples)

    norm_samples = (samples - avg) / std
    norm_samples = norm_samples - k
    sh = np.maximum.accumulate(np.maximum(norm_samples, 0))
    sl = np.minimum.accumulate(np.minimum(norm_samples, 0))

    print(f"h : {h}\n"
          f"sh: {sh[-1]}\n"
          f"sl: {sl[-1]}\n")
    if sh[-1] > h:
        print(f'{sh[-1]} > {h}')
        return True
    if sl[-1] < -h:
        print(f'{sl[-1]} < {h}')
        return True

    return False


# def move_stepper_PID_target(
#         stepper,
#         pid,
#         enc,
#         stepper_dc: float,
#         setpoint: int,
#         error: int 
# ):
#     pid.setpoint = setpoint

#     while True:
#         fnew = pid(enc.get_encoder_count())
#         if fnew > 0:
#             stepper.
        
#         stepper.rotate(freq=abs(fnew), duty_cycle=stepper_dc)

#         if (setpoint - error) < enc.get_encoder_count() <= (setpoint + error):
#             stepper.stop()
#             break

def move_stepper_PID_target(
        stepper,
        pid,
        enc,
        stepper_dc: float,
        setpoint: int,
        error: int
):
    pid.setpoint = setpoint
    while True:
        enc_pos = enc.get_encoder_count()
        fnew = pid(enc_pos)
        stepper.rotate(freq=fnew, duty_cycle=stepper_dc)
        time.sleep(0.01)
        logging.info(f'{enc_pos} / {setpoint}')
        if (setpoint - error) < enc_pos <= (setpoint + error):
            stepper.stop()
            break


def sample_force_sensor(n_samples, components):
    force_sensor = components.get('A201')
    force_sensor_adc = components.get('force_sensor_adc')

    while True:
        state_n = force_sensor_adc.get_state_n(n=n_samples, unit='volts')
        try:
            vout1 = state_n.get('a1')
            vout2 = state_n.get('a0')
            vouts = vout1 - vout2
        except ValueError:
            vouts = np.array([])
        try:
            vref1 = state_n.get('a3')
            vref2 = state_n.get('a2')
            vrefs = vref1 - vref2
        except ValueError:
            vrefs = np.array([])

        # print([vout1.size, vout2.size, vref1.size, vref2.size])
        if all(v >= n_samples for v in [vout1.size, vout2.size, vref1.size, vref2.size]):
            break
        else:
            logging.info(f"Insufficient samples: {force_sensor_adc.name}. {vout1.size}/{n_samples} Retrying...")
            time.sleep(0.5)

    vout = np.array([np.mean(vouts)])
    vref = np.array([np.mean(vrefs)])
    # rs = force_sensor.get_rs(vout=vouts, vref=vrefs)
    load = force_sensor.get_load(vout=vout, vref=vref)
    # print(f"Force Sensor Vout mean: {np.mean(vouts)}")
    # print(f"Force Sensor Vref mean: {np.mean(vrefs)}")
    # print(f"Force Sensor RS mean: {np.mean(rs)}")
    # TODO
    # load =
    #force = np.mean(rs)

    return load


def get_a201_Rf(n_samples: int, components, rs: int):
    force_sensor = components.get('A201')
    force_sensor_adc = components.get('force_sensor_adc')

    while True:
        state_n = force_sensor_adc.get_state_n(n=n_samples, unit='volts')
        try:
            vout1 = state_n.get('a1')
            vout2 = state_n.get('a0')
            vouts = vout1 - vout2
        except ValueError:
            vouts = np.array([])
        try:
            vref1 = state_n.get('a3')
            vref2 = state_n.get('a2')
            vrefs = vref1 - vref2
        except ValueError:
            vrefs = np.array([])

        # print([vout1.size, vout2.size, vref1.size, vref2.size])
        if all(v >= n_samples for v in [vout1.size, vout2.size, vref1.size, vref2.size]):
            break
        else:
            logging.info(f"Insufficient samples: {force_sensor_adc.name}. {vout1.size}/{n_samples} Retrying...")
            time.sleep(0.5)

    rf = force_sensor.get_rf(rs=rs, vout=vouts, vref=vrefs)
    print(f"Force Sensor Rf mean: {np.mean(rf)}")
    # TODO
    # load =
    #force = np.mean(rs)

    return rf


# def move_big_stepper_to_setpoint(
#         components,
#         setpoint: int,
#         error: int = 1,
# ):
#     big_stepper_enc = components.get('e5')
#     big_stepper = components.get('big_stepper')

#     start_pos = big_stepper_enc.read()
#     total_pulses = abs(setpoint - start_pos)

#     if total_pulses > error:
#         min_pwm_frequency=50
#         pos, vel = generate_scaled_s_curve(
#             total_steps=total_pulses,
#             min_pwm_frequency=min_pwm_frequency,
#             max_pwm_frequency=400)

#         logging.info(f"Moving Crushing stepper: {start_pos} -> {setpoint}")
#         if start_pos < (setpoint + error):
#             big_stepper.set_dir(direction='ccw')
#         elif (setpoint - error) < start_pos:
#             big_stepper.set_dir(direction='cw')

#         enc_pos_prev = None
#         stall_count = 0
#         stall_count_limit = 10
#         while True:
#             enc_pos = big_stepper_enc.read()

#             if enc_pos_prev:
#                 if (enc_pos_prev - 10) < enc_pos < (enc_pos_prev + 10):
#                     stall_count += 1
#                     print(f"added one to stall count: {stall_count}")
#                     if stall_count > stall_count_limit:
#                         big_stepper.stop()
#                         logging.info(f"Motor Stalled @ {enc_pos}")
#                         break
#                 else:
#                     if stall_count > 0:
#                         stall_count = stall_count - 1
#                         print(f"subtracted one from stall count: {stall_count}")

#             if (setpoint - error) < enc_pos < (setpoint + error):
#                 big_stepper.stop()
#                 break
#             elif enc_pos_prev:
#                 if enc_pos_prev > enc_pos:  # moving up
#                     if (setpoint - error) < enc_pos:  # moved too far up
#                         big_stepper.stop()
#                         break
#                 elif enc_pos_prev < enc_pos:  # moving down
#                     if enc_pos > (setpoint + error):  # moved too far down
#                         big_stepper.stop()
#                         break

            
            

#             enc_pos_abs = enc_pos - start_pos
#             new_freq = adjust_pwm_based_on_position(
#                 current_position=abs(enc_pos_abs),
#                 positions=pos,
#                 velocities=vel,
#             )
#             big_stepper.rotate(freq=new_freq, duty_cycle=85)

#             enc_pos_prev = enc_pos
#     logging.info(f"Crushing Stepper moved: {start_pos} -> {big_stepper_enc.read()}")
#     return

def move_big_stepper_to_setpoint(
        components,
        setpoint: int,
        error: int = 1,
):
    big_stepper_enc = components.get('e5')
    big_stepper = components.get('big_stepper')

    start_pos = big_stepper_enc.read()
    total_pulses = abs(setpoint - start_pos)

    if total_pulses > error:
        min_pwm_frequency=50
        pos, vel = generate_scaled_s_curve(
            total_steps=total_pulses,
            min_pwm_frequency=min_pwm_frequency,
            max_pwm_frequency=400)

        logging.info(f"Moving Crushing stepper: {start_pos} -> {setpoint}")
        freq_multi = 1
        if start_pos < (setpoint + error):
            direction = 'ccw'
            big_stepper.set_dir(direction='ccw')
        elif (setpoint - error) < start_pos:
            big_stepper.set_dir(direction='cw')
            direction = 'cw'

        enc_pos_prev = None
        # stall_count = 0
        # stall_count_limit = 25
        while True:
            enc_pos = big_stepper_enc.read()

            #if enc_pos_prev:
            #    if (enc_pos_prev - 10) < enc_pos < (enc_pos_prev + 10):
            #        stall_count += 1
            #        print(f"added one to stall count: {stall_count}")
            #        if stall_count > stall_count_limit:
            #            big_stepper.stop()
            #            logging.info(f"Motor Stalled @ {enc_pos}")
            #            break
            #    else:
            #        if stall_count > 0:
            #            stall_count = stall_count - 1
            #            print(f"subtracted one from stall count: {stall_count}")

            if (setpoint - error) < enc_pos < (setpoint + error):
                big_stepper.stop()
                break
            # direction = 0
            # dir_lim = 5

            # USE MOTOR DIR INSTEAD OF MOMENTUM CALC SINCE ENCODER IS UNRELIABLE?
            if enc_pos_prev:
                if direction == 'cw':  # moving up
                    # direction += 1
                    # logging.info("Moving UP")
                    # if ((setpoint - error) < enc_pos) and direction > dir_lim:  # moved too far up
                    if ((setpoint - error) > enc_pos):  # moved too far up
                        big_stepper.stop()
                        break
                elif direction == 'ccw':  # moving down
                    # direction -= 1
                    # logging.info("Moving DOWN")
                    # if (enc_pos > (setpoint + error)) and direction < -dir_lim:  # moved too far down
                    if (enc_pos > (setpoint + error)):  # moved too far down
                        big_stepper.stop()
                        break

            enc_pos_abs = enc_pos - start_pos
            new_freq = adjust_pwm_based_on_position(
                current_position=abs(enc_pos_abs),
                positions=pos,
                velocities=vel,
            )
            big_stepper.rotate(freq=new_freq * freq_multi, duty_cycle=85)

            enc_pos_prev = enc_pos
    logging.info(f"Crushing Stepper moved: {start_pos} -> {big_stepper_enc.read()}")
    return


    # big_stepper_enc = components.get('e5')
    # big_stepper = components.get('big_stepper')

    # start_pos = big_stepper_enc.read()
    # total_pulses = abs(setpoint - start_pos)    

    # if total_pulses > error:
    #     min_pwm_frequency=50
    #     pos, vel = generate_scaled_s_curve(
    #         total_steps=total_pulses,
    #         min_pwm_frequency=min_pwm_frequency,
    #         max_pwm_frequency=400) 
        
    #     logging.info(f"Moving Crushing stepper: {start_pos} -> {setpoint}")
    #     if start_pos < (setpoint + error):
    #         big_stepper.set_dir(direction='ccw')
    #     elif (setpoint - error) < start_pos:
    #         big_stepper.set_dir(direction='cw')

    #     enc_pos_prev = None
    #     stall_count = 0
    #     stall_count_limit = 10
    #     while True:
    #         enc_pos = big_stepper_enc.read()

    #         if enc_pos_prev:
    #             if (enc_pos_prev - 10) < enc_pos < (enc_pos_prev + 10):
    #                 stall_count += 1
    #                 print(f"added one to stall count: {stall_count}")
    #                 if stall_count > stall_count_limit:
    #                     big_stepper.stop()
    #                     logging.info(f"Motor Stalled @ {enc_pos}")
    #                     break
    #             else:
    #                 if stall_count > 0:
    #                     stall_count = stall_count - 1
    #                     print(f"subtracted one from stall count: {stall_count}")

    #         if (setpoint - error) < enc_pos < (setpoint + error):
    #             big_stepper.stop()
    #             break
    #         elif enc_pos_prev:
    #             if enc_pos_prev > enc_pos:  # moving up
    #                 if (setpoint - error) < enc_pos:  # moved too far up
    #                     big_stepper.stop()
    #                     break
    #             elif enc_pos_prev < enc_pos:  # moving down
    #                 if enc_pos > (setpoint + error):  # moved too far down
    #                     big_stepper.stop()
    #                     break

    #         enc_pos_abs = enc_pos - start_pos
    #         new_freq = adjust_pwm_based_on_position(
    #             current_position=abs(enc_pos_abs),
    #             positions=pos,
    #             velocities=vel,
    #         )
    #         big_stepper.rotate(freq=new_freq, duty_cycle=85)

    #         enc_pos_prev = enc_pos
    # logging.info(f"Crushing Stepper moved: {start_pos} -> {big_stepper_enc.read()}")
    # return


if __name__ == '__main__':
    configs = load_configs()
    inst_components(component_configs=configs)


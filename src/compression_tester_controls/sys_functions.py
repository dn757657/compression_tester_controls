import json
import logging
import os
import time

import numpy as np

from collections import OrderedDict
from importlib import resources

from .components.factory import HardwareFactory
from .components.ads1115 import ADS1115
from .components.stepper import StepperMotorDriver
from .components.A201 import A201


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
REQUIRED_CONFIG_ATTRS = ['name', 'type']


def load_configs(
        package: str, 
        directory: str = "configs", 
        config_file_ext: str = 'json'
) -> dict():
    
    component_configs = dict()
    
    # Use importlib.resources to list all entries within the given directory of the package
    if resources.is_resource(package, directory):
        with resources.path(package, directory) as pkg_dir:
            # List all resources in the given directory
            for entry in resources.contents(package):
                entry_path = pkg_dir / entry
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



# def load_configs(
#         base_dir: str = f"./components/configs",
#         config_file_ext: str = 'json'
# ):  
    
#     script_path = os.path.dirname(os.path.realpath(__file__))
#     print(f"{script_path}")

#     component_configs = dict()
#     for file in os.listdir(f"{script_path}/{base_dir}"):
#         if file.endswith(f".{config_file_ext}"):
#             with open(f"{script_path}/{base_dir}/{file}", "r") as f:

#                 d = json.load(f)
#                 all_reqd_attrs = True
#                 for attr in REQUIRED_CONFIG_ATTRS:
#                     if attr not in d.keys():
#                         logging.error(f"Config {file} missing attribute: {attr}")
#                         all_reqd_attrs = False
#                         break
#                 if all_reqd_attrs:
#                     component_configs[file.split(".")[0]] = d

#     return component_configs


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

    return components


def detect_force_anomoly(
        force_sensor_adc: ADS1115,
        force_sensor: A201,
        cusum_h: float = 4,
        cusum_k: float = 0.1,
        sma_window: int = 100,
):

    while True:
        state_n = force_sensor_adc.get_state_n(n=sma_window, unit='volts')
        try:
            vouts = state_n.get('a1') - state_n.get('a0')
        except ValueError:
            vouts = np.array([])
        try:
            vrefs = state_n.get('a3') - state_n.get('a2')
        except ValueError:
            vrefs = np.array([])

        if vrefs.size >= sma_window:
            break
        if vouts.size >= sma_window:
            break
        else:
            logging.info(f"Insufficient samples: {force_sensor_adc.name}. Retrying...")
            time.sleep(0.5)

    rs = force_sensor.get_rs(vout=vouts, vref=vrefs)

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

    # print(f"h : {h}\n"
        #   f"sh: {sh[-1]}\n"
        #   f"sl: {sl[-1]}\n")
    if sh[-1] > h:
        return True
    if sl[-1] < -h:
        return True

    return False    


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
        fnew = pid(enc.read())
        stepper.rotate(freq=fnew, duty_cycle=stepper_dc)

        if (setpoint - error) < enc.read() <= (setpoint + error):
            stepper.stop()
            break 


def get_force_zero(n_samples, components):
    force_sensor = components.get('A201')
    force_sensor_adc = components.get('force_sensor_adc')

    while True:
        state_n = force_sensor_adc.get_state_n(n=n_samples, unit='volts')
        try:
            vouts = state_n.get('a1') - state_n.get('a0')
        except ValueError:
            vouts = np.array([])
        try:
            vrefs = state_n.get('a3') - state_n.get('a2')
        except ValueError:
            vrefs = np.array([])

        if vrefs.size >= n_samples:
            break
        if vouts.size >= n_samples:
            break
        else:
            logging.info(f"Insufficient samples: {force_sensor_adc.name}. {vouts.size}/{n_samples} Retrying...")
            time.sleep(0.5)

    rs = force_sensor.get_rs(vout=vouts, vref=vrefs)
    # TODO
    # load =
    force_zero = np.mean(rs)

    return force_zero 


if __name__ == '__main__':
    configs = load_configs()
    inst_components(component_configs=configs)


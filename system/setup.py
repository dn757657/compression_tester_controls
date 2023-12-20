import json
import os
import sys

# so we can find other same level packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from typing import Union

from utils import load_sys_json, write_sys_json
from motors.stepper_controls import StepperMotorDriver
from adc.ads1115 import ADS1115
from misc_components.switch import DiPoleSwitch
from rpi.setup import init_pi_pins

DEFAULT_INIT_PARAMS = {
    'endstop1': {
        'channel1': "A0",
        'channel2': "A2",
        'trigger_threshold': 2,
        'trigger_above_threshold': False,
    },

    'endstop2': {
        'channel1': "A1",
        'channel2': "A2",
        'trigger_threshold': 2,
        'trigger_above_threshold': False,
    },

    'crushing_stepper': {
        'step_pin': 13,
        'dir_pin': 27,
        'dsbl_pin': 22,
        'cw_pin_high': False,
        'disable_high': False,
        'step_on_rising_edge': False,
        'default_duty_cyle': (3/3.5)*100,
        'default_frequency': 1000
    },

    'camera_stepper': {
        'step_pin': 12,
        'dir_pin': 17,
        'dsbl_pin': 26,
        'cw_pin_high': False,
        'disable_high': False,
        'step_on_rising_edge': True,
        'default_duty_cyle': 50,
        'default_frequency': 500
    },

    'force_sensor_adc': {
        'address': 0x48,
        'gain': 2/3,
        'channel_labels': ["A0", "A1", "A2", "A3"],
    },

    'camera_endstops_adc': {
        'address': 0x49,
        'gain': 2/3,
        'channel_labels': ["A0", "A1", "A2"]
    },

    'rpi4': {
        'pin_mode': 'BCM'
    },
}

STATE_DEFAULTS = {
    'camera_stepper_last_dir': "cw",
    'camera_stepper_steps_to_untrigger_endstop': 112  # determined manually for now - set auto later
}

SYSTEM_JSON_FILEPATH = os.path.join(".", "system_files.json")
STATE_JSON_KEY = 'state_json_fp'
INIT_JSON_KEY = 'init_json_fp'
SYSTEM_FILES_DEFAULTS = {
    STATE_JSON_KEY: os.path.join(".", "system_state_variables.json"),
    INIT_JSON_KEY: os.path.join(".", "system_initialization_parameters.json")
}

SYSTEM_FILES = load_sys_json(SYSTEM_JSON_FILEPATH, SYSTEM_FILES_DEFAULTS)


def load_state(
        system_file=SYSTEM_FILES[STATE_JSON_KEY],
):
    state = load_sys_json(fp=system_file, defaults=STATE_DEFAULTS)

    return state


def save_state(
        state: dict,
        system_file=SYSTEM_FILES[STATE_JSON_KEY],
):
    write_sys_json(fp=system_file, state=state)
    pass


def load_init_vars(
        system_file=SYSTEM_FILES[INIT_JSON_KEY]
):
    init_vars = load_sys_json(fp=system_file, defaults=DEFAULT_INIT_PARAMS)
    return init_vars


def init_components(
        init_vars: dict
):
    """
    initialize any components as defined by init vars
    :param init_vars:
    :return:
    """
    # TODO add some error handling here if components cant be intiialized

    camera_stepper = StepperMotorDriver(**init_vars.get('camera_stepper'))
    crushing_stepper = StepperMotorDriver(**init_vars.get('crushing_stepper'))

    force_sensor_adc = ADS1115(**init_vars.get('force_sensor_adc'))
    camera_endstops_adc = ADS1115(**init_vars.get('camera_endstops_adc'))

    endstop_params = init_vars.get('end_stop1')
    endstop1 = DiPoleSwitch(
        channel1=force_sensor_adc.channel_states[endstop_params.get('channel1')],
        channel2=force_sensor_adc.channel_states[endstop_params.get('channel2')],
        trigger_threshold=endstop_params.get('trigger_threshold'),
        trigger_above_threshold=endstop_params.get('trigger_above_threshold')
    )

    endstop_params = init_vars.get('end_stop2')
    endstop2 = DiPoleSwitch(
        channel1=force_sensor_adc.channel_states[endstop_params.get('channel1')],
        channel2=force_sensor_adc.channel_states[endstop_params.get('channel2')],
        trigger_threshold=endstop_params.get('trigger_threshold'),
        trigger_above_threshold=endstop_params.get('trigger_above_threshold')
    )

    # this sucks but it works for now
    pi_channels = [v for k, v in init_vars.items() if 'pin' in k]
    init_pi_pins(channel_list=pi_channels, pin_mode=init_vars.get('rpi4').get('pin_mode'))

    comps = {
        'camera_stepper': camera_stepper,
        'crushing_stepper': crushing_stepper,
        'force_sensor_adc': force_sensor_adc,
        'camera_endstops_adc': camera_endstops_adc,
        'endstop1': endstop1,
        'endstop2': endstop2
    }

    return comps


def main():
    system_files = load_sys_json(SYSTEM_JSON_FILEPATH, SYSTEM_FILES_DEFAULTS)
    state = load_sys_json(fp=system_files['state_json_fp'], defaults=STATE_DEFAULTS)
    init_vars = load_sys_json(fp=system_files['init_json_fp'], defaults=DEFAULT_INIT_PARAMS)

    comps = init_components(init_vars=init_vars)

    # test adc init - maybe move to adc file
    adc1 = comps.get('force_sensor_adc')
    print(f'{adc1.channel_states.__str__()}')

    endstop1 = comps.get('endstop1')
    print(f'{endstop1.state.__str__()}')

    endstop2 = comps.get('endstop2')
    print(f'{endstop2.state.__str__()}')
    pass


if __name__ == "__main__":
    main()

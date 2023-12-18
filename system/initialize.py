import json
import os

from pathlib import Path
from typing import Union

from .utils import load_sys_json, write_sys_json

INIT_VARS = {
    # end stop switch thresholds - what voltage is considered on/off?
    # endstop input voltage
    # endstop trigger threshhold
    # endstop trigger_above_treshold: False  # triggered state is above or below threshold

    # motor params
    'crushing_stepper_step_pin': 13,
    'crushing_stepper_dir_pin': 27,
    'crushing_stepper_dsbl_pin': 22,
    'crushing_stepper_cw_pin_high': False,
    'crushing_stepper_disable_high': False,
    'crushing_stepper_step_on_rising_edge': False,

    'camera_stepper_step_pin': 12,
    'camera_stepper_dir_pin': 17,
    'camera_stepper_dsbl_pin': 26,
    'camera_stepper_cw_pin_high': False,
    'camera_stepper_disable_high': False,
    'camera_stepper_step_on_rising_edge': True,

    # adc params
    'force_adc_addr': 0x48,
    'force_adc_gain': 2/3,
    'force_adc_channels': ["A0", "A1", "A2", "A3"],

    'camera_position_adc_addr': 0x49,
    'camera_position_adc_gain': 2/3,
    'camera_position_adc_channels': ["A0", "A1", "A2"]
}

STATE_DEFAULTS = {
    'camera_stepper_last_dir': "cw",
    'camera_stepper_end_stop_last_triggered': "cw"
}

SYSTEM_JSON_FILEPATH = os.path.join(".", "system_files.json")
STATE_JSON_KEY = 'state_json_fp'
INIT_JSON_KEY = 'init_json_fp'
SYSTEM_FILES_DEFAULTS = {
    STATE_JSON_KEY: os.path.join(".", "system_state_variables.json"),
    INIT_JSON_KEY: os.path.join(".", "system_initialization_variables.json")
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


def init_system(
        system_file=SYSTEM_FILES[INIT_JSON_KEY]
):
    init_vars = load_sys_json(fp=system_file, defaults=INIT_VARS)
    return init_vars


def main():
    system_files = load_sys_json(SYSTEM_JSON_FILEPATH, SYSTEM_FILES_DEFAULTS)
    state = load_sys_json(fp=system_files['state_json_fp'], defaults=STATE_DEFAULTS)
    init_vars = load_sys_json(fp=system_files['init_json_fp'], defaults=INIT_VARS)

    pass


if __name__ == "__main__":
    main()

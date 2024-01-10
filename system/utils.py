import json
import os

from pathlib import Path
from typing import Union


def load_sys_json(
        fp: Union[Path, str],
        defaults: dict
):
    """
    :return:
    """

    if not os.path.exists(fp):  # if not present make using defaults
        write_sys_json(fp=fp, state=defaults)

    with open(fp, 'r') as file:
        d = json.load(file)

    return d


def write_sys_json(
        fp: Union[Path, str],
        state: dict
):

    with open(fp, 'w') as file:
        json.dump(state, file, indent=4)

    pass


def num_photos_2_cam_stepper_freq(
        num_photos: int,
        seconds_per_photo: int = 1.5,
        steps_per_rotation: int = 54600,
):
    """
    num photos is photos desired per rotation
    need to estimate since cam is inconsistent
    :param num_photos:
    :param seconds_per_photo:
    :return:
    """

    freq = 1 / (num_photos * seconds_per_photo * steps_per_rotation)

    return freq

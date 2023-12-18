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

import Encoder
import time

from simple_pid import PID
from compression_tester_controls.protocols_dev import load_configs, inst_components

configs = load_configs()
components = inst_components(component_configs=configs)

print(f"{components.__str__()}")

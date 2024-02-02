# import Encoder
import time
import serial

from simple_pid import PID
from compression_tester_controls.protocols_dev import load_configs, inst_components


configs = load_configs()
components = inst_components(component_configs=configs)

time.sleep(1)

a201 = components.get('A201')
load, rs = a201.sample(n_samples = 100)

print(f"A201 Rs: {rs}")
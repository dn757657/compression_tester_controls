# import Encoder
import time
import serial

from simple_pid import PID
from compression_tester_controls.protocols_dev import load_configs, inst_components


configs = load_configs()
components = inst_components(component_configs=configs)

a = components.get('force_sensor_adc')
x = a.a0.sample()
print(x)
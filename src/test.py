import Encoder
import time

from compression_tester_controls.protocols_dev import load_configs, inst_components

configs = load_configs()
components = inst_components(component_configs=configs)

enc = Encoder.Encoder(23, 24)
big_stepper = components.get('big_stepper')

big_stepper.rotate(freq=500, duty_cyle=85, direction='cw')

start = time.time()
while True:
    print(f"{enc.read()}")
    if time.time() - start >= 10:
        big_stepper.stop()
import time

from compression_tester_controls.protocols_dev import load_configs, inst_components

configs = load_configs()
components = inst_components(component_configs=configs)

big_stepper = components.get('big_stepper')
big_stepper.rotate(freq=500, duty_cyle=85, direction='cw')
time.sleep(1)
big_stepper.stop()

print() 
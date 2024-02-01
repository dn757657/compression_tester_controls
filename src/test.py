import Encoder
import time

from simple_pid import PID
from compression_tester_controls.protocols_dev import load_configs, inst_components

configs = load_configs()
components = inst_components(component_configs=configs)

big_stepper = components.get("big_stepper")
enc = components.get("e5")

setpoint = 100
pid = PID(10, 0, 0, setpoint=setpoint)

print(f"{components.__str__()}")

enc_pos = enc.read()

pid.output_limits = (0, 1000)
pid.sample_time = 0.01

err = 0.1
while True:
    enc_pos = enc.read()

    freq = pid(enc_pos)
    big_stepper.rotate(
        freq=freq,
        direction='ccw',
        duty_cyle=85
    )

    if (setpoint - (setpoint * err)) > setpoint > (setpoint + (setpoint * err)):
        # big_stepper.stop()
        break
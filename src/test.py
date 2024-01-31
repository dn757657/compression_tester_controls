import Encoder
import time

from simple_pid import PID
from compression_tester_controls.protocols_dev import load_configs, inst_components

configs = load_configs()
components = inst_components(component_configs=configs)

enc = Encoder.Encoder(23, 24)
big_stepper = components.get('big_stepper')

# big_stepper.rotate(freq=500, duty_cyle=85, direction='cw')
setpoint = 100
pid = PID(1, 0.1, 0.05, setpoint=setpoint)
pid.sample_time = 0.01

if enc.read() > setpoint:
    direction = 'cw'
else:
    direction = 'ccw'

while True:
    enc_pos = enc.read()
    print(f"encoder position: {enc_pos}")

    freq = pid(enc_pos)
    big_stepper.rotate(freq=freq, duty_cyle=85, direction=direction)

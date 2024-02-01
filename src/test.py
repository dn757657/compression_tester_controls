import Encoder
import time

from simple_pid import PID
from compression_tester_controls.protocols_dev import load_configs, inst_components

configs = load_configs()
components = inst_components(component_configs=configs)

big_stepper = components.get("big_stepper")
#big_stepper.rotate(freq=-500, duty_cyle=85)
#time.sleep(10)
enc = components.get("e5")

setpoint = 300
pid = PID(5, 0, 0, setpoint=setpoint)

print(f"{components.__str__()}")

enc_pos = enc.read()

pid.output_limits = (-10, 10)
pid.sample_time = 0.01

err = 0

while True:
    setpoint = int(input("enter setpoint: "))
    pid.setpoint = int(setpoint)
    while True:
        enc_pos = enc.read()
        print(f"encoder position: {enc_pos}")
        
        freq = pid(enc_pos)
        print(f"control command: {freq}")
        big_stepper.rotate(
            freq=freq,
#            direction='ccw',
            duty_cyle=85
        )

        if (setpoint - err) <= enc.read() <= (setpoint + err):
        #if setpoint == enc.read():
            big_stepper.stop()
            
            print(f"setpoint reached")
            print(f"enc pos = {enc_pos}")
            break

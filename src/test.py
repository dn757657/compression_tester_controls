# import Encoder
import time
import serial

from simple_pid import PID
from compression_tester_controls.protocols_dev import load_configs, inst_components


def get_encoder_position(ser, port='/dev/ttyACM0', baudrate=9600,):
    # with serial.Serial(port, baudrate, timeout=1) as ser:
        # time.sleep(2)  # Allow time for serial connection to initialize
    ser.flushInput()  # Clear input buffer

    # Send request
    ser.write(b'R')  # Request encoder position
    time.sleep(0.001)   # Short delay to ensure data is processed
    
    # Read response
    if ser.in_waiting > 0:
        position = ser.readline().decode().strip()
        return int(position)
    else:
        return None

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)
configs = load_configs()
components = inst_components(component_configs=configs)

stepper = components.get('big_stepper')
stepper.rotate(freq=-500, duty_cyle=85)

start = time.time()
while True:
    enc_pos = get_encoder_position(port='COM4', ser=ser)

    print(f"enc pos: {enc_pos}")
    if (time.time() - start)  > 1:
        stepper.stop()
        break

# big_stepper = components.get("big_stepper")
# #big_stepper.rotate(freq=-500, duty_cyle=85)
# #time.sleep(10)
# # enc = components.get("e5")

# setpoint = 300
# pid = PID(5, 0, 0, setpoint=setpoint)

# print(f"{components.__str__()}")

# enc_pos = enc.read()

# pid.output_limits = (-10, 10)
# pid.sample_time = 0.01

# err = 0

# while True:
#     setpoint = int(input("enter setpoint: "))
#     pid.setpoint = int(setpoint)
#     while True:
#         enc_pos = enc.read()
#         print(f"encoder position: {enc_pos}")
        
#         freq = pid(enc_pos)
#         print(f"control command: {freq}")
#         big_stepper.rotate(
#             freq=freq,
# #            direction='ccw',
#             duty_cyle=85
#         )

#         if (setpoint - err) <= enc.read() <= (setpoint + err):
#         #if setpoint == enc.read():
#             big_stepper.stop()
            
#             print(f"setpoint reached")
#             print(f"enc pos = {enc_pos}")
#             break

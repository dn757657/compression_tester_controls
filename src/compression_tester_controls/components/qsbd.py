import serial
import time

# Initialize serial connection
serial_port = '/dev/ttyUSB0'  # Adjust this to your encoder's port
baud_rate = 9600  # Standard baud rate for communication
ser = serial.Serial(serial_port, baud_rate, timeout=1)

def send_command(command):
    ser.write((command + '\r').encode())  # Commands must end with carriage return
    time.sleep(0.2)  # Wait for the command to be processed
    response = ser.readline().decode().strip()  # Read the response, if any
    print(f"Sent: {command}, Received: {response}")  # Optional: print command and response

try:
    # Configuration commands based on assumptions
    send_command('R')    # Reset the device
    send_command('QM')   # Set mode to Quadrature with Index
    send_command('SE10000')  # Set encoder resolution, adjust as needed
    send_command('SB9600')   # Set baud rate, adjust if different
    send_command('OF1')   # Set output format to ASCII
    
    # Read position command
    while True:
        send_command('RP')  # Read position
        time.sleep(1)  # Adjust the delay based on how frequently you want to read the position

except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    ser.close()  # Ensure serial connection is closed on termination
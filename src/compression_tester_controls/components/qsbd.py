import serial
import time

# Replace '/dev/ttyUSB0' with the correct serial port for your Raspberry Pi
serial_port = '/dev/ttyUSB0'
baud_rate = 9600  # Adjust as necessary

# Open the serial connection
ser = serial.Serial(serial_port, baud_rate, timeout=1)

# Function to send command to QSB-D encoder
def send_command(command):
    serial_port = '/dev/ttyUSB0'
    baud_rate = 9600  # Adjust as necessary

    # Open the serial connection
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    ser.write(command.encode())
    time.sleep(0.1)  # Short delay to ensure command is processed
    response = ser.readline().decode().strip()  # Read the response
    ser.close()
    
    return response

# Example: Initialize encoder (replace 'XX' with actual commands)
# Example command to read position: "RP"
# You may need to send initialization commands here based on your preferences

# Reading the encoder position
position = send_command('RP')
print(f"Encoder Position: {position}")

# Close the serial connection
ser.close()

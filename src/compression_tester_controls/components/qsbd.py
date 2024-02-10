import serial
import time
import logging


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


class E5UsDigitalEncoder():
    def __init__(
            self,
            name: str,
            serial_port: str = '/dev/ttyUSB0',
            baud_rate: int = 230400,
    ):

        self.name = name
        self.ser = serial.Serial(serial_port, baud_rate, timeout=1)

        self._send_command('W0000')  # init in quadrature mode
        self._send_command('W0902')  # reset counter
        self._send_command('W166')  # confirm baud rate

        pass
    
    def _send_command(self, command: str):
        self.ser.write((command + '\r').encode())  # Commands must end with carriage return
        response = self.ser.readline().decode().strip()  # Read the response, if any
        return response

    def read(self):
        response = self._send_command('R0E')
        if response[0] == 'r':  # Check if it's a read response
            register = response[1:3]
            data = response[3:11]  # Extract the data part
            position = int(data, 16)  # Convert data to integer
        else:
            position = None
        
        return position
    

def main():
    enc = E5UsDigitalEncoder(name='E5')
    enc_pos = enc.read()
    print(f"E5 Pos: {enc_pos}")


if __name__ == '__main__':
    main()
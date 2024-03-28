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
            **kwargs
    ):

        self.name = name
        self.ser = serial.Serial(serial_port, baud_rate, timeout=1)
        
        self._send_command('W0000')  # init in quadrature mode
        self._send_command('W04000')  # set count direction
        self._send_command('W0902')  # reset counter
        self._send_command('W1660A')  # confirm baud rate
        self._send_command('W0300')
        self._send_command('S0E')

        self.initial_count = self.read()

        logging.info("Initialized QSB-D.")

        pass
    
    def _send_command(self, command: str):
        self.ser.write((command + '\r').encode())  # Commands must end with carriage return
        response = self.ser.readline().decode().strip()  # Read the response, if any
        return response

    def read(self):
        response = self._send_command('R0E')
        if response[0] == 'r':  # Check if it's a read response
            s = response.split(" ")
            register = s[0]
            data = s[2]  # Extract the data part
            position = int(data, 16)  # Convert data to integer
        else:
            position = None
        
        return position


# testing
import threading
import serial
import logging
import time
from enum import Enum, unique

logging.basicConfig(level=logging.INFO)

@unique
class QuadratureMode(Enum):
    X1 = 1
    X2 = 2
    X4 = 4

@unique
class EncoderDirection(Enum):
    CountUp = 0
    CountDown = 1

class DeviceController:
    def __init__(self, port_name, baud_rate, quadrature_mode, encoder_direction, encoder_resolution_nm):
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.quadrature_mode = quadrature_mode
        self.encoder_direction = encoder_direction
        self.encoder_resolution_nm = encoder_resolution_nm

        self.serial_port = None
        self.connected = False
        self.encoder_count = 0
        self._stop_reading_thread = threading.Event()
        self._reading_thread = None

        self._connection_lock = threading.Lock()
        self._encoder_count_lock = threading.Lock()

    def connect(self):
        with self._connection_lock:
            try:
                self.serial_port = serial.Serial(port=self.port_name, baudrate=self.baud_rate,
                                                 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                                                 bytesize=serial.EIGHTBITS, timeout=1)
                logging.info(f"Connected to {self.port_name}.")

                # Configure the device as needed
                self.configure_device()

                self.connected = True
                self.start_reading_thread()

            except Exception as e:
                logging.error(f"Failed to connect: {e}")
                self.disconnect()

    def configure_device(self):
        # Send configuration commands to the device
        # Example: self.write_command('03', self.quadrature_mode.value)
        pass

    def write_command(self, register, data):
        if self.serial_port and self.serial_port.isOpen():
            command = f'W{register}{data:08X}\n'  # Adapt command format as needed
            self.serial_port.write(command.encode('utf-8'))
            logging.info(f"Sent command: {command}")

    def start_reading_thread(self):
        self._stop_reading_thread.clear()
        self._reading_thread = threading.Thread(target=self._reading_loop, daemon=True)
        self._reading_thread.start()

    def _reading_loop(self):
        while not self._stop_reading_thread.is_set():
            if not self.connected:
                break
            # Implement reading logic here, similar to EncoderCountReaderLoop in C#
            # Example reading and parsing logic
            try:
                response = self.serial_port.readline().decode('utf-8').strip()
                with self._encoder_count_lock:
                    self.encoder_count += 1  # Example operation; adapt as needed
            except Exception as e:
                logging.error(f"Reading loop error: {e}")
            time.sleep(0.1)  # Sleep to simulate reading interval; adjust as necessary

    def disconnect(self):
        with self._connection_lock:
            if self.serial_port and self.serial_port.isOpen():
                self.serial_port.close()
            self.connected = False
            self._stop_reading_thread.set()
            if self._reading_thread:
                self._reading_thread.join()
            logging.info("Disconnected.")

    def get_encoder_count(self):
        with self._encoder_count_lock:
            return self.encoder_count

# Example usage
if __name__ == '__main__':
    device_controller = DeviceController(
        port_name='COM3',  # Change to your port
        baud_rate=115200,
        quadrature_mode=QuadratureMode.X4,
        encoder_direction=EncoderDirection.CountUp,
        encoder_resolution_nm=0.01
    )
    device_controller.connect()
    time.sleep(2)  # Simulate operation time
    if device_controller.connected:
        print(f"Encoder count: {device_controller.get_encoder_count()}")
    device_controller.disconnect()


def test():
    device_controller = DeviceController(
        port_name='COM5',  # Change to your port
        baud_rate=230400,
        quadrature_mode=QuadratureMode.X4,
        encoder_direction=EncoderDirection.CountUp,
        encoder_resolution_nm=0.01
    )
    device_controller.connect()
    time.sleep(2)  # Simulate operation time

    if device_controller.connected:
        print(f"Encoder count: {device_controller.get_encoder_count()}")
    device_controller.disconnect()
    


def main():
    enc = E5UsDigitalEncoder(name='E5')
    enc_pos = enc.read()
    print(f"E5 Pos: {enc_pos}")


if __name__ == '__main__':
    main()
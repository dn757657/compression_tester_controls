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
        try:
            if self.serial_port is not None:
                raise Exception("Cannot reconnect using the same DeviceController instance.")
            self.serial_port = serial.Serial(self.port_name, self.baud_rate, timeout=1)
            logging.info(f"Connected to {self.port_name}.")

            # Resetting the device (assuming DTR line usage is applicable in your context)
            self.serial_port.dtr = False
            self.serial_port.dtr = True

            # Example configuration commands
            self.write_command('15', 0x0000000F)  # Adjust the command as necessary

            # Read the first line if needed (handling the specific device behavior on reset)
            try:
                first_line = self.serial_port.readline().decode('utf-8').strip()
                logging.info(f"Received initial response: {first_line}")
            except serial.SerialTimeoutException:
                logging.info("No initial response received.")

            # Device-specific configuration
            # Set quadrature mode, encoder direction, etc., by sending appropriate commands
            self.configure_device()

            # Starting the reading thread
            self.start_reading_thread()
        except Exception as e:
            logging.error(f"Failed to connect and configure the device: {e}")
            self.disconnect()

    def configure_device(self):
        # Send configuration commands to the device, similar to the C# Connect method logic
        # For example:
        self.write_command('03', self.quadrature_mode.value)  # Setting quadrature mode
        self.write_command('04', self.encoder_direction.value) 
        self.write_command('0B', 0x00000000)

        # Set the output interval to 1/512 x 1 Hz (1.953125 ms)
        self.write_command('0C', 0x00000001)

        # Reset the 32-bit timestamp register to minimize the chance of rollover
        self.write_command('0D', 0x00000001)

        # Start streaming the encoder count at the specified interval
        self.stream_command('0E')
        pass

    # def start_reading_thread(self):
    #     # Starting the background thread for continuous reading
    #     self.reading_thread = threading.Thread(target=self._reading_loop, daemon=True)
    #     self.reading_thread.start()
    #     pass

    def write_command(self, register, data):
        if self.serial_port and self.serial_port.isOpen():
            command = f'W{register}{data:08X}\n'  # Adapt command format as needed
            self.serial_port.write(command.encode('utf-8'))
            logging.info(f"Sent command: {command}")

    def stream_command(self, register, data):
        """
        Send a command to the device to start streaming data, such as encoder counts.
        
        Args:
            register (str): The register or command code to write to.
            data (int): The data value to send with the command.
        """
        try:
            # Construct the command string. Adjust formatting as necessary for your device.
            command = f'S{register}{data:08X}\n'
            self.serial_port.write(command.encode('utf-8'))
            logging.info(f"Sent stream command: {command}")

            # Wait for and process the response to confirm successful command execution.
            # This is a simplified example. Adjust parsing as necessary based on your device's protocol.
            response = self.serial_port.readline().decode('utf-8').strip()
            logging.info(f"Received response to stream command: {response}")

            # Validate the response. This example checks for a simple acknowledgment pattern.
            # You'll need to replace this with validation logic appropriate for your device's responses.
            if not response or response[0] != 's':
                raise ValueError("Invalid response to stream command.")

        except serial.SerialException as e:
            logging.error(f"Serial communication error during stream command: {e}")
            # Handle serial communication errors appropriately.
            # This might involve retrying the command, resetting the connection, etc.
        except ValueError as e:
            logging.error(f"Response validation error: {e}")
            # Handle unexpected or invalid responses.
            # This might involve logging the error, retrying, or taking corrective action.


    def start_reading_thread(self):
        self._stop_reading_thread.clear()
        self._reading_thread = threading.Thread(target=self._reading_loop, daemon=True)
        self._reading_thread.start()
        pass

    def _reading_loop(self):
        while not self._stop_reading_thread.is_set():
            if not self.connected:
                break

            try:
                raw_response = self.serial_port.readline().decode('utf-8').strip()
                logging.info(f"Raw response: {raw_response}")

                # Parse the response
                encoder_count, timestamp = self.parse_encoder_count_stream_response(raw_response)
                
                # Update the internal state with the parsed values
                with self._encoder_count_lock:
                    self.encoder_count = encoder_count

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
        
    def parse_encoder_count_stream_response(self, response):
        fields = response.split(' ')
        if len(fields) != 5:
            raise ValueError("The stream response was expected to have 5 fields.")
        if fields[0] != 's' or fields[1] != '0E' or len(fields[2]) != 8 or len(fields[3]) != 8 or fields[4] != '!':
            raise ValueError("Response format validation failed.")
        
        try:
            count = int(fields[2], 16)  # Parsing hexadecimal to integer
            timestamp = int(fields[3], 16)  # Parsing hexadecimal to integer
            return count, timestamp
        except ValueError as e:
            logging.error(f"Failed to parse count or timestamp: {e}")
            raise ValueError("Failed to parse count or timestamp.") from e


def test():
    device_controller = DeviceController(
        port_name='/dev/ttyUSB1',  # Change to your port
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
    test()
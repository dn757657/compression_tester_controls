import serial
import logging
import threading
import serial
import logging
import time
from enum import Enum, unique


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

@unique
class QuadratureMode(Enum):
    X1 = 1
    X2 = 2
    X4 = 4

@unique
class EncoderDirection(Enum):
    CountUp = 0x00
    CountDown = 0x80

class E5UsDigitalEncoder:
    def __init__(self, port_name, baud_rate, quadrature_mode, encoder_direction, **kwargs):
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.quadrature_mode = quadrature_mode
        self.encoder_direction = encoder_direction

        self.serial_port = None
        self.connected = False
        self.encoder_count = 0
        self._stop_reading_thread = threading.Event()
        self._reading_thread = None

        self._connection_lock = threading.Lock()
        self._encoder_count_lock = threading.Lock()
        self._serial_port_lock = threading.Lock()

    def connect(self):
        try:
            if self.serial_port is not None:
                raise Exception("Cannot reconnect using the same DeviceController instance.")
            
            self.serial_port = serial.Serial(self.port_name, self.baud_rate, timeout=1)
            logging.info(f"Connected to {self.port_name}.")

            # Resetting the device (assuming DTR line usage is applicable in your context)
            self.serial_port.dtr = True
            self.serial_port.dtr = False
            self.serial_port.dtr = True
            self.connected = True

            x = True  # clear out the serial - otherwise may fail to configure
            while x:
                try:
                    first_line = self.serial_port.readline().decode('utf-8').strip()
                    if len(first_line) == 0:
                        x = False
                    else:
                        logging.info(f"Received initial response: {first_line}")
                except serial.SerialTimeoutException:
                    logging.info("No initial response received.")
                    x = False
            # Example configuration commands
            self.write_command('15', 0x0000000F)  # Adjust the command as necessary
            self.configure_device()

            self.start_reading_thread()
        except Exception as e:
            logging.error(f"Failed to connect and configure the device: {e}")
            self.disconnect()

    def configure_device(self):
        # self.write_command('03', self.quadrature_mode.value)  # Squadrature mode
        self.write_command('03', 0x43)  # Squadrature mode
        self.write_command('04', 0x100) # direcrtion

        # self.write_command('04', self.encoder_direction.value) # direcrtion
        self.write_command('0B', 0x00000000)  # threshold

        self.write_command('0C', 0x00000001) # set output freq to max
        self.write_command('0D', 0x00000001)  # reset timestampt
        self.write_command('09', 0x00000002)  # reset counter

        self.stream_command('0E')  # start streaming
        pass

    def write_command(self, register, data):
        """
        Sends a command to the device, including a register and data, then reads and validates the response.

        Args:
            register (str): The register code, to be formatted as a two-digit hexadecimal string.
            data (int): The data to send, to be formatted as an eight-digit hexadecimal string.
        """
        with self._serial_port_lock:  # Ensure this uses the correct lock initialized for serial port access
            try:
                # register_str = format(register, '02X')
                # data_str = format(data, '08X')

                command = f'W{register}{data:08X}'
                logging.info(f"Sending command: {command}")
                self.serial_port.write(f"{command}\r\n".encode('utf-8'))

                response = self.serial_port.readline().decode('utf-8').strip()
                logging.info(f"Received response: {response}")

                fields = response.split(' ')
                if len(fields) != 5:
                    raise ValueError("The response was expected to have 5 fields.")
                elif fields[0] != 'w':
                    raise ValueError("The first field in the response was expected to be 'w'.")
                elif fields[1].upper() != register.upper():
                    raise ValueError(f"The second field in the response was expected to be '{register}'.")
                elif int(fields[2], 16) != data:
                    raise ValueError(f"The third field in the response was expected to be '{data}'.")
                elif len(fields[3]) != 8:
                    raise ValueError("The fourth field in the response was expected to be 8 bytes.")
                elif fields[4] != '!':
                    raise ValueError("The fifth field in the response was expected to be '!'.")

            except serial.SerialTimeoutException as e:
                logging.error(f"The device didn't respond to command '{command}': {e}")
                raise TimeoutError("The device didn't respond to the command.") from e
            except ValueError as e:
                logging.error(f"Response validation error: {e}")
                raise

    def stream_command(self, register):
        """
        Send a stream command to the device using the specified register.
        
        Args:
            register (str): The register or command code to write to, formatted as a hexadecimal string.
        """
        with threading.Lock():  # Assuming you've initialized this lock elsewhere as self._serial_port_lock
            try:
                command = f'S{register}\n'
                self.serial_port.write(command.encode('utf-8'))
                logging.info(f"Sent stream command: {command}")

                # Reading the response
                response = self.serial_port.readline().decode('utf-8').strip()
                logging.info(f"Received response: {response}")

                # Validate the response format
                fields = response.split(' ')
                if len(fields) != 5:
                    raise ValueError("The response was expected to have 5 fields.")
                elif fields[0] != 's':
                    raise ValueError("The first field in the response was expected to be 's'.")
                elif fields[1].upper() != register.upper():
                    raise ValueError(f"The second field in the response was expected to be '{register}'.")
                elif len(fields[2]) != 8:
                    raise ValueError(f"The third field in the response was expected to be 8 bytes.")
                elif len(fields[3]) != 8:
                    raise ValueError("The fourth field in the response was expected to be 8 bytes.")
                elif fields[4] != '!':
                    raise ValueError("The fifth field in the response was expected to be '!'.")

            except serial.SerialException as e:
                logging.error(f"Serial communication error during stream command: {e}")
                # Consider re-throwing or handling the exception as needed
            except ValueError as e:
                logging.error(f"Validation error for the response: {e}")
                # Handle validation errors, possibly re-throwing or taking corrective action

    def start_reading_thread(self):
        self._stop_reading_thread.clear()
        self._reading_thread = threading.Thread(target=self._reading_loop, daemon=True)
        self._reading_thread.start()
        pass
    
    def _reading_loop(self):
        logging.info("Started EncoderCountReaderLoop.")

        try:
            while True:
                if not self.connected:
                    logging.info("Terminating EncoderCountReaderLoop.")
                    break
                with self._serial_port_lock:
                    if self.serial_port is None or not self.serial_port.isOpen():
                        logging.info("Terminating EncoderCountReaderLoop.")
                        break

                    response = self.serial_port.readline().decode('utf-8').strip()
                    # logging.info(response)

                encoder_count, timestamp = self.parse_encoder_count_stream_response(response)

                with self._encoder_count_lock:
                    self.encoder_count = encoder_count

        except Exception as e:
            logging.error(f"Terminating EncoderCountReaderLoop because of an exception: {e}")
            self.disconnect()
        pass

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
        # fields = response.split(' ')
        # if len(fields) != 5:
        #     raise ValueError(f"The response was expected to have 5 fields. \n{response}")
        # elif fields[0] != 's':
        #     raise ValueError(f"The first field in the response was expected to be 's'. \n{response}")
        # elif fields[1].upper() != '0E':
        #     raise ValueError(f"The second field in the response was expected to be '0E'. \n{response}")
        # elif len(fields[2]) != 8:
        #     raise ValueError(f"The third field in the response was expected to be 8 bytes. \n{response}")
        # elif len(fields[3]) != 8:
        #     raise ValueError(f"The fourth field in the response was expected to be 8 bytes. \n{response}")
        # elif fields[4] != '!':
        #     raise ValueError(f"The fifth field in the response was expected to be '!'. \n{response}")
        
        # try:
        #     count = int(fields[2], 16)  # Parsing hexadecimal to integer
        #     timestamp = int(fields[3], 16)  # Parsing hexadecimal to integer
        #     return count, timestamp
        # except ValueError as e:
        #     logging.error(f"Failed to parse count or timestamp: {e}")
        #     raise ValueError("Failed to parse count or timestamp.") from e

        fields = response.split(' ')
        count = int(fields[2], 16)
        return count


def test():
    device_controller = E5UsDigitalEncoder(
        port_name='/dev/ttyUSB1',  # Change to your port
        baud_rate=230400,
        quadrature_mode=QuadratureMode.X4,
        encoder_direction=EncoderDirection.CountUp,
    )
    device_controller.connect()

    if device_controller.connected:
        print(f"Encoder count: {device_controller.get_encoder_count()}")
    device_controller.disconnect()
    


def main():
    enc = E5UsDigitalEncoder(name='E5')
    enc_pos = enc.read()
    print(f"E5 Pos: {enc_pos}")


if __name__ == '__main__':
    test()
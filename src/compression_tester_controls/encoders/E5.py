import RPi.GPIO as GPIO
import threading
import time

class RotaryEncoder:
    def __init__(self, pin_a, pin_b, pin_index=None):
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.pin_index = pin_index
        self.position = 0
        self.last_state = None
        self.lock = threading.Lock()

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        if self.pin_index is not None:
            GPIO.setup(self.pin_index, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self._setup_encoder()

    def _setup_encoder(self):
        GPIO.add_event_detect(self.pin_a, GPIO.BOTH, callback=self._update_encoder)
        GPIO.add_event_detect(self.pin_b, GPIO.BOTH, callback=self._update_encoder)
        if self.pin_index is not None:
            GPIO.add_event_detect(self.pin_index, GPIO.RISING, callback=self._reset_position)

    def _update_encoder(self, channel):
        state_a = GPIO.input(self.pin_a)
        state_b = GPIO.input(self.pin_b)

        with self.lock:
            if self.last_state is None:
                self.last_state = (state_a, state_b)
                return

            if (state_a, state_b) != self.last_state:
                if state_a == state_b:
                    self.position += 1
                else:
                    self.position -= 1

            self.last_state = (state_a, state_b)

    def _reset_position(self, channel):
        with self.lock:
            self.position = 0

    def get_position(self):
        with self.lock:
            return self.position

# Example usage
encoder = RotaryEncoder(pin_a=17, pin_b=27, pin_index=22)

try:
    while True:
        print("Position:", encoder.get_position())
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()

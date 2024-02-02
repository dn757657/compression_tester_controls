import board
import busio
import threading
import logging

import numpy as np
import adafruit_ads1x15.ads1115 as ADS

from adafruit_ads1x15.analog_in import AnalogIn

from .base import Observer

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


ADS1115_GAINS = [
    2/3,
    1,
    2,
    4,
    8,
    16
]

ADS1115_UNITS = [
    'volts',
    'bits'
]


class ADCChannel(Observer):
    def __init__(
            self,
            name: str,
            i2c_device,
            i2c_device_channel,
            device_lock: threading.Lock,
            **kwargs 
    ):
        super().__init__(**kwargs)
        self.channel = AnalogIn(i2c_device, i2c_device_channel)
        self.name = name
        self.device_lock = device_lock

        self.start()
        logging.info(f"{self.name} started")

        pass

    def _read(self):
        with self.device_lock:
            return np.array([self.channel.value])


class ADS1115:
    def __init__(
            self,
            name: str,
            gain: float,
            address,
            **kwargs
    ):
        if gain not in ADS1115_GAINS:
            raise ValueError(f'Gain must be one of: {[g for g in ADS1115_GAINS]}')
        try:
            address = int(address, 16)
        except TypeError:
            logging.info(f"Cannot cast {address} as Hex - Aborting ads1115 init.")

        self.name = name
        self.gain = gain
        self.address = address

        i2c = busio.I2C(board.SCL, board.SDA)
        self.device = ADS.ADS1115(
            i2c,
            address=self.address,
            gain=self.gain
        )

        lock = threading.Lock()  # lock all channels together
        self.a0 = ADCChannel(i2c_device=self.device, name='a0', i2c_device_channel=ADS.P0, device_lock=lock)
        self.a1 = ADCChannel(i2c_device=self.device, name='a1', i2c_device_channel=ADS.P1, device_lock=lock)
        self.a2 = ADCChannel(i2c_device=self.device, name='a2', i2c_device_channel=ADS.P2, device_lock=lock)
        self.a3 = ADCChannel(i2c_device=self.device, name='a3', i2c_device_channel=ADS.P3, device_lock=lock)

        self.channels = [
            self.a0,
            self.a1,
            self.a2,
            self.a3
        ]

        # states are always in volts
        self.state = dict()
        self.state_n = dict()
        self.state_SMA = dict()

        logging.info(f"{self.name}: initialized")

        pass

    
    def _update(self, unit: str):
        if unit not in ADS1115_UNITS:
            logging.error(f"{self.name}: incorrect units provided. Must be in {ADS1115_UNITS.__str__()}")
        
        for channel in self.channels:
            if unit == 'volts':
                self.state[channel.name] = self.bits_to_volts(channel.sample())
            elif unit == 'bits':
                self.state[channel.name] = channel.sample()

        pass

    def get_state(self, unit: str = 'volts'):
        self._update(unit=unit)
        return self.state
    

    def _update_n(self, unit: str, n: int):
        if unit not in ADS1115_UNITS:
            logging.error(f"{self.name}: incorrect units provided. Must be in {ADS1115_UNITS.__str__()}")
        
        for channel in self.channels:
            if unit == 'volts':
                self.state_n[channel.name] = self.bits_to_volts(channel.sample_n(n=n))
            elif unit == 'bits':
                self.state_n[channel.name] = channel.sample_n(n=n)

        pass

    def get_state_n(self, n: int, unit: str = 'volts'):
        self._update_n(n=n, unit=unit)
        return self.state_n


    def _update_SMA(self, n: int, unit: str):
        if unit not in ADS1115_UNITS:
            logging.error(f"{self.name}: incorrect units provided. Must be in {ADS1115_UNITS.__str__()}")
        
        for channel in self.channels:
            if unit == 'volts':
                self.state_SMA[channel.name] = self.bits_to_volts(np.average(channel.sample_n(n=n)))
            elif unit == 'bits':
                self.state_SMA[channel.name] = np.average(channel.sample_n(n=n))
        pass

    def get_state_SMA(self, n: int,  unit: str = 'volts'):
        self._update_SMA(n=n, unit=unit)
        return self.state_SMA

    def bits_to_volts(
                self,
                bits_val
        ):
        gains_ranges_mappings = {
            2/3: 6.144,
            1: 4.096,
            2: 2.048,
            4: 1.024,
            8: 0.512,
            16: 0.256,
        }

        max_ads1115_bits_value = 32767
        full_scale_voltage = gains_ranges_mappings.get(self.gain)

        volts_val = (bits_val / max_ads1115_bits_value) * full_scale_voltage

        return volts_val


import board
import busio
import threading
import logging
import time

import adafruit_ads1x15.ads1115 as ADS
import numpy as np

from typing import List

from adafruit_ads1x15.analog_in import AnalogIn


class Observer:
    def __init__(self):
        self.running = False
        self.data = np.array([])
        self.lock = threading.Lock()

    def start(self):
        """Start the continuous process in a new thread."""
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def _run(self):
        """The method that runs continuously in the background."""
        while self.running:
            new_samples = self._read()
            with self.lock:
                self.data = np.append(self.data, new_samples)

    def _read(self):
        new_samples = np.array([])
        return new_samples

    def sample_n(self, n: int):
        """Method to sample the current data."""
        with self.lock:
            idx = max(-n, -len(self.data))
            samples = self.data[idx:]
            return samples

    def sample(self):
        """Method to sample the current data."""
        with self.lock:
            try:
                sample = self.data[-1]
            except IndexError:
                sample = None
            return sample

    def stop_running(self):
        """Stop the continuous process."""
        self.running = False
        self.thread.join()


class ADCChannel(Observer):
    def __init__(
            self,
            name: str,
            i2c_device,
            i2c_device_channel,
            device_lock: threading.Lock
    ):
        super().__init__()
        self.channel = AnalogIn(i2c_device, i2c_device_channel)
        self.name = name
        self.device_lock = device_lock

        pass

    def _read(self):
        with self.device_lock:
            return np.array([self.channel.value])


class ADS1115:
    def __init__(
            self,
            gain: float,
            address: hex,
    ):
        gains = [
            2/3,
            1,
            2,
            4,
            8,
            16
        ]

        if gain not in gains:
            raise ValueError(f'Gain must be one of: {[g for g in gains]}')

        self.gain = gain
        self.address = address

        i2c = busio.I2C(board.SCL, board.SDA)
        self.device = ADS.ADS1115(
            i2c,
            address=self.address,
            gain=self.gain
        )

        self.gain = gain
        self.address = address

        lock = threading.Lock()

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

        pass

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

    # def _read(
    #         self,
    # ):
    #     """
    #     sample channels requested from i2c ADS1115 device
    #     :param req_channels: list of channels as named on board
    #     :return: dict indexed by channel name
    #     """
    #
    #     volt_samples = {}
    #     try:
    #         for channel in self.channels:
    #             chan
    #
    #         self.channel_states = volt_samples  # update state
    #     except OSError:
    #         self.read()  # retry
    #
    #     return volt_samples

# def init_ads1115(
#         gain: float,
#         address: hex,
# ):
#     gains = [
#         2/3,
#         1,
#         2,
#         4,
#         8,
#         16
#     ]
#
#     if gain in gains:
#         logging.info(f'Gain {gain} not in available gains {gains}')
#
#     i2c = busio.I2C(board.SCL, board.SDA)
#     adc = ADS.ADS1115(
#         i2c,
#         address=address,
#         gain=gain
#     )
#
#     return adc




# def bits_to_volts(
#         adc,
#         bits_val
# ):
#     gains_ranges_mappings = {
#         2/3: 6.144,
#         1: 4.096,
#         2: 2.048,
#         4: 1.024,
#         8: 0.512,
#         16: 0.256,
#     }
#
#     max_ads1115_bits_value = 32767
#     full_scale_voltage = gains_ranges_mappings.get(adc.gain)
#
#     volts_val = (bits_val / max_ads1115_bits_value) * full_scale_voltage
#
#     return volts_val
#
#
# def read_ads1115(
#         adc,
#         channels: List[str],
#         volts_samples: {} = None
# ):
#     """
#     :param adc: adc object
#     :param channels:
#     :return:
#     """
#
#     bits_samples = ads1115_read_channels(req_channels=channels, adc=adc)
#
#     volts_samples = {}
#     for k, v in bits_samples.items():
#         volts_samples[k] = ads1115_bits_to_volts(adc=adc, bits_val=v)
#
#     return volts_samples


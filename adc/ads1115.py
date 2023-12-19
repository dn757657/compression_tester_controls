import board
import busio
import logging
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

from typing import List


class ADS1115:
    def __init__(
            self,
            gain: float,
            address: hex,
            channel_labels: List[str]
    ):
        ads1115_gains = [
            2/3,
            1,
            2,
            4,
            8,
            16
        ]

        if gain not in ads1115_gains:
            raise ValueError(f'Gain must be one of: {[g for g in ads1115_gains]}')

        self.gain = gain
        self.address = address
        self.channel_labels = channel_labels

        i2c = busio.I2C(board.SCL, board.SDA)
        self.device = ADS.ADS1115(
            i2c,
            address=self.address,
            gain=self.gain
        )
        self.channels = [
            ADS.P0,
            ADS.P1,
            ADS.P2,
            ADS.P3
        ]
        self.channel_map = dict(zip(self.channel_labels, self.channels))

        self.channel_states = dict()  # last known channel states

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

    def read(
            self,
    ):
        """
        sample channels requested from i2c ADS1115 device
        :param req_channels: list of channels as named on board
        :return: dict indexed by channel name
        """

        volt_samples = {}

        for channel in self.channel_labels:
            if channel not in self.channel_labels:
                logging.info(f'Channel {channel} not in available channels: {self.channel_labels}, Skipping')
            else:
                bit_sample = AnalogIn(self.device, self.channel_map.get(channel)).value
                volt_sample = self.bits_to_volts(bits_val=bit_sample)
                volt_samples[channel] = volt_sample

        self.channel_states = volt_samples  # update state

        return volt_samples

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


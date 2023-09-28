import board
import busio
import logging
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


def ads1115_read_channels(req_channels: list):
    """
    sample channels requested from i2c ADS1115 device
    :param req_channels: list of channels as named on board
    :return: dict indexed by channel name
    """

    i2c = busio.I2C(board.SCL, board.SDA)
    adc = ADS.ADS1115(i2c)

    channels = [
        'A0',
        'A1',
        'A2',
        'A3',
    ]

    samples = {}

    channel_mappings = {
        'A0': ADS.P0,
        'A1': ADS.P1,
        'A2': ADS.P2,
        'A3': ADS.P3,
    }

    for channel in req_channels:
        if channel not in channels:
            logging.info(f'Channel {channel} not in available channels: {channels}, Skipping')
        else:
            samples[channel] = AnalogIn(adc, channel_mappings.get(channel))

    return samples

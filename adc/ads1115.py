import board
import busio
import logging
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


def init_ads1115(
        gain: str,
        address: hex,
):
    gain_mappings = {
        '2/3': ADS.GAIN.TWO_THIRDS,
        '1': ADS.GAIN.ONE,
        '2': ADS.GAIN.TWO,
        '4': ADS.GAIN.FOUR,
        '8': ADS.GAIN.EIGHT,
        '16': ADS.GAIN.SIXTEEN
    }

    i2c = busio.I2C(board.SCL, board.SDA)
    adc = ADS.ADS1115(
        i2c,
        address=address,
        gain=gain_mappings.get(gain)
    )

    return adc


def ads1115_read_channels(
        req_channels: list,
        adc
):
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

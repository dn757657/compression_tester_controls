import logging
import Encoder

from .stepper import StepperMotorDriver
from .ads1115 import ADS1115
from .A201 import A201

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


class HardwareFactory:
    @staticmethod
    def create_component(config: dict):
        component = None

        id_key = 'type'
        if id_key not in config.keys():
            logging.error(f"{config.__str__()} has no {id_key} key! Config Failed.")
            return component
        else:
            type = config.get(id_key)

        if 'stepper'.lower() in type.lower():
            return StepperMotorDriver(**config)
        
        # TODO need to implement with decoder
        # elif 'encoder'.lower() in type.lower():
            # return Encoder.Encoder(**config)
        
        elif 'ads1115'.lower() in type.lower():
            return ADS1115(**config)
        
        elif 'A201'.lower() in type.lower():
            return A201(**config)
        
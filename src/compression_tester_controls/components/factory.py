import logging
import Encoder

from .stepper_controls import StepperMotorDriver
from .ads1115 import ADS1115

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
            config.pop('type', None)
            return StepperMotorDriver(**config)
        
        elif 'encoder'.lower() in type.lower():
            config.pop('type', None)
            config.pop('name', None)
            return Encoder.Encoder(**config)
        
        elif 'ads1115'.lower() in type.lower():
            config.pop('type', None)
            config.update({'address', hex(config.get('address'))})

            return ADS1115(**config)
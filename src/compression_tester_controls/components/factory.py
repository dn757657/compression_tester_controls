import logging
# import Encoder

from simple_pid import PID

from .stepper import StepperMotorDriver
from .ads1115 import ADS1115
from .A201 import A201
from.switch import DiPoleSwitch
from .qsbd import E5UsDigitalEncoder

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
        elif 'encoder'.lower() in type.lower():
            encoder = E5UsDigitalEncoder(**config)
            encoder.connect()
            return encoder
        
        elif 'ads1115'.lower() in type.lower():
            return ADS1115(**config)
        
        elif 'A201'.lower() in type.lower():
            return A201(**config)
        
        elif 'PID'.lower() in type.lower():
            upper_output_limit = config.get('upper_output_limit')
            lower_output_limit = config.get('lower_output_limit')
            output_limits = (lower_output_limit, upper_output_limit)
            
            config.pop('upper_output_limit', None)
            config.pop('lower_output_limit', None)
            config['output_limits'] = output_limits

            config.pop('name', None)
            config.pop('type', None)
            config.pop('init_priority', None)
            return PID(**config)
        
        elif 'switch'.lower() in type.lower():
            if 'dipole'.lower() in type.lower():
                return DiPoleSwitch(**config)
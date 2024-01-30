import json
import logging
import os

from .components.factory import HardwareFactory


REQUIRED_CONFIG_ATTRS = ['name', 'type']


def load_configs(
        base_dir: str = f"./components/configs",
        config_file_ext: str = 'json'
):  
    
    script_path = os.path.dirname(os.path.realpath(__file__))
    print(f"{script_path}")

    component_configs = dict()
    for file in os.listdir(f"{script_path}/{base_dir}"):
        if file.endswith(f".{config_file_ext}"):
            with open(f"{script_path}/{base_dir}/{file}", "r") as f:

                d = json.load(f)
                all_reqd_attrs = True
                for attr in REQUIRED_CONFIG_ATTRS:
                    if attr not in d.keys():
                        logging.error(f"Config {file} missing attribute: {attr}")
                        all_reqd_attrs = False
                        break
                if all_reqd_attrs:
                    component_configs[file.split(".")[0]] = d

    return component_configs


def inst_components(
        component_configs: dict
):
    components = dict()
    for config_name, config in component_configs.items():
        name = config.get('name')
        components[name] = HardwareFactory().create_component(config=config)

    return components

import json
import logging
import os

from collections import OrderedDict

#from .components.factory import HardwareFactory

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
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
    sort_key = "init_priority"
    if all(sort_key in inner_dict for inner_dict in component_configs.values()):
        # Sort the dictionary of dictionaries by the specified key in the inner dictionaries
        sorted_tuples = sorted(component_configs.items(), key=lambda x: x[1][sort_key])
        # Convert the sorted list of tuples back into an OrderedDict to maintain the sorted order
        component_configs = OrderedDict(sorted_tuples)
    else:
        # Not all inner dictionaries contain the key, handle this case as needed
        raise ValueError(f"Not all component configs have the key '{sort_key}'")

    for config_name, config in component_configs.items():
        name = config.get('name')
        for k in config.keys():
            ref_tag = '_ref'
            new_config = None
            if ref_tag.lower() in k.lower():
                obj_ref = config.get(k)
                # print(f"assigning {k} object reference")
                # config.pop(k)  # drop old

                s = obj_ref.split(".")
                if len(s) > 2:
                    logging.info(f"Cannot configure {name}: incorrect object refernce")
                    continue
                ref_obj_name = s[0]
                ref_obj_attr = s[1]
                comp = components.get(ref_obj_name)
                if not comp:
                    logging.info(f"No component named: {ref_obj_name}, referenced in config: {name}")
                    continue
                try:
                    if not new_config:
                        new_config = dict()
                    new_config[k.rsplit('_', 1)[0]] = getattr(comp, ref_obj_attr)
                except ValueError:
                    logging.info(f"Component: {ref_obj_name} does not have attribute: {ref_obj_attr} - referenced in config: {name}")
                    continue
            if new_config:
                config = config | new_config

        # config_objects = [x for x in config.values() if "." in x]
        # for ob in config_objects:
        #     s = ob.split(".")
        #     if len(s) > 2:
        #         logging.info(f"Cannot configure {name}: incorrect object refernce")
        #         continue
        #     else:
        #         ref_obj_name = s[0]
        #         ref_obj_attr = s[1]
        #         comp = components.get(ref_obj_name)
        #         config[ob] = comp.ref_obj_attr

        #components[name] = HardwareFactory().create_component(config=config)

    return components


if __name__ == '__main__':
    configs = load_configs()
    inst_components(component_configs=configs)
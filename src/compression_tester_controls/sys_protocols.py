import time
import logging

from compression_tester_controls.sys_functions import load_configs, inst_components, detect_force_anomoly

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def sys_init():
    configs = load_configs()
    components = inst_components(component_configs=configs)
    return components

COMPONENTS = sys_init()


def trial_init(
        force_sensor_adc_sma_window: int = 100,
        stepper_freq: int = 500,
        stepper_dc: float = 85
):
    force_sensor_adc = COMPONENTS.get('force_sensor_adc')
    big_stepper = COMPONENTS.get('big_stepper')
    big_stepper_pid = COMPONENTS.get('big_stepper_PID')
    force_sensor = COMPONENTS.get('A201')
    enc = COMPONENTS.get('e5')

    while True:
        state_n = force_sensor_adc.get_state_n(n=force_sensor_adc_sma_window, unit='volts')
        states = [x.size for x in state_n.values()]
        x = list()
        for state in states:
            if state >= force_sensor_adc_sma_window:
                x.append(True)
            else:
                x.append(False)

        if False in x:
            logging.info(f"Insufficient samples: {force_sensor_adc.name}. Retrying...")
            time.sleep(0.5)
        else:
            break
    
    logging.info("Aligning Platons...")
    big_stepper.rotate(freq=stepper_freq, duty_cycle=stepper_dc)

    anomoly = False
    while not anomoly:
        anomoly = detect_force_anomoly(
            force_sensor_adc=force_sensor_adc,
            force_sensor=force_sensor
        )
    
    big_stepper.stop()
    logging.info("Platon Found: Pressing to Align...")
    
    # move down a few steps to push platons together
    enc_pos = enc.read()
    new_target = enc_pos + 100
    big_stepper_pid.setpoint = new_target

    error = 1
    while True:
        fnew = big_stepper_pid(enc.read())
        big_stepper.rotate(freq=fnew, duty_cycle=stepper_dc)

        if (new_target - error) < enc.read() <= (new_target + error):
            big_stepper.stop()
            break 

    logging.info("Platons Aligned...")


    big_stepper.rotate(freq=-stepper_freq, duty_cycle=stepper_dc)
    time.sleep(5)
    big_stepper.stop()

    pass
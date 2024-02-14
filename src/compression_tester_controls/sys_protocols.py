import time
import logging
import threading

from compression_tester_controls.sys_functions import load_configs, move_big_stepper_to_setpoint, inst_components, detect_force_anomoly, move_stepper_PID_target
from compression_tester_controls.components.canon_eosr50 import eosr50_init, gphoto2_get_active_ports, eosr50_continuous_capture_and_save

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def sys_init():
    configs = load_configs()
    components = inst_components(component_configs=configs)
    return components

# COMPONENTS = sys_init()


def platon_setup(
        components,
        # stepper_freq: int = 500,
        # stepper_dc: float = 85
):
    # force_sensor_adc = components.get('force_sensor_adc')
    # big_stepper = components.get('big_stepper')
    # big_stepper_pid = components.get('big_stepper_PID')
    # force_sensor = components.get('A201')
    enc = components.get('e5')
    
    logging.info("Manually Mate Platons by jogging...")
    logging.info("Enter q when complete...")

    while True:
        setpoint = input(f"Encoder Position: {enc.read()}, Move to:")
        if setpoint == 'q':
            break
        else:
            move_big_stepper_to_setpoint(setpoint=int(setpoint), components=components)

    platon_zero_count = enc.read()

    logging.info("Manually Align Platon with Top of Sample by jogging...")
    logging.info("Enter q when complete...")

    while True:
        setpoint = input(f"Encoder Position: {enc.read()}, Move to:")
        if setpoint == 'q':
            break
        else:
            move_big_stepper_to_setpoint(setpoint=int(setpoint), components=components)
    
    sample_height_count = enc.read()

    # move down a few steps to push platons together
    # enc_pos = enc.read()
    # additional_steps = 100  # TODO dial this in
    # new_target = enc_pos + additional_steps
    
    # move_stepper_PID_target(
    #     stepper=big_stepper, 
    #     pid=big_stepper_pid, 
    #     enc=enc,
    #     stepper_dc=80, 
    #     setpoint=new_target,
    #     error=2
    #     )
    
    # # big_stepper_pid.setpoint = new_target

    # # error = 2
    # # while True:
    #     # fnew = big_stepper_pid(enc.read())
    #     # big_stepper.rotate(freq=fnew, duty_cycle=stepper_dc)

    #     # if (new_target - error) < enc.read() <= (new_target + error):
    #         # big_stepper.stop()
    #         # break 

    # logging.info(f"Platons Aligned @ {enc.read()}...")
    # logging.info(f"Platons Returning Home...")

    # new_target = enc.read() - 2000
    # move_stepper_PID_target(
    #     stepper=big_stepper, 
    #     pid=big_stepper_pid, 
    #     enc=enc, 
    #     setpoint=new_target,
    #     error=2
    #     )
    
    # # new_target = enc.read() - 2000
    # # big_stepper_pid.setpoint = new_target
    # # while True:
    #     # fnew = big_stepper_pid(enc.read())
    #     # big_stepper.rotate(freq=fnew, duty_cycle=stepper_dc)

    #     # if (new_target - error) < enc.read() <= (new_target + error):
    #         # big_stepper.stop()
    #         # break

    # input("Insert Sample and Press ENTER:")

    # logging.info("Aligning Platon to Sample...")
    # bumps = 3
    # for i in range(0, bumps):
    #     # big_stepper.rotate(freq=-stepper_freq, duty_cycle=stepper_dc)
    #     # time.sleep(3)
    #     # big_stepper.stop()

    #     big_stepper.rotate(freq=stepper_freq, duty_cycle=stepper_dc)

    #     anomoly = False
    #     while not anomoly:
    #         anomoly = detect_force_anomoly(
    #             force_sensor_adc=force_sensor_adc,
    #             force_sensor=force_sensor
    #         )
        
    #     big_stepper.stop()
    #     # TODO could check enc position and see if theyre the same, failsafe against cusum errors
    #     print(f"bumps: {i}, bumps: {bumps - 1}")
    #     if i != bumps - 1:
    #         big_stepper.rotate(freq=-stepper_freq, duty_cycle=stepper_dc)
    #         time.sleep(3)
    #         big_stepper.stop()

    # logging.info("Platons Aligned to Sample")

    return platon_zero_count, sample_height_count


def camera_system_setup(components):
    # pull cam settings and setup cams
    
    cam_stepper = components.get('cam_stepper')
    lsw_adc = components.get('cam_limit_switch_adc')
    lsw1 = components.get('cam_limit_swtich1')
    lsw2 = components.get('cam_limit_swtich2')

    adc_state = lsw_adc.get_state(unit='volts')
    sig_lsw1 = adc_state.get('a0') - adc_state.get('a2')
    sig_lsw2 = adc_state.get('a1') - adc_state.get('a2')

    # print(f"sig1: {sig_lsw1}, sig2: {sig_lsw2}")
    logging.info("Initializing Camera System...")

    states = {
        'lsw1': lsw1.update(sig_lsw1),
        'lsw2': lsw2.update(sig_lsw2)
    }
    # print(f"state1: {states.get('lsw1')}, state2: {states.get('lsw2')}")

    if True in states.values():
        if not cam_stepper.frequency:
            logging.info("Previous Stepper Direction Not Known! Untrigger Switch Manually by Moving Camera System Assembly.")
            input("Press Enter When Collision Resolved...")
    home_camera_system(components=components)

    logging.info("Camera System Initialized.")
    return
        
        
def home_camera_system(
        components,
        stepper_freq: int = 500,
        stepper_dc: float = 50
):
    cam_stepper = components.get('cam_stepper')
    lsw_adc = components.get('cam_limit_switch_adc')
    lsw1 = components.get('cam_limit_swtich1')
    lsw2 = components.get('cam_limit_swtich2')

    logging.info("Homing Camera System...")
    cam_stepper.rotate(freq=stepper_freq * 2, duty_cycle=stepper_dc)
    
    while True:
        adc_state = lsw_adc.get_state(unit='volts')
        sig_lsw1 = adc_state.get('a0') - adc_state.get('a2')
        sig_lsw2 = adc_state.get('a1') - adc_state.get('a2')

        states = {
            'lsw1': lsw1.update(sig_lsw1),
            'lsw2': lsw2.update(sig_lsw2)
        }

        if True in states.values():
            cam_stepper.stop()
            break   

    bumps = 3
    for i in range(0, bumps - 1):
        cam_stepper.reverse_direction()
        cam_stepper.rotate(freq=cam_stepper.frequency, duty_cycle=stepper_dc)  # move off
        while True:
            adc_state = lsw_adc.get_state(unit='volts')
            sig_lsw1 = adc_state.get('a0') - adc_state.get('a2')
            sig_lsw2 = adc_state.get('a1') - adc_state.get('a2')

            states = {
                'lsw1': lsw1.update(sig_lsw1),
                'lsw2': lsw2.update(sig_lsw2)
            }

            if True not in states.values():
                cam_stepper.stop()
                break
        cam_stepper.reverse_direction()
        cam_stepper.rotate(freq=cam_stepper.frequency, duty_cycle=stepper_dc)  # move on
        while True:
            adc_state = lsw_adc.get_state(unit='volts')
            sig_lsw1 = adc_state.get('a0') - adc_state.get('a2')
            sig_lsw2 = adc_state.get('a1') - adc_state.get('a2')

            states = {
                'lsw1': lsw1.update(sig_lsw1),
                'lsw2': lsw2.update(sig_lsw2)
            }

            if True in states.values():
                cam_stepper.stop()
                break

    cam_stepper.reverse_direction()
    cam_stepper.rotate(freq=cam_stepper.frequency, duty_cycle=stepper_dc)  # move off
    while True:
        adc_state = lsw_adc.get_state(unit='volts')
        sig_lsw1 = adc_state.get('a0') - adc_state.get('a2')
        sig_lsw2 = adc_state.get('a1') - adc_state.get('a2')

        states = {
            'lsw1': lsw1.update(sig_lsw1),
            'lsw2': lsw2.update(sig_lsw2)
        }

        if True not in states.values():
            cam_stepper.stop()
            break

    logging.info("Camera Homed.")
    return


def init_cameras(cam_settings):
    cam_ports = gphoto2_get_active_ports()
    for port in cam_ports:
        eosr50_init(port=port, config=cam_settings)
    
    return cam_ports


def move_platon_to_strain():
    # pass in strain
    # pass in initial sample height
    # calc encoder steps for moving motor 1000ppr
    # move motor steps
    pass


def capture_step_frames(cam_ports, components, stepper_freq):
    cam_threads = []
    photos = [list() for x in cam_ports]
    stop_event = threading.Event()

    for i, port in enumerate(cam_ports, start=0):
        cam = threading.Thread(
                target=eosr50_continuous_capture_and_save,
                args=(port, stop_event, photos[i])
            )
        cam_threads.append(cam)

    cam_stepper = components.get('cam_stepper')
    lsw_adc = components.get('cam_limit_switch_adc')
    lsw1 = components.get('cam_limit_swtich1')
    lsw2 = components.get('cam_limit_swtich2')

    # set this frequency in same dir but as needed for frame rates
    cam_stepper.rotate(freq=stepper_freq, duty_cycle=50)
    
    for thread in cam_threads:
        thread.start()

    while True:
        adc_state = lsw_adc.get_state(unit='volts')
        sig_lsw1 = adc_state.get('a0') - adc_state.get('a2')
        sig_lsw2 = adc_state.get('a1') - adc_state.get('a2')

        states = {
            'lsw1': lsw1.update(sig_lsw1),
            'lsw2': lsw2.update(sig_lsw2)
        }

        if True in states.values():
            cam_stepper.stop()
            stop_event.set()
            for thread in cam_threads:
                thread.join()
            break
    
    cam_stepper.reverse_direction()
    cam_stepper.rotate(freq=cam_stepper.frequency, duty_cycle=50)
    while True:
        adc_state = lsw_adc.get_state(unit='volts')
        sig_lsw1 = adc_state.get('a0') - adc_state.get('a2')
        sig_lsw2 = adc_state.get('a1') - adc_state.get('a2')

        states = {
            'lsw1': lsw1.update(sig_lsw1),
            'lsw2': lsw2.update(sig_lsw2)
        }

        if True not in states.values():
            cam_stepper.stop()
            break

    # start = time.time()
    # while True:
        # if (time.time() - start) > 5:
            # stop_event.set()
            # for thread in cam_threads:
                # thread.join()
            # break
    
    all_photos = [item for sublist in photos for item in sublist]
    return all_photos

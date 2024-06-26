import time
import logging
import threading

from compression_tester_controls.sys_functions import load_configs, inst_components, detect_force_anomoly, move_stepper_PID_target
from compression_tester_controls.components.canon_eosr50 import eosr50_init, gphoto2_get_active_ports, eosr50_continuous_capture, eosr50_get_all_files, eosr50_clear_all_files

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
        setpoint = input(f"Encoder Position: {enc.get_encoder_count()}, Move to:")
        if setpoint == 'q':
            break
        else:
            move_stepper_PID_target(
                stepper=components.get('big_stepper'),
                pid=components.get('big_stepper_PID'),
                enc=components.get('e5'),
                stepper_dc=85, 
                setpoint=int(setpoint), 
                error=1
            )

    platon_zero_count = enc.get_encoder_count()

    logging.info("Manually Align Platon with Top of Sample by jogging...")
    logging.info("Enter q when complete...")

    while True:
        setpoint = input(f"Encoder Position: {enc.get_encoder_count()}, Move to:")
        if setpoint == 'q':
            break
        else:
            move_stepper_PID_target(
                stepper=components.get('big_stepper'),
                pid=components.get('big_stepper_PID'),
                enc=components.get('e5'),
                stepper_dc=85, 
                setpoint=int(setpoint), 
                error=1
            )

    sample_height_count = enc.get_encoder_count()
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


def transfer_step_frames(cam_ports):
    for port in cam_ports:
        eosr50_get_all_files(port=port)
    pass


def clear_cam_frames(cam_ports):
    for port in cam_ports:
        eosr50_clear_all_files(port=port)
    pass


def capture_step_frames(cam_ports, components, stepper_freq):
    cam_threads = []
    # photos = [list() for x in cam_ports]
    stop_event = threading.Event()

    for i, port in enumerate(cam_ports, start=0):
        cam = threading.Thread(
                target=eosr50_continuous_capture,
                args=(port, stop_event)
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

    state_count = 0  
    state_count_limit = 200
    # an occasional false positive on a endstop switch in this instance can ruin a trial
    # so we confirm it a few times 
    while True:
        adc_state = lsw_adc.get_state(unit='volts')
        sig_lsw1 = adc_state.get('a0') - adc_state.get('a2')
        sig_lsw2 = adc_state.get('a1') - adc_state.get('a2')

        states = {
            'lsw1': lsw1.update(sig_lsw1),
            'lsw2': lsw2.update(sig_lsw2)
        }

        if True in states.values():
            state_count += 1
            if state_count >= state_count_limit:  # only stop if state is confirmed!
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
    
    # all_photos = [item for sublist in photos for item in sublist]
    pass


def test_frame_speed(runtime):
    cam_ports = gphoto2_get_active_ports()
    # eosr50_init(port=port)
    
    cam_threads = []
    photos = [list() for x in cam_ports]
    stop_event = threading.Event()

    start = time.time()
    for i, port in enumerate(cam_ports, start=0):
        eosr50_init(port=port)
        cam = threading.Thread(
                target=eosr50_continuous_capture,
                args=(port, stop_event, photos[i])
            )
        cam_threads.append(cam)

    for thread in cam_threads:
        thread.start()

    while True:
        t = time.time()
        if t - start > runtime:
            stop_event.set()
            for thread in cam_threads:
                thread.join()
            break
    
    all_photos = [item for sublist in photos for item in sublist]
    print(f"{len(all_photos)} photos taken in {t - start} seconds: {len(all_photos) / (t - start)} [photos/sec]")

    return all_photos

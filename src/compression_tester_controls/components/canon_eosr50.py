import subprocess
import os
import re
import uuid
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def gpohoto2_get_camera_settings(port, config_options):

    settings = {}
    for option in config_options:
        get_command = ['sudo', 'gphoto2', '--port', port, '--get-config', option]
        get_result = subprocess.run(get_command, capture_output=True, text=True)
        settings[option] = get_result.stdout

    return settings


def gphoto2_get_active_ports():
    try:
        active_ports = subprocess.run(['sudo', 'gphoto2', '--auto-detect'], capture_output=True, text=True, check=True)

    except subprocess.CalledProcessError:
        active_ports = []

    active_ports = active_ports.stdout
    # detect command returns a table in string format, find the ports in this table-string
    active_ports = re.findall(r"usb:\d+,\d+", active_ports)

    return active_ports


def eosr50_init(
        port,
        config: None
):

    try:
        if config:
            gcommand = ['sudo', 'gphoto2', '--port', port, '--set-config', 'autopoweroff=0']
            for setting in config:
                gcommand.append('--set-config')
                gcommand.append(setting)

            subprocess.run(gcommand)
        else:
            subprocess.run(['sudo', 'gphoto2', '--port', port, '--set-config', 'autopoweroff=0'])
        logging.info(f"EOS R50 configured @ port: {port}.")
    
    except subprocess.CalledProcessError:
        logging.info(f"Failed to configure EOS R50 @ port: {port}.")

    pass


def eosr50_capture_and_save(
        port,
        file_name: str = uuid.uuid4(),
        file_ext: str = 'jpeg',
):
    """
    can use date characters like %Y in filename see naming standard?
    :param port: get ports from gphoto for attached cameras
    :param filename: must end in .jpg
    :return:
    """

    # sudo gphoto2 --capture-image-and-download -filename "%Y%m%d%H%M%S.jpg"
    filename = f"{file_name}.{file_ext}"
    try:
        subprocess.run([
            'sudo',
            'gphoto2',
            '--port', port,
            '--capture-image-and-download',
            '--filename', filename,
            '--keep'
        ],
            check=True
        )
        print(f"Image {filename} Captured")

    except subprocess.CalledProcessError:
        print("Failed to configure EOS R50.")

    pass


def eosr50_continuous_capture_and_save(
        port,
        stop_event,
        filenames: list = list()
):
    """
    can use date characters like %Y in filename see naming standard?
    :param port: get ports from gphoto for attached cameras
    :param filename: must end in .jpg
    :return:
    """
    i = 0
    while not stop_event.is_set():
        # sudo gphoto2 --capture-image-and-download -filename "%Y%m%d%H%M%S.jpg"
        id = uuid.uuid4()
        filename = f"{id}.%C"  # %C uses extension assigned by cam
        try:
            subprocess.run([
                'sudo',
                'gphoto2',
                '--port', port,
                '--capture-image-and-download',
                '--filename', filename,
            ],
                check=True
            )
            filenames.append(id)
            logging.info(f"Image {filename} Captured")
            i += 1  # only increment if captured

        except subprocess.CalledProcessError:
            logging.info(f"Failed to capture @ {port}.")

    pass
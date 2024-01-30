import subprocess
import os
import re
import uuid


def gpohoto2_get_camera_settings(port):
    # List all configuration options
    list_command = ['sudo', 'gphoto2', '--port', port, '--list-config']
    list_result = subprocess.run(list_command, capture_output=True, text=True)
    config_options = list_result.stdout.splitlines()

    # Retrieve current settings
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
        port
):

    # configure camera to not turn off/ go to sleep mode
    # cannot wake up from pi
    try:
        subprocess.run(['sudo', 'gphoto2', '--port', port, '--set-config', 'autopoweroff=0'])
        print("EOS R50 configured.")

    except subprocess.CalledProcessError:
        print("Failed to configure EOS R50.")

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
        file_name: str = uuid.uuid4(),
        file_ext: str = 'jpeg',
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
        filename = f"{file_name}.{file_ext}"  # will need some sort of uid system eventually
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
            i += 1  # only increment if captured

        except subprocess.CalledProcessError:
            print("Failed to configure EOS R50.")

    pass
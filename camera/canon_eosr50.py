import subprocess
import os


def gphoto2_get_active_ports():
    try:
        active_ports = subprocess.run(['sudo', 'gphoto2', '--auto-detect'], capture_output=True, text=True, check=True)

    except subprocess.CalledProcessError:
        active_ports = []

    active_ports = active_ports.stdout
    print(f"{active_ports}")

    print(f'{type(active_ports)}')

    return active_ports


def eosr50_init(
        port
):

    # configure camera to not turn off/ go to sleep mode
    # cannot wake up from pi
    try:
        subprocess.run(['sudo', 'gphoto2', f'--port {port}', '--set-config', 'autopoweroff=0'])
        print("EOS R50 configured.")

    except subprocess.CalledProcessError:
        print("Failed to configure EOS R50.")

    pass


def eosr50_capture_and_save(
        port,
        filename
):
    """
    can use date characters like %Y in filename see naming standard?
    :param port: get ports from gphoto for attached cameras
    :param filename: must end in .jpg
    :return:
    """

    # sudo gphoto2 --capture-image-and-download -filename "%Y%m%d%H%M%S.jpg"
    try:
        subprocess.run(['sudo', 'gphoto2', f'--port {port}', '--capture-image-and-download', f'-filename {filename}'])
        print("Image Captured")

    except subprocess.CalledProcessError:
        print("Failed to configure EOS R50.")

    pass

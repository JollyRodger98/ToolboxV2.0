from toolbox.hardware import HardwareInfo


def get_default_os_profile():
    os = HardwareInfo.get_os()
    if os == "Darwin":
        return "MacOS"
    elif os == "Windows":
        return "Windows"
    else:
        return "Default"

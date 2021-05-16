from toolbox.hardware import HardwareInfo


def get_default_os_profile():
    os = HardwareInfo.get_os()
    if os == "Darwin":
        return "MacOS"
    elif os == "Windows":
        # TODO create Windows profile on DB
        return "Default"
    else:
        return "Default"

from toolbox.hardware import HardwareInfo


class WidgetAPI(HardwareInfo):
    def __init__(self):
        super().__init__()

    def get_cpu_usage(self):
        cpu_data = self.get_cpu()
        return cpu_data["cpu usage total"]

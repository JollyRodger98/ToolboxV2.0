from toolbox.hardware import HardwareInfo
from jinja2 import Markup


class WidgetDataAPI:
    HWinfo = HardwareInfo()

    def __init__(self):
        pass

    @classmethod
    def get_cpu_usage(cls):
        cpu_data = cls.HWinfo.get_cpu_percentage()
        cpu_data = float(cpu_data.replace("%", ""))
        return cpu_data

    @classmethod
    def get_memory_usage(cls):
        cpu_data = cls.HWinfo.get_memory_percentage()
        cpu_data = float(cpu_data.replace("%", ""))
        return cpu_data

    @classmethod
    def get_cpu_usage_by_core(cls):
        cpu_data = cls.HWinfo.get_cpu_percentage_by_core()

        cores = []
        for index, field in enumerate(cpu_data):
            percentage = int(float(cpu_data[field].replace('%', '')))
            cores.append(f"<span class=\"text-nowrap\">"
                         f"<strong>{field + 1:02d}</strong>:{percentage:02d}%;"
                         f"</span>")
            if (index + 1) % 4 == 0:
                cores.append(" ")

        row_data = Markup("".join(cores))

        return row_data


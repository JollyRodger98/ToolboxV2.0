import re
import psutil
import platform
from pytz import timezone
from dateutil import parser
from datetime import datetime
from collections import OrderedDict


def sort_ordered_dict_by_key(ordered_dict: OrderedDict) -> OrderedDict:
    """Sorts and returns an OrderedDict by key"""
    return OrderedDict(sorted(ordered_dict.items(), key=lambda x: x[0]))


class HardwareInfo:
    """Class to query local hardware

    Collect and return dict with various local hardware specs.

    :param suffix: default data suffix for get_size()
    :type suffix: str
    """
    FACTOR = 1024
    UNITS = ["", "K", "M", "G", "T", "P", "E", "Z", "Y"]
    TZ = {"PST": "UTC-8"}
    DT_FMT = "%H:%M - %d.%m.%Y"
    T_FMT = "%H:%M:%S"
    D_FMT = "%d.%m.%Y"

    def __init__(self, suffix="B"):
        self.suffix = suffix
        self.os = self.get_os()

    def get_size(self, input_bytes: [int]) -> str:
        """Converts bytes to larger and readable units.

        Takes an int or converted str and tries to return a str with a suitable unit. Goes up the list of unit sizes,
        if KB is to small it uses MB and so on.

        :param input_bytes: Bytes to convert to larger units
        :type input_bytes: int
        :raise Exception: if input_bytes is not int or int convertible
        :return: input_bytes in readable unit
        :rtype: str

        :example:
        >> HardwareInfo().get_size(3245343)
        3.10 MB
        """
        try:
            input_bytes = int(input_bytes)
        except ValueError:
            raise Exception(f"invalid value for get_size() with int: '{input_bytes}'")
        for unit in self.UNITS:
            if input_bytes < self.FACTOR:
                return f"{input_bytes:.2f} {unit}{self.suffix}"
            input_bytes /= self.FACTOR

    def get_memory(self) -> OrderedDict:
        """Query local hardware for RAM/Memory specs.

        Returns dict with human readable memory specifications.

        :return: dict with local memory specs
        :rtype: dict
        """
        memory = psutil.virtual_memory()
        return_dict = OrderedDict({
            "total": self.get_size(memory.total),
            "available": self.get_size(memory.available),
            "free": self.get_size(memory.free),
            "used": self.get_size(memory.used),
            "percent": f"{memory.percent}%",
            # "display_settings": ["total", "available", "percent", "used"],
        })
        return return_dict

    def get_partitions(self) -> OrderedDict:
        """Query local hardware for partition specs.

        Returns a list with specifications for each partition on accessible local disks.

        :raise PermissionError: if access is denied when getting disk usage specs
        :return: dict with local partitions specs
        :rtype: dict
        """
        partition_list: list[OrderedDict] = []
        if self.os == "Darwin":
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                except PermissionError:
                    continue
                if partition.mountpoint == "/":
                    name = partition.mountpoint
                else:
                    name = f"/{str(partition.mountpoint).split('/')[-1]}"
                data = OrderedDict({
                    "name": name,
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "total space": self.get_size(disk_usage.total),
                    "free space": self.get_size(disk_usage.free),
                    "used space": self.get_size(disk_usage.total),
                    "used space percent": f"{disk_usage.percent}%",
                })
                partition_list.append(data)
        elif self.os == "Windows":
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                except PermissionError:
                    continue
                data = OrderedDict({
                    "name": partition.device,
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "total space": self.get_size(disk_usage.total),
                    "free space": self.get_size(disk_usage.free),
                    "used space": self.get_size(disk_usage.total),
                    "used space percent": f"{disk_usage.percent}%",
                })
                partition_list.append(data)
        else:
            partition_list = [OrderedDict({"device": "OS not identified"})]

        return_dict = OrderedDict({
            "data_list": partition_list
        })
        return return_dict

    def get_cpu(self) -> dict:
        """Query local cpu for specs.

        Returns a dict with specifications and statistics of the local CPU.

        :return: dict with local cpu specs
        :rtype: dict
        """
        cpu_frequency = psutil.cpu_freq()
        core_usage = {}
        for core, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            core_usage[core] = f"{percentage}%"
        return_dict = OrderedDict({
            "physical cores": psutil.cpu_count(logical=False), "logical cores": psutil.cpu_count(logical=True),
            "min frequency": f"{cpu_frequency.min/1000:.2f} Khz", "max frequency": f"{cpu_frequency.max/1000:.2f} Khz",
            "current frequency": f"{cpu_frequency.current/1000:.2f} Khz", "cpu usage by core": core_usage,
            "cpu usage total": f"{psutil.cpu_percent()}%"
        })
        return return_dict

    def get_system(self) -> OrderedDict:
        """Query local hardware for general system specs.

        Returns a dict with various system specs.

        :return: dict with local general system specs
        :rtype: OrderedDict
        """
        if "Windows" in self.os:
            system = platform.uname()
            name = system.node
            architecture = re.search(r"^.*(32|64).*$", system.machine)
            architecture = f"{architecture.groups()[0]}-Bit"
            last_boot = datetime.fromtimestamp(psutil.boot_time())
            processor = " ".join(system.processor.split(' ')[0:5])
            kernel = f"{system.system} {system.release}"
            kernel_update = "N/A"

        elif "Darwin" in self.os:
            system = platform.uname()
            name = system.node.split(".")[0]
            architecture = f"{system.machine.split('_')[-1]}-Bit"
            last_boot = datetime.fromtimestamp(psutil.boot_time())
            processor = system.processor
            kernel = f"{system.system} {system.release}"
            kernel_update = system.version.split(";").pop(0).split(": ").pop(1)
            kernel_update = parser.parse(kernel_update, tzinfos=self.TZ)
            kernel_update = kernel_update.astimezone(timezone("CET"))

        else:
            name = "OS not identified"
            architecture = "OS not identified"
            last_boot = "OS not identified"
            processor = "OS not identified"
            kernel = "OS not identified"
            kernel_update = "OS not identified"

        return_dict = OrderedDict({
            "name": name,
            "architecture": architecture,
            "last boot": last_boot,
            "processor": processor,
            "kernel": kernel,
            "kernel update": kernel_update,
        })
        return return_dict

    @staticmethod
    def get_os():
        return platform.system()

    @staticmethod
    def get_cpu_percentage() -> str:
        return f"{psutil.cpu_percent(interval=1)}%"

    @staticmethod
    def get_memory_percentage() -> str:
        return f"{psutil.virtual_memory().percent}%"

    @staticmethod
    def get_cpu_percentage_by_core():
        core_usage: dict[int, str] = {}
        for core, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            core_usage[core] = f"{percentage}%"
        return core_usage

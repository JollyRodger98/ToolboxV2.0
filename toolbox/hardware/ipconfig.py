import ipaddress
import random
import re
import subprocess
from collections import OrderedDict
from re import Match
from subprocess import CompletedProcess
from ._re_patterns import mac_os, windows, _re_netconf_name


class Terminal:
    _re_ifconfig_status = re.compile(r"(?m)^\tstatus: (active|inactive)$")
    _re_ifconfig_type = re.compile(r"(?m)^\ttype: ((?:\w*[ -]?)*)$")
    _re_ifconfig_ether = re.compile(r"(?m)^\tether ([a-f0-9]{2}:(?:[a-f0-9]{2}:){4}[a-f0-9]{2}) $")
    _re_ifconfig_addresses = re.compile(r"(?m)^\tinet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
                                        r" netmask ([\w|\d]{10})"
                                        r"(?: broadcast )?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})?"
                                        r".*$")
    _re_ifconfig_up_down = re.compile(r"(?m)^\t((?:down|up)link) rate: "
                                      r"(\d{1,3}\.\d{2} Mbps) \[eff\] / (\d{1,3}\.\d{2} Mbps)(?: \[max\])?$")
    _re_ifconfig_rate = re.compile(r"(?m)^\tlink rate: (\d{1,3}\.\d{2} Mbps)$")
    _re_ifconfig_quality = re.compile(r"(?m)^\t(link quality: )(\d{1,3} \(\w*\))$")

    _re_netconf_name = _re_netconf_name
    _re_ipconfig_name = windows["ipconfig"]["int_name"]
    network_conf_dict_default = OrderedDict({"address": "", "netmask": "", "broadcast": "", "status": "", "type": "",
                                             "mac": "", "rate": "", "uplink rate max": "", "uplink rate eff": "",
                                             "downlink rate max": "", "downlink rate eff": "", "quality": ""})

    def __init__(self, os: str):
        """Parsing output of various CLIs.

        Parsing the output of ipconfig, ifconfig and other commands from MacOS, Linux and Windows

        :param os: local operating system, normally not passed on manually
        """
        self._os = os

    def get_ipconfig(self):
        ipconfig_raw_output = subprocess.check_output(["ipconfig", "-all"])
        ipconfig_raw_output = ipconfig_raw_output.split(b"\r\n\r\n")
        parsed_ipconfig = {}
        interface_name: str = ""
        for index, line in enumerate(ipconfig_raw_output):
            if index % 2 == 0:
                interface_name = line.strip().decode("UTF-8").replace(":", "")
                parsed_ipconfig[interface_name] = []
            elif index % 2 != 0:
                parsed_ipconfig[interface_name] = list(map(lambda x: x.decode("UTF-8").strip(), line.splitlines()))
                parsed_ipconfig[interface_name] = list(map(
                    lambda x: {x.split(':')[0].replace('.', '').strip(): x.split(':')[1].strip()},
                    parsed_ipconfig[interface_name]
                ))
                tmp = {}
                for item in parsed_ipconfig[interface_name]:
                    tmp.update(item)
                parsed_ipconfig[interface_name] = tmp
                del tmp
        tmp = parsed_ipconfig
        for i, v in tmp.items():
            for int_name in parsed_ipconfig:
                for field_name in parsed_ipconfig[int_name]:
                    if not v.get(field_name):
                        tmp[i].update({field_name: ""})

        parsed_ipconfig = OrderedDict(tmp)
        for int_name, int_data in parsed_ipconfig.items():
            parsed_ipconfig[int_name] = OrderedDict(sorted(int_data.items()))

        return parsed_ipconfig

    def ipconfig_ps(self):
        ps_cmd = ["powershell", "-command"]
        netconf_interface_list: OrderedDict = OrderedDict()
        cmd = ps_cmd + ["Get-NetIPConfiguration", "-All", "-Detailed", "-AllCompartments"]
        net_conf_cmd: CompletedProcess = subprocess.run(cmd, capture_output=True)
        net_conf_cmd_out = net_conf_cmd.stdout.decode().split("\r\n\r")
        net_conf_cmd_out = [interface.strip() for interface in net_conf_cmd_out if interface not in ['\n', ""]]
        for interface_data in net_conf_cmd_out:
            interface_name = self._netconf_int_name(interface_data)
            netconf_interface_list.update({interface_name: {}})
            # print(f"{interface_data}\n")
            re_tmp = re.compile(r"^InterfaceAlias\s*:\s((?:\w|[ *-])+\d)\r$", re.MULTILINE)
            re_tmp_result = re.search(re_tmp, interface_data)
            if re_tmp_result:
                # print(re_tmp_result.groups())
                pass
        return netconf_interface_list

    def ipconfig_cmd(self):
        ipconfig_interface_list: OrderedDict = OrderedDict()
        ipconfig_cmd: CompletedProcess = subprocess.run(["ipconfig", "/all"], capture_output=True)
        ipconfig_cmd_out = ipconfig_cmd.stdout.decode().split("\r\n\r\n")
        ipconfig_cmd_out = [[name.strip(), data] for name, data in zip(ipconfig_cmd_out[::2], ipconfig_cmd_out[1::2])]
        # print(*ipconfig_cmd_out, sep=f"\n{'='*50}\n")
        test = {"dict_test": r"(?:Ethernet|Wireless LAN) adapter ((?:\w|[-* ])* \d):"}
        for int_name, int_data in ipconfig_cmd_out:
            interface_name = self._ipconfig_int_name(int_name)
            ipconfig_interface_list.update({interface_name: {}})
            re_int_name: Match = re.search(test["dict_test"], int_name)
            if re_int_name:
                print(re_int_name.group(1))
                pass

            # print(interface_name)
        return ipconfig_interface_list

    def _ipconfig_int_name(self, interface_cli_output: str) -> str:
        re_name: Match = re.search(self._re_ipconfig_name, interface_cli_output)
        int_name: str
        if re_name:
            int_name = re_name.group(1)
        elif interface_cli_output == "Windows IP Configuration":
            int_name = interface_cli_output
        else:
            int_name = f"Unknown Interface {random.randint(1, 999)}"
        return int_name

    def _netconf_int_name(self, interface_cli_output: str) -> str:
        re_name: Match = re.search(self._re_netconf_name, interface_cli_output)
        int_name: str = str()
        if re_name:
            int_name = re_name.group(1)
        else:
            int_name = f"Unknown Interface {random.randint(1, 999)}"
        return int_name

    def network_conf(self) -> OrderedDict:
        """Get Network specification and configuration based on OS.

        :return: Dictionary with information about local network configuration.
        """
        if self._os == "Darwin":
            return self._macos_net_conf()

    def _macos_net_conf(self) -> OrderedDict:
        ifconfig_interface_list = OrderedDict()
        interface_list_cmd: CompletedProcess = subprocess.run(["ifconfig", "-l"], capture_output=True)
        interface_list_cmd_out: list = interface_list_cmd.stdout.decode().split()
        for interface in interface_list_cmd_out:
            ifconfig_interface_list.update({interface: OrderedDict()})
            interface_cmd: CompletedProcess = subprocess.run(["ifconfig", "-v", interface], capture_output=True)
            interface_cmd_out: str = interface_cmd.stdout.decode()
            ifconfig_interface_list[interface].update(self._ifconfig_int_type(interface_cmd_out))
            ifconfig_interface_list[interface].update(self._ifconfig_int_addr(interface_cmd_out))
            ifconfig_interface_list[interface].update(self._ifconfig_int_status(interface_cmd_out))
            ifconfig_interface_list[interface].update(self._ifconfig_int_ether(interface_cmd_out))
            ifconfig_interface_list[interface].update(self._ifconfig_int_up_down(interface_cmd_out))
            ifconfig_interface_list[interface].update(self._ifconfig_int_quality(interface_cmd_out))

        return ifconfig_interface_list

    def _ifconfig_int_quality(self, interface_cli_output: str) -> OrderedDict:
        re_quality: Match = re.search(self._re_ifconfig_quality, interface_cli_output)
        rate_dict: OrderedDict = OrderedDict({"quality": ""})
        if re_quality:
            int_quality = re_quality.group(1)
            rate_dict["quality"] = int_quality
        return rate_dict

    def _ifconfig_int_up_down(self, interface_cli_output: str) -> OrderedDict:
        re_up_down: list = re.findall(self._re_ifconfig_up_down, interface_cli_output)
        rate_dict: OrderedDict = OrderedDict({"rate": "", "uplink rate max": "", "uplink rate eff": "",
                                              "downlink rate max": "", "downlink rate eff": ""})
        if re_up_down:
            rate_dict["uplink rate eff"] = re_up_down[0][1]
            rate_dict["uplink rate max"] = re_up_down[0][2]
            rate_dict["downlink rate eff"] = re_up_down[1][1]
            rate_dict["downlink rate max"] = re_up_down[1][2]
        elif not re_up_down:
            re_rate: Match = re.search(self._re_ifconfig_rate, interface_cli_output)
            if re_rate:
                rate_dict["rate"] = re_rate.group(1)
        return rate_dict

    def _ifconfig_int_ether(self, interface_cli_output: str) -> OrderedDict:
        re_ether: Match = re.search(self._re_ifconfig_ether, interface_cli_output)
        ether_dict: OrderedDict = OrderedDict({"mac": ""})
        if re_ether:
            int_ether = re_ether.group(1)
            ether_dict["mac"] = int_ether
        return ether_dict

    def _ifconfig_int_type(self, interface_cli_output: str) -> OrderedDict:
        re_type: Match = re.search(self._re_ifconfig_type, interface_cli_output)
        type_dict: OrderedDict = OrderedDict({"type": ""})
        if re_type:
            int_type = re_type.group(1)
            type_dict["type"] = int_type
        return type_dict

    def _ifconfig_int_status(self, interface_cli_output: str) -> OrderedDict:
        re_status: Match = re.search(self._re_ifconfig_status, interface_cli_output)
        status_dict: OrderedDict = OrderedDict({"status": ""})
        if re_status:
            int_status = re_status.group(1)
            status_dict["status"] = int_status
        return status_dict

    def _ifconfig_int_addr(self, interface_cli_output: str) -> OrderedDict:
        re_addresses: Match = re.search(self._re_ifconfig_addresses, interface_cli_output)
        keys: list = ["address", "netmask", "broadcast"]
        addresses_dict: OrderedDict = OrderedDict({"address": "", "netmask": "", "broadcast": ""})
        if re_addresses:
            interface_addresses = list(re_addresses.groups())
            hex_netmask = interface_addresses[1][2:]
            if all(char.isalnum() for char in hex_netmask):
                hex_netmask = int(interface_addresses[1][2:], 16)
                interface_addresses[1] = ipaddress.IPv4Address(hex_netmask).compressed
            for index, address in enumerate(interface_addresses):
                addresses_dict.update({keys[index]: address})
        return addresses_dict


t = Terminal("Darwin")
output = t.ipconfig_cmd()
for i in output.items():
    print(i)
    pass

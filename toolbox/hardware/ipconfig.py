import ipaddress
import random
import re
import subprocess
from typing import Dict
from collections import OrderedDict
from re import Match
from subprocess import CompletedProcess
from ._re_patterns import windows, mac_os, _re_netconf_name


class _MacOSParser:
    _re_ifconfig_status = mac_os["int_status"]
    _re_ifconfig_type = mac_os["int_type"]
    _re_ifconfig_ether = mac_os["int_ether"]
    _re_ifconfig_addresses = mac_os["int_addresses"]
    _re_ifconfig_up_down = mac_os["int_up_down"]
    _re_ifconfig_rate = mac_os["int_rate"]
    _re_ifconfig_quality = mac_os["int_quality"]
    _re_ifconfig_gateway = mac_os["int_gateway"]
    _re_ifconfig_media = mac_os["int_media"]
    _re_ifconfig_ipv6 = mac_os["int_ipv6"]

    def ifconfig_int_quality(self, interface_cli_output: str) -> Dict:
        re_quality: Match = re.search(self._re_ifconfig_quality, interface_cli_output)
        quality_dict: Dict = {"quality": ""}
        if re_quality:
            int_quality = re_quality.group(1)
            quality_dict = {"quality": int_quality}
        return quality_dict

    def ifconfig_int_up_down_rate(self, interface_cli_output: str) -> Dict:
        re_up_down: list = re.findall(self._re_ifconfig_up_down, interface_cli_output)
        int_rate: dict = {
            "rate": "", "uplink rate max": "", "uplink rate eff": "",
            "downlink rate max": "", "downlink rate eff": ""
        }

        if re_up_down:
            int_rate["uplink rate eff"] = re_up_down[0][1]
            int_rate["uplink rate max"] = re_up_down[0][2]
            int_rate["downlink rate eff"] = re_up_down[1][1]
            int_rate["downlink rate max"] = re_up_down[1][2]
        elif not re_up_down:
            re_rate: Match = re.search(self._re_ifconfig_rate, interface_cli_output)
            if re_rate:
                int_rate["rate"] = re_rate.group(1)
        return int_rate

    def ifconfig_int_ether(self, interface_cli_output: str) -> Dict:
        re_ether: Match = re.search(self._re_ifconfig_ether, interface_cli_output)
        ether_dict: Dict = {"mac": ""}
        if re_ether:
            int_ether = re_ether.group(1)
            ether_dict["mac"] = int_ether
        return ether_dict

    def ifconfig_int_type(self, interface_cli_output: str) -> Dict:
        re_type: Match = re.search(self._re_ifconfig_type, interface_cli_output)
        type_dict: Dict = {"type": ""}
        if re_type:
            int_type = re_type.group(1)
            type_dict["type"] = int_type
        elif interface_cli_output.startswith("utun"):
            type_dict["type"] = "Virtual P2P Interface (Back to My Mac)"
        elif interface_cli_output.startswith("lo0"):
            type_dict["type"] = "Loopback"
        return type_dict

    def ifconfig_int_status(self, interface_cli_output: str) -> Dict:
        re_status: Match = re.search(self._re_ifconfig_status, interface_cli_output)
        status_dict: Dict = {"status": ""}
        if re_status:
            int_status = re_status.group(1)
            status_dict["status"] = int_status
        return status_dict

    def ifconfig_int_addr(self, interface_cli_output: str) -> OrderedDict:
        re_addresses: Match = re.search(self._re_ifconfig_addresses, interface_cli_output)
        keys: list = ["ipv4", "netmask", "broadcast"]
        addresses_dict: OrderedDict = OrderedDict({"ipv4": "", "netmask": "", "broadcast": ""})
        if re_addresses:
            interface_addresses = list(re_addresses.groups())
            hex_netmask = interface_addresses[1][2:]
            if all(char.isalnum() for char in hex_netmask):
                hex_netmask = int(interface_addresses[1][2:], 16)
                interface_addresses[1] = ipaddress.IPv4Address(hex_netmask).compressed
            for index, address in enumerate(interface_addresses):
                addresses_dict.update({keys[index]: address})
        return addresses_dict

    def ifconfig_int_gateway(self, routing_table_cli_output: str, interface: str) -> Dict:
        re_pat = re.compile(self._re_ifconfig_gateway.format(interface=interface))
        re_gateway: Match = re.search(re_pat, routing_table_cli_output)
        gateway_dict: Dict = {"gateway": ""}
        if re_gateway:
            int_gateway = re_gateway.group(1)
            gateway_dict["gateway"] = int_gateway
        return gateway_dict

    def ifconfig_int_media(self, interface_cli_output: str) -> Dict:
        re_media: Match = re.search(self._re_ifconfig_media, interface_cli_output)
        media_dict: Dict = {"media": "", "speed": "", "duplex": ""}
        if re_media:
            if re_media.group(1) is not None:
                media_dict["media"] = re_media.group(1)
            if re_media.group(2) is not None:
                media_dict["speed"] = re_media.group(2)
            if re_media.group(3) is not None:
                media_dict["duplex"] = re_media.group(3)
        return media_dict

    def ifconfig_int_ipv6(self, interface_cli_output: str) -> Dict:
        re_ipv6: Match = re.search(self._re_ifconfig_ipv6, interface_cli_output)
        ipv6_dict: Dict = {"ipv6": ""}
        if re_ipv6:
            int_ipv6 = re_ipv6.group(1)
            ipv6_dict["ipv6"] = int_ipv6
        return ipv6_dict


class _WindowsParser:
    _re_ipconfig_name = windows["ipconfig"]["int_name"]
    _re_ipconfig_mac = windows["ipconfig"]["int_mac"]
    _re_ipconfig_status = windows["ipconfig"]["int_status"]
    _re_ipconfig_ipv4 = windows["ipconfig"]["int_ipv4"]
    _re_ipconfig_netmask = windows["ipconfig"]["int_netmask"]

    def ipconfig_int_name(self, interface_cli_output: str) -> str:
        re_name: Match = re.search(self._re_ipconfig_name, interface_cli_output)
        int_name: str
        if re_name:
            int_name = re_name.group(1)
        elif interface_cli_output == "Windows IP Configuration":
            int_name = interface_cli_output
        else:
            int_name = f"Unknown Interface {random.randint(1, 999)}"
        return int_name

    def ipconfig_int_mac(self, interface_cli_output: str) -> Dict:
        re_mac: Match = re.search(self._re_ipconfig_mac, interface_cli_output)
        mac_dict: Dict = {"mac": ""}
        if re_mac:
            int_mac = re_mac.group(1)
            mac_dict["mac"] = int_mac
        return mac_dict

    def ipconfig_int_status(self, interface_cli_output: str) -> Dict:
        re_status = re.search(self._re_ipconfig_status, interface_cli_output)
        status_dict = {"status": ""}
        if re_status:
            int_status = re_status.group(1)
            status_dict["status"] = int_status
        else:
            status_dict["status"] = "Media connected"
        return status_dict

    def ipconfig_int_ipv4(self, interface_cli_output: str) -> Dict:
        re_ipv4: Match = re.search(self._re_ipconfig_ipv4, interface_cli_output)
        ipv4_dict: Dict = {"ipv4": ""}
        if re_ipv4:
            int_ipv4 = re_ipv4.group(1)
            ipv4_dict["ipv4"] = int_ipv4
        return ipv4_dict

    def ipconfig_int_netmask(self, interface_cli_output: str) -> Dict:
        re_netmask: Match = re.search(self._re_ipconfig_netmask, interface_cli_output)
        netmask_dict: Dict = {"netmask": ""}
        if re_netmask:
            int_netmask = re_netmask.group(1)
            netmask_dict["netmask"] = int_netmask
        return netmask_dict


class Terminal:
    _network_conf_dict_default = OrderedDict({
        "type": "",
        "status": "",
        "mac": "",
        "ipv4": "",
        "ipv6": "",
        "netmask": "",
        "broadcast": "",
        "gateway": "",
        "media": "",
        "speed": "",
        "duplex": "",
        "rate": "",
        "uplink rate max": "",
        "uplink rate eff": "",
        "downlink rate max": "",
        "downlink rate eff": "",
        "quality": "",
    })
    _win_parse = _WindowsParser()
    _osx_parse = _MacOSParser()

    def __init__(self, os: str):
        """Parsing output of various CLIs.

        Parsing the output of ipconfig, ifconfig and other commands from MacOS, Linux and Windows

        :param os: local operating system, normally not passed on manually
        """
        self._os = os

    # TODO Replace this, legacy function
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

    # TODO Delete
    def ipconfig_ps(self):
        def _netconf_int_name(interface_cli_output: str) -> str:
            re_name: Match = re.search(_re_netconf_name, interface_cli_output)
            int_name: str
            if re_name:
                int_name = re_name.group(1)
            else:
                int_name = f"Unknown Interface {random.randint(1, 999)}"
            return int_name
        ps_cmd = ["powershell", "-command"]
        netconf_interface_list: OrderedDict = OrderedDict()
        cmd = ps_cmd + ["Get-NetIPConfiguration", "-All", "-Detailed", "-AllCompartments"]
        net_conf_cmd: CompletedProcess = subprocess.run(cmd, capture_output=True)
        net_conf_cmd_out = net_conf_cmd.stdout.decode().split("\r\n\r")
        net_conf_cmd_out = [interface.strip() for interface in net_conf_cmd_out if interface not in ['\n', ""]]
        for interface_data in net_conf_cmd_out:
            interface_name = _netconf_int_name(interface_data)
            netconf_interface_list.update({interface_name: {}})
            # print(f"{interface_data}\n")
            re_tmp = re.compile(r"^InterfaceAlias\s*:\s((?:\w|[ *-])+\d)\r$", re.MULTILINE)
            re_tmp_result = re.search(re_tmp, interface_data)
            if re_tmp_result:
                # print(re_tmp_result.groups())
                pass
        return netconf_interface_list

    def network_config(self) -> OrderedDict:
        """Get Network specification and configuration based on OS.

        :return: Dictionary with information about local network configuration.
        """
        if self._os == "Darwin":
            return self._macos_net_conf()
        elif self._os == "Windows":
            return self._windows_net_conf()

    def _windows_net_conf(self) -> OrderedDict:
        ipconfig_interface_list: OrderedDict = OrderedDict()
        ipconfig_cmd: CompletedProcess = subprocess.run(["ipconfig", "/all"], capture_output=True)
        ipconfig_cmd_out = ipconfig_cmd.stdout.decode().split("\r\n\r\n")
        ipconfig_cmd_out = [[name.strip(), data] for name, data in zip(ipconfig_cmd_out[::2], ipconfig_cmd_out[1::2])]
        # print(*ipconfig_cmd_out, sep=f"\n{'='*50}\n")
        for int_name, int_data in ipconfig_cmd_out:
            interface_name = self._win_parse.ipconfig_int_name(int_name)
            ipconfig_interface_list.update({interface_name: self._network_conf_dict_default.copy()})
            ipconfig_interface_list[interface_name].update(self._win_parse.ipconfig_int_mac(int_data))
            ipconfig_interface_list[interface_name].update(self._win_parse.ipconfig_int_status(int_data))
            ipconfig_interface_list[interface_name].update(self._win_parse.ipconfig_int_ipv4(int_data))
            ipconfig_interface_list[interface_name].update(self._win_parse.ipconfig_int_netmask(int_data))
            # print(f"=== {interface_name} ===\n{int_data}\n")
            re_tmp = re.compile(r"(?m)^\s{3}Subnet Mask (?:\. )*: (\d{1,3}(?:\.\d{1,3}){3})\r$")
            re_int_name: Match = re.search(re_tmp, int_data)
            if re_int_name:
                print(f"{interface_name:30}: {re_int_name.groups()}")
                pass

            # print(interface_name)
        return ipconfig_interface_list

    def _macos_net_conf(self) -> OrderedDict:
        ifconfig_interface_list: OrderedDict = OrderedDict()
        routing_table_cmd: CompletedProcess = subprocess.run(["netstat", "-rn"], capture_output=True)
        interface_list_cmd: CompletedProcess = subprocess.run(["ifconfig", "-l"], capture_output=True)
        routing_table_cmd_out: str = routing_table_cmd.stdout.decode()
        interface_list_cmd_out: list = interface_list_cmd.stdout.decode().split()
        for interface in interface_list_cmd_out:
            ifconfig_interface_list.update({interface: self._network_conf_dict_default.copy()})
            interface_cmd: CompletedProcess = subprocess.run(["ifconfig", "-v", interface], capture_output=True)
            interface_cmd_out: str = interface_cmd.stdout.decode()
            ifconfig_interface_list[interface].update(self._osx_parse.ifconfig_int_type(interface_cmd_out))
            ifconfig_interface_list[interface].update(self._osx_parse.ifconfig_int_status(interface_cmd_out))
            ifconfig_interface_list[interface].update(self._osx_parse.ifconfig_int_ether(interface_cmd_out))
            ifconfig_interface_list[interface].update(self._osx_parse.ifconfig_int_quality(interface_cmd_out))
            ifconfig_interface_list[interface].update(self._osx_parse.ifconfig_int_up_down_rate(interface_cmd_out))
            ifconfig_interface_list[interface].update(self._osx_parse.ifconfig_int_addr(interface_cmd_out))
            ifconfig_interface_list[interface].update(
                self._osx_parse.ifconfig_int_gateway(routing_table_cmd_out, interface))
            ifconfig_interface_list[interface].update(self._osx_parse.ifconfig_int_media(interface_cmd_out))
            ifconfig_interface_list[interface].update(self._osx_parse.ifconfig_int_ipv6(interface_cmd_out))
        return ifconfig_interface_list


t = Terminal("Windows")
output = t.network_config()
for o_key, o_value in output.items():
    # print(f"{o_key:30}: {o_value}")
    pass

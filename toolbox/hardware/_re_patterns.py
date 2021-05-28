import re
from typing import Dict

_re_netconf_name = re.compile(r"(?m)^InterfaceAlias\s*:\s((?:\w|[ *-])+\d)\r$")

mac_os: Dict = {
    "int_status": re.compile(r"(?m)^\tstatus: (active|inactive)$"),
    "int_type": re.compile(r"(?m)^\ttype: ((?:\w*[ -]?)*)$"),
    "int_ether": re.compile(r"(?m)^\tether ([a-f0-9]{2}:(?:[a-f0-9]{2}:){4}[a-f0-9]{2}) $"),
    "int_addresses": re.compile(r"(?m)^\tinet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) netmask ([\w|\d]{10})(?: broadcast )?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})?.*$") ,
    "int_up_down": re.compile(r"(?m)^\t((?:down|up)link) rate: (\d{1,3}\.\d{2} Mbps) \[eff\] / (\d{1,3}\.\d{2} Mbps)(?: \[max\])?$"),
    "int_rate": re.compile(r"(?m)^\tlink rate: (\d{1,3}\.\d{2} [GM]bps)$"),
    "int_quality": re.compile(r"(?m)^\tlink quality: (\d{1,3} \(\w*\))$"),
    "int_gateway": "(?m)^(?:\d{{1,3}}\.\d{{1,3}}\.\d{{1,3}}\.\d{{1,3}}(?:/\d\d)?|default)\s*(\d{{1,3}}\.\d{{1,3}}\.\d{{1,3}}\.\d{{1,3}})\s*[UHGSCLWImircg]*\s*({interface})\s*$",
    "int_media": re.compile(r"(?m)^\tmedia: (autoselect)?(?: ?\(?<unknown type>\)?| \(?(?:(\d{2,4})\w*)? ?<(full|half)-duplex>\)?)$"),
    "int_ipv6": re.compile(r"(?m)^\tinet6 ([a-f\d:]*)%[\d\w]* prefixlen \d{1,2} scopeid 0x[a-f\d]* $")
}

windows = {
    "ipconfig": {
        "int_name": re.compile(r"^(?:Ethernet|Wireless LAN) adapter ((?:\w|[-* ])* \d):$")
    }
}
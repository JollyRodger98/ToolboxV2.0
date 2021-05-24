from collections import OrderedDict
import subprocess
from subprocess import CompletedProcess


def _get_ipconfig():
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


def _foobar():
    ps_cmd = ["powershell", "-command"]
    parsed_ipconfig: OrderedDict = OrderedDict()
    net_adapter_cmd: CompletedProcess = subprocess.run(
        ps_cmd + ["Get-NetAdapter", "|", "FT", "-HideTableHeaders", "Name"],
        capture_output=True
    )
    net_adapters: list = net_adapter_cmd.stdout.decode().strip().splitlines()
    net_adapters = list(map(lambda x: x.strip(), net_adapters))
    print(net_adapters)
    THA_list = list()
    for adapter in net_adapters:
        print(subprocess.run(ps_cmd + ["Get-NetIPConfiguration", "-InterfaceAlias", f'"{adapter}"', "-Detailed"], capture_output=True))

    print(THA_list)
    # cmd = ["ping", "8.8.8.8", "-n", "1", "-w", "100", "-l", "1"]
    # ping_cmd: CompletedProcess = subprocess.run(cmd, capture_output=True)
    return parsed_ipconfig


output = _foobar()
for key, value in output.items():
    print(f"==============\n"
          f"  Key: {key}\n"
          f"Value: {value}\n")

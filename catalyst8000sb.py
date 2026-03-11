from netmiko import ConnectHandler
from dotenv import load_dotenv
import os 
import re
import xlwt                                     

load_dotenv()


hostname = os.getenv("C8K_HOSTNAME")
username = os.getenv("C8K_USERNAME")
password = os.getenv("C8K_PASSWORD")
device_info = {
    "device_type" : "cisco_xe",
    "host" : hostname,
    "username" : username,
    "password" : password,
    "port" : 22
    
}

def connect_to_device(device_info):
    device_connect = ConnectHandler(**device_info)
    print("Connected to device")
    return device_connect


def show_version(connect,pattern):
    running_config = connect.send_command("show version")
    version_object = re.search(pattern,running_config)
    version = version_object.group(1)
    print(version)
    

def show_interfaces(connect):
    ip_output = connect.send_command("show ip int bri")
    print(ip_output)

def show_inventory(connect):
    out_inventory = connect.send_command("show inventory")
    print(out_inventory)

def running_config(connect):
    out_running_config = connect.send_command("show running-config")
    print(out_running_config)
    return out_running_config

def parse_config(output):
    version_pattern = r"version\s+([\w\.]+)"
    hostname_pattern = r"hostname\s+(\w+)"
    http_pattern = r"^ip http server"
    https_pattern = r"^ip http secure-server"
    ssh_pattern = r"transport input ssh"
    restconf_pattern = r"^restconf"
    netconf_pattern = r"^netconf-yang"
    model_sn_pattern = r"license udi pid (\S+) sn (\S+)"

    http_enabled = bool(re.search(http_pattern, output, re.MULTILINE))
    https_enabled = bool(re.search(https_pattern, output, re.MULTILINE))
    netconf_enabled = bool(re.search(netconf_pattern, output, re.MULTILINE))
    restconf_enabled = bool(re.search(restconf_pattern, output, re.MULTILINE))
    ssh_enabled = bool(re.search(ssh_pattern, output, re.MULTILINE))
    version_object = re.search(version_pattern,output)
    version = version_object.group(1)
    hostname_object = re.search(hostname_pattern,output)
    hostname = hostname_object.group(1)
    model_sn_object = re.search(model_sn_pattern,output)
    model = model_sn_object.group(1)
    sn = model_sn_object.group(2)

    print(hostname,sn,model,version,ssh_enabled,http_enabled,https_enabled,netconf_enabled,restconf_enabled)
    value_dict = {
        "Hostname" : hostname,
        "S/No" : sn,
        "Model" : model,
        "OS Version" : version,
        "SSH_ENABLED" : ssh_enabled,
        "HTTP_ENABLED" : http_enabled,
        "HTTPS_ENABLED" : https_enabled,
        "NETconf_ENABLED" : netconf_enabled,
        "RESTconf_ENABLED" : restconf_enabled
    }
    return value_dict

def write_excel(device_data):
    
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Device Info")

    for col,header in enumerate(device_data.keys()):
        sheet.write(0,col,header)

    row = sheet.last_used_row + 1 if hasattr(sheet, "last_used_row") else 1

    for col, value in enumerate(device_data.values()):
        sheet.write(row, col, value)
    workbook.save("device_info.xls")

def main_tasks():
    connect = connect_to_device(device_info)
    output_config = running_config(connect)
    device_data = parse_config(output_config)
    write_excel(device_data)

if __name__ == "__main__":
    main_tasks()
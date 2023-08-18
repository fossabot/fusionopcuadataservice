import json
from opcua import Client
import os
import socket
import time
import oisp

OISP_API_ROOT = os.environ.get('OISP_API_ROOT')
USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')
device_id = os.environ.get('OISP_DEVICE_ID')
opc_url = os.environ.get('OPC_URL')
opc_port = os.environ.get('OPC_PORT')
oisp_url = os.environ.get('OISP_URL')
oisp_port = os.environ.get('OISP_PORT')

oisp_client = oisp.Client(api_root=OISP_API_ROOT)
oisp_client.auth(USERNAME, PASSWORD)

time.sleep(25)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client = Client(opc_url + ":" + opc_port)

client.connect()
s.connect((str(oisp_url), int(oisp_port)))
root = client.get_root_node()

# Opening JSON file
f = open("../resources/config.json")
target_configs = json.load(f)
f.close()


def registerComponent(n, t):
    try:
        msgFromClient = '{"n": "' + n + '", "t": "' + t + '"}'
        print(msgFromClient)
        s.send(str.encode(msgFromClient))
        print("Registered component to OISP: " + n + " " + t)
    except Exception as e:
        print(e)
        print("Could not register component to OISP")


def fetchOpcData(n, i):
    try:
        var = client.get_node(n + ";" + i)
        print("Fetched data from OPC UA: " + n + " " + i)
        print(var.get_value())
    except Exception as e:
        print(e)
        print("Could not fetch data from OPC UA")
        return None
    
    return var.get_value()


def sendOispData(n, v):
    try:
        msgFromClient = '{"n": "' + n + '", "v": "' + str(v) + '"}'
        s.send(str.encode(msgFromClient))
        print("Sent data to OISP: " + n + " " + str(v))
        print(msgFromClient)
    except Exception as e:
        print(e)
        print("Could not send data to OISP")


if __name__ == "__main__":
    time.sleep(20)

    accounts = oisp_client.get_accounts()
    account = accounts[0]
    devices = account.get_devices()
    for j in range(len(devices)):
        if str(device_id) == str(devices[j].device_id):
            device = devices[j]
            print(device.components)
            for components in device.components:
                print("Deleting component: " + components['cid'])
                time.sleep(2)
                device.delete_component(components['cid'])
            
    for item in target_configs['fusionopcuadataservice']['specification']:
        oisp_n = "Property/http://www.industry-fusion.org/fields#" + item['parameter']
        oisp_t = "property.v1.0"
        registerComponent(oisp_n, oisp_t)
        time.sleep(10)

    while 1:
        for item in target_configs['fusionopcuadataservice']['specification']:
            time.sleep(0.5)
            opc_n = item['node_id']
            opc_i = item['identifier']
            oisp_n = "Property/http://www.industry-fusion.org/fields#" + item['parameter']
            opc_value = fetchOpcData(n=opc_n, i=opc_i)
            if str(oisp_n) == "Property/http://www.industry-fusion.org/fields#base-objects-v0.1-operation-conditions-runtime-machine-state":
                opc_value = 2
            else:
                opc_value = 1

            sendOispData(n=oisp_n, v=opc_value)
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
opc_username = os.environ.get('OPC_USERNAME')
opc_password = os.environ.get('OPC_PASSWORD')

oisp_client = oisp.Client(api_root=OISP_API_ROOT)
oisp_client.auth(USERNAME, PASSWORD)

time.sleep(30)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client = Client(opc_url + ":" + opc_port)
    print("Connected to OPC UA server")
except:
    print("Could not connect to OPC UA server")
    exit()

async def make_connection():
    global client
    client.set_user(opc_username)
    client.set_password(opc_password)
    await client.connect()

if opc_username != "" and opc_password != "":
    make_connection()
else:
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
        return "0.0"
    
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
            check = str(oisp_n).split("-")
            if "state" in check and opc_value != "0.0":
                opc_value = 2
            elif "state" in check and opc_value == "0.0":
                opc_value = 0
            else:
                opc_value = str(opc_value)

            sendOispData(n=oisp_n, v=opc_value)
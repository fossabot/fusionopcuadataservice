from opcua import Client
import os
import socket
import time

target_configs = os.environ.get('TARGET_CONFIGS').split(",")

opc_url = os.environ.get('OPC_URL')
opc_port = os.environ.get('OPC_PORT')

oisp_url = os.environ.get('OISP_URL')
oisp_port = os.environ.get('OISP_PORT')

time.sleep(20)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client = Client(opc_url + ":" + opc_port)

client.connect()
s.connect((str(oisp_url), int(oisp_port)))
root = client.get_root_node()


def registerComponent(n, t):
    try:
        msgFromClient = '{"n": "' + n + '", "t": "' + t + '"}'
        s.send(str.encode(msgFromClient))
        print("Registered component to OISP: " + n + " " + t)
    except:
        print("Could not register component to OISP")


def fetchOpcData(n, i):
    try:
        var = client.get_node(n + ";" + i)
        print("Fetched data from OPC UA: " + n + " " + i)
    except:
        print("Could not fetch data from OPC UA")
        return None
    
    return var.get_value()


def sendOispData(n, v):
    try:
        msgFromClient = '{"n": "' + n + '", "v": "' + str(v) + '"}'
        s.send(str.encode(msgFromClient))
        print("Sent data to OISP: " + n + " " + str(v))
    except:
        print("Could not send data to OISP")


if __name__ == "__main__":
    for item in target_configs:
        oisp_n = item.split("|")[2]
        oisp_t = item.split("|")[3]
        
        registerComponent(oisp_n, oisp_t)

    while 1:
        time.sleep(5)
        for item in target_configs:
            opc_n = item.split("|")[0]
            opc_i = item.split("|")[1]
            oisp_n = item.split("|")[2]
            opc_value = fetchOpcData(n=opc_n, i=opc_i)
            sendOispData(n=oisp_n, v=opc_value)
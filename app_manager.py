# intended to manage the Trash can Valume system

import paho.mqtt.client as mqtt
import time

import random
from mqtt_init import *

from icecream import ic
from datetime import datetime

def time_format():
    return f'{datetime.now()}  Manager|> '

ic.configureOutput(prefix=time_format)
ic.configureOutput(includeContext=False) # use True for including script file context file

# Define callback functions
def on_log(client, userdata, level, buf):
        ic("log: "+buf)

def on_connect(client, userdata, flags, rc):
    if rc==0:
        ic("connected OK")
    else:
        ic("Bad connection Returned code=",rc)

def on_disconnect(client, userdata, flags, rc=0):
    ic("DisConnected result code "+str(rc))

def on_message(client, userdata, msg):
    topic=msg.topic
    m_decode=str(msg.payload.decode("utf-8","ignore"))
    ic("message from: " + topic, m_decode)
    if float(m_decode.split(': ')[1]) < trash_valume_THR:
        ic("Threshold warning! Empty the trash: " + m_decode.split(': ')[1])
        send_msg(client, topic_alarm, "Threshold warning! Empty the trash: " + m_decode.split(': ')[1]+" space left")


def send_msg(client, topic, message):
    ic("Sending message: " + message)
    client.publish(topic, message)

def client_init(cname: str):
    r=random.randrange(1,10000000)
    ID=str(cname+str(r+21))
    client = mqtt.Client(ID, clean_session=True) # create new client instance
    # define callback function       
    client.on_connect=on_connect  #bind callback function
    client.on_disconnect=on_disconnect
    client.on_log=on_log
    client.on_message=on_message
    if username !="":
        client.username_pw_set(username, password)
    ic("Connecting to broker ",broker_ip)
    client.connect(broker_ip,int(port))     #connect to broker
    return client




def main():
    cname = "Manager-"
    client = client_init(cname)
    # main monitoring loop
    client.loop_start()  # Start loop
    client.subscribe(comm_topic+'5976397/sts')
    try:
        while conn_time==0:
            time.sleep(conn_time+manag_time)
            ic("Time for sleep: "+str(conn_time+manag_time))
            time.sleep(3)
        ic("con_time ending")
    except KeyboardInterrupt:
        client.disconnect() # disconnect from broker
        ic("interrrupted by keyboard")

    client.loop_stop()    #Stop loop
    # end session
    client.disconnect() # disconnect from broker
    ic("End manager run script")

if __name__ == "__main__":
    main()
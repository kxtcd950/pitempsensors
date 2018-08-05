#!/usr/bin/python3
import os
import time
import glob
import re
import paho.mqtt.client as mqtt
from time import sleep
import json

with open('config.json') as config:
    conf = json.load(config)

# add defaults for sensor location and the pattern we use to discover them.
# This simplifies the config for people who've not messed about with udev
# but means the script can work for those which do.
if 'sensordir' in conf:
    sensordir=conf['sensordir']
else:
    sensordir='/sys/bus/w1/devices/'
if 'sensorregex' in conf:
    sensorregex=r''+conf["sensorregex"]
else:
    sensorregex=r'[0-9a-f]{2}-[0-9a-f]{12}'
sensornames=conf['sensornames']
mqttsrv=conf['mqttsrv']
mqttuser=conf['mqttuser']
mqttpass=conf['mqttpass']
mqtttopic=conf['mqtttopic']

if (mqtttopic[-1:] != '/'):
    mqtttopic += '/'

def on_connect(client,userdata,flags,rc):
    print("Connected to mqtt server!\n")
    return

def get_device_list():
    if (os.path.isdir(sensordir) == False):
        return []
    dirs = [[f,sensordir+f+'/w1_slave',-100.0] for f in os.listdir(sensordir) if (re.match(sensorregex, f, re.I) and (os.path.exists(f+"w1_slave") == True))]
    return dirs

def get_temperature_raw(dev_file):
    f = open(dev_file, "r")
    lines = f.readlines()
    f.close()
    return lines

def get_temperature(dev_file):
    lines = get_temperature_raw(dev_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = get_temperature_raw(dev_file)
    temp_output = lines[1].find('t=')
    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_c, temp_f

client = mqtt.Client()
client.on_connect=on_connect
client.username_pw_set(mqttuser, mqttpass)
client.connect(mqttsrv, 8883, 60)
devices = get_device_list()
if (len(devices) == 0):
    print("Didn't find any devices.\n")
    print("Are the directory and regex parameters correct?")
    print("These parameters are currently set to:")
    print(" sensordir: '"+sensordir+"'")
    print(" sensorregex: /"+sensorregex+"/\n")
    print("Also check if the device is connected correctly.");
    exit()

client.loop_start()

while (1):
    for device in devices:
        thistemp = get_temperature(device[1])
        repval = round(thistemp[0] * 2) / 2
        if (repval != device[2]):
            client.publish(mqtttopic+sensornames[device[0]], str(repval))
            device[2] = repval
    sleep(10)


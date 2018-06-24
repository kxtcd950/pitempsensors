# pitempsensors
Read temperature sensors connected to GPIO on Raspberry pi, and inject into the specified mqtt instance.

## Purpose
This script is designed to remove all the hassle of discovering 1 wire temperature sensors connected to the Raspberry pi, making them useful in a home-automation setting by interfacing to an MQTT instance and publishing the sensors' values.

## Configuring
The script is configured by a JSON snippet which is loaded by the main script at startup.
The configuration snippet takes the form:

```
{
    "sensordir": "/sys/bus/w1/devices/",
    "sensorregex": "[0-9a-f]{2}-[0-9a-f]{12}",
    "sensornames":{
            "30-0517600759ff": "test probe",
            "30-232453fd3345": "another probe"
    },
    "mqttsrv":"192.168.30.187",
    "mqttuser":"username",
    "mqttpass":"user-password",
    "mqtttopic":"temp probes"
}
```

* "sensordir" and "sensorregex" are used to find the sensor devices; this is done by looking for all files in the directory associated with "sensordir" and applying the regex "sensorregex" to each filename.  Files which match are deemed to be sensors.
* "sensornames" is a list of key: pair values mapping the computer generated sensor names into nice human readable names.  The key is the device filename and the value is the human readable name.
* "mqttsrv" is the name (or IP address) of the MQTT server to publish the read values onto.
* "mqttuser" and "mqttpass" are the username and password to use to authenticate to the MQTT broker.  You *do* use authentication on your broker, don't you?
* "mqtttopic" is the topic under which the temperature values are written.  The format of the published data is "mqtttopic/human name degreesC".


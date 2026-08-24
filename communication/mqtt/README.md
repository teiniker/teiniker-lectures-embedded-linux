# Message Queuing Telemetry Transport

Message Queuing Telemetry Transport (MQTT) is a lightweight, publish-subscribe 
messaging protocol designed for efficient communication between devices, especially 
in IoT environments. 

It uses a broker to facilitate message distribution, enabling clients to subscribe 
or publish messages to specific "topics." 

MQTT is optimized for low bandwidth, high latency, and unreliable networks, 
making it ideal for remote monitoring, sensor data collection, and device-to-device
communication.


## Setup Mosquitto Server 

```
$ sudo apt update
$ sudo apt install -y mosquitto mosquitto-clients
```

```
$ sudo systemctl status mosquitto
mosquitto.service - Mosquitto MQTT Broker
     Loaded: loaded (/lib/systemd/system/mosquitto.service; enabled; preset: enabled)
     Active: active (running) since Wed 2024-01-03 17:33:14 CET; 18s ago
```

Don't start Mosquitto MQTT Message Broker automatically when the Linux boots
```
$ sudo systemctl disable mosquitto
// $ sudo systemctl enable mosquitto     // default setting 

$ sudo systemctl start mosquitto
$ sudo systemctl stop mosquitto
```
The Mosquitto server will work with TCP port 1883.
Check whether the Mosquitto MQTT server is listening at the default port, 1883:
```
$ netstat -an | grep 1883
```

If we want to interact with the Mosquitto server from a different device or computer, 
we have to make sure that the firewall that is running on your computer has the 
appropriate configuration for this port number.


### Enable Remote Access (No Authentication)

```bash
$ sudo vim /etc/mosquitto/mosquitto.conf

listener 1883
allow_anonymous true
```

Subscribe to a remote MQTT broker
```bash
$ mosquitto_sub  -h 192.168.0.73 -t sensors/distance -d
```

Publish to a remote MQTT broker
```bash
$ mosquitto_pub -h 192.168.0.73 -t sensors/distance -m  "10cm" -d
```



## References

* [Install Mosquitto MQTT Broker on Raspberry Pi](https://randomnerdtutorials.com/how-to-install-mosquitto-broker-on-raspberry-pi/)

# MQTT Security 

Security for IoT applications is an extremely important topic.

The different levels of security come at a price. There is always an 
additional overhead. Hence, we should always keep a balance to avoid 
overheads that can make the entire solution unfeasible and unusable. 

Whenever we add more security, we will require additional bandwidth and 
we will add a processing overhead in the clients and the server. 

We have to take into account that some cryptographic algorithms that 
work without problems in modern smartphones aren't suitable for IoT 
boards with constrained processing power. 

Sometimes, security requirements can force us to use specific hardware, 
such as more powerful IoT boards.

Another important thing that we must take into account is that many 
security levels require maintenance tasks that might be unfeasible in 
certain cases or extremely difficult to achieve in other cases.
For example, if we decide to use a certificate for each device that will 
become a client of the MQTT server, we will have to generate and distribute 
a certificate for each device.

Each MQTT server or broker implementation can provide specific security features.
When we work with Mosquitto, we can implement security at the following levels: 
* **Network**: We can use a VPN (short for virtual private network) to extend 
    a private network across the internet.

* **Transport**: MQTT uses TCP as the transport protocol, and therefore by default 
    communications aren't encrypted. We can use TLS to secure and encrypt communications 
    between MQTT clients and the MQTT server. The use of TLS with MQTT is sometimes 
    referred to as MQTTS.

* **Application**: At this level, we can take advantage of features included in MQTT 
    to provide application-level **authentication and authorization**. 
    
    We can add additional security mechanisms at this level. For example, we can 
    **encrypt the message payload** and/or add **integrity checks** to ensure data 
    integrity. 
    However, the topic will still be unencrypted, and therefore TLS is the only way 
    of making sure everything is encrypted. 

## TLS with Mosquitto

So far, we have been working with a Mosquitto server with its **default configuration**, 
which listens on port 1883 and uses plain TCP as the transport protocol. 
The data sent between each MQTT client and the MQTT server isn't encrypted. 
There are no restrictions on subscribers or publishers.




## References
* Gaston C. Hillar.
	**Hands-On MQTT Programming with Python: Work with the lightweight IoT protocol in Python**.
	Packt Publishing, Kindle-Version, 2018
    * Chapter: Securing an MQTT 3.1.1 Mosquitto Server
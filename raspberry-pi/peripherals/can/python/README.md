# SocketCAN in Python Applications

SocketCAN exposes the CAN interface as a network socket, allowing you to write 
applications in languages like C, Python, or others. 

Install python-can:

```
$ pip install python-can
```

_Example:_ Send and receive CAN messages

```Python
import can

# Create a CAN bus interface
bus = can.interface.Bus(channel='can0', bustype='socketcan')

# Send a CAN message
msg = can.Message(arbitration_id=0x123, data=[0xDE, 0xAD, 0xBE, 0xEF], is_extended_id=False)
bus.send(msg)
print("Message sent on CAN bus")

# Receive CAN messages
for msg in bus:
    print(f"Received: ID={msg.arbitration_id}, Data={msg.data}") 
```


## References

* [CAN Bus With Linux And Python](https://www.faschingbauer.me/trainings/material/soup/linux/hardware/can/group.html)


*Egon Teiniker, 2024-2025, GPL v3.0*

import can

# Create a CAN bus interface
bus = can.interface.Bus(channel='can0', bustype='socketcan')

# Send a CAN message
msg = can.Message(arbitration_id=0x123, data=[0xDE, 0xAD, 0xBE, 0xEF], is_extended_id=False)
bus.send(msg)
print("Message sent on CAN bus")

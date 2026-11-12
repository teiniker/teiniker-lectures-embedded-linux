import can

# Create a CAN bus interface
bus = can.interface.Bus(channel='can0', bustype='socketcan')

# Receive CAN messages
for msg in bus:
    print(f"Received: ID={msg.arbitration_id}, Data={msg.data}") 
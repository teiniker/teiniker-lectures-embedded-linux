import time
from smbus2 import SMBus

I2C_BUS = 1
# Default address with all A0-A2 tied low/open is usually 0x20 (or 0x38 for PCF8574A)
PCF_ADDR = 0x20


def read_inputs(bus, addr):
    """Read the current logic state of P0-P7."""
    return bus.read_byte(addr)

def main():
    with SMBus(I2C_BUS) as bus:
        print(f"Connected to PCF8574 at address {hex(PCF_ADDR)}")
        print("Reading inputs (P7 configured as input, pull-up high)...")

        # Ensure bit 7 is set to 1 before reading
        bus.write_byte(PCF_ADDR, 0xFF)

        while True:
            data = read_inputs(bus, PCF_ADDR)
            print(f"Raw Byte: {bin(data):>010s}", end="\r")
            
            p7_state = (data >> 7) & 1

            # If connected with a button pulling to GND, 0 = pressed
            status = "PRESSED (LOW)" if p7_state == 0 else "RELEASED (HIGH)"
            print(f"P7 Input: {status} | Raw Byte: {bin(data):>010s}", end="\r")
            time.sleep(0.1)

if __name__ == "__main__":
    main()
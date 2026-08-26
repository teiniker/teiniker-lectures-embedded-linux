import time
from smbus2 import SMBus

I2C_BUS = 1
# Default address with all A0-A2 tied low/open is usually 0x20 (or 0x38 for PCF8574A)
PCF_ADDR = 0x20


def set_outputs(bus, addr, byte_val):
    """Write an 8-bit state to all P0-P7 pins."""
    bus.write_byte(addr, byte_val)


def main():
    with SMBus(I2C_BUS) as bus:
        print(f"Connected to PCF8574 at address {hex(PCF_ADDR)}")
        print("Blinking LED on P0...")
        for _ in range(5):
            # Turn ON P0 (bit 0 = 0), keep other pins HIGH (1)
            bus.write_byte(PCF_ADDR, 0xFE)
            time.sleep(0.5)

            # Turn OFF P0 (bit 0 = 1)
            bus.write_byte(PCF_ADDR, 0xFF)
            time.sleep(0.5)


if __name__ == "__main__":
    main()

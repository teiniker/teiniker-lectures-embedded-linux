import time
import spidev

from mcp3008 import MCP3008

SPI_BUS = 0
SPI_DEVICE = 0      # CE0 -> CS/SHDN of the MCP3008


def main():
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEVICE)
    try:
        adc = MCP3008(spi, vref=3.3)
        print(f"Connected to MCP3008 at /dev/spidev{SPI_BUS}.{SPI_DEVICE}")

        while True:
            raw = adc.read_raw(0)
            voltage = raw * adc.vref / MCP3008.RESOLUTION
            print(f"CH0: raw = {raw:4d} | voltage = {voltage:5.3f} V")
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        spi.close()


if __name__ == "__main__":
    main()

import spidev

# Loopback test: connect MOSI (GPIO 10, pin 19) with MISO (GPIO 9, pin 21).
# Every byte sent on MOSI is received again on MISO in the same clock cycle.
SPI_BUS = 0
SPI_DEVICE = 0      # CE0 -> /dev/spidev0.0


def main():
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEVICE)
    try:
        spi.max_speed_hz = 1_000_000
        spi.mode = 0

        tx = [0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF]
        rx = spi.xfer2(tx)      # full-duplex: one byte received per byte sent

        print("TX:", " ".join(f"{b:02X}" for b in tx))
        print("RX:", " ".join(f"{b:02X}" for b in rx))

        if rx == tx:
            print("Loopback OK: SPI is working")
        else:
            print("Loopback FAILED: is MOSI connected to MISO?")
    finally:
        spi.close()


if __name__ == "__main__":
    main()

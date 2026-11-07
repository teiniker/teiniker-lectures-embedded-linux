import time
import spidev

SPI_BUS = 0
SPI_DEVICE = 0      # CE0 -> STCP (latch) of the 74HC595


def main():
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEVICE)
    try:
        spi.max_speed_hz = 1_000_000
        spi.mode = 0    # 74HC595 shifts on the rising edge of SHCP

        print("Running light on Q0..Q7 (Ctrl+C to stop)...")
        while True:
            for bit in range(8):
                # MSB first: bit 7 ends up in Q7, bit 0 in Q0.
                # The outputs change when CE0 goes high after the transfer.
                spi.writebytes([1 << bit])
                time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        spi.writebytes([0x00])  # all LEDs off
        spi.close()


if __name__ == "__main__":
    main()

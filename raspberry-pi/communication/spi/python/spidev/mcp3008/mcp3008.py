class MCP3008:
    """Driver for the MCP3008 8-channel 10-bit ADC (SPI)."""

    MAX_SPEED_HZ = 1_000_000    # datasheet: 1.35 MHz at 2.7 V, 3.6 MHz at 5 V
    SPI_MODE = 0                # modes 0 and 3 are supported
    CHANNELS = 8
    RESOLUTION = 1024           # 10 bit

    def __init__(self, spi, vref=3.3):
        """spi: an opened spidev.SpiDev object, vref: voltage at the VREF pin."""
        self.spi = spi
        self.vref = vref
        self.spi.max_speed_hz = self.MAX_SPEED_HZ
        self.spi.mode = self.SPI_MODE

    def read_raw(self, channel):
        """Return the raw 10-bit value (0..1023) of a single-ended channel."""
        if not 0 <= channel < self.CHANNELS:
            raise ValueError(f"channel must be 0..{self.CHANNELS - 1}, not {channel}")

        # Byte 0: start bit
        # Byte 1: SGL/DIFF = 1 (single-ended), D2 D1 D0 = channel, then 4 don't care bits
        # Byte 2: dummy byte, only needed to clock out the rest of the result
        rx = self.spi.xfer2([0x01, (0x08 | channel) << 4, 0x00])

        # rx[1] bits 1..0 = B9 B8, rx[2] = B7..B0
        return ((rx[1] & 0x03) << 8) | rx[2]

    def read_voltage(self, channel):
        """Return the voltage of a single-ended channel in volts."""
        return self.read_raw(channel) * self.vref / self.RESOLUTION

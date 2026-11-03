import time
from smbus2 import i2c_msg


class DHT20:
    """Driver for the DHT20 temperature and humidity sensor."""

    # The DHT20 has a fixed I2C address
    ADDRESS = 0x38

    CMD_TRIGGER = [0xAC, 0x33, 0x00]    # start a measurement
    STATUS_BUSY = 0x80                  # bit 7: measurement in progress
    STATUS_CALIBRATED = 0x18            # bits 3 and 4 must be set after power-on

    def __init__(self, bus):
        """Use the given (open) I2C bus and initialize the sensor."""
        self.bus = bus
        self._initialize()

    def read_status(self):
        """Read the status byte of the sensor."""
        return self.bus.read_byte(self.ADDRESS)

    def read(self):
        """Trigger a measurement and return (temperature in °C, relative humidity in %)."""
        # Write 0xAC 0x33 0x00 to start the measurement
        self._write(self.CMD_TRIGGER)
        time.sleep(0.08)    # measurement takes 80ms

        # Read 7 bytes: status, 5 data bytes, CRC
        # (the sensor has no registers, so we use a plain I2C read)
        for _ in range(10):
            data = self._read(7)
            if not data[0] & self.STATUS_BUSY:
                break
            time.sleep(0.01)
        else:
            raise RuntimeError("DHT20 measurement timed out")

        if self._crc8(data[:6]) != data[6]:
            raise RuntimeError("DHT20 CRC error")

        # Humidity: 20 bits = data[1], data[2], upper nibble of data[3]
        raw_humidity = (data[1] << 12) | (data[2] << 4) | (data[3] >> 4)
        # Temperature: 20 bits = lower nibble of data[3], data[4], data[5]
        raw_temperature = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]

        humidity = raw_humidity / 2**20 * 100.0
        temperature = raw_temperature / 2**20 * 200.0 - 50.0
        return temperature, humidity

    def _initialize(self):
        """Check the status after power-on and initialize the sensor if necessary."""
        time.sleep(0.1)     # sensor needs 100ms after power-on
        if not self._is_calibrated():
            for reg in (0x1B, 0x1C, 0x1E):
                self._reset_register(reg)
            time.sleep(0.01)
            if not self._is_calibrated():
                raise RuntimeError("DHT20 initialization failed")

    def _is_calibrated(self):
        return (self.read_status() & self.STATUS_CALIBRATED) == self.STATUS_CALIBRATED

    def _reset_register(self, reg):
        """Re-initialize an internal register (procedure from the datasheet sample code)."""
        self._write([reg, 0x00, 0x00])
        time.sleep(0.005)
        values = self._read(3)
        time.sleep(0.010)
        self._write([0xB0 | reg, values[1], values[2]])

    def _write(self, data):
        """Write bytes to the sensor as a raw I2C message."""
        self.bus.i2c_rdwr(i2c_msg.write(self.ADDRESS, data))

    def _read(self, length):
        """Read bytes from the sensor as a raw I2C message."""
        msg = i2c_msg.read(self.ADDRESS, length)
        self.bus.i2c_rdwr(msg)
        return list(msg)

    @staticmethod
    def _crc8(data):
        """CRC-8 used by the DHT20: polynomial x^8 + x^5 + x^4 + 1 (0x31), init 0xFF."""
        crc = 0xFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ 0x31) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

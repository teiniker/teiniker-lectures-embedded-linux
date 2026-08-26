# Python Libraries for I2C Programming


## mbus2 

`smbus2` is a pure-Python 3 implementation of the SMBus/I2C protocol. It is a
drop-in replacement for the older `python-smbus` C extension, offering the
same API plus a few Pythonic extras (context manager support, raw I2C
message transactions). It does not talk to the hardware directly - it drives
the Linux `i2c-dev` character device interface, so any bus exposed as
`/dev/i2c-N` can be used.

### Setup

1. Enable the I2C interface on the Raspberry Pi:

   ```
   sudo raspi-config   # Interface Options -> I2C -> Enable
   ```

   or add `dtparam=i2c_arm=on` to `/boot/config.txt` and reboot.

2. Make sure the `i2c-dev` kernel module is loaded (`/dev/i2c-1` should
   exist):

   ```
   lsmod | grep i2c_dev
   ls /dev/i2c-*
   ```

3. Add the current user to the `i2c` group so `/dev/i2c-1` can be accessed
   without root:

   ```
   sudo usermod -aG i2c $USER
   ```

4. Install the library:

   ```
   pip install smbus2
   ```

### Key Architectural Concepts

* **`SMBus`**: represents an open connection to one I2C bus
  (`/dev/i2c-<bus>`). It can be used directly (`bus = SMBus(1)`) or as a
  context manager (`with SMBus(1) as bus:`), which guarantees the underlying
  file descriptor is closed.

* **SMBus-level calls**: `read_byte`, `write_byte`, `read_byte_data`,
  `write_byte_data`, `read_i2c_block_data`, `write_i2c_block_data`, etc.
  cover the standard SMBus protocol subset (single register reads/writes,
  block transfers) used by most sensors and I/O expanders such as the
  PCF8574.

* **`i2c_msg`**: represents a single raw I2C read or write message
  (address, direction, byte buffer), independent of the SMBus protocol
  restrictions.

* **`i2c_rdwr()`**: combines one or more `i2c_msg` objects into a single
  atomic I2C transaction with a repeated START condition, which is required
  by devices that don't follow the SMBus subset (e.g. some EEPROMs and
  sensors that need a write-then-read without releasing the bus).


### The Propagation Path to the Kernel

1. `smbus2` opens `/dev/i2c-<bus>`, the character device created by the
   kernel's `i2c-dev` module for that bus.

2. Each call (`read_byte_data`, `i2c_rdwr`, ...) is translated into an
   `ioctl()` system call on that file descriptor - `I2C_SLAVE` to set the
   target device address, and `I2C_SMBUS` or `I2C_RDWR` to carry the actual
   transfer.

3. The `i2c-dev` module hands the request to the Linux I2C core, which
   routes it to the `i2c_adapter`/`i2c_algorithm` pair registered for that
   bus number.

4. On the Raspberry Pi this adapter is the platform driver for the
   Broadcom BSC (Broadcom Serial Controller) peripheral, which programs the
   actual I2C hardware registers.

5. The BSC controller drives the physical SDA/SCL lines on the GPIO header,
   completing the transaction with the connected device (e.g. the PCF8574).

So a single Python call such as `bus.write_byte(0x20, 0xFE)` travels:
Python (smbus2) -> ioctl() -> `i2c-dev` -> I2C core -> BSC adapter driver ->
I2C hardware -> physical bus.



## References

* [I2C on the Raspberry Pi - HOW TO use I2C with Python](https://youtu.be/GSmq8ZH01Sg?si=w9WfimX5cy2gEISf)

* [I2C with Arduino and Raspberry Pi - Two Methods](https://youtu.be/me7mhrRbspk?si=7zYiHBGsDAteiaZd)

* [smbus2 0.4.3](https://pypi.org/project/smbus2/)

* [Using the I2C Interface](https://raspberry-projects.com/pi/programming-in-python/i2c-programming-in-python/using-the-i2c-interface-2)

* [Raspberry Pi: Python Libraries for I2C, SPI, UART](https://medium.com/geekculture/raspberry-pi-python-libraries-for-i2c-spi-uart-3df092aeda42)

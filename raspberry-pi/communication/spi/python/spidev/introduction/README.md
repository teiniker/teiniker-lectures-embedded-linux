# spidev

`spidev` is a Python module for the Linux `spidev` interface. It is
implemented as a small C extension, which opens a device `/dev/spidevB.C`
and executes SPI transfers with `ioctl()` system calls. Any SPI bus and chip
select exposed as an `spidev` device can be used.

## Setup

1. Enable the SPI interface on the Raspberry Pi
   (see [Setup SPI](../../../setup/README.md)):

   ```
   $ sudo raspi-config   # Interface Options -> SPI -> Enable
   ```

   or add `dtparam=spi=on` to `/boot/firmware/config.txt` and reboot.

2. Make sure the `spidev` devices exist:

   ```
   $ ls /dev/spidev*
   /dev/spidev0.0  /dev/spidev0.1
   ```

3. Add the current user to the `spi` group so `/dev/spidev0.0` can be
   accessed without root:

   ```
   $ sudo usermod -aG spi $USER
   ```

4. Install the library (it is usually pre-installed on Raspberry Pi OS):

   ```
   $ sudo apt install python3-spidev
   ```

   or, in a virtual environment:

   ```
   $ pip install spidev
   ```

## Key Architectural Concepts

* **`SpiDev`**: represents one SPI **device**, i.e. one chip select of a
  bus. `open(bus, device)` opens `/dev/spidev<bus>.<device>`, `close()`
  releases it. Every SPI target (chip select) gets its own `SpiDev`
  object.

* **Configuration attributes**: are set **after** `open()` and apply to all
  following transfers:

  | Attribute        | Description                                          |
  |------------------|------------------------------------------------------|
  | `max_speed_hz`   | Clock rate in Hz. **Always set it**, the default may be far too high for the device. |
  | `mode`           | SPI mode 0 - 3 (CPOL/CPHA).                          |
  | `bits_per_word`  | Word size, usually 8.                                |
  | `lsbfirst`       | `True` for LSB first (rarely needed).                |
  | `cshigh`         | `True` if the chip select is active high.            |

* **Transfer methods**: since SPI is full-duplex, the basic operation
  sends a list of bytes and returns the list of bytes received at the same
  time:

  | Method                   | Description                                               |
  |--------------------------|-----------------------------------------------------------|
  | `xfer2(data)`            | Sends `data`, returns the received bytes. CS stays active for the whole transfer. **Use this one.** |
  | `xfer(data)`             | Like `xfer2()`, but the chip select may be released between the bytes (depends on the driver). |
  | `xfer3(data)`            | Like `xfer2()`, but splits large buffers into several transfers. |
  | `writebytes(data)`       | Sends `data`, ignores the received bytes.                  |
  | `readbytes(n)`           | Sends `n` zero bytes and returns the `n` received bytes.   |

  `xfer2()` and `writebytes()` are limited to the `spidev` buffer size
  (4096 bytes by default).


### The Propagation Path to the Kernel

1. `spidev.SpiDev.open(0, 0)` opens `/dev/spidev0.0`, the character device
   created by the kernel's `spidev` driver for chip select 0 of SPI bus 0.

2. Setting an attribute (e.g. `spi.mode = 0`) is translated into an
   `ioctl()` such as `SPI_IOC_WR_MODE`. A call such as `xfer2()` fills a
   `struct spi_ioc_transfer` and executes `ioctl(fd, SPI_IOC_MESSAGE(1), ...)`.

3. The `spidev` driver hands the message to the Linux **SPI core**, which
   queues it for the `spi_controller` registered for that bus.

4. On the Raspberry Pi 1 - 4, this controller is the `spi-bcm2835` driver
   for the Broadcom SPI peripheral (on the Raspberry Pi 5, the SPI
   controller in the RP1 chip). The driver activates the chip select and
   programs the hardware registers (clock divider, mode, FIFO).

5. The SPI hardware generates SCLK, shifts the bytes out on MOSI and reads
   MISO at the same time. The received bytes travel back the same path.

So a single Python call such as `spi.xfer2([0x01, 0x80, 0x00])` travels:
Python (spidev) -> ioctl() -> `spidev` driver -> SPI core -> SPI controller
driver -> SPI hardware -> physical bus.


## Examples

* [Loopback test](../loopback/loopback.py) (no device needed, MOSI connected to MISO)

* [74HC595 shift register](../74hc595/README.md) (write only)

* [MCP3008 analog-to-digital converter](../mcp3008/README.md) (write and read)


## References

* [spidev (PyPI)](https://pypi.org/project/spidev/)

* [Linux Kernel Documentation: SPI userspace API (spidev)](https://docs.kernel.org/spi/spidev.html)

* [Raspberry Pi Documentation: Serial Peripheral Interface (SPI)](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#serial-peripheral-interface-spi)

*Egon Teiniker, 2025-2026, GPL v3.0*

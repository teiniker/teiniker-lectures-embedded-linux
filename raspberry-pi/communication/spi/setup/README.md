# Setup SPI on the Raspberry Pi

In Linux, SPI devices can be accessed in two ways:

* **Kernel driver**: Many SPI devices (CAN controllers, displays, ADCs,
  touch controllers, ...) have their own kernel driver, which is enabled with
  a **device tree overlay**. The application then uses the interface of that
  driver (e.g. a network interface `can0` for the MCP2515).

* **spidev**: The generic `spidev` driver makes a chip select available to
  user space as a character device `/dev/spidevB.C`. The application sends
  and receives the raw bytes itself (with `ioctl()`, the SPI tools or the
  Python `spidev` package). This is the way to go for simple devices and
  for learning the protocol.


## Enable SPI

Enable the SPI interface with `raspi-config`:

```bash
$ sudo raspi-config        # Interface Options -> SPI -> Enable
```

or add the following line to **/boot/firmware/config.txt** and reboot:

```bash
$ sudo vim /boot/firmware/config.txt

dtparam=spi=on

$ sudo reboot
```

This enables the controller **SPI0** with two chip selects and creates one
`spidev` device for each of them:

```bash
$ ls -l /dev/spidev*
crw-rw---- 1 root spi 153, 0 Nov  7 10:12 /dev/spidev0.0
crw-rw---- 1 root spi 153, 1 Nov  7 10:12 /dev/spidev0.1
```

| Device            | Bus  | Chip select     |
|-------------------|------|-----------------|
| `/dev/spidev0.0`  | SPI0 | CE0 (GPIO 8, pin 24) |
| `/dev/spidev0.1`  | SPI0 | CE1 (GPIO 7, pin 26) |

The data lines are MOSI (GPIO 10, pin 19), MISO (GPIO 9, pin 21) and
SCLK (GPIO 11, pin 23).


## Check the Configuration

Loaded kernel modules:

```bash
$ lsmod | grep spi
spidev                 ...
spi_bcm2835            ...
```

`spi_bcm2835` is the driver of the SPI controller (Raspberry Pi 1 - 4; the
Raspberry Pi 5 uses a different controller in its RP1 chip), `spidev` is
the generic user space driver.

The function of the GPIO pins can be checked with `pinctrl`:

```bash
$ pinctrl get 7-11
```

GPIO 7 - 11 must show the alternate function of SPI0 (e.g. `SPI0_MOSI`)
and not `input` or `output`.


## Permissions

The `spidev` devices belong to the group `spi`. The default user of
Raspberry Pi OS is already a member; other users have to be added:

```bash
$ groups
$ sudo usermod -aG spi $USER     # log out and in again
```


## Additional Chip Selects and SPI1

The second SPI controller **SPI1** can be enabled with an overlay. The
number in the overlay name is the number of chip selects:

```bash
dtoverlay=spi1-3cs
```

| Signal | GPIO    | Header pin |
|--------|---------|------------|
| MOSI   | GPIO 20 | Pin 38     |
| MISO   | GPIO 19 | Pin 35     |
| SCLK   | GPIO 21 | Pin 40     |
| CE0    | GPIO 18 | Pin 12     |
| CE1    | GPIO 17 | Pin 11     |
| CE2    | GPIO 16 | Pin 36     |

This creates `/dev/spidev1.0`, `/dev/spidev1.1` and `/dev/spidev1.2`.

Other overlays change the chip selects of SPI0, e.g. `dtoverlay=spi0-1cs`
(only CE0, GPIO 7 becomes a free GPIO). All overlays and their parameters
are described in `/boot/firmware/overlays/README`.


## Transfer Size

By default, `spidev` accepts at most **4096 bytes** per transfer. For
larger transfers (e.g. displays), the buffer size can be increased by adding
the following parameter to the (single) line in
**/boot/firmware/cmdline.txt**:

```
spidev.bufsiz=65536
```


## Loopback Test

The easiest way to test the SPI interface without any device is a
**loopback**: connect **MOSI (pin 19)** with **MISO (pin 21)** using a
jumper wire. Everything the controller sends is then received again.

```bash
$ ./spidev_test -D /dev/spidev0.0 -v -p "Hello SPI"
spi mode: 0x0
bits per word: 8
max speed: 500000 Hz (500 KHz)
TX | 48 65 6C 6C 6F 20 53 50 49 ...  |Hello SPI
RX | 48 65 6C 6C 6F 20 53 50 49 ...  |Hello SPI
```

If RX matches TX, SPI is working. Without the jumper wire, RX shows only
`00` (or `FF`). See [SPI Tools](../spi-tools/README.md) for how to build
`spidev_test`, and [loopback.py](../python/spidev/loopback/loopback.py)
for the same test in Python.


## References

* [Raspberry Pi Documentation: Serial Peripheral Interface (SPI)](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#serial-peripheral-interface-spi)

* [Linux Kernel Documentation: SPI userspace API (spidev)](https://docs.kernel.org/spi/spidev.html)


*Egon Teiniker, 2025-2026, GPL v3.0*

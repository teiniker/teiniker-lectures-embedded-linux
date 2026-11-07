# SPI Tools

There are command-line tools for SPI, but compared to `i2c-tools`, they
are simple: SPI has **no addresses** and **no acknowledge**, so there is no
way to **scan** the bus for devices (no equivalent of `i2cdetect`). A
missing device just returns `0x00` or `0xFF`.

The two common tools are:

* **spi-tools** (`spi-config`, `spi-pipe`): configure an `spidev` device and
  send data from stdin to the device (and the received data to stdout).

* **spidev_test**: a test program from the Linux kernel sources, which sends
  a given byte sequence and prints the sent and received bytes.

Both use the `spidev` devices `/dev/spidevB.C`, so SPI has to be enabled
first (see [Setup SPI](../setup/README.md)).


## spi-tools

Install the package:

```bash
$ sudo apt install spi-tools
```

If the package is not available, it can be built from the sources
([github.com/cpb-/spi-tools](https://github.com/cpb-/spi-tools)).


### spi-config

`spi-config` shows or changes the configuration of an `spidev` device.

Syntax:

```bash
$ spi-config -d <device> [options]
```

| Option             | Description                                    |
|--------------------|------------------------------------------------|
| `-d <dev>`         | `spidev` device, e.g. `/dev/spidev0.0`.         |
| `-q`               | Print the current configuration.                |
| `-m <0..3>`        | SPI mode.                                      |
| `-l <0,1>`         | LSB first (1) or MSB first (0).                |
| `-b <bits>`        | Bits per word.                                 |
| `-s <hz>`          | Maximum clock rate in Hz.                      |
| `-w`               | Wait: keep the device open (and the settings active) until terminated. |


#### Show the Current Configuration

```bash
$ spi-config -d /dev/spidev0.0 -q
/dev/spidev0.0: mode=0, lsb=0, bits=8, speed=500000, spiready=0
```


#### Change the Configuration

```bash
$ spi-config -d /dev/spidev0.0 -m 3 -s 1000000
```

Sets SPI mode 3 and a clock rate of 1 MHz. Since the settings may be reset
when the device is closed, it is more reliable to pass the mode and speed
directly to `spi-pipe` (see below).


### spi-pipe

`spi-pipe` reads bytes from **stdin**, sends them to the device, and writes
the **received bytes** to **stdout**. Since SPI is full-duplex, one byte is
received for every byte sent.

Syntax:

```bash
$ spi-pipe -d <device> [options] < input > output
```

| Option           | Description                                                  |
|------------------|--------------------------------------------------------------|
| `-d <dev>`       | `spidev` device.                                             |
| `-m <0..3>`      | SPI mode.                                                    |
| `-s <hz>`        | Maximum clock rate in Hz.                                    |
| `-b <n>`         | Block size: number of bytes per transfer (CS stays low during one block). |
| `-n <n>`         | Number of blocks to transfer (`-1` = infinite).               |

Since the data is binary, `printf` is used to create the input and
`hexdump` (or `xxd`) to display the output.


#### Loopback Test

Connect MOSI (pin 19) with MISO (pin 21):

```bash
$ printf 'Hello' | spi-pipe -d /dev/spidev0.0 -s 1000000 | hexdump -C
00000000  48 65 6c 6c 6f                                    |Hello|
```


#### Read a Channel of the MCP3008 ADC

The MCP3008 expects the bytes `0x01`, `0x80 | channel << 4`, `0x00` in **one
transfer** (block size 3) and returns the 10-bit result in the last two
bytes:

```bash
$ printf '\x01\x80\x00' | spi-pipe -d /dev/spidev0.0 -s 1000000 -b 3 -n 1 | hexdump -C
00000000  00 02 1f                                          |...|
```

Result: `((0x02 & 0x03) << 8) | 0x1F = 0x21F = 543`, i.e.
543 / 1024 · 3.3 V ≈ 1.75 V.


#### Write to a 74HC595 Shift Register

Every byte written to a 74HC595 appears on its outputs Q0 - Q7 when CS goes
high:

```bash
$ printf '\x55' | spi-pipe -d /dev/spidev0.0 -s 1000000
```


## spidev_test

`spidev_test` is part of the Linux kernel sources (`tools/spi/`). It is not
packaged, but it is a single C file that can be compiled directly on the
Raspberry Pi:

```bash
$ wget https://raw.githubusercontent.com/torvalds/linux/master/tools/spi/spidev_test.c
$ gcc -o spidev_test spidev_test.c
```

Syntax:

```bash
$ ./spidev_test -D <device> [options]
```

| Option        | Description                                                        |
|---------------|--------------------------------------------------------------------|
| `-D <dev>`    | `spidev` device (default: `/dev/spidev1.1`, so always specify it). |
| `-s <hz>`     | Maximum clock rate in Hz (default: 500 kHz).                       |
| `-p <data>`   | Data to send; escape sequences such as `\x9F` are allowed.         |
| `-v`          | Verbose: also print the transmitted bytes.                         |
| `-H`, `-O`    | Set CPHA and CPOL (i.e. the SPI mode).                             |
| `-L`          | LSB first.                                                         |
| `-b <bits>`   | Bits per word.                                                     |
| `-S <n>`, `-I <n>` | Transfer size and number of iterations (for speed tests).    |


### Loopback Test

Connect MOSI (pin 19) with MISO (pin 21):

```bash
$ ./spidev_test -D /dev/spidev0.0 -v -p "\x01\x23\x45\x67"
spi mode: 0x0
bits per word: 8
max speed: 500000 Hz (500 kHz)
TX | 01 23 45 67 ...  |.#Eg|
RX | 01 23 45 67 ...  |.#Eg|
```


### Read the MCP3008

```bash
$ ./spidev_test -D /dev/spidev0.0 -s 1000000 -v -p "\x01\x80\x00"
...
TX | 01 80 00 ...
RX | 00 02 1F ...
```


### Set the SPI Mode

```bash
$ ./spidev_test -D /dev/spidev0.0 -H -O -v -p "\x9F\x00\x00\x00"    # mode 3
```

`-H` sets CPHA = 1, `-O` sets CPOL = 1. Without these options, mode 0 is
used.


## References

* [spi-tools: Simple command line tools to help using Linux spidev devices](https://github.com/cpb-/spi-tools)

* [Linux Kernel: tools/spi/spidev_test.c](https://github.com/torvalds/linux/blob/master/tools/spi/spidev_test.c)

* [Linux Kernel Documentation: SPI userspace API (spidev)](https://docs.kernel.org/spi/spidev.html)


*Egon Teiniker, 2025-2026, GPL v3.0*

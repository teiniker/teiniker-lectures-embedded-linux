# Setup UART on the Raspberry Pi

The UART on **GPIO 14 (TXD, pin 8)** and **GPIO 15 (RXD, pin 10)** can be
used in two ways:

* **Serial console**: The kernel messages and a login shell are available
  on the UART (115200 baud, 8N1). This is very useful to access a Raspberry
  Pi without network, keyboard and monitor, e.g. with a USB-serial adapter
  from a PC.

* **Serial port for devices**: The UART is free for an application that
  talks to a device (GPS receiver, GSM module, microcontroller, ...).

Both at the same time is not possible: if the console is active, the
login shell would read the data of the device, and the device would
receive the kernel messages.


## The UARTs of the Raspberry Pi

The Raspberry Pi has two types of UARTs:

| UART          | Device         | Description                                                 |
|---------------|----------------|-------------------------------------------------------------|
| **PL011**     | `/dev/ttyAMA0` | Full-featured ARM UART: parity, break and error detection, independent baud rate clock. |
| **mini UART** | `/dev/ttyS0`   | Reduced UART (Raspberry Pi 1 - 4): no parity, no framing error detection, small FIFO. Its baud rate is derived from the **core clock** of the GPU and changes when the clock changes. |

On models **with Bluetooth** (Raspberry Pi 3, 4, 400, Zero W), the PL011 is
used for the Bluetooth module, and the **mini UART** is connected to
GPIO 14/15. To avoid having to know this, Raspberry Pi OS creates two
symbolic links:

| Link            | Meaning                                    |
|-----------------|--------------------------------------------|
| `/dev/serial0`  | The UART on **GPIO 14/15** (primary UART)  |
| `/dev/serial1`  | The UART used for **Bluetooth**            |

```bash
$ ls -l /dev/serial*
lrwxrwxrwx 1 root root 5 Nov  8 10:12 /dev/serial0 -> ttyS0
lrwxrwxrwx 1 root root 7 Nov  8 10:12 /dev/serial1 -> ttyAMA0
```

> Always use **`/dev/serial0`** in programs and scripts, then they work on
> every model.

On the **Raspberry Pi 5**, all UARTs are PL011 UARTs in the **RP1** chip,
and Bluetooth has its own UART. The UART on GPIO 14/15 is
`/dev/ttyAMA0`. In addition, the Pi 5 has a separate 3-pin **debug UART**
connector (`/dev/ttyAMA10`), which is used for the serial console, and to
which `/dev/serial0` points by default.


## Enable the UART

Use `raspi-config`:

```bash
$ sudo raspi-config        # Interface Options -> Serial Port
```

* "Would you like a login shell to be accessible over serial?" -> **No**
* "Would you like the serial port hardware to be enabled?" -> **Yes**

and reboot. This removes `console=serial0,115200` from
**/boot/firmware/cmdline.txt** and adds the following line to
**/boot/firmware/config.txt**:

```
enable_uart=1
```

On Raspberry Pi 3 and 4, `enable_uart=1` also fixes the core clock, so that
the baud rate of the mini UART is stable.

On the **Raspberry Pi 5**, the UART on GPIO 14/15 is enabled with:

```
dtparam=uart0=on
```

If you want to use the **serial console** instead (e.g. to log in from a
PC), answer the first question with **Yes**.


## Use the PL011 on GPIO 14/15

Because of the limitations of the mini UART, it is better to use the PL011
on GPIO 14/15 (Raspberry Pi 3 and 4). There are two device tree overlays
for this in **/boot/firmware/config.txt**:

```
dtoverlay=disable-bt       # disable Bluetooth, PL011 on GPIO 14/15
```

or

```
dtoverlay=miniuart-bt      # Bluetooth on the mini UART, PL011 on GPIO 14/15
```

After a reboot, `/dev/serial0` points to `ttyAMA0`:

```bash
$ ls -l /dev/serial0
lrwxrwxrwx 1 root root 7 Nov  8 10:20 /dev/serial0 -> ttyAMA0
```

With `disable-bt`, the system service that initializes the Bluetooth modem
should also be disabled:

```bash
$ sudo systemctl disable hciuart
```


## Additional UARTs

The Raspberry Pi 4 has four more PL011 UARTs, which can be enabled with
overlays. Each of them appears as a further `/dev/ttyAMA` device:

| Overlay           | TXD     | RXD     |
|-------------------|---------|---------|
| `dtoverlay=uart2` | GPIO 0  | GPIO 1  |
| `dtoverlay=uart3` | GPIO 4  | GPIO 5  |
| `dtoverlay=uart4` | GPIO 8  | GPIO 9  |
| `dtoverlay=uart5` | GPIO 12 | GPIO 13 |

Note that these pins are shared with other interfaces (e.g. GPIO 0/1 with
the ID EEPROM I2C bus, GPIO 8/9 with SPI0). All overlays and their
parameters are described in `/boot/firmware/overlays/README`.


## Check the Configuration

The function of the GPIO pins can be checked with `pinctrl`:

```bash
$ pinctrl get 14,15
14: a0    pn | hi // GPIO14 = TXD0
15: a0    pu | hi // GPIO15 = RXD0
```

GPIO 14 and 15 must show the alternate function of a UART (`TXD0`/`RXD0`
for the PL011, `TXD1`/`RXD1` for the mini UART) and not `input` or
`output`.

Check that no serial console is running on the port:

```bash
$ cat /proc/cmdline | grep -o 'console=[^ ]*'
console=tty1
```

Only `console=tty1` (the screen) must be listed, not `console=ttyS0` or
`console=ttyAMA0`.


## Permissions

The serial devices belong to the group `dialout`. The default user of
Raspberry Pi OS is already a member; other users have to be added:

```bash
$ ls -l /dev/ttyAMA0
crw-rw---- 1 root dialout 204, 64 Nov  8 10:20 /dev/ttyAMA0
$ groups
$ sudo usermod -aG dialout $USER     # log out and in again
```


## Loopback Test

The easiest way to test the UART without any device is a **loopback**:
connect **TXD (pin 8)** with **RXD (pin 10)** using a jumper wire. Everything
the UART sends is then received again.

```bash
$ stty -F /dev/serial0 115200 raw -echo
$ cat /dev/serial0 &
$ echo "Hello UART" > /dev/serial0
Hello UART
$ kill %1
```

If the text appears, the UART is working. See [UART Tools](../uart-utils/README.md)
for the commands, and [loopback.py](../python/pyserial/loopback/loopback.py)
for the same test in Python.


## Connect a PC with a USB-Serial Adapter

A **USB-serial adapter** (e.g. with an FTDI FT232, CP2102 or CH340 chip)
connects the Raspberry Pi to a PC. Use an adapter with **3.3 V** signal
levels, and connect:

| USB-serial adapter | Raspberry Pi        |
|--------------------|---------------------|
| RXD                | TXD, GPIO 14 (pin 8)  |
| TXD                | RXD, GPIO 15 (pin 10) |
| GND                | GND (pin 6)         |

Do **not** connect the 5 V or 3.3 V pin of the adapter if the Pi has its
own power supply. On the PC, the adapter appears as `/dev/ttyUSB0` (Linux)
or as a `COM` port (Windows).


## References

* [Raspberry Pi Documentation: Configure UARTs](https://www.raspberrypi.com/documentation/computers/configuration.html#configure-uarts)

* [Linux Serial Console](https://docs.kernel.org/admin-guide/serial-console.html)


*Egon Teiniker, 2025-2026, GPL v3.0*

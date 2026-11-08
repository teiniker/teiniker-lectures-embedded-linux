# pyserial

`pyserial` is a Python module for serial ports. It runs on Linux, Windows
and macOS; on Linux, it opens a TTY device such as `/dev/serial0`,
`/dev/ttyAMA0` or `/dev/ttyUSB0` and configures it with the **termios**
interface. Any UART that Linux exposes as a serial device can be used,
including USB-serial adapters.

## Setup

1. Enable the UART and disable the serial console on the Raspberry Pi
   (see [Setup UART](../../../setup/README.md)):

   ```
   $ sudo raspi-config   # Interface Options -> Serial Port
                         # login shell: No, serial port hardware: Yes
   ```

2. Make sure the device exists:

   ```
   $ ls -l /dev/serial0
   lrwxrwxrwx 1 root root 7 Nov  8 10:20 /dev/serial0 -> ttyAMA0
   ```

3. Add the current user to the `dialout` group so the port can be accessed
   without root:

   ```
   $ sudo usermod -aG dialout $USER
   ```

4. Install the library (it is usually pre-installed on Raspberry Pi OS):

   ```
   $ sudo apt install python3-serial
   ```

   or, in a virtual environment:

   ```
   $ pip install pyserial
   ```

   Note: the package is called `pyserial`, but the module is imported as
   `serial`. Do **not** install the unrelated package `serial`.

## Key Architectural Concepts

* **`Serial`**: represents one open serial port. The constructor opens and
  configures the port; it can be used as a context manager
  (`with serial.Serial(...) as ser:`), which guarantees that the port is
  closed.

  ```python
  import serial

  ser = serial.Serial("/dev/serial0", baudrate=115200, timeout=1)
  ```

* **Configuration**: the parameters of the character frame and the flow
  control (default: 9600 baud, 8N1, no flow control):

  | Parameter    | Description                                                   |
  |--------------|---------------------------------------------------------------|
  | `baudrate`   | Baud rate, e.g. 9600 or 115200.                               |
  | `bytesize`   | Data bits: `serial.EIGHTBITS` (default), `SEVENBITS`, ...     |
  | `parity`     | `serial.PARITY_NONE` (default), `PARITY_EVEN`, `PARITY_ODD`.  |
  | `stopbits`   | `serial.STOPBITS_ONE` (default), `STOPBITS_TWO`.              |
  | `rtscts`     | `True` for hardware flow control (RTS/CTS).                   |
  | `xonxoff`    | `True` for software flow control (XON/XOFF).                  |

* **Timeouts**: define how long a read call waits. This is the most
  important setting, because a UART device may send nothing at all:

  | `timeout` | Behavior of `read()`                                          |
  |-----------|---------------------------------------------------------------|
  | `None`    | Blocks until the requested number of bytes has been received (default). |
  | `0`       | Non-blocking: returns immediately with the bytes that are available. |
  | `x > 0`   | Returns after the requested bytes or after `x` seconds, with the bytes received so far. |

  A read with a timeout returns **fewer bytes** (or `b''`) when the time is
  over. This must be checked by the program.

* **Read and write**: data is always of type **`bytes`**, not `str`:

  | Method                    | Description                                           |
  |---------------------------|-------------------------------------------------------|
  | `write(data)`             | Sends `bytes`; returns the number of bytes written.   |
  | `read(n)`                 | Reads up to `n` bytes (see timeout).                  |
  | `readline()`              | Reads up to and including `b'\n'` (or until timeout). |
  | `in_waiting`              | Number of bytes in the receive buffer.                |
  | `flush()`                 | Waits until all data has been sent.                   |
  | `reset_input_buffer()`    | Discards all received, not yet read data.             |

  Text must be converted explicitly: `ser.write("Hello\n".encode())` and
  `ser.readline().decode()`.


### The Propagation Path to the Kernel

1. `serial.Serial("/dev/serial0", ...)` executes `open()` on the device
   with `O_RDWR | O_NOCTTY | O_NONBLOCK`. `/dev/serial0` is a symbolic link
   to the character device of the UART driver (e.g. `/dev/ttyAMA0`).

2. The configuration is set with `tcsetattr()`: pyserial switches the port
   to **raw mode** and sets the baud rate, frame format and flow control in
   a `struct termios`. Internally this is an `ioctl()` on the file
   descriptor (`TCSETS`).

3. `write()` and `read()` are translated into `write()` and `read()` system
   calls. pyserial implements the timeouts with `select()`.

4. In the kernel, the **TTY layer** passes the data through the line
   discipline (in raw mode without any processing) to the **serial core**,
   which calls the UART driver: `amba-pl011` for the PL011, `8250` for the
   mini UART (ttyS0).

5. The driver writes the bytes into the **transmit FIFO** of the UART
   hardware, which sends them as character frames on TXD. Received frames
   are collected in the receive FIFO; an interrupt moves them into the
   kernel's buffer, where `read()` picks them up.

So a single Python call such as `ser.write(b"Hello")` travels:
Python (pyserial) -> write() -> TTY layer -> serial core -> UART driver ->
UART hardware -> TXD line.


## Testing without Hardware

`socat` can create a pair of connected **virtual serial ports**
(pseudo-terminals). Everything written to one of them can be read from the
other, so programs can be tested on any Linux PC:

```bash
$ socat -d -d pty,raw,echo=0,link=/tmp/ttyV0 pty,raw,echo=0,link=/tmp/ttyV1
... N PTY is /dev/pts/4
... N PTY is /dev/pts/5
```

The examples accept the port as a command-line argument, e.g.
`python3 main.py /tmp/ttyV1`.


## Examples

* [Loopback test](../loopback/loopback.py) (no device needed, TXD connected to RXD)

* [GPS receiver](../gps/README.md) (read NMEA sentences)


## References

* [pyserial documentation](https://pyserial.readthedocs.io/)

* [pyserial (PyPI)](https://pypi.org/project/pyserial/)

* [Raspberry Pi Documentation: Configure UARTs](https://www.raspberrypi.com/documentation/computers/configuration.html#configure-uarts)

*Egon Teiniker, 2025-2026, GPL v3.0*

# UART Tools

Since a serial port is a normal **file** in Linux, no special tools are
needed to send and receive data: `echo`, `cat` and `hexdump` work directly
on the device. The port is configured with `stty`. For interactive work,
a **terminal program** such as `picocom`, `minicom` or `screen` is more
convenient.

Like SPI, a UART connection has **no addresses** and **no acknowledge**,
so there is no way to scan for devices. Since there is no clock line, both
sides must use the **same baud rate and frame format**; otherwise, only
garbage or nothing is received.

All tools use the serial devices (`/dev/serial0`, `/dev/ttyAMA0`,
`/dev/ttyUSB0`, ...), so the UART has to be enabled first, and the serial
console must be disabled (see [Setup UART](../setup/README.md)).


## stty

`stty` (set tty) shows and changes the termios settings of a terminal
device. With `-F`, it works on a given device instead of the current
terminal.

### Show the Current Settings

```bash
$ stty -F /dev/serial0
speed 9600 baud; line = 0;
...
```

`stty -F /dev/serial0 -a` shows all settings.

### Configure the Port

```bash
$ stty -F /dev/serial0 115200 cs8 -parenb -cstopb raw -echo
```

| Setting          | Description                                                  |
|------------------|--------------------------------------------------------------|
| `115200`         | Baud rate                                                    |
| `cs8`            | 8 data bits (`cs5` - `cs8`)                                  |
| `-parenb`        | No parity (`parenb` enables it, `parodd` selects odd parity) |
| `-cstopb`        | 1 stop bit (`cstopb`: 2 stop bits)                           |
| `raw`            | Raw mode: no line editing, no conversion of `\r`/`\n`, no signals (`Ctrl-C`) |
| `-echo`          | Don't send received characters back                         |
| `crtscts`        | Enable hardware flow control (RTS/CTS)                       |
| `ixon ixoff`     | Enable software flow control (XON/XOFF)                      |

The result for 115200 baud, 8N1, raw:

```bash
$ stty -F /dev/serial0
speed 115200 baud; line = 0;
min = 1; time = 0;
-brkint -icrnl -imaxbel
-opost
-isig -icanon -echo
```

* `min = 1; time = 0`: `read()` returns as soon as at least 1 byte has
  arrived (`VMIN`, `VTIME`).
* `-icanon`: no canonical mode, the data is not collected into lines.
* `-opost`: no output processing (e.g. `\n` is not converted to `\r\n`).

The settings stay active until they are changed (or the system is
rebooted), so other programs such as `cat` and `echo` use them.


## echo and cat

_Example:_ Send a line of text.

```bash
$ echo "Hello UART" > /dev/serial0
```

`echo -n` sends the text without the `\n` at the end. Binary data can be
sent with `printf`:

```bash
$ printf 'AT\r\n' > /dev/serial0          # AT command (modems, GSM modules)
$ printf '\x01\x03\x00\x00' > /dev/serial0  # binary bytes
```

_Example:_ Receive data (until `Ctrl-C`).

```bash
$ cat /dev/serial0
```

_Example:_ Show the received bytes in hexadecimal (here: exactly 9 bytes).

```bash
$ head -c 9 /dev/serial0 | hexdump -C
00000000  48 65 6c 6c 6f 0d 0a 01  ff                       |Hello....|
00000009
```

This is useful for binary protocols and to see the line endings (`0d 0a`
= `\r\n`).

_Example:_ Loopback test (TXD connected to RXD).

```bash
$ stty -F /dev/serial0 115200 raw -echo
$ cat /dev/serial0 &
$ echo "Hello UART" > /dev/serial0
Hello UART
$ kill %1
```


## picocom

`picocom` is a small, simple terminal program. Everything typed on the
keyboard is sent, everything received is shown on the screen.

```bash
$ sudo apt install picocom
```

```bash
$ picocom -b 115200 /dev/serial0
picocom v3.1
port is        : /dev/serial0
flowcontrol    : none
baudrate is    : 115200
parity is      : none
databits are   : 8
stopbits are   : 1
...
Type [C-a] [C-h] to see available commands
Terminal ready
```

| Option              | Description                                          |
|---------------------|------------------------------------------------------|
| `-b <baud>`         | Baud rate                                            |
| `-d <5..8>`         | Data bits                                            |
| `-p <n,e,o>`        | Parity                                               |
| `-f <n,h,s>`        | Flow control: none, hardware (RTS/CTS), software (XON/XOFF) |
| `-c`                | Local echo: show the typed characters                |
| `--omap crlf`       | Send `\r\n` when Enter (`\r`) is pressed             |
| `--imap lfcrlf`     | Show received `\n` as `\r\n`                         |

The commands start with **`Ctrl-A`**:

| Keys                 | Command                      |
|----------------------|------------------------------|
| `Ctrl-A` `Ctrl-X`    | Exit                         |
| `Ctrl-A` `Ctrl-U` / `Ctrl-D` | Increase / decrease baud rate |
| `Ctrl-A` `Ctrl-\`    | Send a break                 |
| `Ctrl-A` `Ctrl-H`    | Help                         |


## minicom

`minicom` is the classic, menu-based terminal program (modeled on the DOS
program Telix).

```bash
$ sudo apt install minicom
$ minicom -D /dev/serial0 -b 115200
```

| Keys            | Command                                                   |
|-----------------|-----------------------------------------------------------|
| `Ctrl-A` `X`    | Exit                                                      |
| `Ctrl-A` `O`    | Configuration menu (serial port setup, flow control, ...) |
| `Ctrl-A` `E`    | Local echo on/off                                         |
| `Ctrl-A` `Z`    | Help                                                      |

> minicom enables **hardware flow control** by default. If no data is sent
> and RTS/CTS are not connected, switch it off with `Ctrl-A` `O` ->
> "Serial port setup" -> "Hardware Flow Control: No".


## screen

`screen` is a terminal multiplexer, but it can also be used as a simple
terminal program:

```bash
$ screen /dev/serial0 115200
```

Exit with `Ctrl-A` `K` and confirm with `y`.


## Serial Console from a PC

The tools also work in the other direction: with a USB-serial adapter
connected to the Raspberry Pi, and the **serial console enabled** on the
Pi, a PC can log in to the Pi:

```bash
pc$ picocom -b 115200 /dev/ttyUSB0
...
raspberrypi login: pi
Password:
pi@raspberrypi:~$
```

This shows the boot messages of the kernel as well, which is useful when
the Pi doesn't boot or has no network. On Windows, use PuTTY with the
connection type "Serial" and the COM port of the adapter.


## socat: Virtual Serial Ports

`socat` connects two data channels. It can create a pair of connected
**virtual serial ports** (pseudo-terminals), so serial programs can be
tested without any hardware:

```bash
$ sudo apt install socat
$ socat -d -d pty,raw,echo=0,link=/tmp/ttyV0 pty,raw,echo=0,link=/tmp/ttyV1
... N PTY is /dev/pts/4
... N PTY is /dev/pts/5
... N starting data transfer loop with FDs [5,5] and [7,7]
```

In a second terminal:

```bash
$ cat /tmp/ttyV1
```

In a third terminal:

```bash
$ echo "Hello" > /tmp/ttyV0
```

`socat` can also make a serial port available over the network, e.g. a
device on the Raspberry Pi's UART for a program on a PC:

```bash
$ socat TCP-LISTEN:5000,reuseaddr FILE:/dev/serial0,b115200,raw,echo=0
```


## References

* Linux man pages: [stty(1)](https://man7.org/linux/man-pages/man1/stty.1.html),
  [termios(3)](https://man7.org/linux/man-pages/man3/termios.3.html)

* [picocom (GitHub)](https://github.com/npat-efault/picocom)

* [Linux Serial HOWTO](https://tldp.org/HOWTO/Serial-HOWTO.html)

*Egon Teiniker, 2025-2026, GPL v3.0*

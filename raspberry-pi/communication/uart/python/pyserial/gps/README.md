# Example: GPS Receiver (NMEA 0183)

GPS modules such as the **u-blox NEO-6M** (or NEO-M8N) are connected via
UART. After power-on, they send their data once per second as **NMEA 0183**
text sentences, by default at **9600 baud, 8N1**. No command has to be sent
to the module.

* Supply voltage: 3.3 V to 5 V (most breakout boards have a regulator)
* Signal levels: 3.3 V
* The first fix (**cold start**) takes about 30 s to several minutes and
  needs a clear view of the sky. Until then, the sentences contain empty
  fields.


## Wiring

| GPS module | Raspberry Pi          |
|------------|-----------------------|
| VCC        | 3.3V (pin 1)          |
| GND        | GND (pin 6)           |
| TX         | RXD, GPIO 15 (pin 10) |
| RX         | TXD, GPIO 14 (pin 8)  |

The RX line of the module is only needed to configure it (e.g. with the
binary UBX protocol of u-blox).

Check that data arrives (see [UART Tools](../../../uart-utils/README.md)):

```bash
$ stty -F /dev/serial0 9600 raw -echo
$ cat /dev/serial0
$GPRMC,092751.000,A,4704.3956,N,01526.4562,E,0.02,31.66,081126,,,A*51
$GPGGA,092751.000,4704.3956,N,01526.4562,E,1,07,1.03,368.2,M,47.3,M,,*65
$GPGSA,A,3,...
...
```


## Protocol

Each NMEA sentence is a **text line**:

```
$GPGGA,092751.000,4704.3956,N,01526.4562,E,1,07,1.03,368.2,M,47.3,M,,*65\r\n
```

| Part              | Meaning                                                    |
|-------------------|------------------------------------------------------------|
| `$`               | Start of the sentence                                      |
| `GP`              | Talker: `GP` = GPS, `GN` = several systems (GPS + GLONASS + ...) |
| `GGA`             | Sentence type: **G**lobal Positioning System Fix Data     |
| `092751.000`      | UTC time: 09:27:51                                         |
| `4704.3956,N`     | Latitude: 47° 04.3956' North (format **ddmm.mmmm**)        |
| `01526.4562,E`    | Longitude: 15° 26.4562' East (format **dddmm.mmmm**)       |
| `1`               | Fix quality: 0 = no fix, 1 = GPS fix, 2 = DGPS fix         |
| `07`              | Number of satellites used                                  |
| `1.03`            | Horizontal dilution of precision (HDOP)                    |
| `368.2,M`         | Altitude above mean sea level in meters                    |
| `*65`             | Checksum: XOR of all characters between `$` and `*`        |
| `\r\n`            | End of the sentence                                        |

Other common sentences are `RMC` (recommended minimum: time, date,
position, speed, course), `GSA` (active satellites) and `GSV` (satellites
in view).

The position is given in **degrees and minutes**. For decimal degrees, the
minutes must be divided by 60:

```
4704.3956 N  ->  47 + 04.3956 / 60  =  47.07326°
```


## Usage

`nmea.py` contains the functions to check the checksum (`checksum_ok()`)
and to parse a GGA sentence (`parse_gga()`), which returns a `Position`
object or `None` if there is no fix. These functions only work with
strings, so they can be tested without a serial port.

`main.py` reads one line after another with `readline()`, checks it and
prints the position:

```python
with serial.Serial(PORT, 9600, timeout=2) as ser:
    line = ser.readline()
    sentence = line.decode("ascii", errors="replace").strip()
    if nmea.checksum_ok(sentence) and sentence[3:6] == "GGA":
        pos = nmea.parse_gga(sentence)
```

The timeout ensures that the program does not block forever if the module
sends nothing (wrong wiring or baud rate).


## Run

```bash
$ python3 main.py
Reading NMEA sentences from /dev/serial0 at 9600 baud
Waiting for fix ...
Waiting for fix ...
09:27:51 UTC |  47.07326,   15.44094 |  368.2 m | 7 satellites
09:27:52 UTC |  47.07326,   15.44094 |  368.3 m | 7 satellites
...
```

Without a GPS module, the program can be tested with two virtual serial
ports (see [pyserial](../introduction/README.md#testing-without-hardware)):

```bash
$ socat pty,raw,echo=0,link=/tmp/ttyV0 pty,raw,echo=0,link=/tmp/ttyV1 &
$ python3 main.py /tmp/ttyV1 &
$ printf '$GPGGA,092751.000,4704.3956,N,01526.4562,E,1,07,1.03,368.2,M,47.3,M,,*65\r\n' > /tmp/ttyV0
09:27:51 UTC |  47.07326,   15.44094 |  368.2 m | 7 satellites
```


## References

* u-blox: NEO-6 Data Sheet and u-blox 6 Receiver Description (protocol specification)

* [NMEA 0183 sentences (GPSD documentation)](https://gpsd.gitlab.io/gpsd/NMEA.html)

* [pyserial](https://pyserial.readthedocs.io/)

*Egon Teiniker, 2025-2026, GPL v3.0*

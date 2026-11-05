# Example: DHT20 Temperature and Humidity Sensor

The DHT20 (Aosong, based on the AHT20 chip) measures temperature and relative humidity
and is connected via I2C at the fixed address **0x38**.

* Temperature: -40 to 80 °C, accuracy ±0.5 °C
* Relative humidity: 0 to 100 %, accuracy ±3 %
* Supply voltage: 2.2 to 5.5 V (use **3.3V** on the Raspberry Pi)


## Wiring

| DHT20 | Raspberry Pi       |
|-------|--------------------|
| VDD   | 3.3V (pin 1)       |
| SDA   | GPIO 2 (pin 3)     |
| GND   | GND (pin 6)        |
| SCL   | GPIO 3 (pin 5)     |

Check that the sensor is visible on the bus:

```bash
$ i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
...
30: -- -- -- -- -- -- -- -- 38 -- -- -- -- -- -- --
...
```


## Protocol

Unlike most I2C sensors, the DHT20 has **no register map**. It is controlled by
commands and returns its data in a plain I2C read:

1. **Initialization**: wait 100 ms after power-on, then read the status byte.
   If bits 3 and 4 (`0x18`) are not set, the registers `0x1B`, `0x1C` and `0x1E`
   must be re-initialized (procedure from the datasheet sample code).

2. **Trigger measurement**: write the bytes `0xAC 0x33 0x00`.

3. **Wait** 80 ms, then **read 7 bytes**:

   | Byte | Content |
   |------|---------|
   | 0    | Status (bit 7 = busy) |
   | 1, 2, 3[7:4] | Humidity (20 bits) |
   | 3[3:0], 4, 5 | Temperature (20 bits) |
   | 6    | CRC-8 (polynomial `0x31`, init `0xFF`) over bytes 0-5 |

   If the busy bit is still set, read again.

4. **Convert** the raw values:

   ```
   RH [%] = raw_humidity / 2^20 * 100
   T [°C] = raw_temperature / 2^20 * 200 - 50
   ```

Because there are no registers, the SMBus functions with a register argument
(e.g. `read_i2c_block_data(addr, reg, n)`) can't be used: they would send the register
byte first. Instead, the example uses raw I2C messages (`i2c_msg.write()`,
`i2c_msg.read()`) with `bus.i2c_rdwr()`.


## Usage

The `DHT20` class (`dht20.py`) takes an open `SMBus` object, so several devices can
share one bus. The constructor initializes the sensor, and `read()` returns temperature
and humidity. `main.py` uses the class like this:

```python
from smbus2 import SMBus
from dht20 import DHT20

with SMBus(1) as bus:
    sensor = DHT20(bus)
    temperature, humidity = sensor.read()
```


## Run

```bash
$ python3 main.py
Connected to DHT20 at address 0x38
Temperature:  23.51 °C | Humidity:  45.02 %
Temperature:  23.52 °C | Humidity:  44.98 %
...
```

The example reads the sensor every 2 seconds, because frequent measurements heat
up the sensor and distort the result.


## References

* DHT20 Datasheet (Aosong / ASAIR)
* [smbus2](https://pypi.org/project/smbus2/)

*Egon Teiniker, 2025-2026, GPL v3.0*

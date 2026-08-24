# I2C on the Raspberry Pi

I2C (Inter-Integrated Circuit) is a simple, two-wire communication protocol 
that allows multiple devices (slaves) to communicate with one or more 
controllers (masters) over a shared bus. 

It uses a **data line (SDA)** and a **clock line (SCL)** along with pull-up 
resistors. Each device on the bus has a **unique address**, making it easy 
for the master to send commands or data to specific devices. 

This protocol is popular for connecting peripherals like sensors, EEPROMs, 
and other modules in embedded systems due to its simplicity and low pin count.


## Wiring

In order to control an I2C bus to the Raspberry Pi we need to connect the 
following pins:

- **VCC** (Power) - 3.3V
- **GND** (Ground) - GND
- **SDA** (Serial Data Line) - GPIO 2
- **SCL** (Serial Clock Line) - GPIO 3

Also activate the I2C interface on the Raspberry Pi. This can be done by
running the `raspi-config` command and enabling the I2C interface.

```bash
sudo raspi-config
```

## I2C Tools

The I2C Tools are a collection of command-line utilities provided on Raspberry Pi 
(and other Linux systems) that allow you to interact directly with devices on the 
I2C bus. 

```bash
$ sudo apt-get install i2c-tools
```

They are part of the i2c-tools package, which is typically installed by default 
on Raspberry Pi OS or can be installed via the package manager.

* **i2cdetect**: Scans one or more I2C buses for devices.

	_Example:_ Scan I2c bus for devices.
	```bash
	$ i2cdetect -y 1

		0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
	00:          -- -- -- -- -- -- -- -- -- -- -- -- --
	10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	20: 20 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	70: -- -- -- -- -- -- -- --	
	```	

	* `-y`: Disables interactive mode. By default, i2cdetect will prompt you 
		to confirm before scanning each address.
	* `1`: Specifies I2C bus 1 (common on recent Raspberry Pi models).

	* `0x20`: Address of PCF8574 IO extension chip.

	Display a grid showing all active I2C addresses on bus 1.
	For modern Raspberry Pi models (from Revision 2 onward), I2C bus number 1 
	is used. 

* **i2cset**: Writes a byte or word to a register of an I2C device, allowing 
	you to 	configure devices or test communication.

* **i2cget**: Reads a byte or word from a specified register of an I2C device. 
	This is useful for checking the value of specific registers.

* **i2cdump**: Reads a block of data from an I2C device, dumping the contents of 
	registers in a formatted output. This is particularly useful for debugging 
	device configurations.

* **i2ctransfer**: Sends a sequence of I2C messages to a device, allowing 
	us to perform more complex operations than with i2cset and i2cget.


## PCF8574 Port Expander

The PCF8574 is an 8-bit I/O expander that uses the I2C bus for communication.

_Example:_ Set a byte to the PCF8574 port extension IC.
```bash
$ i2cset -y 1 0x20 0xF0
```	
* `-y`: Disables interactive mode.
* `1`: Specifies I2C bus 1 (common on recent Raspberry Pi models).
* `0x20`: The I2C address of the PCF8574 device.
* `0xFF`: The byte to write (in this case, setting all 8 I/O pins to 
	a high state).


_Example:_ Read a byte from the PCF8574 port extension IC.
```bash
$ i2cset -y 1 0x21 
```	
* `-y`: Disables interactive mode.
* `1`: Specifies I2C bus 1 (common on recent Raspberry Pi models).
* `0x21`: The I2C address of the PCF8574 device.
* The command returns a byte in hexadecimal.

The PCF8574 pins have an **internal pull-up resistor**, so they will 
read as high when not connected to anything. When you connect a pin 
to ground, it will read as low.


## EEPROM 24C256A

24C256A uses 16‑bit addressing, so every transaction must send two address 
bytes before the actual data.

_Example:_ Write 3 bytes (2 address bytes, 1 data byte) to the 24C256A EEPROM at address 0x50.
```bash
$ i2ctransfer -y 1 w3@0x50 0x01 0x23 0xAB

```
* w3@0x50: Write 3 bytes to the device at address 0x50.
* 0x01 0x23: The 16-bit memory address (0x0123) split into high and low bytes.
* 0xAB: The data byte to be stored.

_Example:_ Read 3 bytes from the 24C256A EEPROM at address 0x50.
To read, first you must set the internal address pointer to the desired 
location by doing a short write of the two address bytes. Then, perform 
a read transaction to fetch the data.
```bash
$ i2ctransfer -y 1 w2@0x50 0x01 0x23
$ i2ctransfer -y 1 r1@0x50
```
The read command returns the byte stored at address 0x0123.



## References
* [YouTube (The Linux Foundation): Basics of I2C on Linux - Luca Ceresoli, Bootlin](https://youtu.be/g9-wgdesvwA?si=FsbD1XtAw5ytEySx)

* [Raspberry Pi Tutorial Series: I2C](https://www.waveshare.com/wiki/Raspberry_Pi_Tutorial_Series:_I2C)





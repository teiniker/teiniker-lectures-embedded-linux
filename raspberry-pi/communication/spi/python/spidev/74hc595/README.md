# Example: 74HC595 Shift Register

The 74HC595 is an **8-bit serial-in, parallel-out shift register** with an
output latch. It is the simplest possible SPI target: it has no commands and
no registers, every byte that is shifted in appears on its 8 outputs
**Q0 - Q7**. It is often used to drive LEDs or 7-segment displays with only
three GPIO pins.

* Supply voltage: 2 - 6 V (use **3.3 V** on the Raspberry Pi)
* Only write direction: the 74HC595 has no MISO output
  (Q7' is used for daisy chaining)


## Wiring

| 74HC595 pin       | Function                | Raspberry Pi            |
|-------------------|-------------------------|-------------------------|
| 16 VCC            | Supply                  | 3.3 V (pin 1)           |
| 8 GND             | Ground                  | GND (pin 6)             |
| 14 DS (SER)       | Serial data input       | MOSI, GPIO 10 (pin 19)  |
| 11 SHCP (SRCLK)   | Shift register clock    | SCLK, GPIO 11 (pin 23)  |
| 12 STCP (RCLK)    | Storage register (latch) clock | CE0, GPIO 8 (pin 24) |
| 13 OE             | Output enable (active low) | GND                  |
| 10 MR (SRCLR)     | Reset (active low)      | 3.3 V                   |
| 15, 1 - 7 Q0 - Q7 | Outputs                 | LED + 330 Ω resistor to GND |
| 9 Q7'             | Serial output           | DS of the next 74HC595 (optional) |


## Protocol

The 74HC595 contains two registers:

1. With each **rising edge** on SHCP (= SCLK), the bit on DS (= MOSI) is
   shifted into the **shift register** (SPI mode 0).

2. With the **rising edge** on STCP, the shift register is copied to the
   **storage register**, which drives the outputs Q0 - Q7.

STCP is connected to the chip select CE0. CE0 goes high at the **end of
every transfer**, so the new byte appears on the outputs at once, without
flickering while the bits are being shifted.

Since the data is sent MSB first, bit 7 of the byte ends up in Q7 and
bit 0 in Q0. Writing `0x01` switches on the LED at Q0.

Several 74HC595 can be connected as a **daisy chain** (Q7' to DS of the
next one, shared SHCP and STCP). Then one byte per chip is sent in a single
transfer, e.g. `spi.writebytes([byte_for_chip2, byte_for_chip1])`: the
first byte is shifted furthest, into the last chip.


## Run

```bash
$ python3 write.py
Running light on Q0..Q7 (Ctrl+C to stop)...
```

The same can be tested from the command line (see
[SPI Tools](../../../spi-tools/README.md)):

```bash
$ printf '\x55' | spi-pipe -d /dev/spidev0.0 -s 1000000    # Q0, Q2, Q4, Q6 on
```


## References

* 74HC595 Datasheet (Nexperia, Texas Instruments)
* [spidev](https://pypi.org/project/spidev/)

*Egon Teiniker, 2025-2026, GPL v3.0*

"""
UART loopback test: connect TXD (GPIO 14, pin 8) with RXD (GPIO 15, pin 10).
Everything that is sent must be received again.

Usage: python3 loopback.py [port] [baudrate]
"""
import sys
import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/serial0"
BAUDRATE = int(sys.argv[2]) if len(sys.argv) > 2 else 115200


def main():
    with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
        print(f"Port: {ser.name}, {ser.baudrate} baud, "
              f"{ser.bytesize}{ser.parity}{ser.stopbits}")
        ser.reset_input_buffer()            # discard old data

        tx = b"Hello UART \x00\x7f\xff"     # text and binary bytes
        ser.write(tx)
        ser.flush()                         # wait until all bytes are sent
        rx = ser.read(len(tx))              # returns after len(tx) bytes or 1 s

        print(f"TX: {tx.hex(' ')}")
        print(f"RX: {rx.hex(' ')}")
        if rx == tx:
            print("OK: loopback works")
        elif not rx:
            print("ERROR: nothing received - is TXD connected to RXD?")
        else:
            print("ERROR: received data differs - wrong baud rate or noise?")


if __name__ == "__main__":
    main()

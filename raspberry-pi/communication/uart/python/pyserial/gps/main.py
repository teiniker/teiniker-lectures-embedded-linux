"""
Read the position from a GPS receiver (e.g. u-blox NEO-6M) connected to the UART.

Usage: python3 main.py [port]
"""
import sys
import serial

import nmea

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/serial0"
BAUDRATE = 9600         # default of most GPS modules


def main():
    with serial.Serial(PORT, BAUDRATE, timeout=2) as ser:
        print(f"Reading NMEA sentences from {ser.name} at {ser.baudrate} baud")
        while True:
            line = ser.readline()           # up to b'\n' or timeout
            if not line:
                print("No data - check wiring (GPS TX -> Pi RX) and baud rate")
                continue

            sentence = line.decode("ascii", errors="replace").strip()
            if not nmea.checksum_ok(sentence):
                print(f"Invalid sentence: {sentence!r}")
                continue

            if sentence[3:6] == "GGA":
                pos = nmea.parse_gga(sentence)
                if pos is None:
                    print("Waiting for fix ...")
                else:
                    print(f"{pos.time[:2]}:{pos.time[2:4]}:{pos.time[4:6]} UTC | "
                          f"{pos.latitude:9.5f}, {pos.longitude:10.5f} | "
                          f"{pos.altitude:6.1f} m | {pos.satellites} satellites")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

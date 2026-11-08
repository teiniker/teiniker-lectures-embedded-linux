"""Minimal parser for NMEA 0183 sentences (GGA and RMC) of a GPS receiver."""
from dataclasses import dataclass
from functools import reduce


@dataclass
class Position:
    time: str           # UTC, hhmmss.ss
    latitude: float     # degrees, negative = south
    longitude: float    # degrees, negative = west
    satellites: int
    altitude: float     # meters above mean sea level


def checksum_ok(sentence: str) -> bool:
    """'$...*hh': XOR of all characters between '$' and '*' must be hh."""
    if not sentence.startswith("$") or "*" not in sentence:
        return False
    data, _, checksum = sentence[1:].partition("*")
    calculated = reduce(lambda acc, c: acc ^ ord(c), data, 0)
    try:
        return calculated == int(checksum[:2], 16)
    except ValueError:
        return False


def to_degrees(value: str, hemisphere: str) -> float:
    """Convert NMEA (d)ddmm.mmmm to decimal degrees: 4807.038 N -> 48.1173."""
    dot = value.index(".")
    degrees = int(value[:dot - 2])
    minutes = float(value[dot - 2:])
    result = degrees + minutes / 60
    return -result if hemisphere in ("S", "W") else result


def parse_gga(sentence: str) -> Position | None:
    """Parse a GGA sentence (fix data). Returns None if there is no fix."""
    fields = sentence.partition("*")[0].split(",")
    # fields: 0 type, 1 time, 2 lat, 3 N/S, 4 lon, 5 E/W, 6 fix quality,
    #         7 satellites, 8 HDOP, 9 altitude, 10 unit, ...
    if not fields[0].endswith("GGA") or fields[6] in ("", "0"):
        return None
    return Position(
        time=fields[1],
        latitude=to_degrees(fields[2], fields[3]),
        longitude=to_degrees(fields[4], fields[5]),
        satellites=int(fields[7]),
        altitude=float(fields[9]),
    )

import time
from smbus2 import SMBus

from dht20 import DHT20

I2C_BUS = 1


def main():
    with SMBus(I2C_BUS) as bus:
        sensor = DHT20(bus)
        print(f"Connected to DHT20 at address {hex(DHT20.ADDRESS)}")

        while True:
            temperature, humidity = sensor.read()
            print(f"Temperature: {temperature:6.2f} °C | Humidity: {humidity:6.2f} %")
            time.sleep(2)   # avoid self-heating: at most one measurement every 2s


if __name__ == "__main__":
    main()

# Example: LED blink 

This example uses the **gpiozero** library, which provides an 
object-oriented abstraction for GPIO devices instead of raw pin 
numbers and register access.

```python
from gpiozero import LED
from time import sleep

led = LED(17)

while True:
    led.on()
    sleep(1)
    led.off()
    sleep(1)
```

* `LED(17)` creates an `LED` device object bound to GPIO pin 17 (BCM 
    numbering). Behind the scenes, `gpiozero` asks its active pin 
    factory (typically `LGPIOFactory` on Pi OS Bookworm/Trixie) to open 
    the GPIO character device that owns this pin (e.g. `/dev/gpiochip4` 
    on a Raspberry Pi 5) and requests an output line via the 
    `GPIO_V2_GET_LINE_IOCTL` call.

* `led.on()` and `led.off()` set the line's value through the 
    `GPIO_V2_LINE_SET_VALUES_IOCTL` call, which the kernel's `gpiolib` 
    subsystem forwards to the SoC's GPIO driver, physically driving the 
    pin high (3.3V) or low (0V).

* `sleep(1)` simply blocks the Python interpreter for one second between 
    state changes, so the LED connected to GPIO 17 blinks at 1Hz.

Note that `gpiozero` opens and configures the GPIO line once, when the 
`LED` object is created, rather than on every `on()`/`off()` call, the 
loop only toggles the already-configured line.

## Run

```bash
$ python3 blink.py
```

Press `Ctrl-C` to stop the program.

## References

* [gpiozero: LED](https://gpiozero.readthedocs.io/en/stable/api_output.html#led)
* [Raspberry Pi: Read Digital Inputs with Python](https://randomnerdtutorials.com/raspberry-pi-digital-inputs-python/)

_Egon Teiniker, 2026, GPL v3.0_

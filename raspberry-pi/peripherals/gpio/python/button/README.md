# Example: Button 

The button wires GPIO21 to **GND** through a switch. Without any pull 
resistor, the pin would float (read an undefined value) whenever the 
switch is open. To avoid this, the Raspberry Pi's SoC provides internal 
**pull-up/pull-down resistors** that can be enabled per GPIO line 
without any extra hardware.

`gpiozero`'s `Button` class enables the **internal pull-up resistor** by 
default (`pull_up=True`), which weakly ties GPIO21 to 3.3V. This means:

* Button **not pressed**: the pull-up holds the line **HIGH**.
* Button **pressed**: the switch connects the line to **GND**, pulling 
    it **LOW**.

Because the logic is inverted (pressed = LOW), `gpiozero` interprets a 
LOW line as `is_pressed == True` and fires `when_pressed` accordingly, 
so the application code never has to deal with the inverted voltage 
level directly.

`bounce_time=0.05` additionally enables a **50ms software debounce**: 
mechanical switches "bounce" for a few milliseconds, producing several 
spurious HIGH/LOW transitions on a single press. `gpiozero` ignores 
further edges for the given time window after the first one, so only a 
single, clean press/release is reported.


## Polling

```python
from gpiozero import Button
from time import sleep

button = Button(21, bounce_time=0.05)

while True:
    if button.is_pressed:
        print("Button: ON")
    else:
        print("Button: OFF")
    sleep(0.5)
```

`button.is_pressed` reads the **current, debounced state** of the GPIO 
line on demand: each access issues a `GPIO_V2_LINE_GET_VALUES_IOCTL` 
call through the active pin factory and returns `True` if the line 
reads LOW (i.e. the button is pressed). The `while` loop actively 
**polls** this state every 0.5 seconds — the CPU repeatedly asks 
"is it pressed *right now*?" instead of being notified. Short presses 
that happen entirely between two polls can be missed.


## Event-Driven

```python
from gpiozero import Button
from signal import pause

button = Button(21, bounce_time=0.05)

def on_pressed():
    print("Button: ON")

def on_released():
    print("Button: OFF")

button.when_pressed = on_pressed
button.when_released = on_released

pause()  # Keep the script running to wait for events
```

Instead of polling, `Button` can watch the line for **edge events**. 
Internally, `gpiozero` requests the GPIO line with 
`GPIO_V2_LINE_FLAG_EDGE_RISING | GPIO_V2_LINE_FLAG_EDGE_FALLING` and 
starts a background thread that blocks on `poll()`/`epoll()` for that 
line's file descriptor.

* When the kernel reports a falling edge (line goes LOW), `gpiozero` 
    applies the debounce window and, once settled, invokes the 
    `when_pressed` callback (`on_pressed`) from the background thread.
* A rising edge (line goes HIGH again) triggers `when_released` 
    (`on_released`) the same way.

The main thread does no work at all — `signal.pause()` simply suspends 
it until a signal (e.g. `Ctrl+C`) arrives, while the background thread 
delivers callbacks the instant the hardware reports a change. This is 
more responsive and far less CPU-intensive than polling, since no 
presses can be missed and the CPU stays idle between events.


## References

* [gpiozero: Button](https://gpiozero.readthedocs.io/en/stable/api_input.html#button)
* [Raspberry Pi: Read Digital Inputs with Python](https://randomnerdtutorials.com/raspberry-pi-digital-inputs-python/)

_Egon Teiniker, 2026, GPL v3.0_

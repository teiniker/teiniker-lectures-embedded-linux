# gpiod Tools

These tools come from **libgpiod**, the official Linux GPIO character-device interface
(`/dev/gpiochipN`). They work on all Raspberry Pi models, **including the Pi 5**, where
the old sysfs interface (`/sys/class/gpio`) and register-based tools (e.g. WiringPi)
no longer work because the GPIOs are provided by the **RP1** I/O controller.

> **Note:** Raspberry Pi OS Trixie ships **libgpiod v2** (2.2.x), whose tools have a
> **different command-line syntax** than v1 (e.g. Bookworm, 1.6.x).
> The examples below use the **v2 syntax**. Check the installed version with:

> ```bash
> $ gpiodetect --version
> ```

## Setup

```bash
$ sudo apt install gpiod
```

Members of the `gpio` group can access `/dev/gpiochip*` without `sudo`:
```bash
$ groups
... gpio ...
```

## Commands

| Command      | What it does                                         |
| ------------ | ---------------------------------------------------- |
| `gpiodetect` | Lists available gpiochips (e.g., `gpiochip0`)        |
| `gpioinfo`   | Shows all GPIO lines, names, direction, consumers    |
| `gpioset`    | Set line(s) high or low (holds the value until exit) |
| `gpioget`    | Read line value(s)                                   |
| `gpiomon`    | Monitor line edges (interrupt-like)                  |
| `gpionotify` | Monitor line info changes (request, release, ...)    |

Lines can be addressed either by **name** (e.g. `GPIO17`) or by **chip and offset**
(e.g. `-c gpiochip0 17`). Using names is recommended because the chip number depends
on the kernel version.


## Find the GPIO Chip

```bash
$ gpiodetect
gpiochip0 [pinctrl-rp1] (54 lines)
gpiochip1 [gpio-brcmstb@107d508500] (32 lines)
gpiochip2 [gpio-brcmstb@107d508520] (4 lines)
gpiochip3 [gpio-brcmstb@107d517c00] (17 lines)
gpiochip4 [gpio-brcmstb@107d517c20] (6 lines)
```

On the Raspberry Pi 5 the 40-pin header is connected to the **RP1** chip (`pinctrl-rp1`).
With current kernels this is `gpiochip0`, with older kernels it was `gpiochip4`.

_Example_: Show information about a single line
```bash
$ gpioinfo GPIO17
gpiochip0 17    "GPIO17"                input
```

_Example_: Show all lines of the header chip
```bash
$ gpioinfo -c gpiochip0
```


## Output: LED on GPIO17

In libgpiod v2, `gpioset` **keeps the line requested** and runs in the foreground until
it is terminated with `Ctrl+C`. When the process exits, the line is released and its
state is no longer guaranteed.

_Example_: Set GPIO17 high (until `Ctrl+C`)
```bash
$ gpioset GPIO17=1
```

_Example_: Set GPIO17 low (until `Ctrl+C`)
```bash
$ gpioset GPIO17=0
```

_Example_: Same, using chip and offset
```bash
$ gpioset -c gpiochip0 17=1
```

_Example_: Set GPIO17 high and exit immediately (no `Ctrl+C` needed)
```bash
$ gpioset -t0 GPIO17=1
```
A toggle period of `0` means "set the value, then exit". Use `-p` to hold the value
for a minimum time before exiting (e.g. `gpioset -p 20ms -t0 GPIO17=1`).

> **Note:** After `gpioset` exits, the line is released. On the Raspberry Pi 5 the pin
> usually keeps its value, but this is **not guaranteed** by the kernel.

_Example_: Blink GPIO17 (toggle every 500 ms)
```bash
$ gpioset -t 500ms GPIO17=1
```

_Example_: Set GPIO17 high and run in the background (daemon)
```bash
$ gpioset -z GPIO17=1
$ pkill gpioset          # release the line
```


## Input: Push Button on GPIO21

The button connects GPIO21 to GND, therefore the internal **pull-up** resistor is enabled.

_Example_: Read GPIO21
```bash
$ gpioget -b pull-up GPIO21
"GPIO21"=active
```

_Example_: Read GPIO21 as a number (`1` = high, `0` = low)
```bash
$ gpioget --numeric -b pull-up GPIO21
1
```

_Example_: Monitor rising/falling edges (until `Ctrl+C`)
```bash
$ gpiomon -e both -b pull-up GPIO21
```

_Example_: Wait for 5 falling edges (button presses) with 10 ms debouncing
```bash
$ gpiomon -e falling -b pull-up -p 10ms -n 5 GPIO21
```


## References

* [libgpiod: Command-line tools](https://libgpiod.readthedocs.io/en/latest/gpio_tools.html)
* [Raspberry Pi Documentation: GPIO](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#gpio)


_Egon Teiniker, 2025-2026, GPL v3.0_

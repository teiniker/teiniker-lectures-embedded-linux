# libgpiod Library

libgpiod is the C library (plus command-line tools) for the Linux **GPIO character
device** interface (`/dev/gpiochipN`). It is the official, board-independent way to
access GPIOs from user space and works on all Raspberry Pi models, **including the Pi 5**.

* No direct register access: the kernel GPIO driver does the hardware work.
* No root privileges required: members of the `gpio` group may open `/dev/gpiochip*`.
* Lines are **requested** by a process; the kernel prevents conflicting use and
  releases the lines automatically when the process exits.
* Supports inputs, outputs, bias (pull-up/down), active-low, open-drain/source,
  and edge events (interrupts) with kernel timestamps.

> **Note:** libgpiod v1 (e.g. Raspberry Pi OS Bookworm, 1.6.x) and v2 (e.g. Raspberry Pi OS
> Trixie, 2.2.x) have **incompatible APIs**. These examples use the **v2 API**.
> Check the installed version with `gpiodetect --version`.


## Setup

```bash
$ sudo apt install gpiod libgpiod-dev
```

On the Raspberry Pi 5 the 40-pin header was `gpiochip4` with older kernels and is
`gpiochip0` with current kernels. Use `gpioinfo` to check which chip has the lines
`GPIO17`, `GPIO27`, ... and adjust `CHIP_PATH` in the examples if necessary.


## Examples

* [gpio_blink](gpio_blink/): Blink an LED (GPIO17)
* [gpio_input](gpio_input/): Read a push button (GPIO27) with internal pull-up


## References

* [libgpiod (kernel.org)](https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/)
* [libgpiod API documentation](https://libgpiod.readthedocs.io/)

*Egon Teiniker, 2025-2026, GPL v3.0*

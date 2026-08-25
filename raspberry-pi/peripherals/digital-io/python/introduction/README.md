# Python Libraries for GPIO Programming


## gpiozero

`gpiozero` is an **object-oriented Python library** designed to abstract 
hardware components into logical software devices (like LED, Button, 
MotionSensor, or Motor).

Instead of requiring manual pin configuration, bit-masking, or polling 
loops, it encapsulates hardware logic into declarative classes with 
built-in event handling, background polling threads, and mathematical 
transformations.

### Setup

```bash
$ sudo apt update
$ sudo apt install python3-gpiozero python3-lgpio
```

### Key Architectural Concepts

* **Device-Centric Abstraction**: Rather than addressing pins by raw 
    numbers and directions, you instantiate physical devices 
    (`btn = Button(2)`).

* **Pluggable Pin Factories**: `gpiozero` acts as a frontend API. 
    It delegates the actual hardware manipulation to interchangeable 
    backends called Pin Factories (e.g., `LGPIOFactory`, `RPiGPIOFactory`, 
    `PigpioFactory`, `NativeFactory`).

* **Source/Values System**: Provides functional programming utilities to 
    pipe values between devices directly without writing explicit loops 
    (e.g., `led.source = button`).


### The Propagation Path to the Kernel

On the Raspberry Pi 5, GPIOs are physically wired to the **RP1 southbridge chip** 
over a PCIe bus. Direct memory mapping is no longer practical (used in earlier 
Raspberry Pi models (Pi 1–4)), so all operations must route through the official 
Linux kernel character device subsystem.

---

_Example:_ Run `led = LED(17); led.on()` on a Raspberry Pi 5:

1. **Instantiation (`LED(17)`):**
    * `gpiozero` queries its active pin factory (typically `LGPIOFactory` on 
        Pi OS Bookworm/Trixie).
    * The factory identifies which `/dev/gpiochipX` owns physical header pin 17 
        (on Pi 5, the 40-pin header belongs to **`gpiochip4`**).
    * It issues an `open("/dev/gpiochip4", O_RDWR)` system call to obtain a file 
    descriptor for the chip.


2. **Line Configuration (`ioctl`):**
    * The pin factory requests a line handle using the `GPIO_V2_GET_LINE_IOCTL` 
        system call, passing flags for output mode (`GPIO_V2_LINE_FLAG_OUTPUT`) 
        and an initial low state.
    * Inside the kernel, the **`gpiolib`** subsystem verifies the line is not 
        in use and invokes the RP1 driver hook (`pinctrl-rp1.c`).


3. **Hardware State Change (`led.on()`):**
    * Calling `.on()` invokes `ioctl(line_fd, GPIO_V2_LINE_SET_VALUES_IOCTL, ...)`.
    * The kernel driver writes to the RP1's memory-mapped control registers via 
        the internal **PCIe link**.
    * The RP1 physical pad drives 3.3V out on GPIO pin 17.


4. **Edge Detection / Interrupts (e.g., `Button.when_pressed`):**
    * For input events, `gpiozero` configures the kernel to watch for rising 
        or falling edges using `GPIO_V2_LINE_FLAG_EDGE_RISING` / `FALLING`.
    * The underlying library calls `poll()` or `epoll()` on the line file 
        descriptor in a background worker thread.
    * When hardware voltage transitions, the RP1 signals an interrupt over PCIe. 
        The kernel services the IRQ, wakes the waiting thread from `poll()`, 
        and `gpiozero` triggers your Python callback function.

---






## gpiod

If you prefer direct, low-level control over the Linux GPIO character 
device interface without device abstractions.

### Setup

```bash
sudo apt install python3-libgpiod gpiod
```
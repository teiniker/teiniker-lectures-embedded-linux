# File Abstraction in Linux

Linux follows the Unix philosophy that **"everything is a file"**. Regular
text files, directories, hardware devices, pipes, sockets, and even kernel
interfaces such as `/proc` and `/sys` are all represented as **file-like
objects** that can be manipulated through the same small set of system
calls: `open()`, `read()`, `write()`, `lseek()`, `ioctl()`, and `close()`.

This uniform interface is implemented by the kernel's **Virtual File System
(VFS)**, an abstraction layer that sits between user-space programs and the
many different concrete file systems and drivers:

* A program calls `open("path", ...)` and receives back a small integer,
  the **file descriptor**, that identifies an entry in the process' open
  file table - it doesn't need to know whether "path" refers to a file on
  an ext4 partition, a FIFO, a terminal, or a physical device.

* Every subsequent `read()`/`write()`/`close()` call is dispatched by the
  VFS to the correct underlying driver (a file system driver, a device
  driver, a pipe implementation, ...) through a common set of function
  pointers (`file_operations` in kernel terms).

* Because the interface is uniform, the same tools and the same C code
  work regardless of what is
  actually behind the file descriptor - a text file, a serial port, or a
  block device.

The three standard file descriptors (`0` = `stdin`, `1` = `stdout`, `2` =
`stderr`) that every process inherits are a direct consequence of this
abstraction: they are just pre-opened files, which is why the same
`read()`/`write()` calls used for disk files also work for the terminal
or for redirected pipes.

## Hardware Access in Embedded Linux

On embedded Linux systems, the "everything is a file" abstraction is what
makes user-space hardware access possible without writing kernel code for
every peripheral. Device drivers expose hardware through special files
instead of a custom API, so ordinary file IO system calls become the
interface to physical hardware:

* **Device files in `/dev`**: Character devices (e.g. `/dev/ttyS0` for a
  serial port, `/dev/i2c-1` for an I2C bus, `/dev/spidev0.0` for SPI,
  `/dev/gpiochip0` for GPIO) and block devices (e.g. `/dev/mmcblk0` for an
  SD card) are opened with `open()` just like a regular file. Reading and
  writing bytes to/from the device is done with the very same `read()` and
  `write()` calls used for text files.

* **`ioctl()`**: Extends this model for operations that don't fit the
  read/write pattern - e.g. configuring a UART's baud rate, setting an SPI
  clock frequency, or toggling a single GPIO line - by sending a
  device-specific control request through the same file descriptor.

* **`/sys` (sysfs)**: Exposes kernel objects and device attributes as plain
  text files and directories. Many embedded peripherals (LEDs, GPIOs,
  PWM channels, thermal sensors, ...) can be controlled entirely from a
  shell or a C program by simply reading or writing small text files, e.g.
  `echo 1 > /sys/class/gpio/gpio17/value`.

* **`/proc` (procfs)**: Similarly exposes kernel and process state as files,
  e.g. `/proc/cpuinfo` or `/proc/interrupts`, which is often used on
  embedded boards to inspect hardware and system state without dedicated
  tooling.

* **Memory-mapped hardware**: Can be reached from user space via
  `/dev/mem` (or the safer `/dev/gpiomem` on the Raspberry Pi) together
  with `mmap()`, letting a program map a peripheral's physical register
  address range directly into its own address space.

The consequence for embedded developers is that the low-level IO system
calls covered here - `open()`, `read()`, `write()`, `close()`, and
`ioctl()` - are not just a way to work with text files; they are the same
primitives used to talk to almost every piece of hardware on a Linux-based
embedded system.

## References

* [YouTube (Chris Brown): Linux System Programming with C](https://youtube.com/playlist?list=PLysdvSvCcUhbrU3HhGhfQVbhjnN9GXCq4&si=Mk3o-qZxlVJln5zb)
    - [Lowlevel IO](https://youtu.be/29bM2WZLuHQ?si=pJ1Bs8ZjIll_-fih)
    - [Demo File Copy 1](https://youtu.be/KnYB1dRJAI0?si=ENWI-UGzZxQHBc6N)
    - [Random Access](https://youtu.be/zBxuyRtUEI4?si=I4HHOvCx_6-LMbXL)
    - [Buffered and Formatted IO](https://youtu.be/3_CRpnuO5DA?si=dvNKJONpwRlzVdtO)

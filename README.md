# Embedded Linux Systems

This repository contains lecture material for learning 
**Linux System Programming** using a **Raspberry Pi 5** 
as the target platform.

The Raspberry Pi 5 runs a full Linux operating system 
(Raspberry Pi OS) on an ARM64 processor, which makes it 
an ideal, low-cost embedded Linux board:
we can explore the Linux system call interface (files, 
processes, signals, permissions, environment) directly 
on real hardware and, at the same time, access peripherals 
such as GPIO, I2C, and CAN from user space.

The material is organized into two parts:

* **Linux System Programming**
    - [Introduction](system-programming/introduction/README.md)
    - [System Calls](system-programming/system-calls/README.md)
    - [Files](system-programming/files/)

* **Raspberry Pi 5 Programming**
    - [Raspberry Pi Boards](raspberry-pi/boards/README.md)
    - Setup 
        - [Raspberry Pi OS](raspberry-pi/setup/pi-os/README.md)
        - [SSH](raspberry-pi/setup/ssh/SSH.md)
        - [VS Code Remote Development](raspberry-pi/setup/vscode-remote/README.md)
    - Peripherals
        - [Hardware Inspection](raspberry-pi/peripherals/hardware-inspection/README.md)
        - [GPIO Port](raspberry-pi/peripherals/gpio-port/)
        - [Digital IO](peripherals/digital-io/)
        - [I2C Bus](raspberry-pi/peripherals/i2c/)
        - [CAN Bus](raspberry-pi/peripherals/can/)
    - Communication
        - [MQTT](raspberry-pi/communication/mqtt/)

*Egon Teiniker, 2025-2026, GPL v3.0* 

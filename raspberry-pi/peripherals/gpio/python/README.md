# Python Libraries for GPIO Programming


## gpiozero

`gpiozero` is the official, high-level library developed and maintained 
by Raspberry Pi. It automatically uses the modern libgpiod backend to 
handle the Raspberry Pi 5 RP1 chip.

### Setup

```bash
$ sudo apt update
$ sudo apt install python3-gpiozero python3-lgpio
```




## gpiod

If you prefer direct, low-level control over the Linux GPIO character 
device interface without device abstractions.

### Setup

```bash
sudo apt install python3-libgpiod gpiod
```
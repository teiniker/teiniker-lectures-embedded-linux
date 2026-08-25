# Inspecting Hardware in Linux 

## List USB devices

**lsusb**  is  a  utility for displaying information about USB buses 
in the system and the devices connected to them. It uses udev's hardware 
database to associate a full human-readable name to the vendor ID and the 
product ID.

_Example:_ List USB devices (Raspberry Pi)
```
$ lsusb
Bus 001 Device 004: ID 0c45:0520 Microdia MaxTrack Wireless Mouse
Bus 001 Device 005: ID 0424:7800 Microchip Technology, Inc. (formerly SMSC) 
Bus 001 Device 003: ID 0424:2514 Microchip Technology, Inc. (formerly SMSC) USB 2.0 Hub
Bus 001 Device 002: ID 0424:2514 Microchip Technology, Inc. (formerly SMSC) USB 2.0 Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

_Example:_ List USB devices in a tree format
```
$ lsusb -t
/:  Bus 01.Port 1: Dev 1, Class=root_hub, Driver=dwc_otg/1p, 480M
    |__ Port 1: Dev 2, If 0, Class=Hub, Driver=hub/4p, 480M
        |__ Port 1: Dev 3, If 0, Class=Hub, Driver=hub/3p, 480M
            |__ Port 1: Dev 5, If 0, Class=Vendor Specific Class, Driver=lan78xx, 480M
        |__ Port 2: Dev 4, If 0, Class=Human Interface Device, Driver=usbhid, 1.5M
        |__ Port 2: Dev 4, If 1, Class=Human Interface Device, Driver=usbhid, 1.5M
```

## List PCI Devices
**lspci** is a utility for displaying information about PCI buses in the system 
and devices connected to them.

_Example:_ List PCI devices (Debian12 VM)
```
$ lspci
00:00.0 Host bridge: Intel Corporation 440FX - 82441FX PMC [Natoma] (rev 02)
00:01.0 ISA bridge: Intel Corporation 82371SB PIIX3 ISA [Natoma/Triton II]
00:01.1 IDE interface: Intel Corporation 82371AB/EB/MB PIIX4 IDE (rev 01)
00:02.0 VGA compatible controller: VMware SVGA II Adapter
00:03.0 Ethernet controller: Intel Corporation 82540EM Gigabit Ethernet Controller (rev 02)
00:04.0 System peripheral: InnoTek Systemberatung GmbH VirtualBox Guest Service
00:05.0 Multimedia audio controller: Intel Corporation 82801AA AC'97 Audio Controller (rev 01)
00:07.0 Bridge: Intel Corporation 82371AB/EB/MB PIIX4 ACPI (rev 08)
00:0c.0 USB controller: Intel Corporation 7 Series/C210 Series Chipset Family USB xHCI Host Controller
00:0d.0 SATA controller: Intel Corporation 82801HM/HEM (ICH8M/ICH8M-E) SATA Controller [AHCI mode] (rev 02)
```



## References
*  [YouTube (Linux Crash Course):Easy Terminal Commands for Inspecting Hardware](https://youtu.be/oGyJr-iUwt8?si=Wq5ivxnfVIo9STuf)

* [Definitive Guide to Attaching Sensors to the Raspberry Pi](https://youtu.be/gnE4v-PcYKQ?si=DU5bvBCnMWnaPuVX)

*Egon Teiniker, 2024-2025, GPL v3.0*

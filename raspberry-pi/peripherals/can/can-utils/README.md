# CAN Utils

**can-utils** is a collection of command-line tools for working with **SocketCAN**, 
the Linux kernel's CAN bus interface. It provides utilities for debugging, 
analyzing, and interacting with CAN networks, such as **candump** for monitoring 
CAN messages, **cansend** for sending CAN frames, **cangen** for generating random 
CAN traffic, and **canplayer** for replaying recorded CAN data. 

These tools are essential for developers and engineers working with CAN-based systems, 
enabling efficient testing, diagnostics, and network analysis.


## candump 

`candump` is a command-line tool provided by the `can-utils` package to monitor and 
display CAN messages on a specific CAN interface. It is a useful utility for debugging 
and analyzing CAN bus traffic, especially when working with SocketCAN.

Use Cases:

* **Monitoring Traffic**: Debugging or analyzing messages on a live CAN network.

* **Testing Filters**: Ensure that your CAN ID filters are correctly configured.

* **Troubleshooting**: Identify anomalies or errors in CAN traffic.

* **Performance Analysis**: Track message timestamps to analyze communication timing.

Syntax: 

```bash
$ candump [options] <CAN interface(s)>
```

Where `<CAN interface(s)>` refers to the CAN interfaces you want to monitor, such as 
`can0`, `can1`, etc.


### Dump CAN Messages From an Interface

```bash
$ candump can0
```
This command monitors and displays all CAN messages received on the `can0` 
interface in real-time.


### Monitor Multiple CAN Interfaces

```bash
$ candump can0 can1
```
This command monitors messages on both `can0` and `can1` interfaces simultaneously.


### Output Format

A typical `candump` output line looks like this:

```
 (1605818473.123456)  can0  123   [4]  DE AD BE EF
```
* `(1605818473.123456)`: Timestamp (optional, depending on options).
* `can0`: The CAN interface name.
* `123`: The arbitration ID of the CAN message (in hexadecimal).
* `[4]`: The length of the CAN message data (DLC - Data Length Code).
* `DE AD BE EF`: The CAN message data (in hexadecimal format).


### Log CAN Messages to a File
    
```bash
$ candump can0 -l
```
* `-l`: Log to a file.
* `-L`: log tho the stdout.

The logging format looks like:
```
(1726488365.296423) can0 050#555B
...
```
We can replay these log files using **canplayer**.


### Timestamped Output

Enable timestamps for each message to see when they were received:

```bash
$ candump -t a can0
```
* `-t a`: Prints absolute timestamps.
* `-t d`: Prints delta timestamps (time elapsed since the previous message).
* `-t z`: Prints no timestamps.


### Color-Coded Output

Enable color-coded output for better visibility:

```bash
$ candump -c can0
```


### Set Filters

Filters are used to capture only specific CAN messages.

* **Single Filter**: Monitor messages with a specific CAN ID (e.g., `0x123`):
    ```bash
    $ candump can0,123:7FF
    ```

    - `123` is the CAN ID you want to monitor.
    - `7FF` is the mask. It ensures that only CAN messages with a matching ID are 
        captured. In this case, it monitors all IDs in the range `0x100` to `0x1FF`.

- **Multiple Filters**:
    ```bash
    $ candump can0,123:7FF can0,200:7FF
    ```

    This sets up two filters on `can0`, one for IDs in the range `0x100` to `0x1FF`, 
    and another for IDs in the range `0x200` to `0x2FF`.


### Monitor CAN FD Messages
To monitor CAN FD (Flexible Data-rate) traffic:

```bash
$ candump -x can0
```
- The `-x` option displays CAN FD flags and extended information.


### Stop Monitoring

To stop `candump`, press `Ctrl+C`.


## cansend

**cansend** is a command-line tool provided by the can-utils package that 
allows us to send CAN frames (messages) to a specified CAN interface. 

It is a simple and effective tool for testing and debugging CAN networks 
by **simulating CAN message transmission**.

Use Cases:

* **Testing CAN Nodes**: Verify that devices on the CAN bus respond 
    to specific messages.

* **Simulating CAN Traffic**: Simulate real-world traffic for testing 
    applications or devices.

* **Debugging**: Ensure the CAN interface is functional by sending 
    frames and observing responses.

Syntax: 

```Bash
$ cansend <CAN interface> <CAN ID>#<DATA>
```

* `<CAN interface>`: The CAN interface to use, such as can0.
* `<CAN ID>`: The hexadecimal arbitration ID of the CAN frame.
* `#`: Delimiter between the CAN ID and the data payload.
* `<DATA>`: The data payload of the CAN frame, written in hexadecimal format.


### Send a Standard CAN Frame

To send a CAN frame with a standard **11-bit CAN ID** (0x123) and a data 
payload of DEADBEEF:

```Bash
$ cansend can0 123#DEADBEEF
```

This sends a frame with:

* Arbitration ID: `0x123`
* Data: `DE AD BE EF`
* Data Length: `4` bytes (calculated from the data provided).


### Send a Frame with No Data

To send a CAN frame with only an ID and no data:

```Bash
$ cansend can0 123#
```

This is useful for sending remote request frames (RTR) or testing.


### Send a Frame with Specific Data Length

The data payload can be padded to a specific length by **adding zeros**. 

For example, to send an 8-byte frame:

```Bash
$ cansend can0 123#DEADBEEF00000000
```

This sends:

Arbitration ID: `0x123`
Data: `DE AD BE EF 00 00 00 00`
Data Length: `8` bytes.


### Send an Extended CAN Frame

For an extended **29-bit CAN ID**, use an 8 hex chars as ID:

```Bash
$ cansend can0 12345678#DEADBEEF
```

This sends an extended frame with:

Extended Arbitration ID: `0x12345678`
Data: `DE AD BE EF`


### Examples

_Example:_ Send single CAN messages

```Bash
$ cansend can0 123+1122334455667788
```


## cangen

**cangen** is a command-line tool included in the can-utils package that 
**generates and sends random CAN frames** (messages) to a specified CAN 
interface. 

It is particularly useful for stress testing, benchmarking, and debugging 
CAN networks by simulating a high volume of traffic.

Syntax:

```Bash
$ cangen <CAN interface> [options]
```

* `<CAN interface>`: The name of the CAN interface (e.g., `can0`).
* `[options]`: Optional parameters to control the behavior of the message generation.

    | Option      | Description                                                                 |
    |-------------|-----------------------------------------------------------------------------|
    | `-e`        | Generate extended CAN frames (29-bit IDs).                                 |
    | `-L`        | Randomize data length (DLC).                                               |
    | `-D <len>`  | Set fixed data length (e.g., `-D 8` for 8 bytes).                          |
    | `-g <ms>`   | Set the gap (interval) between frames in milliseconds.                     |
    | `-p <data>` | Use a fixed data payload (e.g., `-p 11223344` for specific byte values).    |
    | `-I`        | Randomize the CAN IDs.                                                     |
    | `-b`        | Enable burst mode (generate multiple frames rapidly).                      |


Use Cases:

* **Stress Testing**: Simulate high traffic loads to test the robustness of 
    the CAN network.

* **Performance Benchmarking**: Evaluate the performance of CAN devices under 
    heavy traffic.

* **Device Debugging**: Test how a CAN node behaves under random traffic 
    conditions.

* **Network Validation**: Identify potential issues in CAN bus communication 
    under various scenarios.

### Generate Random Standard CAN Frames

```Bash
$ cangen can0
```

This generates random CAN frames with:

* Standard 11-bit CAN IDs.
* Random data payloads.
* Random data length (DLC).


### Generate Extended CAN Frames

To generate random extended **(29-bit) CAN IDs**:

```Bash
$ cangen can0 -e
```

The `-e` flag enables extended frame generation.


### Control Data Length

To fix the length of the data payload in all generated frames:

```Bash
$ cangen can0 -D 8
```

This sets the data payload length to 8 bytes.

Alternatively, we can randomize the data length:

```Bash
$ cangen can0 -L
```

The `-L` flag randomizes the data length for each frame.


### Control the Frame Generation Rate

To limit the number of frames sent per second, use the `-g` (gap) option:

```Bash
$ cangen can0 -g 100
```

This introduces a **gap of 100 milliseconds between each frame**.

For high-speed frame generation with **minimal delay**:

```Bash
$ cangen can0 -g 0
```

### Set Custom Data

You can specify a fixed data payload for all generated frames:

```Bash
$ cangen can0 -p 1122334455667788
```

This sets the payload to `11 22 33 44 55 66 77 88`.


### Generate Frames for Stress Testing

To flood the CAN bus with traffic for stress testing:

```Bash
$ cangen can0 -g 0 -e -D 8
```

This sends extended frames `-e` with an 8-byte payload `-D 8` as fast as possible `-g 0`.


## cansniffer

**cansniffer** is a command-line tool from the can-utils package that monitors 
and displays CAN messages on a specified interface in real-time. 

Unlike candump, which passively dumps all CAN traffic, cansniffer provides a more 
**dynamic and focused view of CAN bus activity by grouping, filtering, and 
highlighting changes in CAN message data**. 

This makes it particularly useful for debugging and analyzing active CAN networks.

Syntax:

```Bash
$ cansniffer [options] <CAN interface>
```

* `<CAN interface>`: The CAN interface to monitor, such as can0.
* `[options]`: Additional flags to customize the behavior of cansniffer.

    | **Option**       | **Description**                                                                                         |
    |-------------------|---------------------------------------------------------------------------------------------------------|
    | `-c `            | Color changes
    | `-e`              | Enables monitoring of extended (29-bit) CA IDs                                                        |
    | `-t <time>`         | Timeout for ID display (x10ms) default: 500                      |
    | `-h <time>`         | Hold marker on changes (x10ms) default: 100                      |    
    | `-l <time>`         | Loop time (display) (x10ms) default: 20                      |
    | `-b`              | Start with binary mode                                      |

Use Cases:

* **Dynamic Data Analysis**: Quickly identify which bytes in CAN 
    messages are changing.

* **Reverse Engineering**: Monitor and analyze proprietary CAN messages 
    (e.g., vehicle diagnostics).

* **Debugging**: Spot irregular or unexpected changes in CAN traffic.

* **Testing Devices**: Verify if a specific device is sending/receiving 
    the expected data on the CAN bus.


### Monitor CAN Messages

To start monitoring CAN traffic on can0:

```Bash
$ cansniffer -t 0 -c can0
```

This displays all received CAN messages, grouped by their IDs. 
Each row represents a unique CAN ID, showing the latest data bytes 
and highlighting changes in real time.


### Output Format

A typical cansniffer output line looks like this:

```Bash
  can0  123   [8]  DE AD BE EF 00 00 00 01
```

* `can0`: CAN interface name.
* `123`: CAN ID (arbitration ID).
* `[8]`: Data Length Code (DLC).
* `DE AD BE EF 00 00 00 01`: Data bytes (highlighted if changes occur).


### Interactive Mode
cansniffer allows interactive filtering while running:

* Press `+` to add a CAN ID to the display.
* Press `-` to remove a CAN ID from the display.
* Press `q` to quit the tool.


### Highlight Changes

Using the `-c` flag, **cansniffer** automatically highlights data bytes that 
change during runtime:

* Bytes that have changed are highlighted or bolded (depending on the 
    terminal's capabilities).
* This helps you quickly identify which parts of the CAN messages are 
    dynamic.


### Ignore Certain Messages

To suppress specific CAN IDs or a range of IDs, use the `-i` option:

```Bash
$ cansniffer -i 300:3FF can0
```

This ignores all messages with IDs from `0x300` to `0x3FF`.


### Monitor Extended CAN IDs

If your network uses extended **(29-bit) CAN IDs**, enable them with 
the `-e` flag:

```Bash
$ cansniffer -e can0
```

### Stop Monitoring

To exit cansniffer, press `Ctrl+C` or use the interactive quit key `q`.


### candump vs. cansniffer

* Use **candump** to first understand the overall traffic on the bus.

* Switch to **cansniffer** for a more focused and interactive analysis 
    of message contents.


## canplayer

**canplayer** is a tool in the can-utils package that **replays previously 
recorded CAN traffic on a CAN interface**. 

It reads log files or streams that contain recorded CAN messages and sends 
them back onto the specified CAN network. 

This tool is especially useful for testing, simulation, and reproducing 
specific CAN traffic patterns to debug or analyze a system.

Syntax:

```Bash
$ canplayer [options] <logfile>
```

* `<logfile>`: The file containing recorded CAN traffic (usually in candump 
    log format).
* `[options]`: Optional parameters to customize the playback behavior.

    | Option         | Description                                                                   |
    |----------------|-------------------------------------------------------------------------------|
    | `-I <file>`    | Specify the input log file in `candump` format.                              |
    | `-l`           | Replay the log file in a continuous loop.                                    |
    | `-x <factor>`  | Adjust replay speed (e.g., `0.5` for faster, `2` for slower).                |
    | `-f <filter>`  | Apply a filter to replay only specific CAN IDs (e.g., `123:7FF`).            |
    | `-g <ms>`      | Set a fixed gap (delay) between messages (e.g., `-g 0` for no delay).        |


Use Cases:

* **Testing and Debugging**:
    * Replay recorded CAN traffic to test how devices react to specific 
        message sequences.
    * Simulate a real-world CAN environment for debugging applications.

* **Reproducing Issues**:
    Replay captured traffic to reproduce bugs or issues in a controlled 
    environment.
    
* **Performance Testing**:
    Stress test a system by looping or modifying the speed of replayed 
    messages.

* **System Validation**:
    Verify that a system behaves as expected when subjected to recorded 
    CAN traffic.


### Basic Replay of a Recorded Log

Replay a log file `logfile.log` on a CAN interface:

```Bash
$ canplayer -I logfile.log
```

* The `-I` option specifies the input log file in candump format.
* Messages will be replayed with the same timing as recorded in the log.


### Input Log File Format

The log file used by canplayer is typically in candump format. 
An example log looks like this:

```
(1609459200.123456) can0 123#DEADBEEF
(1609459201.234567) can0 124#CAFE0102
(1609459201.234567) can0 124#CAFE0102
```

* `(1609459200.123456)`: Timestamp of the message.
* `can0`: CAN interface name.
* `123#DEADBEEF`: CAN frame with ID 0x123 and data payload DE AD BE EF.


### Replay with a Modified Speed

To speed up the replay (e.g., 2x faster than the original timing):

```Bash
$ canplayer -I logfile.log -x 0.5
```

The `-x` option is a timing factor. A value of `0.5` doubles the speed, 
while `2` slows it down by half.


### Continuous Replay (Looping)

To continuously replay the log file in a loop:

```Bash
$ canplayer -I logfile.log -l
```

The `-l´ option enables looping.


### Replay Only Specific CAN IDs

To replay only messages with a specific CAN ID (0x123):

```Bash
$ canplayer -I logfile.log -f 123:7FF
```

The `-f` option sets a filter to replay only messages matching 
the specified CAN ID `0x123` and mask `0x7FF`.


###  Replay with Modified Timestamps

To ignore timestamps in the log file and replay messages as fast as possible:

```Bash
$ canplayer -I logfile.log -g 0
```

The `-g` option specifies the delay between messages. 
A value of `0` means no delay.


### Use Multiple CAN Interfaces

To replay a log file and redirect messages to multiple CAN interfaces 
(e.g., `can0` and `can1`):

```Bash
$ canplayer -I logfile.log can0 can1
```

This sends the replayed messages to both `can0` and `can1`.



## References

* [YouTube: Can-utils Candump Explained. CANbus communications 101](https://youtu.be/ef4akXEDKOQ?si=GwlNYUzHJSh5MjEx)

* [YouTube: Hacking my Roommates Car - Linux CAN Bus sniffing](https://youtu.be/LnDq5oujfK0?si=jAYqHWEbaBEfP3mb)

* [Manpages of can-utils in Debian testing](https://manpages.debian.org/testing/can-utils/index.html)

*Egon Teiniker, 2024-2025, GPL v3.0*

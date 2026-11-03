# Controller Area Network Protocol

The **Controller Area Network (CAN)** was developed by **Robert Bosch GmbH** in
the 1980s to reduce the amount of wiring in vehicles. Instead of connecting
every control unit with every other one point-to-point, all **nodes** (ECUs,
sensors, actuators, ...) share a **single two-wire bus**. Today CAN is
standardized in **ISO 11898** and is used in cars, trucks, industrial
automation, medical devices, and many embedded systems.

Key properties of CAN:

* **Multi-master**: Every node may start a transmission when the bus is idle.
  There is no central bus master.

* **Message-oriented (broadcast)**: Frames do not contain a sender or receiver
  address. Instead, each frame carries an **identifier (ID)** that describes
  the **content** of the message (e.g. "engine speed"). All nodes receive
  every frame and decide (via acceptance filters) whether it is relevant.

* **Priority-based arbitration**: The identifier also defines the **priority**
  of a message. The lower the ID value, the higher the priority. Collisions
  are resolved **without losing data or time** (non-destructive arbitration).

* **Robust error handling**: CRC, acknowledge, bit monitoring, bit stuffing
  and form checks detect errors. Faulty frames are automatically
  retransmitted, and defective nodes switch themselves off the bus
  (**fault confinement**).

* **Differential signaling** on a twisted pair makes the bus resistant to
  electromagnetic interference.

Protocol versions:

| Version                 | Identifier         | Payload         | Bit rate                       |
|-------------------------|--------------------|-----------------|--------------------------------|
| CAN 2.0A (Standard)     | 11 bit             | 0 - 8 bytes     | up to 1 Mbit/s                 |
| CAN 2.0B (Extended)     | 29 bit             | 0 - 8 bytes     | up to 1 Mbit/s                 |
| CAN FD (Flexible Data)  | 11 or 29 bit       | 0 - 64 bytes    | up to 1 Mbit/s arbitration, up to ~8 Mbit/s data phase |

The Bosch specification describes CAN in the following layers:

```
+----------------------------+
|     Application Layer      |   messages, identifiers, payload meaning
+----------------------------+
|      Transfer Layer        |   framing, arbitration, error detection, ACK
+----------------------------+
|      Physical Layer        |   bit timing, signal levels, cable, termination
+----------------------------+
```

Note that the CAN standard only defines the lower layers. The meaning of IDs
and payload bytes is defined by **higher-layer protocols** such as
**CANopen**, **J1939** (trucks), **ISO-TP / UDS** (vehicle diagnostics), or
simply by a project-specific message catalog (often stored as a **DBC file**).


## Application Layer

From the application's point of view, a CAN message consists of:

* an **identifier** (11 or 29 bit), which describes the content and priority,
* a **data length code (DLC)**, which gives the number of payload bytes (0-8),
* up to **8 data bytes** (64 bytes for CAN FD).

### Frame Types

| Frame type         | Purpose                                                          |
|--------------------|------------------------------------------------------------------|
| **Data frame**     | Transports data from a transmitter to all receivers.             |
| **Remote frame**   | Requests a data frame with the same ID from another node (RTR=1). |
| **Error frame**    | Sent by any node that detects an error on the bus.               |
| **Overload frame** | Requests an extra delay between two frames (rarely used).        |

### Standard Data Frame (CAN 2.0A)

```
 1    11          1   1   1    4        0..64        15       1   1   1    7      3
+---+------------+---+---+---+------+-------------+---------+---+---+---+-------+-----+
|SOF| Identifier |RTR|IDE|r0 | DLC  |    Data     |   CRC   |CD |ACK|AD |  EOF  | IFS |
+---+------------+---+---+---+------+-------------+---------+---+---+---+-------+-----+
    |<- Arbitration->|<-Control--->|<-- Data --->|<-- CRC -->|<- ACK ->|
```

| Field                    | Bits   | Description                                                        |
|--------------------------|--------|--------------------------------------------------------------------|
| **SOF** (Start of Frame) | 1      | Dominant bit, marks the start of a frame and synchronizes all nodes. |
| **Identifier**           | 11     | Message ID; defines content and priority (lower = higher priority). |
| **RTR** (Remote Transmission Request) | 1 | Dominant (0) for a data frame, recessive (1) for a remote frame. |
| **IDE** (Identifier Extension) | 1 | Dominant (0) for an 11-bit ID, recessive (1) for a 29-bit ID.     |
| **r0**                   | 1      | Reserved bit.                                                      |
| **DLC** (Data Length Code) | 4    | Number of data bytes (0-8).                                        |
| **Data**                 | 0-64   | Payload (0-8 bytes).                                               |
| **CRC**                  | 15     | Cyclic redundancy check over SOF ... Data.                         |
| **CD** (CRC Delimiter)   | 1      | Always recessive.                                                  |
| **ACK** slot             | 1      | Sent recessive by the transmitter; every receiver that received the frame correctly overwrites it with a dominant bit. |
| **AD** (ACK Delimiter)   | 1      | Always recessive.                                                  |
| **EOF** (End of Frame)   | 7      | 7 recessive bits.                                                  |
| **IFS** (Interframe Space) | 3    | At least 3 recessive bits before the next frame may start.         |

### Extended Data Frame (CAN 2.0B)

In an extended frame, the identifier is split into an **11-bit base ID** and
an **18-bit ID extension**:

```
+---+-------------+---+---+-----------------+---+---+---+-----+------+-----+...
|SOF| Base ID(11) |SRR|IDE| ID Extension(18)|RTR|r1 |r0 | DLC | Data | CRC |...
+---+-------------+---+---+-----------------+---+---+---+-----+------+-----+...
```

The **SRR** (Substitute Remote Request) and **IDE** bits are recessive. Since
the IDE bit of a standard frame is dominant, a **standard frame always wins
arbitration** against an extended frame with the same base ID.

### Bit Stuffing

To keep all nodes synchronized, the transmitter inserts a **complementary
bit** after **5 consecutive bits of the same level** (from SOF to the end of
the CRC). Receivers remove these stuff bits automatically. Six equal bits in
a row therefore indicate an error (this is exactly how error frames work:
they consist of 6 dominant bits).

```
Original:  0 0 0 0 0 0 1 1 1 1 1 1 1
Stuffed:   0 0 0 0 0 1 0 1 1 1 1 0 1 1
                     ^           ^
                     stuff bits
```

### CAN Frames in Linux (SocketCAN)

In SocketCAN, a classical CAN frame is represented by `struct can_frame`
(`<linux/can.h>`):

```C
struct can_frame {
    canid_t can_id;  /* 32 bit CAN_ID + EFF/RTR/ERR flags */
    __u8    len;     /* frame payload length in bytes (0 .. 8), formerly can_dlc */
    __u8    __pad;
    __u8    __res0;
    __u8    len8_dlc;
    __u8    data[8] __attribute__((aligned(8)));
};
```

The upper bits of `can_id` are used as flags: `CAN_EFF_FLAG` (extended
frame), `CAN_RTR_FLAG` (remote frame) and `CAN_ERR_FLAG` (error frame).
SOF, CRC, ACK, EOF and stuff bits are handled by the CAN controller hardware
and are not visible to the application.

The `can-utils` tools use a compact notation for frames:

```
$ cansend can0 123#DEADBEEF        # standard ID 0x123, 4 data bytes
$ cansend can0 12345678#1122       # extended ID 0x12345678, 2 data bytes
$ cansend can0 123#R               # remote frame with ID 0x123
```


## Transfer Layer

### Dominant and Recessive Bits

On the CAN bus, the two logical levels are not equal:

* **Dominant** = logical **0**
* **Recessive** = logical **1**

If one node sends a dominant bit and another node sends a recessive bit at
the same time, the bus shows a **dominant** bit. Electrically, the bus
behaves like a **wired-AND**: the bus is only recessive if **all** nodes send
recessive.

| Node A    | Node B    | Bus level |
|-----------|-----------|-----------|
| 1 (rec.)  | 1 (rec.)  | 1 (rec.)  |
| 1 (rec.)  | 0 (dom.)  | 0 (dom.)  |
| 0 (dom.)  | 1 (rec.)  | 0 (dom.)  |
| 0 (dom.)  | 0 (dom.)  | 0 (dom.)  |

### Bitwise Arbitration (CSMA/CR)

CAN uses **CSMA/CR** (Carrier Sense Multiple Access with **Collision
Resolution**), sometimes also called CSMA/CD+AMP (Arbitration on Message
Priority):

1. **Carrier sense**: A node only starts sending when the bus is idle
   (at least 11 recessive bits, i.e. after EOF and IFS).

2. **Multiple access**: Several nodes may start sending at exactly the same
   time (synchronized by the SOF bit).

3. **Collision resolution**: While sending the **identifier** (arbitration
   field), every transmitter **reads back** each bit from the bus. If a node
   sends a **recessive** bit but reads a **dominant** bit, it has **lost
   arbitration**. It immediately stops transmitting and becomes a receiver.

4. The node with the **lowest identifier** (the most leading dominant bits)
   wins and transmits its frame **without any delay or corruption**. The
   losing nodes automatically retry as soon as the bus is idle again.

Example: Three nodes start transmitting at the same time:

```
Bit:            SOF 10  9  8  7  6  5  4  3  2  1  0
Node A (0x65A):  0   1  1  0  0  1  0  1  1  0  1  0
Node B (0x64F):  0   1  1  0  0  1  0  0  1  1  1  1
Node C (0x65F):  0   1  1  0  0  1  0  1  1  1  1  1
-------------------------------------------------------
Bus:             0   1  1  0  0  1  0  0  1  1  1  1
```

* Bits 10 to 5 are identical for all nodes, so nobody notices a collision.
* At **bit 4**, nodes A and C send recessive (1), node B sends dominant (0).
  The bus is dominant, so **A and C lose arbitration** and stop sending.
* **Node B (0x64F)** has the lowest ID and continues transmitting its
  frame as if no collision had happened.

Consequences:

* Each identifier must be **unique** on a bus (only one node may send a
  given ID), otherwise two nodes could both "win" and later collide in the
  data field, which leads to an error.

* High priority messages (low IDs) have a **deterministic, bounded latency**,
  while low priority messages may have to wait when the bus load is high.

### Acknowledge

The transmitter sends the ACK slot as recessive. **Every** node that has
received the frame correctly (CRC OK) writes a dominant bit into the ACK
slot. If the transmitter reads back a recessive ACK bit, no node has received
the frame, and the transmitter signals an **ACK error** and retransmits the
frame. A single node on a bus (without a second node to acknowledge) will
therefore keep retransmitting its first frame.

### Error Detection and Fault Confinement

CAN detects errors with five mechanisms:

| Error             | Detected by   | Description                                              |
|-------------------|---------------|----------------------------------------------------------|
| **Bit error**     | Transmitter   | The bit read back differs from the bit sent (outside arbitration and ACK slot). |
| **Stuff error**   | Receiver      | Six consecutive bits with the same level.                |
| **CRC error**     | Receiver      | The calculated CRC does not match the received CRC.      |
| **Form error**    | Receiver      | A fixed-format field (delimiter, EOF) contains an illegal bit. |
| **ACK error**     | Transmitter   | No node acknowledged the frame.                          |

A node that detects an error sends an **error frame** (6 dominant bits),
which intentionally violates the bit stuffing rule, so all other nodes also
discard the current frame. The transmitter then **retransmits** the frame
automatically.

To prevent a defective node from blocking the bus, each node maintains a
**Transmit Error Counter (TEC)** and a **Receive Error Counter (REC)**.
Errors increase the counters, successful transmissions decrease them:

```
               TEC or REC > 127               TEC > 255
 +--------------+  ---------->  +---------------+  ------->  +---------+
 | Error Active |               | Error Passive |            | Bus Off |
 +--------------+  <----------  +---------------+            +---------+
               TEC and REC < 128                                   |
        ^                                                           |
        +-------- 128 x 11 recessive bits (and restart) ------------+
```

* **Error active**: Normal state; the node sends active error frames
  (6 dominant bits).
* **Error passive**: The node only sends passive error frames (6 recessive
  bits) and must wait longer before retransmitting, so it cannot disturb
  the bus anymore.
* **Bus off**: The node is disconnected from the bus. In Linux, the
  interface can be restarted automatically with
  `ip link set can0 type can restart-ms 100`.

The current state and counters can be inspected with:

```
$ ip -details -statistics link show can0
```


## Physical Layer

### Controller and Transceiver

A CAN node consists of:

* a **microcontroller / host** (e.g. the Raspberry Pi),
* a **CAN controller** which implements the transfer layer (framing,
  arbitration, CRC, error handling), e.g. the **MCP2515** (connected via
  SPI) or a controller integrated in a microcontroller,
* a **CAN transceiver** which converts the logic signals (TX/RX) of the
  controller into the differential bus signals, e.g. **SN65HVD230**
  (3.3 V) or **MCP2551 / TJA1050** (5 V).

```
 +--------------+   SPI   +----------------+  TX/RX  +-------------+
 | Raspberry Pi | <-----> | CAN controller | <-----> | Transceiver | ==== CAN_H
 |              |   INT   |   (MCP2515)    |         | (SN65HVD230)| ==== CAN_L
 +--------------+ <------ +----------------+         +-------------+
```

### Wiring and Topology

The bus consists of two wires, **CAN_H** (CAN High) and **CAN_L** (CAN Low),
usually as a **twisted pair** (often shielded), plus a common **GND**
reference. All nodes are connected in a **line (bus) topology** with only
short stubs to each node.

```
 120 Ω                                                        120 Ω
+-/\/\-+                                                     +-/\/\-+
|      |                                                     |      |
CAN_H ---+-------------+-------------+-------------+---------+ CAN_H
         |             |             |             |
CAN_L ---+-------------+-------------+-------------+---------+ CAN_L
         |             |             |             |
      +------+      +------+      +------+      +------+
      |Node 1|      |Node 2|      |Node 3|      |Node 4|
      +------+      +------+      +------+      +------+
```

### Signal Levels (High-Speed CAN, ISO 11898-2)

The information is transmitted as the **voltage difference** between CAN_H
and CAN_L (differential signaling). Interference affects both wires equally
and is cancelled out by the receiver.

| Bus state              | CAN_H    | CAN_L    | V_diff = CAN_H - CAN_L |
|------------------------|----------|----------|------------------------|
| **Recessive** (1, idle)| ~2.5 V   | ~2.5 V   | ~0 V  (< 0.5 V)        |
| **Dominant** (0)       | ~3.5 V   | ~1.5 V   | ~2 V  (> 0.9 V)        |

```
        recessive   dominant   recessive   dominant   recessive
 3.5 V             +---------+           +---------+                CAN_H
 2.5 V ------------+         +-----------+         +------------    CAN_H / CAN_L
 1.5 V             +---------+           +---------+                CAN_L
```

In the recessive state, the transceivers do not drive the bus; the
termination resistors pull both lines to the same level. In the dominant
state, a transceiver actively drives CAN_H up and CAN_L down. This is the
reason why a dominant bit always overwrites a recessive bit.

### Termination Resistors

Each **end** of the bus must be terminated with a **120 Ω** resistor between
CAN_H and CAN_L (matching the characteristic impedance of the cable):

* The termination **prevents signal reflections** at the cable ends.
* It pulls the bus back to the recessive state when no node drives it.

Only the two physical ends of the bus are terminated, not every node. Many
CAN HATs and adapters provide a jumper or switch to enable their 120 Ω
resistor.

A quick check: with the **power switched off**, measure the resistance
between CAN_H and CAN_L:

| Measured value | Meaning                                       |
|----------------|-----------------------------------------------|
| ~60 Ω          | Correct (two 120 Ω resistors in parallel)     |
| ~120 Ω         | Only one termination resistor                 |
| ~40 Ω or less  | Too many termination resistors                |
| open / very high | No termination                              |

### Bit Rate and Bus Length

All nodes on a bus must use the **same bit rate**. Since every node must see
each bit (including the dominant ACK bit of the farthest node) within one bit
time, the maximum bus length depends on the bit rate (signal propagation
delay of approx. 5 ns/m):

| Bit rate     | Max. bus length (approx.) |
|--------------|---------------------------|
| 1 Mbit/s     | 40 m                      |
| 500 kbit/s   | 100 m                     |
| 250 kbit/s   | 250 m                     |
| 125 kbit/s   | 500 m                     |
| 50 kbit/s    | 1000 m                    |

### Bit Timing

CAN has no separate clock line. Each bit time is divided into **time
quanta (tq)** and the receivers resynchronize on recessive-to-dominant
edges:

```
|<-------------------------- 1 bit time ------------------------->|
+---------+-----------------+------------------+-------------------+
|  Sync   |  Propagation    |  Phase Segment 1 |  Phase Segment 2  |
|  1 tq   |    Segment      |                  |                   |
+---------+-----------------+------------------+-------------------+
                                               ^
                                         Sample point
                                       (typically 75 - 87.5 %)
```

In Linux, the bit rate (and optionally the sample point) is set when the
interface is brought up; the driver calculates the segment lengths:

```
$ sudo ip link set can0 up type can bitrate 500000 sample-point 0.875
```


## References

* [YouTube (Hardwire Electronics): CAN Bus: A Beginners Guide Part 1](https://youtu.be/YBrU_eZM110?si=h0w9qiuRXwpP_lGI)

* [YouTube (Hardwire Electronics):](CAN Bus: A Beginners Guide Part 2)(https://youtu.be/z5CVljiLhvc?si=bjL7kD0CVmatNLWG)

* [YouTube (Inside Embedded | Polezero): Everything About CAN Bus | CAN Protocol Explained: Arbitration, Frames, CAN FD](https://youtu.be/aAR7xyTaXIo?si=ca5--SnVs3RSvFms)

* Robert Bosch GmbH: [CAN Specification Version 2.0](http://esd.cs.ucr.edu/webres/can20.pdf), 1991


*Egon Teiniker, 2025-2026, GPL v3.0*

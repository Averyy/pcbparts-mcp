---
source: "ADI -- Fundamentals of RS-232 Serial Communications"
url: "https://www.analog.com/en/resources/technical-articles/fundamentals-of-rs232-serial-communications.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 25857
---

# Fundamentals of RS-232 Serial Communications

## Abstract

Due to its relative simplicity and low hardware overhead (when compared to parallel interfacing), serial communications is used extensively within the electronics industry. Today, the most popular serial communications standard is certainly the EIA/TIA-232-E specification. This standard, which was developed by the Electronic Industry Association and the Telecommunications Industry Association (EIA/TIA), is more popularly called simply RS-232, where RS stands for \"recommended standard.\" Although this RS prefix has been replaced in recent years with EIA/TIA to help identify the source of the standard, this paper uses the common RS-232 notation.

## Introduction

The official name of the EIA/TIA-232-E standard is "Interface Between Data Terminal Equipment and Data Circuit-Termination Equipment Employing Serial Binary Data Interchange." Although the name may sound intimidating, the standard is simply concerned with serial data communication between a host system (Data Terminal Equipment, or DTE) and a peripheral system (Data Circuit-Terminating Equipment, or DCE).

The EIA/TIA-232-E standard was introduced in 1962 and has since been updated four times to meet the evolving needs of serial communication applications. The letter "E" in the standard's name indicates that this is the fifth revision of the standard.

## RS-232 Specifications

RS-232 is a complete standard. This means that the standard sets out to ensure compatibility between the host and peripheral systems by specifying:

1. Common voltage and signal levels
2. Common pin-wiring configurations
3. A minimal amount of control information between the host and peripheral systems.

Unlike many standards which simply specify the electrical characteristics of a given interface, RS-232 specifies electrical, functional, and mechanical characteristics to meet the above three criteria. Each of these aspects of the RS-232 standard is discussed below.

## Electrical Characteristics

The electrical characteristics section of the RS-232 standard specifies voltage levels, rate of change for signal levels, and line impedance.

As the original RS-232 standard was defined in 1962 and before the days of TTL logic, it is no surprise that the standard does not use 5V and ground logic levels. Instead, a high level for the driver output is defined as between +5V to +15V, and a low level for the driver output is defined as between -5V and -15V. The receiver logic levels were defined to provide a 2V noise margin. As such, a high level for the receiver is defined as between +3V to +15V, and a low level is between -3V to -15V. Figure 1 illustrates the logic levels defined by the RS-232 standard. It is necessary to note that, for RS-232 communication, a low level (-3V to -15V) is defined as a logic 1 and is historically referred to as "marking." Similarly, a high level (+3V to +15V) is defined as a logic 0 and is referred to as "spacing."

Figure 1. RS-232 logic-level specifications.

The RS-232 standard also limits the maximum slew rate at the driver output. This limitation was included to help reduce the likelihood of crosstalk between adjacent signals. The slower the rise and fall time, the less chance of crosstalk. With this in mind, the maximum slew rate allowed is 30V/ms. Additionally, standard defines a maximum data rate of 20kbps , again to reduce the chance of crosstalk.

The impedance of the interface between the driver and receiver has also been defined. The load seen by the driver is specified at 3kΩ to 7kΩ. In the original RS-232 standard the cable length between the driver and receiver was specified to be 15 meters maximum. Revision "D" (EIA/TIA-232-D) changed this part of the standard . Instead of specifying the maximum length of cable, the standard specified a maximum capacitive load of 2500pF, clearly a more adequate specification. The maximum cable length is determined by the capacitance per unit length of the cable, which is provided in the cable specifications.

Table 1 summarizes the electrical specifications in the current standard.

Table 1. RS-232 Specifications

|  |  |
| --- | --- |
| Cabling | Single-ended |
| Number of Devices | 1 transmit, 1 receive |
| Communication Mode | Full duplex |
| Distance (max) | 50 feet at 19.2kbps |
| Data Rate (max) | 1Mbps |
| Signaling | Unbalanced |
| Mark (data 1) | -5V (min) -15V (max) |
| Space (data 0) | 5V (min) 15V (max) |
| Input Level (min) | ±3V |
| Output Current | 500mA (Note that the driver ICs normally used in PCs are limited to 10mA) |
| Impedance | 5kΩ (Internal) |
| Bus Architecture | Point-to-Point |

## Functional Characteristics

Because RS-232 is a complete standard, it includes more than just specifications on electrical characteristics. The standard also addresses the functional characteristics of the interface, #2 on our list above. This essentially means that RS-232 defines the function of the different signals used in the interface. These signals are divided into four different categories: common, data, control, and timing. See Table 2. The standard provides abundant control signals and supports a primary and secondary communications channel. Fortunately few applications, if any, require all these defined signals. For example, only eight signals are used for a typical modem. Examples of how the RS-232 standard is used in real-world applications are discussed later. The complete list of defined signals is included here as a reference. Reviewing the functionality of all these signals is, however, beyond the scope of this paper.

Table 2. RS-232 Defined Signals

|  |  |  |  |
| --- | --- | --- | --- |
| AB | Signal Common | — | Common |
| BA  BB | Transmitted Data (TD)  Received Data (RD) | To DCE  From DCE | Data |
| CA  CB  CC  CD  CE  CF  CG  CH  CI  CJ  RL  LL  TM | Request to Send (RTS)  Clear to Send (CTS)  DCE Ready (DSR)  DTE Ready (DTR)  Ring Indicator (RI)  Received Line Signal Detector\*\* (DCD)  Signal Quality Detector  Data Signal Rate Detector from DTE  Data Signal Rate Detector from DCE  Ready for Receiving  Remote Loopback  Local Loopback  Test Mode | To DCE  From DCE  From DCE  To DCE  From DCE  From DCE  From DCE  To DCE  From DCE  To DCE  To DCE  To DCE  From DCE | Control |
| DA | ransmitter Signal Element Timing from DTE | To DCE |  |
| DB  DD | Transmitter Signal Element Timing from DCE  Receiver Signal Element Timing from DCE | From DCE  From DCE | Timing |
| SBA  SBB | Secondary Transmitted Data  Secondary Received Data | To DCE  From DCE | Data |
| SCA  SCB  SCF | Secondary Request to Send  Secondary Clear to Send  Secondary Received Line Signal Detector | To DCE  From DCE  From DCE | Control |
| \*Signals with abbreviations in parentheses are the eight most commonly used signals.  \*\*This signal is more commonly referred to as Data Carrier Detect (DCD). | | | |

## Mechanical Interface Characteristics

The third area covered by RS-232 is the mechanical interface. Specifically, RS-232 specifies a 25-pin connector as the minimum connector size that can accommodate all the signals defined in the functional portion of the standard. The pin assignment for this connector is shown in Figure 2. The connector for DCE equipment is male for the connector housing and female for the connection pins. Likewise, the DTE connector is a female housing with male connection pins. Although RS-232 specifies a 25-position connector, this connector is often not used. Most applications do not require all the defined signals, so a 25-pin connector is larger than necessary. Consequently, other connector types are commonly used. Perhaps the most popular connector is the 9-position DB9S connector, also illustrated in Figure 2. This 9-position connector provides, for example, the means to transmit and receive the necessary signals for modem applications. This type pf application will be discussed in greater detail later.

Figure 2. RS-232 connector pin assignments.

## Evolution of RS-232 IC Design

#### Regulated Charge Pumps

The original MAX232 Driver/Receiver and its related parts simply doubled and inverted the input voltage to supply the RS-232 driver circuitry. This design enabled much more voltage than actually required; it wasted power. The EIA-232 levels are defined as ±5V into 5kΩ. With a new low-dropout output stage, Maxim introduced RS-232 transceivers with internal charge pumps that provided regulated ±5.5V outputs. This design allows the transmitter outputs to maintain RS-232-compatible levels with a minimum amount of supply current.

#### Low-Voltage Operation

The reduced output voltages of the new regulated charge pumps and low-dropout transmitters allow use of reduced supply voltages. Most of Maxim's recent RS-232 transceivers operate with supply voltages down to +3.0V.

#### AutoShutdown™

In the never-ending battle to extend battery life, Maxim pioneered a technique called auto-shutdown. When the device is not detecting valid RS-232 activity, it enters a low-power shutdown mode. An RS-232-valid output indicates to the system processor whether an active RS-232 port is connected at the other end of the cable. The MAX3212 goes one step further: it includes a transition-detect circuit whose latched output, applied as an interrupt, can awaken the system when a change of state occurs on any incoming line.

#### AutoShutdown Plus™

Building on the success of AutoShutdown, devices with Maxim's AutoShutdown Plus capability achieve a 1µA supply current. These devices automatically enter a low-power shutdown mode either when the RS-232 cable is disconnected or the transmitters of the connected peripherals are inactive, or when the UART driving the transmitter inputs is inactive for more than 30 seconds. The devices turn on again when they sense a valid transition at any transmitter or receiver input. AutoShutdown Plus saves power without changes to the existing BIOS or operating system.

#### MegaBaud

Moving beyond the EIA-232 specification is megabaud mode, which allows the driver slew rate to increase, thereby providing data rates up to 1Mbps. MegaBaud mode is useful for communication between high-speed peripherals such DSL or ISDN modems over short distances.

#### High ESD

Some ICs are designed to provide high ESD protection. These ICs specify and achieve ±15kV ESD protection using both the human body model and the IEC 801-2 air-gap discharge method. Maxim's high-ESD protection eliminates the need for costly external protection devices such as TransZorbs™, while preventing expensive field failures.

## Support Issues

#### Capacitor Selection

The charge pumps of Maxim RS-232 transceivers rely on capacitors to convert and store energy, so choosing these capacitors affects the circuit's overall performance. Although some data sheets indicate polarized capacitors in their typical application circuits, this information is shown only for a customer who wants to use polarized capacitors. In practice, ceramic capacitors work best for most Maxim RS-232 ICs.

Choosing the ceramic capacitor is also important. Capacitor dielectric types of Z5U and Y5V are unacceptable because of their incredible voltage and temperature coefficients. Types X5R and X7R provide the necessary performance.

#### Unused Inputs

RS-232 receiver inputs contain an internal 5kΩ pull-down resistor. If this receiver input is unused, it can be left floating without causing any problems. The CMOS transmitter inputs are high-impedance and must be driven to valid logic levels for proper IC operation. If a transmitter input is unused, connect it to VCC or GND.

#### Layout Guidelines

Maxim RS-232 ICs should be treated like DC-DC converters for layout purposes. The AC current flow must be analyzed for both the charge and discharge stages of the charge-pump cycle. To facilitate an easy and effective layout, Maxim conveniently places all the critical pins in close proximity to their external components.

## RS-232 Transceivers in Tiny Packages

Low-power RS-232 transceivers are available in space-saving chip-scale (UCSP), TQFN, and TSSOP packages. The MAX3243E in a 32-pin (7mm x 7mm) thin QFN package saves 20% board space over TSSOP solutions. The MAX3222E, also available in a 20-pin (5mm x 5mm) TQFN, improves and thus saves board space by 40%. Other transceiver part families packaged in a TQFN, the MAX3222E and MAX3232E with two drivers and two receivers and the MAX3221E with a single driver and single receiver, feature AutoShutdown capability to reduce the supply current to 1µA (See Table 3). These RS-232 transceivers are ideal for battery-powered equipment.

The MAX3228E/MAX3229E family in a 30-bump (3mm x 2.5mm) UCSP package saves about 70% board space, making these ICs ideal for space-constrained applications such as notebook, cell phone, and handheld equipment. Low-power RS-232 transceivers in space-saving UCSP with a low 1µA shutdown supply current are ideal for ultra-low-power system applications.

Table 3. RS232 Transceivers in Space-Saving Packages

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| MAX3221E | 20-Pin TQFN | 1 | 250 | 1/1 | 15 |
| MAX3222E | 16-Pin TQFN | 1 | 250 | 2/2 | 15 |
| MAX3223E | 20-Pin TQFN | 1 | 250 | 2/2 | 15 |
| MAX3230E | 20-Bump UCSP | 1 | 250 | 2/2 | 15 |
| MAX3231E | 20-Bump UCSP | 1 | 250 | 1/1 | 15 |
| MAX3232E | 16-Pin TQFN | 1 | 250 | 2/2 | 15 |
| MAX3237E | 28-Pin SSOP | 10nA | 1Mbps | 5/3 | 15 |
| MAX3243E | 32-Pin TQFN | 1 | 250 | 3/5 | 15 |
| MAX3246E | 36-Bump UCSP | 1 | 250 | 3/5 |  |

## Practical RS-232 Implementation

Most systems designed today do not operate using RS-232 voltage levels. Consequently, level conversion is necessary to implement RS-232 communication. Level conversion is performed by special RS-232 ICs with both line drivers that generate the voltage levels required by RS-232, and line receivers that can receive RS-232 voltage levels without being damaged. These line drivers and receivers typically invert the signal as well, since a logic 1 is represented by a low voltage level for RS-232 communication, and a logic 0 is represented by a high logic level.

Figure 3 illustrates the function of an RS-232 line driver/receiver in a typical modem application. In this example, the signals necessary for serial communication are generated and received by the Universal Asynchronous Receiver/Transmitter (UART). The RS-232 line driver/receiver IC performs the level translation necessary between the CMOS/TTL and RS-232 interface.

Figure 3. Typical RS-232 modem application.

The UART performs the "overhead" tasks necessary for asynchronous serial communication. Asynchronous communication usually requires, for example, that the host system initiate start and stop bits to indicate to the peripheral system when communication will start and stop. Parity bits are also often employed to ensure that the data sent has not been corrupted. The UART usually generates the start, stop, and parity bits when transmitting data, and can detect communication errors upon receiving data. The UART also functions as the intermediary between byte-wide (parallel) and bit-wide (serial) communication; it converts a byte of data into a serial bit stream for transmitting and converts a serial bit stream into a byte of data when receiving.

Now that an elementary explanation of the TTL/CMOS to RS-232 interface has been provided, we can consider some real-world RS-232 applications. It has already been noted in the Functional Characteristics section above that RS-232 applications rarely follow the RS-232 standard precisely. The unnecessary RS-232 signals are usually omitted. Many applications, such as a modem, require only nine signals (two data signals, six control signals, and ground). Other applications require only five signals (two for data, two for handshaking, and ground), while others require only data signals with no handshake control. We begin our investigation of real-world implementations by considering the typical modem application.

## RS-232 in Modem Applications

Modem applications are one of the most popular uses for the RS-232 standard. Figure 4 illustrates a typical modem application. As can be seen in the diagram, the PC is the DTE and the modem is the DCE. Communication between each PC and its associated modem is accomplished using the RS-232 standard. Communication between the two modems is accomplished through telecommunication. It should be noted that, although a microcontroller is usually the DTE in RS-232 applications, this is not mandated by a strict interpretation of the standard.

Figure 4. Modem communication between two PCs.

Although some designers choose to use a 25-pin connector for this application, it is not necessary as there are only nine interface signals (including ground) between the DTE and DCE. With this in mind, many designers use 9- or 15-pin connectors. (Figure 2 above shows a 9-pin connector design.) The "basic nine" signals used in modem communication are illustrated in Figure 3 above; three RS-232 drivers and five receivers are necessary for the DTE. The functionality of these signals is described below. Note that for the following signal descriptions, ON refers to a high RS-232 voltage level (+5V to +15V), and OFF refers to a low RS-232 voltage level (-5V to -15V). Keep in mind that a high RS-232 voltage level actually represents a logic 0, and that a low RS-232 voltage level refers to a logic 1.

**Transmitted Data (TD)**: One of two separate data signals, this signal is generated by the DTE and received by the DCE.

**Received Data (RD)**: The second of two separate data signals, this signals is generated by the DCE and received by the DTE.

**Request to Send (RTS)**: When the host system (DTE) is ready to transmit data to the peripheral system (DCE), RTS is turned ON. In simplex and duplex systems, this condition maintains the DCE in receive mode. In half-duplex systems, this condition maintains the DCE in receive mode and disables transmit mode. The OFF condition maintains the DCE in transmit mode. After RTS is asserted, the DCE must assert CTS before communication can commence.

**Clear to Send (CTS)**: CTS is used along with RTS to provide handshaking between the DTE and the DCE. After the DCE sees an asserted RTS, it turns CTS ON when it is ready to begin communication.

**Data Set Ready (DSR)**: This signal is turned on by the DCE to indicate that it is connected to the telecommunications line.

**Data Carrier Detect (DCD)**: This signal is turned ON when the DCE is receiving a signal from a remote DCE, which meets its suitable signal criteria. This signal remains ON as long as a suitable carrier signal can be detected.

**Data Terminal Ready (DTR)**: DTR indicates the readiness of the DTE. This signal is turned ON by the DTE when it is ready to transmit or receive data from the DCE. DTR must be ON before the DCE can assert DSR.

**Ring Indicator (RI)**: RI, when asserted, indicates that a ringing signal is being received on the communications channel.

The signals described above form the basis for modem communication. Perhaps the best way to understand how these signals interact is to examine a step-by-step example of a modem interfacing with a PC. The following steps describe a transaction in which a remote modem calls a local modem.

1. The local Pc uses software to monitor the RI (Ring Indicate) signal.
2. When the remote modem wants to communicate with the local modem, it generates an RI signal. This signal is transferred by the local modem to the local PC.
3. The local PC responds to the RI signal by asserting the DTR (Data Terminal Ready) signal when it is ready to communicate.
4. After recognizing the asserted DTR signal, the modem responds by asserting DSR (Data Set Ready) after it is connected to the communications line. DSR indicates to the PC that the modem is ready to exchange further control signals with the DTE to commence communication. When DSR is asserted, the PC begins monitoring DCD for an indication that data is being sent over the communication line.
5. The modem asserts DCD (Data Carrier Detect) after it has received a carrier signal from the remote modem that meets the suitable signal criteria.
6. At this point data transfer can began. If the local modem has full-duplex capability, the CTS (Clear to Send) and RTS (Request to Send) signals are held in the asserted state. If the modem has only half-duplex capability, CTS and RTS provide the handshaking necessary for controlling the direction of the data flow. Data is transferred over the RD and TD signals.
7. When the transfer of data has been completed, the PC disables the DTR signal. The modem follows by inhibiting the DSR and DCD signals. At this point the PC and modem are in the original state described in step number 1.

## RS-232 in Minimal Handshake Applications

Although the modem application discussed above is simplified from the RS-232 standard because of the number of signals needed, it is still more complex than many system requirements. For many applications, only two data lines and two handshake control lines are necessary to establish and control communication between a host system and a peripheral system. For example, an environmental control system may need to interface with a thermostat using a half-duplex communication scheme. At times the control systems read the temperature from the thermostat and at other times they load temperature trip points to the thermostat. In this type of simple application, only five signals could be needed (two for data, two for handshake control, and ground).

Figure 5 illustrates a simple half-duplex communication interface. As can be seen, data is transferred over the TD (Transmit Data) and RD (Receive Data) pins, and the RTS (Ready to Send) and CTS (Clear to Send) pins provide handshake control. RTS is driven by the DTE to control the direction of data. When it is asserted, the DTE is placed in transmit mode. When RTS is inhibited, the DTE is placed in receive mode. CTS, which is generated by the DCE, controls the flow of data. When asserted, data can flow. However, when CTS is inhibited, the transfer of data is interrupted. The transmission of data is halted until CTS is reasserted.

Figure 5. Half-duplex communication scheme.

## RS-232 Application Limitations

In the more than four decades since the RS-232 standard was introduced, the electronics industry has changed immensely. There are, therefore, some limitations in the RS-232 standard. One limitation—the fact that over twenty signals have been defined by the standard—has already been addressed. Designers simply do not use all the signals or the 25-pin connector.

Other limitations in the standard are not necessarily as easy to correct.

#### Generation of RS-232 Voltage Levels

As explained in the **Electrical Characteristics** section, RS-232 does not use the conventional 0 and 5V levels implemented in TTL and CMOS designs. Drivers have to supply +5V to +15V for a logic 0 and -5V to -15V for a logic 1. This means that extra power supplies are needed to drive the RS-232 voltage levels. Typically, a +12V and a -12V power supply are used to drive the RS-232 outputs. This is a great inconvenience for systems that have no other requirements for these power supplies. With this in mind, RS-232 products manufactured by Dallas Semiconductor have on-chip charge-pump circuits that generate the necessary voltage levels for RS-232 communication. The first charge pump essentially doubles the standard +5V power supply to provide the voltage level necessary for driving a logic 0. A second charge pump inverts this voltage and provides the voltage level necessary for driving a logic 1. These two charge pumps allow the RS-232 interface products to operate from a single +5V supply.

#### Maximum Data Rate

Another limitation in the RS-232 standard is the maximum data rate. The standard defines a maximum data rate of 20kbps, which is unnecessarily slow for many of today's applications. RS-232 products manufactured by Dallas Semiconductor guarantee up to 250kbps and typically can communicate up to 350kbps. While providing a communication rate at this frequency, the devices still maintain a maximum 30V/ms maximum slew rate to reduce the likelihood of crosstalk between adjacent signals.

#### Maximum Cable Length

As we have seen, the cable-length specification once included in the RS-232 standard has been replaced by a maximum load-capacitance specification of 2500pF. To determine the total length of cable allowed, one must determine the total line capacitance. Figure 6 shows a simple approximation for the total line capacitance of a conductor. As can be seen, the total capacitance is approximated by the sum of the mutual capacitance between the signal conductors and the conductor to shield capacitance (or stray capacitance in the case of unshielded cable).

As an example, assume that the user decided to use nonshielded cable when interconnecting the equipment. The mutual capacitance (Cm) of the cable is found in the cable's specifications to be 20pF per foot. Assuming that the receiver's input capacitance is 20pF, this leaves the user with 2480pF for the interconnecting cable. From the equation in Figure 6, the total capacitance per foot is 30pF. Dividing 2480pF by 30pF reveals that the maximum cable length is approximately 80 feet. If a longer cable length is required, the user must find a cable with a smaller mutual capacitance.

Figure 6. Interface cable-capacitive model, per unit length.
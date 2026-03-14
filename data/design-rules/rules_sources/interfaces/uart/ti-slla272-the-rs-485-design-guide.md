---
source: "TI SLLA272 -- The RS-485 Design Guide"
url: "https://www.ti.com/lit/pdf/slla272"
format: "PDF 9pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 14153
---
# The RS-485 Design Guide

Thomas Kugelstadt, HPL - Interface

## Abstract

As a short compendium for successful data transmission design, this application report discusses the important aspects of the RS-485 standard.

## 1 Introduction

In 1983, the Electronics Industries Association (EIA) approved a new balanced transmission standard called RS-485. Finding widespread acceptance and usage in industrial, medical, and consumer applications, RS-485 has become the industry's interface workhorse.

This application report presents design guidelines for engineers new to the RS-485 standard that can help them accomplish a robust and reliable data transmission design in the shortest time possible.

## 2 Standard and Features

RS-485 is an electrical-only standard. In contrast to complete interface standards, which define the functional, mechanical, and electrical specifications, RS-485 only defines the electrical characteristics of drivers and receivers that could be used to implement a balanced multipoint transmission line.

This standard, however, is intended to be referenced by higher level standards, such as DL/T645, for example, which defines the communication protocol for electronic energy-meters in China, specifying RS-485 as the physical layer standard.

Key features of RS-485 are:

- Balanced interface
- Multipoint operation from a single 5-V supply
- -7-V to +12-V bus common-mode range
- Up to 32 unit loads
- 10-Mbps maximum data rate (at 40 feet)
- 4000-foot maximum cable length (at 100 kbps)

## 3 Network Topology

The RS-485 standards suggests that its nodes be networked in a daisy-chain, also known as party line or bus topology. In this topology, the participating drivers, receivers, and transceivers connect to a main cable trunk via short network stubs. The interface bus can be designed for full-duplex or half-duplex transmission.

The full-duplex implementation requires two signal pairs (four wires), and full-duplex transceivers with separate bus access lines for transmitter and receiver. Full-duplex allows a node to simultaneously transmit data on one pair while receiving data on the other pair.

In half-duplex, only one signal pair is used, requiring the driving and receiving of data to occur at different times. Both implementations necessitate the controlled operation of all nodes via direction control signals, such as Driver/Receiver Enable signals, to ensure that only one driver is active on the bus at any time. Having more than one driver accessing the bus at the same time leads to bus contention, which, at all times, must be avoided through software control.

## 4 Signal Levels

RS-485 standard conform drivers provide a differential output of a minimum 1.5 V across a 54-Ohm load, whereas standard conform receivers detect a differential input down to 200 mV. The two values provide sufficient margin for a reliable data transmission even under severe signal degradation across the cable and connectors. This robustness is the main reason why RS-485 is well suited for long-distance networking in noisy environment.

## 5 Cable Type

RS-485 applications benefit from differential signaling over twisted-pair cable, because noise from external sources couple equally into both signal lines as common-mode noise, which is rejected by the differential receiver input.

Industrial RS-485 cables are of the sheathed, unshielded, twisted-pair type (UTP), with a characteristic impedance of 120 Ohm and 22-24 AWG. Similar cables, in two-pair and single-pair versions, are available to accommodate the low-cost design of half-duplex systems.

Beyond the network cabling, it is mandatory that the layout of printed-circuit boards and the connector pin assignments of RS-485 equipment maintain the electrical characteristics of the network by keeping both signal lines close and equidistant to another.

## 6 Bus Termination and Stub Length

Data transmission lines should always be terminated and stubs should be as short as possible to avoid signal reflections on the line. Proper termination requires the matching of the terminating resistors, R_T, to the characteristic impedance, Z0, of the transmission cable. Because the RS-485 standard recommends cables with Z0 = 120 Ohm, the cable trunk is commonly terminated with 120-Ohm resistors, one at each cable end.

Applications in noisy environments often have the 120-Ohm resistors replaced by two 60-Ohm low-pass filters to provide additional common-mode noise filtering. It is important to match the resistor values (preferably with 1% precision resistors), to ensure equal rolloff frequencies of both filters. Larger resistor tolerances (i.e., 20%) cause the filter corner frequencies to differ and common-mode noise to be converted into differential noise, thus compromising the receiver's noise immunity.

The electrical length of a stub (the distance between a transceiver and cable trunk) should be shorter than 1/10 of the driver's output rise time:

L_Stub <= (t_r / 10) x v x c

Where:

- L_Stub = maximum stub length (ft)
- t_r = driver (10/90) rise time (ns)
- v = signal velocity of the cable as factor of c
- c = speed of light (9.8 x 10^8 ft/s)

| Device | Signal Rate (kbps) | Rise Time t_r (ns) | Maximum Stub Length (ft) |
|---|---|---|---|
| SN65HVD12 | 1000 | 100 | 7 |
| SN65LBC184 | 250 | 250 | 19 |
| SN65HVD3082E | 200 | 500 | 38 |

**Note:** Drivers with long rise times are well suited for applications requiring long stub lengths and reduced, device-generated EMI.

## 7 Failsafe

Failsafe operation is a receiver's ability to assume a determined output state in the absence of an input signal.

Three possible causes can lead to the loss of signal (LOS):

1. Open-circuit, caused by a wire break or by the disconnection of a transceiver from the bus
2. Short-circuit, caused by an insulation fault connecting the wires of a differential pair to another
3. Idle-bus, occurring when none of the bus drivers is active

Because these conditions can cause conventional receivers to assume random output states when the input signal is zero, modern transceiver designs include biasing circuits for open-circuit, short-circuit, and idle-bus failsafe, that force the receiver output to a determined state, under an LOS condition.

A drawback of these failsafe designs is their worst-case noise margin of 10 mV only, thus requiring external failsafe circuitry to increase noise margin for applications in noisy environments.

An external failsafe circuit consists of a resistive voltage divider that generates sufficient differential bus voltage, to drive the receiver output into a determined state. To ensure sufficient noise margin, V_AB must include the maximum differential noise measured in addition to the 200-mV receiver input threshold: V_AB = 200 mV + V_Noise.

R_B = V_BUS-min / (V_AB x (1/375 + 4/Z0))

For a minimum bus voltage of 4.75 V (5 V - 5%), V_AB = 0.25 V, and Z0 = 120 Ohm, R_B yields 528 Ohm. Inserting two 523-Ohm resistors in series to R_T establishes the failsafe circuit.

## 8 Bus Loading

Because a driver's output depends on the current it must supply into a load, adding transceivers and failsafe circuits to the bus increases the total load current required. To estimate the maximum number of bus loads possible, RS-485 specifies a hypothetical term of a unit load (UL), which represents a load impedance of approximately 12 kOhm. Standard-compliant drivers must be able to drive 32 of these unit loads. Today's transceivers often provide reduced unit loading, such as 1/8 UL, thus allowing the connection of up to 256 transceivers on the bus.

Because failsafe biasing contributes up to 20 unit loads of bus loading, the maximum number of transceivers, N, is reduced to:

N = (32 UL_STANDARD - 20 UL_FAILSAFE) / UL per transceiver

Thus, when using 1/8-UL transceivers, it is possible to connect up to a maximum of 96 devices to the bus.

## 9 Data Rate Versus Bus Length

The maximum bus length is limited by the transmission line losses and the signal jitter at a given data rate. Because data reliability sharply decreases for a jitter of 10% or more of the baud period:

- **Section 1** (high data rates, short cable): The losses of the transmission line can be neglected and the data rate is mainly determined by the driver's rise time. Although the standard recommends 10 Mbps, today's fast interface circuits can operate at data rates of up to 40 Mbps.
- **Section 2** (transition from short to long): The losses of the transmission lines have to be taken into account. With increasing cable length, the data rate must be reduced. A rule of thumb states that the product of the line length (m) times the data rate (bps) should be < 10^7.
- **Section 3** (lower frequency range): The line resistance, and not the switching, limits the cable length. The cable resistance approaches the value of the termination resistor. This voltage divider diminishes the signal by -6 dB. For a 22 AWG cable, 120 Ohm, UTP, this occurs at approximately 1200 m.

## 10 Minimum Node Spacing

The RS-485 bus is a distributed parameter circuit whose electrical characteristics are primarily defined by the distributed inductance and capacitance along the physical media, which includes the interconnecting cables and printed-circuit board traces.

Adding capacitance to the bus in the form of devices and their interconnections lowers the bus impedance and causes impedance mismatches between the media and the loaded section of the bus. Ensuring a valid receiver input voltage level during the first signal transition from an output driver anywhere on the bus requires a minimum loaded bus impedance of Z' > 0.4 x Z0, which can be achieved by keeping the minimum distance, d, between bus nodes:

d > C_L / (5.25 x C')

Where C_L is the lumped load capacitance and C' the media capacitance (cable or PCB trace) per unit length.

Load capacitance includes contributions from the line circuit bus pins, connector contacts, printed-circuit board traces, protection devices, and any other physical connections to the trunk line as long as the distance from the bus to the transceiver (the stub) is electrically short.

Typical values: 5-V transceivers typically possess a capacitance of 7 pF, whereas 3-V transceivers have approximately twice that capacitance at 16 pF. Board traces add approximately 0.5 to 0.8 pF/cm depending on their construction. Media distributed capacitance ranges from 40 pF/m for low capacitance, unshielded, twisted-pair cable to 70 pF/m for backplanes.

## 11 Grounding and Isolation

When designing a remote data link, the designer must assume that large ground potential differences (GPD) exist. These voltages add as common-mode noise, V_n, to the transmitter output. Even if the total superimposed signal is within the receiver's input common-mode range, relying on the local earth ground as a reliable path for the return current is dangerous.

Because remote nodes are likely to draw their power from different sections of the electrical installation, modification to the installation (i.e., during maintenance work) can increase the GPD to the extent that the receiver's input common-mode range is exceeded. Thus, a data link working today might cease operation sometime in the future.

The direct connection of remote grounds through ground wire also is not recommended, as this causes large ground loop currents to couple into the data lines as common-mode noise.

The RS-485 standard recommends the separation of device ground and local system ground via the insertion of resistors. Although this approach reduces loop current, the existence of a large ground loop keeps the data link sensitive to noise generated somewhere else along the loop.

The approach to tolerate GPDs up to several kilovolts across a robust RS-485 data link and over long distance is the galvanic isolation of the signal and supply lines of a bus transceiver from its local signal and supply sources.

In this case, supply isolators (such as isolated DC/DC converters) and signal isolators (such as digital, capacitive isolators) prevent current flow between remote system grounds and avoid the creation of current loops.

For multiple isolated transceivers: All transceivers but one connect to the bus via isolation. The non-isolated transceiver provides the single-ground reference for the entire bus.

## 12 Conclusion

The objective of this application report is to cover the main aspects of an RS-485 system design. Following the discussions presented in this document and consulting the detailed application reports in the reference section can help accomplishing a robust, RS-485-compliant system design in the shortest time possible.

### 12.1 References

1. *Removing Ground Noise in Data Transmission Systems* (SLLA268)
2. *Interface Circuits for TIA/EIA-485 (RS-485)* (SLLA036)
3. *Detection of RS-485 Signal Loss* (SLYT257)
4. *Overtemperature Protection in RS-485 Line Circuits* (SLLA200)
5. *Device Spacing on RS-485 Buses* (SLYT241)
6. *PROFIBUS Electrical-Layer Solutions* (SLLA177)
7. *A Statistical Survey of Common-Mode Noise* (SLYT153)
8. *Failsafe in RS-485 Data Buses* (SLYT080)
9. *The RS-485 Unit Load and Maximum Number of Bus Connections* (SLYT086)
10. *Using Signaling Rate and Transfer Rate* (SLLA098)
11. *Operating RS-485 Transceivers at Fast Signaling Rates* (SLLA173)
12. *RS-485 for E-Meter Applications* (SLLA112)
13. *Failsafe in RS-485 Data Buses* (SLYT064)
14. *Use Receiver Equalization to Extend RS-485 Data Communications* (SLLA169)
15. *The RS-485 Unit Load and Maximum Number of Bus Connections* (SLLA166)
16. *Comparing Bus Solutions* (SLLA067)
17. *RS-485 for Digital Motor Control Applications* (SLLA143)
18. *422 and 485 Standards Overview and System Configurations* (SLLA070)
19. *TIA/EIA-485 and M-LVDS, Power and Speed Comparison* (SLLA106)
20. *Live Insertion with Differential Interface Products* (SLLA107)
21. *The ISO72x Family of High-Speed Digital Isolators* (SLLA198)

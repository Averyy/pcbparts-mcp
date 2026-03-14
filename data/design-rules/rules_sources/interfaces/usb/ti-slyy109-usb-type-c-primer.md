---
source: "TI SLYY109 -- USB Type-C Primer"
url: "https://www.ti.com/lit/pdf/slyy109"
format: "PDF 14pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 13926
---

# A Primer on USB Type-C and USB Power Delivery Applications and Requirements

## Introduction

You may have heard about USB Type-C's reversible cable. When you think about the requirements for a particular system, however, you may be unsure about what's necessary and what's just "nice to have." This paper introduces the most basic USB Type-C applications and works up to full-featured USB Type-C and USB PD applications.

## USB Data Evolution

Table 1 lists the maximum transfer rate of each USB data transfer-related specification.

| Specification | Data rate name | Maximum transfer rate |
|---|---|---|
| USB 1.0 and USB 1.1 | Low Speed | 1.5 Mbps |
| USB 1.0 and USB 1.1 | Full Speed | 12 Mbps |
| USB 2.0 | High Speed | 480 Mbps |
| USB 3.0 | SuperSpeed | 5 Gbps |
| USB 3.1 | SuperSpeed+ | 10 Gbps |

Table 2 shows the evolution of USB power, starting with USB 2.0 through USB PD 3.0. Without USB PD, you can support up to 5 V at 3 A (15 W) with just USB Type-C alone. However, with USB PD, you can support up to 20 V at 5 A (100 W) within the USB Type-C ecosystem.

| Specification | Maximum Voltage | Maximum Current | Maximum Power |
|---|---|---|---|
| USB 2.0 | 5 V | 500 mA | 2.5 W |
| USB 3.0 and USB 3.1 | 5 V | 900 mA | 4.5 W |
| USB BC 1.2 | 5 V | 1.5 A | 7.5 W |
| USB Type-C 1.2 | 5 V | 3 A | 15 W |
| USB PD 3.0 | 20 V | 5 A | 100 W |

## Data and Power Roles

There are three types of data flow in a USB connection:

- **Downstream-facing port (DFP):** Sends data downstream; it is typically the port on a host or a hub to which devices connect. A DFP will source VBUS power (the power path between host and device) and can also source VCONN power (to power electronically marked cables). Example: a docking station.
- **Upstream-facing port (UFP):** Connects to a host or DFP of a hub, receives data on a device or hub. These ports usually sink VBUS. Example: a display monitor.
- **Dual-role data (DRD) port:** Can operate as either a DFP (host) or a UFP (device). The port's power role at attach determines its initial role. A source port takes on the data role of a DFP, while the sink port takes on the data role of a UFP. Using USB PD data-role swap can dynamically change the port's data role. Examples: laptops, tablets and smartphones.

There are three types of power flow in a USB connection:

- **Sink:** A port that when attached consumes power from VBUS. A sink is most often a device, such as a USB-powered light or fan.
- **Source:** A port that when attached provides power over VBUS. Common sources are a host or hub DFP. Example: a USB Type-C wall charger.
- **Dual-role power (DRP) port:** Can operate as either a sink or source, and may alternate between these two states. When a DRP initially operates as a source, the port takes the data role of a DFP. When a DRP initially operates as a sink, the port takes the data role of a UFP. Using USB PD power-role swap can dynamically change the DRP's power role. Two special subclasses:
  - **Sourcing device:** Capable of supplying power, but not capable of acting as a DFP. Example: a USB Type-C and USB PD-compatible monitor that receives data from a laptop's DFP but also charges the laptop.
  - **Sinking host:** Capable of consuming power, but not capable of acting as a UFP. Example: a hub's DFP that sends data to an accessory while being powered by that accessory.

## USB Type-C UFP Sink: USB 2.0 without USB PD

The most simple and likely most common application is a UFP USB 2.0 without USB PD (15 W or less). Common applications include anything USB-powered today that does not require SuperSpeed data, such as a mouse, keyboard, wearables or various other small electronics.

The USB 2.0 physical layer (PHY) serves as the physical layer between the data from USB's D+ and D- lines to the UTMI plus low-pin interface (ULPI) for the application processor. USB 2.0 PHYs are often integrated into processors or microcontrollers; however, discrete PHYs are available.

The configuration channel (CC) logic block introduced in the USB Type-C specification determines cable detection, cable orientation and current-carrying capability:

- **Cable detection** occurs when one of the two CC lines pulls down. A DFP will have both of its CC pins pull up with resistor Rp, and a UFP will have both of its CC pins pull down with resistor Rd. Once a DFP processor detects that one of its CC lines is pulled down, the DFP knows that a connection has been made.
- **Cable orientation** is based on which CC line pulls down (if CC1 pulls down, the cable is not flipped; if CC2 pulls down, the cable is flipped). For non-active cables, the remaining CC line remains open; for active cables, the remaining CC line will pull down with Ra.
- **Current-carrying capability** is determined by the values of Rp. USB Type-C can natively support either 1.5 A or 3 A. A DFP can advertise its current-carrying capability with a specific value pullup resistor. A UFP has a fixed-value pulldown resistor (Rd) such that when connected, it forms a voltage divider with Rp. By sensing the voltage at the center tap, a UFP can detect the DFP's advertised current.

The USB 2.0 multiplexer (high-speed mux) is optional and not required by the USB Type-C specification. In a USB Type-C receptacle, there are two pairs of D+/D- lines for a single channel of USB 2.0 data. The USB Type-C specification allows shorting the pairs together, D+ to D+ and D- to D-, to create a stub. Although it's not required, some designers elect to include a USB 2.0 mux to improve signal integrity.

## USB Type-C DFP: USB 2.0 without USB PD

Another simple and common application is a DFP USB 2.0 without USB PD. One example is a 5-V AC/DC adapter. The CC logic block is the same as the UFP case. The DFP presents Rp and monitors for a pulldown caused by Rd. Once Rp detects a pulldown, the DFP knows that a device is connected and provides 5 V. Providing 5 V only on the VBUS line after detecting a device (cold-plugging), versus always providing 5 V, is a new feature introduced in USB Type-C.

Because USB Type-C implements cold-plugging, the design requires a 5-V VBUS field-effect transistor (FET) as a switch for the 5-V rail.

The USB Type-C specification requires that all sources monitor current and protect themselves if a sink tries to draw in excess of what it can supply. This is where the overcurrent protection block comes into play. These two blocks can be integrated into the point-of-load power converter, or integrated into the USB Type-C device.

**VBUS discharge:** When no device is attached, VBUS should sit at 0 V. The USB Type-C specification requires a source to discharge VBUS within 650 ms of a detached sink. VBUS discharge is often integrated into a USB Type-C device, but can also be integrated with a bleeder resistor.

**VCONN:** Can power passive electronically marked or active cables by switching 5 V onto the unused CC line. VCONN is required for all applications that support USB 3.1 speeds or power delivery higher than 3 A. The VCONN switch is also required to support active cables, such as longer-distance cables requiring signal conditioning with an integrated redriver or retimer.

## USB Type-C DRP/DRD: USB 2.0 without USB PD

The last USB 2.0 non-USB PD application is the DRP/DRD. For non-USB PD applications, DRD and DRP are identical. A common example is a slower-speed laptop port that can send power in either direction. The only noticeable change from the DFP design is adding the Rp/Rd switch. A DRP/DRD can present itself as either a UFP or DFP, requiring a method to pull the CC lines up with Rp or pull them down with Rd (default on a dead battery in order to charge).

## USB Type-C DRP/DRD: USB 2.0 with USB PD

Applications with increasing complexity require USB PD. Systems with USB PD can support power levels of up to 20 V and 5 A (100 W). This is possible by first increasing the voltage on VBUS while holding the maximum current at 3 A. After reaching the maximum voltage of 20 V, you can increase the current up to 5 A.

Key characteristics of USB PD voltage profiles:

- The discrete voltage levels required are 5 V, 9 V, 15 V and 20 V (modified in USB PD specification v3.0).
- The current can vary continuously, depending on the required power level (up to 3 A).
- At any given power level, a source is required to support all previous voltages and power levels.

For example, a 60-W source must be able to supply 20 V at 3 A, 15 V at 3 A, 9 V at 3 A and 5 V at 3 A.

New blocks for USB PD applications:

- The **VBUS FET** can now handle 5 V to 20 V (at discrete levels) and potentially up to 5 A (only when providing 20 V). A **gate driver** block controls the higher-power FET.
- **VBUS-to-short protection:** The USB Type-C connector has a higher pin density than legacy USB connectors. It is easier to accidentally short VBUS to adjacent pins. Since VBUS can be as high as 20 V, a short between 20 V and a 5-V line (such as SBU, CC, etc.) can be catastrophic.
- **USB PD PHY and USB PD manager:** Together, these blocks send packets of data across the CC lines, enabling communication between the DFP and UFP. The USB PD PHY's responsibility is to drive the CC lines. The USB PD manager contains a complex state machine to support USB PD negotiation and to control the PHY, including Alternate Mode negotiation.

If USB PD is required, you need a USB PD PHY and a USB PD manager. You can implement both in an integrated solution, or implement a USB PD manager on a microcontroller and use a separate PHY with a USB Type-C port controller.

## USB 3.1 Gen 1 (SuperSpeed) and Gen 2 (SuperSpeed+)

Applications that require transfer rates faster than 480 Mbps need either USB 3.1 Gen 1 (SuperSpeed, up to 5 Gbps) or Gen 2 (SuperSpeed+, up to 10 Gbps). To enable these higher transfer rates in a USB Type-C application, you need:

- A USB 3.1 PHY interface for the PCI Express (PCIe) PIPE PHY
- A bidirectional differential switch (mux/demux) that supports USB 3.1

Unlike USB 2.0 data, the mux/demux is not optional and is required for all applications except USB Type-C plugs that connect directly to a host (versus a female receptacle). For a USB 3.1 flash drive with a USB Type-C plug physically incorporated into the device, the USB 3.1 data bus is fixed by design.

USB Type-C cables are wired such that the CC wires are position-aligned with the USB 3.1 signal pairs. The host can configure the switch based on which CC pins (CC1/CC2) terminate at the receptacle.

All USB 3.1 applications incorporating a USB Type-C receptacle must include the USB 3.1 switch, because when a USB Type-C cable connects two receptacles, the cable orientation and twist are not fixed.

## Alternate Mode

An important benefit of USB Type-C is its ability to eliminate the need for nearly every cable in consumer devices (HDMI, DisplayPort/Thunderbolt, power barrels, USB Type-A/B). Alternate Mode enables the repurposing of USB Type-C pins (TX/RX pairs and SBU) for a different function. Video has been the primary focus with DisplayPort and Thunderbolt being the main two Alternate Modes.

Two new blocks are required:
- **Alternate Mode PHY** (e.g., a DisplayPort source from the graphics processing unit)
- **Alternate Mode mux** supporting switching in the Alternate Mode PHY while still supporting different cable orientations

Even if USB PD power levels are not required, you must include a USB PD PHY and USB PD manager to support Alternate Mode because it is negotiated the same way as USB PD -- a vendor-defined message over the CC line.

If Alternate Mode negotiation fails, there are two options:
- Support USB functionality without Alternate Mode
- Provide a USB billboard message over the D+/D- lines to communicate information that identifies the device

## USB Type-C Pinout and Reversibility

The USB Type-C connector includes several new pins compared to USB Type-A and Type-B connectors:

- **GND:** Return path for the signal
- **TX/RX:** SuperSpeed twisted pairs for USB 3.1 data (5 to 10 Gbps)
- **VBUS:** Main system bus (5 V to 20 V)
- **CC1/CC2:** Configuration channel lines for cable detection, orientation and current advertisement. With USB PD, the CC lines can also communicate higher power levels and Alternate Mode. One of the CC lines may become VCONN.
- **SBU1/SBU2:** Low-speed lines used only for Alternate Mode and accessory mode. For DisplayPort, AUX+/AUX- transmit over the SBU lines. For audio adapter accessory mode, these lines are used for the microphone input and analog GND.
- **D+/D-:** High-speed twisted pair for USB 2.0 data (up to 480 Mbps)

The pins are almost symmetrical (both vertically and horizontally), which is why the connector can be reversible. However, it's not possible to passively realize reversibility, so additional electronics are required.

Key reversibility characteristics:
- **GND and VBUS** remain in the same position
- **D+/D-** pair is in the same orientation; the plug contains only one D+/D- pair. The spec allows shorting the receptacle pairs together (D+ to D+ and D- to D-)
- **CC1 and CC2** lines are flipped, enabling cable orientation detection
- **TX/RX** pairs are also flipped. Unlike D+/D-, you cannot simply short them together because that creates a stub. At USB 3.1 speeds, a stub degrades signal integrity. Two solutions:
  - Use two PHYs and cable-orientation detection to know which PHY to use
  - Use a single PHY and a SuperSpeed mux (typically the more economical solution)
- **SBU** lines are also flipped, typically handled within the Alternate Mode PHY

## References

1. USB Type-C Cable and Connector Specification Revision 2.0. USB Implementers Forum, Inc., October 2020.
2. USB Power Delivery. USB Implementers Forum, Inc., December 2020.

---
source: "TI SLVAFC1 -- CAN Bus ESD Protection"
url: "https://www.ti.com/document-viewer/lit/html/SLVAFC1"
format: "HTML"
method: "ti-html"
extracted: 2026-02-16
chars: 8639
---

# 1 CAN Bus Overview

CAN is a 2-wire differential
communications interface which has its physical layer defined by the ISO 11898-2
standard. The physical layer consists of the CAN transceiver and the twisted pair
cabling that connects all the CAN nodes together. The two lines connecting the CAN
transceiver to the cabling are referred to as CANH and CANL. It is also recommended
to terminate the CANH and CANL lines with a split termination to avoid signal
reflections and high frequency noise. [Figure 1-1](#GUID-75D5A238-17F0-4EF1-BE75-09DFBDCB94A8) illustrates the typical CAN bus setup.

Figure 1-1 CAN Bus Typical Setup

The CAN protocol can come in many
different flavors and speeds. These flavors include:

* Low speed (LS CAN): Up to 125
  kbps
* High speed (HS CAN): Up to 1
  Mbps
* Flexible data rate (CAN FD): Up
  to 5 Mbps
* Signal Improved capable CAN (CAN
  SIC): Up to 8 Mbps
* CAN XL: Up to 10-20 Mbps (not yet
  released)

# 2 Causes of ESD

ESD can happen to any system with
exposed connectors, including CAN bus interfaces. Typically, these connectors are
exposed during vehicle assembly and maintenance. For example, when a car is going
through assembly, the cabling needed to connect the control modules in the car can
accumulate an excess amount of charge on them as they move through the factory. When
it comes time to connect these cables to the control modules that hold the CAN
transceivers, the excess charge will flow from the cable to the module and into the
CAN transceiver. Depending on the environmental conditions in the factory and how
the cabling is handled, these discharges can get up to 30 kV and permanently damage
the CAN transceivers, making the vehicle inoperable. This can also happen if a
mechanic is performing maintenance on a car and has to disconnect and reconnect this
cabling. In short, any time the cabling is manipulated in the system, there is a
chance for ESD to occur.

Figure 2-1 CAN Bus ESD Event

# 3 ESD Protection Requirements

Many CAN transceivers have built-in
ESD protection cells, but to keep the size of the chip down, most of them only
protect up to 8 kV. As it was previously mentioned, depending on the environment,
some ESD strikes can get up to 30 kV. Due to this, an external ESD protection diode
is needed to increase the system-level ESD performance. Below are the key
considerations and parameters needed to select a proper ESD protection diode:

* Working Voltage (Vrwm) and
  Polarity
  + The Vrwm of the diode is
    dependent on the application they will be used in. Under ideal
    conditions, the CAN bus voltage levels swing between Vcc (5 V or 3.3 V)
    on CANH and 0 V on CANL. However, in vehicles, there is a common mode
    voltage present depending on the battery voltage. Smaller vehicles will
    use 12 V batteries and larger vehicles like 18-wheelers will use 24 V
    batteries. In addition to this common-mode voltage, there is also the
    risk of an improper jumpstart if the vehicle’s battery is almost dead.
    The proper way to jumpstart a vehicle is to connect a battery of another
    car in parallel with the dead battery. A person that does not know this
    might connect both batteries in series, doubling the overall voltage of
    the car. In the case of a 12 V battery, a 24 V ESD diode is needed to
    ensure that it does not burn up in this series jumpstart scenario. In
    the case of a 24 V battery that consists of two 12 V cells, a 36 V diode
    is needed since the cells are charged individually. All diodes need to
    be bidirectional to account for line faults and miswiring.
* IEC 61000-4-2 Rating
  + The [IEC
    61000-4-2](https://www.ti.com/lit/pdf/SLVA711) standard defines a waveform that simulates a
    real-world ESD strike, contrary to waveforms like human body model (HBM)
    and charged device model (CDM) that simulate ESD events in a controlled
    environment. Since certain environmental elements such as humidity and
    temperature make ESD strikes more strenuous, it is recommended that the
    ESD diode has a minimum contact rating of 15 kV.
* ISO 10605 Rating
  + The [ISO
    10605](https://www.ti.com/lit/pdf/SLVA954) standard defines a waveform that simulates a real-world
    ESD strike in an automotive environment. This waveform defines many
    different capacitance and resistance combinations, contrary to IEC
    61000-4-2 that only calls for 150 pF/330 Ω. The most strenuous of these
    combinations is the 330 pF/330 Ω, which is more strenuous than an IEC
    61000-4-2 waveform. To survive ESD strikes in harsh automotive
    environments, it is recommended that the ESD diode has a minimum contact
    rating of 15 kV.
* Capacitance
  + An ESD diode should have
    a low capacitance to minimize signal degradation. The maximum allowable
    diode capacitance can vary between signal speeds (LS CAN vs CAN FD),
    transceiver capacitance, network size, and other components on the CANH
    and CANL lines like filtering capacitors. Generally, it is recommended
    to keep the diode capacitance below 15 pF. However, system architects
    look for diodes with the lowest possible capacitance to maximize their
    total capacitance budget for the system.
* Clamping Voltage
  + Clamping voltage
    requirements can vary depending on the CAN transceiver being used. The
    important thing to note is that the clamping voltage should be less than
    the abs max rating of the CANH and CANL pins.
* Package
  + For CAN applications,
    many systems require automatic optical inspection for their boards to
    confirm that all components are soldered on properly. To allow for this,
    leaded packages like SOT-23 and SC70 are recommended for ESD
    diodes.

# 4 System Level Solutions

TI offers an array of ESD diodes know
as the ESD2CANxx devices to protect all different types of CAN transceivers in many
different environments. They come in leaded, dual-channel packages with matched
capacitance designed specifically for CAN bus ESD protection.

Figure 4-1 Protected CAN
Transceiver

Here, [ESD2CAN24-Q1](https://www.ti.com/product/ESD2CAN24-Q1) was paired with a [TCAN1042V-Q1](https://www.ti.com/product/TCAN1042V-Q1) CAN transceiver to demonstrate how it provides system-level
ESD immunity in a 12 V automotive environment. Two boards were used for this
experiment: one board with just the TCAN1042V-Q1 and the other board with both the
ESD2CAN24-Q1 and the TCAN1042V-Q1.

To measure signal integrity, both
boards were powered to 5 V and a 500 kHz (1Mbps) digital signal was forced on the
TXD pins to simulate a HS CAN environment. An oscilloscope was connected to the CANH
(line 1), CANL (line2), TXD (line 3), and RXD (line 4) to observe the results. As
the results in [Figure 4-2](#GUID-E2713E6A-F2D7-41DF-9698-4FB8C3FC13F2) and [Figure 4-3](#GUID-A4FCDC56-EC76-4DBA-9515-EBA69242DA5A) show, the ESD2CAN24-Q1 diode does not degrade the CANH and CANL signals at
all.

Figure 4-2 No Diode

Figure 4-3 With ESD2CAN24-Q1

To measure system-level ESD immunity,
the CANH and CANL pins of both boards were struck with +/-30 kV ISO 10605 contact
pulses. Since TCAN1042V-Q1 is only rated to withstand 8 kV ISO 10605 pulses, the
system without a diode failed. The system with ESD2CAN24-Q1 survived since the
ESD2CAN24-Q1 clamped the pulse to a low enough voltage for the transceiver to
handle.

# 5 Summary

The CAN bus is an interface that requires
a very robust ESD protection solution to survive in automotive environments. Selecting
the proper protection diode is an integral part of ensuring that the system is not only
protected from high voltage transients, but also minimizes capacitance to allow for
uninhibited signal transmission. TI’s ESD2CANxx devices have high ESD ratings and low
capacitances to provide superior ESD protection for CAN bus interfaces. For device
suggestions, see [Table 5-1](#GUID-0F534CED-1199-476E-9A57-220A0BB7E9E6).

Table 5-1 Device Suggestions

| Device | Vrwm | IEC 61000-4-2/ ISO 10605 Rating (contact) | Capacitance | Package | Supported Protocols |
| --- | --- | --- | --- | --- | --- |
| [ESD2CAN24-Q1](https://www.ti.com/product/ESD2CAN24-Q1) | ±24 V | 30 kV/30 kV | 3 pF | SOT-23, SC70 | LS CAN, HS CAN, CAN FD, CAN SIC |

# 6 References

* Texas Instruments: [*ESD Packaging and Layout Guide*](https://www.ti.com/lit/pdf/SLVAEX9)
* Texas Instruments: [*Introduction to Controller Area Network*](https://www.ti.com/lit/pdf/SLOA101)
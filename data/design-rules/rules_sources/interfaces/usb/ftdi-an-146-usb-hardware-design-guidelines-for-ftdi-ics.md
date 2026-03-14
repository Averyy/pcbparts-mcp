---
source: "FTDI AN_146 -- USB Hardware Design Guidelines for FTDI ICs"
url: "https://ftdichip.com/wp-content/uploads/2020/08/AN_146_USB_Hardware_Design_Guidelines_for_FTDI_ICs.pdf"
format: "PDF 15pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 10326
---

# USB Hardware Design Guidelines for FTDI ICs

## 1. Introduction

While use of FTDI ICs makes USB easy to implement, care must be taken during the hardware design phase of a project to ensure certain practices are followed. This application note provides design guidelines for several common questions that have been asked of the FTDI Applications Engineering team. It is not a full and complete list of PCB design rules but only recommendations.

### 1.1 Overview

USB was introduced in 1998 as a common means of attaching multiple types of peripherals to a personal computer. Since then, it has become the de-facto standard not only for personal computers but embedded systems as well. FTDI provides ICs for all of these USB applications.

### 1.2 Scope

This application note covers USB hardware design as it relates to the FTDI USB ICs. It is not intended to be a comprehensive manual for USB in general. Where appropriate, references will be made to official USB Implementers Forum (USB-IF) documents. The USB-IF documentation should take precedence if there are any conflicts between official USB-IF documentation and this application note.

## 2. USB Hardware Design Practices

### 2.1 Trace Style (Matched Pair, Controlled Impedance, Length)

USB requires two signals to make a single connection. For most data transfers, when one is high, the other is low. This is known as a differential pair. USB has specific shielding, signal and power conductor requirements. These requirements are identified in the USB 2.0 specification, Chapter 7.

At the PCB, the USB connector consists of 4 main signals: VBUS (+5V power), Ground and USB DP and DM. DP and DM are the differential pair. As with twisted pair cabling, these two signals must be closely matched with the following characteristics:

- **Equal length:** Both DP and DM signals must travel the same distance. If one trace ends up longer, then the timing of the signals can be adversely affected and cause data errors.
- **Controlled impedance:** The impedance of the twisted pair cabling must be matched on the PCB in order to minimize signal reflections. USB signals are 90 ohm differential to each other / 45 ohm each to Signal Ground. Most modern PCB layout software can be configured to route both of these signals together with these characteristics.
- **No stubs:** When adding components such as transient voltage protection or additional capacitance for edge rate control, the DP and DM signals should not have any "T"s in order to minimize signal reflections.
- **Ground planes:** With DP and DM being controlled impedance, they should consistently run over the USB Signal Ground plane. There should not be any splits in the plane directly under DP and DM.
- **Overall length:** The DP and DM signals should be made as short as possible. For very short runs, less than 1 cm, it may not be possible to observe the controlled impedance specification. In practice, this is usually acceptable provided the other practices are followed.
- **General design practices:** Keep noisy sources away from the USB signals; avoid right angles; etc.

Figure 2.1: USB signal routing (showing common routing violations)

### 2.2 Electrostatic Protection, Grounds, Common Mode Chokes and Isolation

#### 2.2.1 Electrostatic Protection

FTDI ICs are tested for ESD protection between 2.5 kV and 3 kV. While this is sufficient for most embedded applications, it is often desirable to provide additional ESD protection on the USB DP, USB DM and VBUS signals.

Figure 2.2: ESD protection on USB signals

Transient suppressor devices should be placed as the first board-level device next to any external connection point (i.e. USB connector). This provides the shortest current path to ground, minimizing the possibility of damage elsewhere on the PCB.

#### 2.2.2 Grounds

On designs where a standard USB A-B or A-miniB cable is in use, it is best to avoid directly connecting the USB shield and signal ground on the PCB. Provide pads for a zero-ohm resistor for a DC path or capacitor for a high-frequency path between shield and signal ground. This allows flexibility in the best component selection to minimize signal noise while providing EMC compatibility.

#### 2.2.3 Common Mode Choke

Another means of controlling signal noise is though the use of a common mode choke. Care must be taken to select a component that is rated for USB 2.0 operation. When using a common mode choke it is necessary that both USB signals are on a common core. The USB 2.0 specification notes that while acceptable, use of common mode chokes should be minimized.

#### 2.2.4 Isolation

In applications where the peripheral is in an electrically noisy or potentially dangerous location, galvanic isolation may be provided. This can be done either at the USB interface, or on the peripheral side of the target circuit.

### 2.3 Edge Rate Control

The timing of the rise/fall time of the USB signals is not only dependent on the USB signal drivers, it is also dependent on the system and is affected by factors such as PCB layout, external components and any transient protection present on the USB signals. For USB compliance these may require a slight adjustment. This timing can be modified through a programmable setting stored in the external EEPROM.

Timing can also be changed by adding appropriate passive components to the USB signals:

- **Capacitors** may be placed on each of the USB DP and DM signals to ground:
  - 47 pF / NPO/C0G dielectric for USB 2.0 Full-speed products (FT2xxB, FT2xxR, FT2xxX, FT2232D, VNC1L, VNC2)
  - 0 to 10 pF / NPO/C0G dielectric for USB 2.0 Hi-speed products (FTx232H)

- **Resistors** may be placed in series with USB DP and DM:
  - 27 ohm / 1% for FT2xxB, FT2xxX, FT2232D, FT12x, FT31xD and VNC2 (series termination required for these families)
  - 0 ohm for FT2xxR and FT313H
  - 0 ohm to 10 ohm for FTx232H

Figure 2.3: USB Termination (showing typical placement of termination and transient protection components)

### 2.4 Power Requirements and Considerations

#### 2.4.1 Power Schemes -- USB Peripheral Devices

USB peripheral devices can be configured in one of two settings:

- **Bus-powered:** The entire peripheral draws its power from the USB VBUS signal. Restrictions:
  - Upon initial power-up prior to enumeration, a USB peripheral can draw no more than 100 mA. If the peripheral draws no more than 100 mA under all conditions, it is considered a low-power device.
  - After enumeration and power negotiation, a USB peripheral can draw no more than 500 mA. A peripheral that draws between 100 mA and 500 mA is considered a high-power device.
  - When in USB suspend, a peripheral can draw up to 2.5 mA if it is configured for remote wake capability. If the peripheral does not have remote wake capability, it can draw no more than 500 uA in USB suspend.

- **Self-powered:** Self-powered peripherals provide their own power supply. They do not draw any current from the USB bus. Although a self-powered device does not require USB power while in suspend, it is still necessary to provide a means of waking the system if configured to do so.

**Note:** For all peripheral devices, no power may be back-fed into the USB VBUS signals under any circumstances.

#### 2.4.2 Bulk Capacitance vs. Inrush Current -- USB Peripheral Devices

For bus-powered peripherals, the USB 2.0 specification requires VBUS inrush current limiting equivalent to 10 uF capacitance in parallel with a 44 ohm load for the following conditions:
- Initial plug-in
- Upon enumeration and power negotiation of a high-power circuit
- Upon resuming from a sleep or suspend condition

Larger bulk capacitance may be used, provided power is applied with a soft-start method so that the inrush specification is not exceeded. The FTDI FT-series ICs provide a Power Enable (PWREN#) signal to facilitate switching of a P-channel FET.

Figure 2.4: VBUS PWREN# Soft-Start (showing RC circuit with IRLML6402TRPBF)

#### 2.4.3 Over-Current Protection -- USB Peripheral Devices

- **Bus-powered:** Although most upstream USB host and hub ports provide some form of over-current protection, it may be desirable to provide local protection as well.
- **Self-powered:** Circuit protection is recommended since the upstream USB port is not used for the power supply.
- Common methods are standard and resettable fuses. Inrush and normal operating current requirements will determine the fuse size.

#### 2.4.4 Ferrite Bead Use and Placement -- USB Peripheral Devices

The USB specification prohibits the use of ferrite beads on the USB DP and DM data signals. It does, however, recommend them on the USB power signal (VBUS). It's common to add bulk and decoupling capacitors:

Figure 2.5: USB VBUS Filter (showing ferrite bead BK0603HS330-T with 10 nF, 100 nF, 4.7 uF capacitors)

The 10 nF capacitor and ferrite bead should be placed as close to the USB connector as possible.

Self powered peripherals typically do not require any filtering. The FTDI recommended method of holding the FT-series ICs in reset while a USB cable is not connected:

Figure 2.6: FT-Series Self-Powered Reset Circuit (4.7k and 10k resistor divider from USB_VBUS to RESET#)

#### 2.4.5 USB Host Devices

When designing an embedded USB host product, the design should take into account the power required by each bus-powered device that may be attached. There are numerous USB power control products that can be controlled by GPIO signals and provide feedback whether a peripheral is attempting to consume excess current. At minimum, protection should be provided for at least 500 mA of peripheral current.

## Appendix A -- References

### Suggested Devices

| Device | Description |
|--------|-------------|
| Littelfuse PGB1010603 | TVS |
| Semtech SRV05-4 | TVS |
| Any brand NPO/C0G dielectric, 10% or better | Capacitors (small values) |
| Any brand 1% or better | Resistors |
| Taiyo-Yuden BK0603HS330-T | Ferrite Bead |
| International Rectifier IRLML6402TRPBF | FET |
| Analog Devices ADuM4160 | USB Full-Speed galvanic isolation |

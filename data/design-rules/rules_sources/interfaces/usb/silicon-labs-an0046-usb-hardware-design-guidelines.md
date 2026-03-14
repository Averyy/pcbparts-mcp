---
source: "Silicon Labs AN0046 -- USB Hardware Design Guidelines"
url: "https://www.silabs.com/documents/public/application-notes/an0046-efm32-usb-hardware-design-guidelines.pdf"
format: "PDF 21pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 15618
---

# AN0046: USB Hardware Design Guidelines

This application note gives recommendations on hardware design for implementing USB host and device applications using USB capable EFM32 microcontrollers along with some example schematics for different applications.

## 1. Introduction

Some EFM32 microcontrollers, for instance selected members of the Giant Gecko and Leopard Gecko families, offer on-chip USB support. The USB peripheral embedded on these devices includes the USB PHY and an internal voltage regulator, thus requiring only a minimum number of external components. The on-chip voltage regulator's primary purpose is to power the EFM32 USB PHY. But as it can deliver more current than the EFM32 needs, it can be used to power other components as well, even in non-USB applications.

This document explains how to connect the USB pins of an EFM32 microcontroller and gives general guidelines on PCB design for USB applications.

The EFM32GG-STK3700 has been tested and passes the requirements as a USB Device.

## 2. USB Connection

USB can be operated in 2 different modes: host or device, with hub being a special version of a USB device. A supplement to the USB standard introduces "On-The-Go" mode, which enables a USB product to operate as either a host or a device depending on which kind of controller is in the other end of the cable.

A USB capable EFM32 microcontroller can operate as a host, a device or as an OTG dual role device. EFM32 microcontrollers do not support operation as a USB hub.

### 2.1 EFM32 USB Pin Descriptions

- **USB_DP** -- Data line
- **USB_DM** -- Inverted data line
- **USB_VBUS** -- Sensing if VBUS is connected
- **USB_VBUSEN** -- VBUS Enable, a control signal for enabling VBUS in host applications. Connect to external VBUS switch.
- **USB_DMPU** -- Data Minus Pull-Up, a control signal for enabling external 4.7 kohm pull-up on USB_DM for low-speed operation. If VDD is 3.3 V, pull-up may be connected directly to USB_DMPU pin.
- **USB_ID** -- ID for determining which device should act as bus master in a link between two OTG Dual Role devices. Connect to ID pin on USB Micro-AB receptacle.
- **USB_VREGI** -- Voltage regulator input
- **USB_VREGO** -- Voltage regulator output

### 2.2 EFM32 as USB Host

In host mode, the EFM32 acts as the bus master and is responsible for enumerating the USB devices. The USB host controls data flow on the bus by sequentially polling all devices for data, meaning no device can transmit without a host request. A USB host must supply power to a connected USB device through the +5 V VBUS line.

Design checklist for USB Host:

- Use a 48 MHz (2500 ppm) crystal
- Use a ferrite bead for VBUS. Place near receptacle.
- Use a switch that can shut off VBUS if current exceeds 500 mA
- Provide at least 96 uF decoupling capacitance on VBUS. Place near USB receptacle.
- Terminate D+ and D- with 15 ohm serial resistors. Place near EFM32.
- Use an ESD protection device. Place near USB receptacle.
- Select a USB Series A type receptacle

### 2.3 EFM32 as USB Device

USB devices are bus slaves that provide functionality to the USB host. As a USB host provides +5 V over the VBUS line, a USB device can either be powered over the USB cable or be self powered.

#### 2.3.1 Self Powered Device

Design checklist:

- Use a 48 MHz (2500 ppm) crystal
- Use a ferrite bead for VBUS. Place near receptacle.
- Provide at least 4.7 uF decoupling capacitance on USB_VREGI. Place near EFM32.
- Keep total load capacitance on VBUS below 10 uF
- Provide at least 1 uF decoupling capacitance on USB_VREGO. Place near EFM32.
- Terminate D+ and D- with 15 ohm serial resistors. Place near EFM32.
- Use an ESD protection device. Place near USB receptacle.

#### 2.3.2 Bus Powered Device

Design checklist:

- Use a 48 MHz (2500 ppm) crystal
- Use a ferrite bead for VBUS. Place near receptacle.
- Provide at least 4.7 uF decoupling capacitance on USB_VREGI. Place near EFM32.
- Keep total load capacitance on VBUS below 10 uF
- Provide at least 1 uF decoupling capacitance on USB_VREGO. Place near EFM32.
- Connect USB_VREGO to VDD
- Provide decoupling capacitance on VDD as per AN0002 Hardware Design Considerations
- Terminate D+ and D- with 15 ohm serial resistors. Place near EFM32.
- Use an ESD protection device. Place near USB receptacle.

#### 2.3.3 Low-speed

Speed identification of USB devices is done with a pull-up on one of the data lines. A low-speed capable device is identified by a 1.5 kohm pull-up resistor on the D- line. The internal pull-up resistor on EFM32 microcontrollers is approximately 2.2 kohm, so an external 4.7 kohm resistor must be placed in parallel to be standard compliant. This resistor should be connected to the USB_DMPU pin so it can be switched on and off by the USB PHY.

Even if omitting the external pull-up resistor will most likely work, it will not be USB compliant because the internal resistor value is outside the USB specification.

Low-speed mode is defined to support a limited number of low-bandwidth devices, such as mice. Low-speed devices are not allowed to use standard USB cables.

Design checklist:

- Use a 48 MHz (2500 ppm) crystal
- Use a ferrite bead for VBUS. Place near receptacle.
- Connect a 4.7 kohm resistor between USB_DMPU and D-
- Provide at least 4.7 uF decoupling capacitance on USB_VREGI. Place near EFM32.
- Keep total load capacitance on VBUS below 10 uF
- Provide at least 1 uF decoupling capacitance on USB_VREGO. Place near EFM32.
- Terminate D+ and D- with 15 ohm serial resistors. Place near EFM32.
- Use an ESD protection device. Place near USB receptacle or where the cable connects to the PCB.
- Do not use a standard USB receptacle

If VDD is below USB_VREGO (3.3 V) the external pull-up should be connected to USB_VREGO instead of USB_DMPU and a switch should be used to turn it on or off through USB_DMPU. Otherwise, there will be a leakage current from VREGO to VDD through the pull-up.

### 2.4 EFM32 as USB On-The-Go Dual Role Device

OTG is not yet supported in the EFM32 USB stack, but EFM32 hardware is OTG capable.

A dual role capable device must use a Micro-AB receptacle which can accept both a Micro-A plug and a Micro-B plug. The device where the Micro-A plug is inserted will act as host and must provide +5 V on VBUS. The plug type is detected by the ID pin, which is shorted to GND on a Micro-A plug.

Design checklist:

- Use a 48 MHz (2500 ppm) crystal
- Use a ferrite bead for VBUS. Place near receptacle.
- Connect the ID pin on the receptacle to USB_ID
- Ensure that total capacitance on VBUS is less than 6.5 uF
- Provide at least 1 uF decoupling capacitance on USB_VREGO. Place near EFM32.
- Terminate D+ and D- with 15 ohm serial resistors. Place near EFM32.
- Use an ESD protection device. Place near USB receptacle or where the cable connects to the PCB.
- Use a USB Series Micro-AB receptacle

## 3. PCB Design Guidelines

### 3.1 Recommended Routing Rules of Thumb

- Route D+ and D- as 90 ohm differential pair
- Always provide a good return path (ground) for current
- Do not route over a gap in the reference plane
- Keep away from the edge of the reference plane
- Keep skew less than 400 ps
- Route D+ and D- on top layer
- Route D+ and D- as short as reasonably possible

### 3.2 PCB Stackup

The two common approaches are to either route high speed signals on an inner layer or on the top layer. The advantage of an inner layer is improved noise immunity and avoiding track impedance discontinuities when routing under components and connectors. The benefit of outer layer routing is avoiding vias which easily cause discontinuities in the return current path. For USB signals on EFM32 microcontrollers, the preferred solution is normally to route on an outer layer, as PCB traces are usually short.

Regardless of inner or outer layer routing, signals should always be routed over a solid reference plane. The PCB should have minimum 2 layers.

### 3.3 Routing

Common practice is to apply transmission line models when the trace length is more than 1/10th of the wavelength of the highest frequency component. USB specifies a minimum rise time of 4 ns, which equals a maximum signal bandwidth of 87.5 MHz or a minimum wavelength of 1.7 meters on a typical PCB trace. Thus if PCB traces are shorter than 170 mm, the characteristic impedance of a track may not be critical. However, good design practice is to route USB signals as an impedance matched differential pair.

#### 3.3.1 Differential Pairs

The USB data lines, D- and D+, should be routed as a differential pair. The trace impedance should be matched to the USB cable differential impedance, which is nominally 90 ohms for the signal pair.

The impedance of a signal track is mainly determined by its geometry (trace width and height above the reference plane) and the dielectric constant of the material. When two tracks are closely spaced, they will be coupled and the differential impedance depends on the distance between them.

If the two traces are spaced far apart, the differential impedance will be twice the impedance of each trace. Reducing the distance between the traces decreases the differential impedance due to coupling. To create a 90 ohm differential pair, the single ended impedance of each trace should be above 45 ohms.

**Skew:** Keep less than 1/10th of the fastest rise time. For USB full-speed this translates to 400 ps or 60 mm. This is the total skew over the entire communication link, so skew in the USB cable (max 100 ps per spec) must be included. This leaves a maximum of 300 ps (45 mm) for host and device combined.

When routing from one layer to another, provide a path for the return signals. Even differential signals use a reference plane as return path.

**Stubs:** Should be avoided as they may cause signal reflections. If a test point is desired, route the signal through the test point in a fly-by manner, rather than having a long trace from the signal to the test point.

#### 3.3.2 Reference Planes

Routing high speed signals across a split in the reference plane should be avoided. The return current path follows close to the signal trace at high frequencies. If the trace crosses a split, the return current follows a longer path, creating a larger loop area which will both radiate more and be more susceptible to noise.

If crossing a split cannot be avoided, provide a path for the high frequency return current by connecting the two planes with a 100 nF capacitor (0603 or smaller package) per trace located near the high speed trace.

When crossing from one plane to another, the crossing angle should be 90 degrees.

### 3.4 Input Impedance

The USB standard specifies a maximum input capacitance of 150 pF for a downstream port (host mode) and 100 pF on an upstream port (device mode).

To ensure a constant impedance, route USB signals more than 3*H away from the edge of the reference plane (where H is the height above the plane).

## 4. USB Electrical Specifications

The EFM32 USB peripheral is USB 2.0 compliant. The USB 2.0 standard specifies three data rates: Low-speed (1.5 Mbps), Full-speed (12 Mbps), and High-speed (480 Mbps). The EFM32 supports full-speed and low-speed.

### 4.1 Signalling Levels

Low-speed and full-speed: VOL = 0.0 - 0.3 V, VOH = 2.8 - 3.6 V

Low-speed: Bit period (UI) = 667 ns. Full-speed: Bit period (UI) = 83 ns.

### 4.2 Signal Rise and Fall Times

Full speed: Rise/fall time (10-90%) = 4-20 ns

Low speed: Rise/fall time (10-90%) = 75-300 ns

### 4.3 Speed Identification

USB hosts have a weak pull-down resistor on both data lines, and devices have a strong pull-up on one data line. Nominal values: 15 ohm for the pull-downs on the host side, 1.5 kohm for the pull-up on the device-end.

- Full-speed capable devices have the pull-up on D+
- Low-speed capable devices have the pull-up on D-

High-speed USB connections are initialized as full-speed before a negotiation sequence transitions to high-speed.

### 4.4 USB Connectors

- Series A receptacles: USB hosts
- Series B receptacles: USB devices
- Series Micro-AB receptacles: On-the-Go devices capable of both host and device mode

## 5. Power

### 5.1 USB Voltage Regulator

The EFM32 features an on-chip 5 V to 3.3 V regulator to power the internal USB PHY. As the regulator can output up to 50 mA, it can also power both the rest of the EFM32 and external components.

If another 3.3 V source is available, the USB PHY can be powered by applying 3.3 V to USB_VREGO. In this configuration, USB_VREGI must also be connected to 3.3 V to stabilize the regulator.

The voltage regulator can also be used even if the USB functionality is not used.

### 5.2 Bus Power Switch

A simple MOSFET-based switch (using an FDC6420C dual N/P-channel MOSFET) enables a self-powered device to switch from battery power to +5 V when connected to a USB host, extending battery life. USB VBUS controls the switching transistors. When VBUS is present, the N-channel FET is switched on and the P-channel FET is switched off, and vice versa. The P-channel transistor is oriented with the source towards VDD to prevent applying high voltage to the battery through the body diode.

Limitations:
- MOSFETs depend on a certain Vgs voltage to switch on/off
- When switching VBUS on/off, there is a short time when both transistors are off and VDD drops slightly
- Switching characteristics are temperature dependent

The circuit has been tested on battery voltages above 2.5 V in temperatures from 0 to 55 degrees C.

## 6. Environmental Considerations

### 6.1 Isolation of Cable Shield

Any cable will act as an antenna that can radiate and pick up electromagnetic noise. As the USB cable shield is terminated to the USB receptacle chassis, care should be taken to decouple the USB receptacle chassis from signal ground.

To avoid EMI and EMC problems, surround the USB connector with a solid ground plane. A ferrite bead can be used to isolate the +5 V line of the connector.

### 6.2 ESD Protection

The USB pins on EFM32 devices are tolerant of a 2 kV discharge according to the Human Body Model (HBM). HBM is only intended to model ESD events in a production environment. System level ESD tests are defined in IEC 61000-4-2.

There is a significant difference in both peak level and rise-time between HBM and IEC 61000-4-2. Devices whose protection is only HBM compliant can be damaged by the quick initial ESD spike before protection circuits activate.

External ESD protection must be used for the USB interface. The EFM32 kits use an NXP IP4220CZ6 ESD protection device. Although this device has a maximum output voltage of 9 V (higher than the EFM32 tolerance rating), most of the energy of an ESD event is dissipated in the ESD protection device, and the residual energy is within safe levels.

The EFM32GG-STK3700 Giant Gecko Starter Kit has been tested according to IEC 61000-4-2 and has passed an 8 kV contact discharge.

ESD protection circuitry should be placed near the USB connector to prevent high voltages and frequencies from propagating far into the PCB.

## 7. Further Reading

- Universal Serial Bus Specification (Revision 2.0) including USB On-The-Go and Embedded Host Supplement
- AN0002 Hardware Design Considerations (Silicon Labs)
- AN0016 Oscillator Design Considerations (Silicon Labs)
- High Speed USB Platform Design Guidelines (Intel)

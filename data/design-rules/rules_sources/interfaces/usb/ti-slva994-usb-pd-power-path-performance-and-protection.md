---
source: "TI SLVA994 -- USB PD Power Path Performance and Protection"
url: "https://www.ti.com/lit/an/slva994/slva994.pdf"
format: "PDF 23pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 16734
---

# TPS65987DDH Power Path Performance and Protection

## Abstract

There are many non-compliant PD (Power Delivery) devices available in the market that do not correctly follow the USB PD specification. These devices could severely damage systems by pulling too much current, shorting VBUS to ground, or by having 20 V on VBUS on initial plug in. The TPS65987DDH protects against all of these non-compliant devices while still being able to operate with them. This document describes the functionality of the overcurrent protection (OCP) mechanism of the TPS65987DDH device and how to program it using the Application Customization Tool. This guide defines the peak current and provides steps on how to set the threshold of OCP on the TPS65987DDH device as well as configuring the various protection settings.

## 1. Introduction

Through the introduction of USB Power Delivery (PD) the capabilities of each USB Type-C port was greatly expanded. Each USB Type-C port can now support bidirectional power up to 100 W. This allows for devices to be charged from multiple different ports. When supporting complex USB Type-C and PD power architectures, it is crucial to have adequate protection circuitry to prevent reverse current, overcurrent, overvoltage, or undervoltage. Texas Instruments TPS65987DDH PD controllers have integrated high voltage power paths with full protection built in.

### 1.1 Related Documents

- TPS65987DDH Dual Port USB Type-C and USB PD Controller, data sheet
- TPS65987DDH Host Interface Technical Reference Manual

## 2. Typical Power Path Applications

On the TPS65988DH, the two internal power paths are commonly used as the power source paths for each of the Type-C ports. Per the USB Power Delivery specification, it is mandatory to have power path protection on the power source path. The TPS65988DH integrates this protection on the internal power paths which makes setting up this application simple. If the application requires both source and sink power paths for each port, the TPS65988DH supports the control of two external PFET power paths. It is recommended to add external reverse current protection for the external power paths.

The TPS65987DDH is a single port Type-C and PD controller that contains two internal power paths. Applications using the TPS65987DDH can easily use the two internal power paths to cover both source and sink use cases. No external protection circuitry is required when using both power paths on the TPS65987DDH.

## 3. Overcurrent Protection (OCP) and Overcurrent Clamping (OCC)

### 3.1 FW OCP vs HW OCP

The TPS65987DDH implements overcurrent protection through both firmware (FW) and hardware (HW). This dynamic overcurrent protection allows the TPS65987DDH to safely protect the system while still being able to pass through large inrush currents seen by some non-compliant PD devices available in the market.

When initially connecting a device to a TPS65987DDH, the TPS65987DDH will enable the configured source power path to output 5 V. When 5 V is on VBUS, the TPS65987DDH will implement both overcurrent clamping and hardware overcurrent protection. The overcurrent clamping is implemented for 5 V power contracts as the 5 V rail is typically shared by numerous devices in the system. The overcurrent clamping at 5 V will prevent the 5 V rail from dropping too low when a large current is applied on VBUS and browning out other devices in the system. The overcurrent clamp trip point is configurable through the Application Customization GUI tool. If a current greater than 10 A is seen on VBUS during a 5 V contract, the hardware OCP will open the VBUS FET to protect the system.

When negotiating a high voltage contract on VBUS (VBUS > 5 V), the TPS65987DDH will dynamically adjust the hardware OCP trip point from 10 A to 20 A while the VBUS voltage is transitioning from 5 V to the negotiated high voltage level. This mechanism is implemented as there are many PD devices available in the market that will draw a very large amount of inrush current when the VBUS voltage transitions. After the voltage transition is complete, the hardware overcurrent protection trip point will return to 10 A. During a high voltage contract, the TPS65987DDH will implement overcurrent protection through firmware. The FW OCP is a running average of the current through the internal FET during the last 10 ms. If the average current going through the FET during the last 10 ms of operation is greater than the PDO current setting, the TPS65987DDH will open the FET.

The timing between T1 (voltage begins to rise) and T2 (HW OCP setting returns to 10 A) is roughly 100 ms.

### 3.2 FW OCP

#### 3.2.1 Overcurrent Clamping (OCC) and "Soft Short" Protection

When the TPS65987DDH is sourcing 5 V on VBUS, the TPS65987DDH integrates overcurrent clamping into the power paths. In most customer systems, the 5 V rail is shared by many devices and cannot risk browning out due to an overcurrent event on VBUS. The overcurrent clamp point is programmable through the configuration tool. During an overcurrent clamping protection event, the TPS65987DDH will clamp the current on VBUS at the programmed value by regulating the gate of an internal FET to increase the Rds On. It will then open the power path once a deglitch timer of 640 us has reached 0 and the current still exceeds the overcurrent clamp point. The 640 us countdown serves as an overcurrent clamp deglitch to ensure the overcurrent clamp protection is not too sensitive.

The TPS65987DDH clamps current on implicit Type-C contracts and also PD contracts. With an implicit Type-C contract, the overcurrent clamp point is configured in the Port Control register (0x29). Setting the "Type-C Current" field adjusts the pull-up resistance on the CC line to determine the allowed current with a default Type-C connection. The strongest pull-up allows for 3000 mA, the medium pull-up allows for 1500 mA, and the weakest pull-up allows for 900 mA.

The overcurrent clamp point for a PD contract can be adjusted in the Transmit Source Capabilities register (0x32) in the Application Customization Tool. The maximum current field can be set between 0 and 10.23 A with 10 mA increments. The peak current percentage field in the Transmit Source Capabilities can be used to increase the OCP trip point. For example, if you set a 5 V and 3 A Source Capability with 200% peak current, the overcurrent clamp point will be set around 6 A.

**NOTE:** Overcurrent Clamping is only implemented when the TPS65987DDH is sourcing 5 V on VBUS.

**Soft Short behavior:** The VBUS FET in the TPS65987DDH will try to maintain a constant current across it from PPHV to VBUS when a soft short occurs. A soft short is when a load is present on VBUS that is below the 10 A hard short limit. When a soft short is present, the TPS65987DDH will start the 640 us overcurrent clamp timeout before opening the FET. During this 640 us, the TPS65987DDH will try to maintain a constant current across the FET by dropping the voltage on VBUS slightly through increasing the Rds On of the internal FET.

#### 3.2.2 How Overcurrent Clamp Setting in GUI Relates to Overcurrent Clamp Setting in the TPS65987DDH

The data sheet contains a graph with "Overcurrent Clamp Firmware Selectable Settings" for IOCC. When using the Application Customization Tool to program the overcurrent clamp point, the internal firmware will select one of these programmable settings as the overcurrent clamp point.

For example, when setting the overcurrent clamp point to 3 A with 100% Peak current, the internal firmware will select the setting with the minimum trip point of 3.060 A and maximum of 3.74 A. With that, the TPS65987DDH would clamp current at a minimum of 3.060 A and a maximum of 3.74 A.

However, if setting the overcurrent clamp point to 3.10 A, the internal FW would have to select the setting with a minimum of 3.30 A and maximum of 4.033 A, as we cannot clamp the current before the selected setting.

**Table 1. IOCC Programmable Settings for Overcurrent Clamp Point**

| MIN (A) | TYP (A) | MAX (A) |
|---|---|---|
| 1.140 | 1.267 | 1.393 |
| 1.380 | 1.533 | 1.687 |
| 1.620 | 1.800 | 1.980 |
| 1.860 | 2.067 | 2.273 |
| 2.100 | 2.333 | 2.567 |
| 2.340 | 2.600 | 2.860 |
| 2.580 | 2.867 | 3.153 |
| 2.820 | 3.133 | 3.447 |
| 3.060 | 3.400 | 3.740 |
| 3.300 | 3.667 | 4.033 |
| 3.540 | 3.933 | 4.327 |
| 3.780 | 4.200 | 4.620 |
| 4.020 | 4.467 | 4.913 |
| 4.260 | 4.733 | 5.207 |
| 4.500 | 5.000 | 5.500 |
| 4.740 | 5.267 | 5.793 |
| 4.980 | 5.533 | 6.087 |
| 5.220 | 5.800 | 6.380 |
| 5.460 | 6.067 | 6.673 |
| 5.697 | 6.330 | 6.963 |

### 3.3 Hardware Overcurrent Protection (HW OCP)

In the USB PD specification, the power source is required to implement overcurrent protection. An overcurrent event can be caused by a device pulling too much current from VBUS, or VBUS accidentally getting shorted to ground. All of the power path testing was completed with the TPS65987DEVM. The TPS65987DEVM uses the LM3489 variable DC/DC regulator to control the voltage at PPHV.

The overcurrent trip point is set dynamically in the TPS65987DDH and optimized through internal firmware. Typically, the overcurrent protection point is set at 10 A. However, when a high voltage PD contract is negotiated and VBUS begins to transition from 5 V to the negotiated high voltage, the overcurrent protection point will change from 10 A to 20 A during the voltage transition and return to 10 A once the voltage has settled. The overcurrent protection point is changed to 20 A when the "Request" message is received in PD traffic and returns to 10 A 100 ms after the request message.

#### 3.3.1 HW OCP with VBUS = 5 V

The internal VBUS FET is able to open in less than 15 us during a VBUS short to ground. Typical external FET paths will take longer than 150 us to open during a hard short. This can allow significant damage to the system as the PPHV voltage will drop with a VBUS short to ground.

#### 3.3.2 HW OCP with VBUS = 9 V

As the voltage on VBUS increases, the current seen on the VBUS power path during a hard short increases. The power path is able to open within 17 us and the current through the power path is roughly 22 A.

#### 3.3.3 HW OCP with VBUS = 15 V

When VBUS is 15 V, the current spike on VBUS exceeds 30 A. However, the TPS65987DDH is able to open the VBUS FET within 10 us. The TPS65987DDH has a hardware interrupt set to open the power path once the current exceeds 30 A.

#### 3.3.4 HW OCP with VBUS = 20 V

A VBUS short to GND at 20 V is a tricky short to protect against. The current increases very rapidly; the analog circuitry catches it when it exceeds 30 A and immediately opens the power path. This all happens in less than 7 us and the system remains protected from the short to ground.

## 4. Reverse Current Protection

When designing a complex power architecture with the intention of supporting multiple different source and sink paths, it is crucial to ensure that each power path is protected from reverse currents. In this example, a two port notebook is being emulated using two TPS65987DEVMs configured as TPS65987DDH.

In two port systems, what is connected to port 1 should have no transverse effects on port 2. Both power paths close onto the same SYSPWR rail. When a 5 V adapter is plugged into port 2 and a 20 V adapter is plugged into port 1, port 2 will have to enable reverse current protection. In this scenario, the SYSPWR voltage is higher than the VBUS voltage offered by the 5 V PD adapter connected in port 2. With no RCP, the 5 V PD adapter would be back fed with 20 V, causing damage to it and potentially to the system.

The TPS65987DDH has internal back-to-back VBUS FETs. In this RCP event, port 2 VBUS FET will enable one of the back-to-back FETs and disable the other one as a "Blocking" FET. This will prevent any current being back fed into the 5 V PD adapter from the SYSPWR rail.

### Fast Recovery RCP

When the 20 V PD adapter is disconnected, the port with the 5 V adapter must come out of RCP when the SYSPWR rail drops to 5 V. The TPS65987DDH monitors the system side voltage and waits until SYSPWR has reached 5 V before enabling the power path with the 5 V PD adapter. This prevents any potential for reverse current damage.

When VBUS1 exceeds 5 V after the 20 V adapter is reconnected, VBUS2 quickly enables RCP. The small spike seen is caused by the sudden disconnect of the system load when the power path is blocked by RCP.

### 4.1 Fast Recovery RCP with System Loading

In a real world system, there will always be a load on the system power rail. When VBUS is the only source of power, the device relies on the TPS65987DDH's fast recovery RCP feature to keep the system alive when the VBUS voltage changes. A real world example is a laptop with no battery connected.

Testing with a constant power load (DC/DC converter outputting 12 V at 5 A = 60 W) and only 60 uF on the system power rail (minimum recommended is 100 uF) shows that when the 20 V supply is removed, the 15 V PD adapter comes out of RCP and begins supplying SYSPWR. The current swaps to VBUS and SYSPWR drops to 15 V to match VBUS while drawn power remains constant.

## 5. Over-Voltage Protection (OVP)

The TPS65987DDH integrates overvoltage protection (OVP) on both the internal and external power paths. The TPS65987DDH monitors the VBUS voltage actively during run-time and will open the FET when the voltage exceeds the expected maximum. The OVP trip point is configurable through the application customization tool and can be set to trip at 5%, 10%, or 15% of the expected maximum voltage of the negotiated PD contract.

The OVP trip point can also be set to a hard coded value by selecting "Disconnect VBUS if voltage exceeds OVPTripPoint" in the Overvoltage Protection Usage field of the Port Configuration register (0x28). This Overvoltage Trip Point is also configurable in the Port Configuration register.

**Recommended configuration:** Set to "Disconnect VBUS if voltage exceeds 5% of expected max." With this setting, the internal firmware will adjust the OVP Trip Point internally based on the source or sink voltage.

**Warning:** Setting the "Over Voltage Protection Usage" field to "Disconnect VBUS if voltage exceeds OVPTripPoint" is not a recommended configuration when sourcing 5 V. This allows you to select an OVP Trip Point manually that would be applied to any PD source voltage. If you set the OVP Trip Point to 24 V, you will not open VBUS until the voltage exceeds 24 V, even when sourcing 5 V.

### 5.1 VBUS Ramp On Open Switches

If a non-compliant PD adapter is connected (e.g., one with 20 V on VBUS on initial plug in, or VBUS ramping to 20 V outside of the PD spec), I(VBUS) will be very small and only enough to charge the VBUS caps present on the PCB. The SYSPWR rail and PPHV are unaffected as both internal and external FET paths will not enable. When the power path is off, the blocking diode in the back-to-back FET isolates the system from any non-compliant behavior on VBUS.

## 6. Undervoltage Protection (UVP)

The TPS65987DDH integrates undervoltage protection (UVP) for the internal power paths on the VBUS side of the FETs. The UVP trip point is configurable through the configuration tool and is set to a percentage of the nominal voltage.

Example with a 20 V contract (minimum expected voltage per USB PD 3.0 spec is 18.5 V):

| UVP Setting | Expected Trip Point | Measured Trip Point |
|---|---|---|
| 5% | ~17.575 V | 17.7 V |
| 20% | ~14.8 V | 14.7 V |
| 50% | ~9.25 V | 9.5 V |

When operating as a sink, the UVP settings will trip slightly lower to compensate for potential cable losses.

For 5 V contracts, VSafe5Vmin is 4.75 V from the PD spec:
- 5% UVP should trip around 4.51 V
- 20% should trip around 3.8 V
- 50% should trip around 2.38 V

## 7. Error Recovery

When there is a protection event on VBUS (such as opening the FET after the overcurrent clamp timeout or after an overcurrent protection event), the TPS65987DDH will enter the Error Recovery state as defined in the USB Type-C specification. When the TPS65987DDH enters Error Recovery, it removes the termination from the CC1 and CC2 pins for at least 25 ms. During this timing, the CC lines shall present a high-impedance to ground. After the Error Recovery timeout has completed, the TPS65987DDH will return to an Unattached.SNK state or an Unattached.SRC state depending on the configuration of the port. Error Recovery state can be interpreted as a disconnect and reconnect.

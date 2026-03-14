---
source: "TI SPRABT8A -- AM335x USB Layout Guidelines"
url: "https://www.ti.com/lit/an/sprabt8a/sprabt8a.pdf"
format: "PDF 13pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 13590
---

# AM335x and AM43xx USB Layout Guidelines

## Abstract

This application report discusses best-practice layout guidelines when implementing a universal serial bus (USB).

## 1. Background

The primary source of energy in a USB 2.0 design is the differential signal pair, DATA+ (DP), and DATA- (DM). Depending on the type of USB connection, this differential interface can operate at frequencies as high as 240 MHz, which can present a significant noise source for board designs that do not take steps to ensure signal isolation and overall signal quality.

## 2. USB Layout Guide

### 2.1 Routing and Placement

Use the following routing and placement guidelines when laying out a new design for the USB. These guidelines help minimize signal quality and electromagnetic interference (EMI) problems on a four-or-more layer evaluation module (EVM).

- Route the USB DP and DM signals very early in the layout process to ensure adequate spacing, length matching, and isolation.
- The USB DP and DM signals should be routed using the "3W" rule where the traces are separated from each other by 3x their width. Isolating DP and DM from other signals by 5x trace width is also highly recommended to minimize crosstalk.
- While not always possible, isolating the DP/DM pair from other signals using ground-guard traces further minimizes crosstalk.
- Route the high-speed USB differential signals with minimum trace lengths.
- The USB DP and DM signals should be trace-length matched as closely as possible. Maximum trace-length mismatch between the USB signal pair (DP/DM) should not exceed 150 mils.
- Route the high-speed USB signals on the plane closest to the ground plane whenever possible.
- Route the high-speed USB signals using a minimum of vias and corners. This reduces signal reflections and impedance changes.
- When it becomes necessary to turn 90 deg, use two 45 deg turns or an arc instead of making a single 90 deg turn. This reduces reflections on the signal traces by minimizing impedance discontinuities.
- Do not route USB traces under or near crystals, oscillators, clock signal generators, switching regulators, mounting holes, magnetic devices or ICs that use or duplicate clock signals.
- Do not place stubs on the high-speed USB signals because they may cause signal reflections.
- Route all high-speed USB signal traces over continuous planes (VCC or GND), with no interruptions. Avoid crossing over anti-etch, commonly found with plane splits.

### 2.2 Analog, Digital, and PLL Partitioning

If separate power planes are used, they must be tied together at one point through a low-impedance bridge or preferably through a ferrite bead. Care must be taken to capacitively decouple each power rail close to the device. The analog ground, digital ground, and PLL ground must be tied together to the low-impedance circuit board ground plane.

### 2.3 Board Stackup

Because of the high frequencies associated with the USB, a printed circuit board with at least four layers is recommended.

**Table 2-1. Suggested PCB Stackup**

| 4-Layer | 6-Layer | 8-Layer | 10-Layer |
|---------|---------|---------|----------|
| SIGNAL | SIGNAL | SIGNAL | SIGNAL |
| GROUND | GROUND | GROUND | GROUND |
| POWER | SIGNAL(2) | SIGNAL | SIGNAL(2) |
| SIGNAL | SIGNAL(2) | POWER | SIGNAL(2) |
| | POWER/GROUND(1) | POWER/GROUND(1) | POWER |
| | SIGNAL | SIGNAL | POWER/GROUND(1) |
| | | GROUND | SIGNAL(2) |
| | | SIGNAL | SIGNAL(2) |
| | | | GROUND |
| | | | SIGNAL |

(1) Plane may be split depending on specific board considerations. Ensure that traces on adjacent planes do not cross splits.

(2) Directly adjacent signal layers should be routed at a 90-degree offset to each other.

The majority of USB signal traces should run on a single layer, preferably SIGNAL1. Immediately adjacent to this layer should be the GND plane, which is solid with no cuts. Avoid running signal traces across a split in the ground or power plane. Minimizing the number of signal vias reduces EMI by reducing inductance at high frequencies.

### 2.4 Cable Connector Socket

Short the cable connector sockets directly to a small chassis ground plane that exists immediately underneath the connector sockets. This shorts EMI (and ESD) directly to the chassis ground before it couples onto the USB cable. This etch plane should be as large as possible, but all the USB connector pins must have the board signal GND plane run underneath to provide a reference path. If needed, scoop out the chassis GND ground etch to allow for the signal ground to extend under the connector pins. Note that the etches coming from pins 1 and 4 (VBUS power and GND) should be wide and via-ed to their respective planes as soon as possible, respecting the filtering that may be in place between the connector pin and the plane.

Place a ferrite in series with the cable shield pins near the USB connector socket to prevent EMI from coupling onto the cable shield. The ferrite bead between the cable shield and ground may be valued between 10 ohm and 50 ohm at 100 MHz; it should be resistive to approximately 1 GHz. To prevent EMI from coupling onto the cable bus power wire (a very large antenna), a ferrite can be placed in series with VBUS near the USB connector pin 1. The ferrite bead between connector pin 1 and bus power may be valued between 47 ohm and approximately 1000 ohm at 100 MHz. It should continue being resistive out to approximately 1 GHz.

Figure 2-1. USB Connector (schematic showing SHIELD_GND, GND, DP, DM, VBUS with ferrite beads)

### 2.5 DP/DM Trace

Place the SoC as close as possible to the USB 2.0 connector. The signal swing during high-speed operation on the DP/DM lines is relatively small (400 mV +/- 10%), so any differential noise picked up on the twisted pair can affect the received signal. When the DP/DM traces are not shielded, the traces tend to behave like an antenna and pick up noise generated by the surrounding components in the environment. To minimize the effect of this behavior:

- DP/DM traces should always be length matched and kept as short as possible or the eye opening may be degraded.
- Route DP/DM traces close together for noise rejection on differential signals, parallel to each other and within 100 mils in length of each other (start the measurement at the chip package boundary, not to the balls or pins).
- A high-speed USB connection is made through a shielded, twisted pair cable with a differential characteristic impedance of 90 ohm +/-15%. In layout, the impedance of DP and DM should each be 45 ohm +/- 10%.
- DP/DM traces should not have any extra components to maintain signal integrity. For example, traces cannot be routed to two USB connectors.
- No termination of the DP/DM pair is required.
- No de-coupling caps on the DP/DM pair are required.
- USB 2.0-specific ESD clamps are recommended and should be placed as close as possible to the USB connector.
- If a common mode choke is needed, it should be placed as close as possible to the USB connector (the ESD clamp device should be closer).

### 2.6 DP/DM Vias

When a via must be used, increase the clearance size around it to minimize its capacitance. Each via introduces discontinuities in the signal's transmission line and increases the chance of picking up interference from the other layers of the board.

**Note:** Test points of any kind are NOT permitted on the DP/DM pair.

### 2.7 Image Planes

An image plane is a layer of copper (voltage plane or ground plane), physically adjacent to a signal routing plane. The use of image planes provides a low impedance, shortest possible return path for RF currents. For a USB board, the best image plane is the ground plane because it can be used for both analog and digital circuits.

- Do not route traces so they cross from one plane to the other. This can cause a broken RF return path resulting in an EMI radiating loop. This is important for higher frequency or repetitive signals. Therefore, on a multi-layer board, it is best to run all clock signals on the signal plane above a solid ground plane.
- Avoid crossing the image power or ground plane boundaries with high-speed clock signal traces immediately above or below the separated planes. This also holds true for the twisted pair signals (DP, DM). Any unused area of the top and bottom signal layers of the PCB can be filled with copper that is connected to the ground plane through vias.

Figure 2-2. Do Not Cross Plane Boundaries

- Do not overlap planes that do not reference each other. For example, do not overlap a digital power plane with an analog power plane as this produces a capacitance between the overlapping areas that could pass RF emissions from one plane to the other.

Figure 2-3. Do Not Overlap Planes

- Avoid image plane violations. Traces that route over a slot in an image plane results in a possible RF return loop.

Figure 2-4. Do Not Violate Image Planes

### 2.8 Power Regulators

Switching power regulators are a source of noise and can cause noise coupling if placed close to sensitive areas on a circuit board. Switching power regulators should be kept away from the DP/DM signals.

## 3. Electrostatic Discharge (ESD)

International Electronic Commission (IEC) 61000-4-xx is a set of approximately 25 testing specifications from the IEC. IEC ESD Stressing is done both un-powered and with power applied, and with the device functioning. There must be no physical damage, and the device must continue working normally after the conclusion of the testing. Typically, equipment has to pass IEC stressing at 8 kV contact and 15 kV air discharge, or higher. To market products/systems in the European community, all products/systems must be CE compliant and have the CE Mark. To obtain the CE Mark, all products/systems need to go through and pass IEC standard requirements; for ESD, it is 61000-4-2. 61000-4-2 requires that the products/systems pass contact discharge at 8 kV and air discharge at 15 kV. When performing an IEC ESD Stressing, only pins accessible to the outside world need to pass the test. The system into which the integrated circuit (IC) is placed makes a difference in how well the IC does. For example:

- Cable between the zap point and the IC attenuate the high frequencies in the waveform.
- Series inductance on the PCB board attenuates the high frequencies.
- Unless the capacitor's ground connection is inductive, capacitance to ground shunts away high frequencies.

### 3.1 IEC ESD Stressing Test

#### 3.1.1 Test Mode

The IEC ESD Stressing test is done through two modes: contact discharge mode and air discharge mode.

For the contact discharge test mode, the preferred way is direct contact applied to the conductive surfaces of the equipment under test (EUT). In the case of the USB system, the conductive surface is the outer casing of the USB connector. The electrode of the ESD generator is held in contact with the EUT or a coupling plane prior to discharge. The arc formation is created under controlled conditions, inside a relay, resulting in repeatable waveforms; however, this arc does not accurately recreate the characteristic unique to the arc of an actual ESD event.

#### 3.1.2 Air Discharge Mode

The air discharge usually applies to a non-conductive surface of the EUT. Instead of a direct contact with the EUT, the charged electrode of the ESD generator is brought close to the EUT, and a spark in the air to the EUT actuates the discharge. Compared to the contact discharge mode, the air discharge is more realistic to the actual ESD occurrence. However, due to the variations of the arc length, it may not be able to produce repeatable waveform.

#### 3.1.3 Test Type

The IEC ESD Stressing test has two test types: direct discharge and indirect discharge. Direct discharge is applied directly to the surface or the structure of the EUT. It includes both contact discharge and air discharge modes. Indirect discharge applies to a coupling plane in the vicinity of the EUT. The indirect discharge is used to simulate personal discharge to objects which are adjacent to the EUT. It includes contact discharge mode only.

### 3.2 TI Component Level IEC ESD Test

TI Component Level IEC ESD Test tests only the IC terminals that are exposed in system level applications. It can be used to determine the robustness of on-chip protection and the latch-up immunity. The IC can only pass the TI Component Level IEC ESD test when there is no latch-up and IC is fully functional after the test.

### 3.3 Construction of a Custom USB Connector

A standard USB connector, either type A or type B, provides good ESD protection. However, if a custom USB connector is desired, the following guidelines should be observed to ensure good ESD protection.

- There should be an easily accessible shield plate next to the connector for air-discharge mode purpose.
- Tie the outer shield of the connector to GND. When a cable is inserted into the connector, the shield of the cable should first make contact with the outer shield.
- If the connector includes power and GND, the lead of power and GND need to be longer than the leads of signal.
- The connector needs to have a key to ensure proper insertion of the cable.
- See the standard USB connector for reference.

## 4. References

- USB 2.0 Specification, Intel, 2000, http://www.usb.org/developers/docs/
- High Speed USB Platform Design Guidelines, Intel, 2000

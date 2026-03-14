---
source: "TI TIDUF73 -- High-Voltage Passive Precharge Reference Design"
url: "https://www.ti.com/lit/pdf/tiduf73"
format: "PDF 14pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 15608
---

# Design Guide: TIDA-050080 — High-Voltage Passive Precharge With Overcurrent Protection Reference Design

## Description

This reference design implements a common circuit in high-voltage DC buses — precharge — with newer, smaller, and more cost-efficient components. This design features the TPSI3100-Q1 isolated switch driver, which provides reinforced isolation between voltage domains and does not require a secondary side bias supply for driving field-effect transistors (FET). TPSI3100-Q1 also offers integrated digital comparators for fault detection which, in this design, is used for overcurrent protection. This design is rated for an 800V battery management system (BMS) but can also be implemented in 400V systems.

**Features:**
- 5kV RMS reinforced isolation
- Integrated isolated bias supply
- Supports 800V power train architectures
- Provides low-cost overcurrent detection scheme
- Capable of charging 2mF capacitor to 800V in 500ms

**Applications:**
- High-voltage battery system
- Traction inverter
- Battery energy storage system

**Key components:** TPSI3100-Q1, TPSI2140-Q1, INA180-Q1

## 1. System Description

Precharge is a common circuit in Electric and Hybrid Electric Vehicles (EVs and HEVs) that prepares the high-voltage DC rails before the rails are connected to the battery. The positive and negative high-voltage rails are connected by the DC-Link capacitor, which helps stabilize the rails as loads are connected and disconnected during vehicle operation. A precharge circuit charges the DC-link capacitor to the battery voltage, minimizing the inrush current caused when the main contactors close. For the health of the main contactors, the inrush is minimized as too high of inrush can cause the contacts to weld together, rendering them defective.

This design features passive precharge with solid-state relays. In passive precharge, the switch closes statically until the capacitor is charged. The goal of this design is to replace the mechanical contactor with a solid-state relay, providing a more reliable design. The benefits of passive precharge are the low complexity and low switching noise emissions. This is a very common method of precharge in the industry because of the simplicity and the widespread availability of power resistors. However, as this design has less control logic, sizing components to withstand the power and protecting them from overcurrent is foremost of the design considerations.

Outside of the high-power path, the control circuitry of this design is comprised of a FET driver and an overcurrent detection circuit. This design uses the TPSI3100-Q1 isolated switch driver which, when paired with a FET, creates a seamless solid-state relay design that replaces contactors such as the precharge contactor. Additionally, integrated in the TPSI3100-Q1 are fault and alarm comparators. The fault comparator disables the driver when tripped and sends a signal back across the barrier. The alarm comparator only sends a signal when tripped. Along with an INA180-Q1 current-sense amplifier, these comparators constitute the overcurrent detection circuit. The current-sense amplifier is powered through the internal secondary side supply of the TPSI3100-Q1, a nominal 5V rail generated from the VDDM pin.

The final element of this design is a discharge path for the voltage stored on the capacitor. In EVs, there are different types of discharge requirements. For safety-critical events, such as a crash, the capacitor must be discharged in under a few seconds (exact time varies between manufacturers). For non-emergency cases, the discharge can be on the order of minutes. This design features a non-emergency discharge comprised of the isolated switch TPSI2140-Q1 and a power resistor. Once activated, the capacitor is discharged to below 60V in about 2 minutes from 1000V.

## 2. System Overview

### 2.1 Design Considerations

The precharge design process begins with the requirements.

**Table 2-1. Precharge Design Requirements:**

| Requirement Name | Value |
| --- | --- |
| Precharge Time | 0.5 seconds |
| System Voltage | 800V (1000V) |
| DC-Link Capacitance | 2mF |

This design must charge a 2mF DC-Link capacitor up to the system voltage of 800V in 0.5 seconds. However, 800V EVs can carry as much as 1000V at full charge, so the components must be sized accordingly.

### 2.2 Design Theory

At a high level, a passive precharge circuit is a simple RC circuit that can be represented as an exponentially decaying function. The voltage on the capacitor is calculated using:

VC = VS × (1 - e^(-t/τ))

where VS is the system voltage and τ (Tau) is the time constant that determines the rate of charge.

For this system, the precharge cycle is considered complete when 5τ has passed. Some systems can require longer than 5τ to charge to maintain that the voltage drop across the main contactors meets the contactor switching requirements.

5 × τ = 5 × R × C = 0.5 seconds

Substituting the DC-Link capacitance and solving for R, the system resistance is **50Ω**.

The energy can be calculated:

E = ∫₀^0.5 20,000 × e^(-2t/0.1) dt ≈ 1000 J

Or as a function of the capacitor:

E = ½CV² = 1000 J

### 2.3 Resistor Selection

The correct resistor is most reliably selected through an understanding of the pulse energy. The standard resistor power rating is the limit of continuous power — since precharge is not a continuous cycle, choosing a 20kW resistor is wrong. The characteristics relevant to this design are the **pulse energy handling capabilities**, determined by the thermal robustness of the resistive element and the ability to sink heat.

For this design, a **wire-wound resistor** is the best option because these resistors have additional mass placed within (the core) and often around the coil (the housing). This additional mass sinks the heat generated from the high-power pulse.

**Ways to determine if a resistor can handle the precharge pulse:**

1. **Short-term overload rating:** Wire-wound resistors typically have a short-term overload of 5× or 10× the rated power for 5 seconds. If a resistor has an overload of 5× for 5 seconds, it can also handle 25× for 1 second (if the data sheet explicitly says). If rated at 100W, the overload pulse energy is 2500J. Too short of a pulse length does not allow the coil enough time to distribute heat.

2. **Pulse energy chart:** Typically presented with resistance on the x-axis and pulse energy on the y-axis. Shows the pulse energy limit of each resistor within a family.

3. **Pulse performance chart:** Shows pulse duration on the x-axis and maximum power on the y-axis, both logarithmic.

If none of the pulse information is published, confirm with the manufacturer what the energy limits are for a **capacitive pulse** specifically.

### 2.4 Transistor and Diode Selection

For both the transistor and the diode, the first consideration is the **breakdown and blocking voltage**. Since this is for an 800V BMS, and EV batteries are often charged to higher voltage than the system voltage (an 800V EV can hold as much as 1000V on full charge), select a breakdown that gives additional margin above full charge voltage. For this design: **1200V**.

For the transistor, use the **Safe Operating Area (SOA) chart** on the FET data sheet. In an RC circuit like precharge, the power dissipation in the resistor is nearly one-third of the initial magnitude after one time constant. The pulse length worth considering for component sizing is **100ms**. A FET is likely large enough if the peak expected current is beneath both the 100ms curve and the on-resistance limit curve.

For the diode: a reverse blocking voltage of 1200V is needed and the diode must withstand the maximum forward current. The continuous forward current rating should be no more than 60%–80% of the peak forward current, to withstand a soft short that is too low to trip the overcurrent protection. Alternatively, if a design with lower RDS(on) and lower voltage drop is needed, a second blocking FET can be used (higher cost).

### 2.5 Overcurrent Detection — Short-Circuit Protection

The TPSI3100-Q1 includes two high-speed comparators on the secondary side. The information from both comparators is transmitted to the primary side; however, the fault comparator, when tripped, de-asserts the drive pin. At a system-level perspective, these signals can be sent to a microcontroller to provide current, voltage, or temperature monitoring. Although the fault comparator does not need a monitor to disable the driver, the information can still be useful.

In this design, these comparators are used in an overcurrent protection circuit comprised of the unidirectional current sense amplifier INA180-Q1 which outputs into a resistor divider that feeds the fault and alarm comparators of the TPSI3100-Q1. The fault current is 25A because at a full 1000V charge the initial current can reach 20A. To reduce the risk of false positives throughout the life of the design, add some margin.

**Table 2-2. ALM Configuration Examples:**

| Configuration | FLT Current | ALM Current | R9 | R6 | R5 | ALM Purpose |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2A | 20A | 0.75mΩ | 2.5kΩ | 10kΩ | ALM must deassert in less than 10ms to 50ms |
| 2 | 25A | 12.5A | 1.2mΩ | 10kΩ | 10kΩ | ALM must deassert in less than 50ms to 70ms |
| 3 | 25A | 2A | 7.5mΩ | 115kΩ | 10kΩ | ALM must deassert in less than 300ms |

In configuration 1, the alarm signal is not tripped on a regular basis as the circumstance requires a 1000V charge. The alarm serves as a warning that the current has reached a level that can prove harmful if not addressed quickly. Since the driver is disabled at 25A, the expected range is 20A–25A. A reasonable time period for the alarm to be active is 10ms to 50ms. The alarm information is transmitted across the isolation barrier in 30μs, giving a microcontroller the ability to act if the alarm signal remains active.

In configurations 2 and 3, expect the alarm signal to trip and remain tripped for a longer time. A microcontroller can be tasked with timekeeping and given authority to disable the device if the time limit is exceeded.

Beyond current and voltage sensing, the alarm and fault signals can be used for temperature or humidity monitoring. Because of the low latency with which signals are transmitted to the primary side, more complex operations are possible with a microcontroller.

## 3. Highlighted Products

### 3.1 TPSI3100-Q1

The TPSI3100-Q1 is a fully integrated isolated switch driver which, when combined with an external power switch, forms a complete isolated solid-state relay design. Features:
- Gate drive voltage of 15.8V with 1.5A, 2.5A peak source/sink current
- Generates a secondary bias supply from power received on the primary side — no isolated secondary supply required
- Provides additional power through the nominal 5V rail (VDDM) for auxiliary circuits (current/voltage monitoring, remote temperature detection)
- Integrates a communication back channel that transfers status information from secondary to primary side
- When FLT1_CMP exceeds the voltage reference, the driver is immediately asserted low and FLT1 is driven low (fault)
- When ALM1_CMP exceeds the voltage reference, ALM1 is asserted low but no action is taken by the driver (alarm/warning)

In this design: 5V supply powers primary side pins VDDP and CE with 1100nF input capacitance. External 5V signal tied to EN pin. PGOOD, nFLT, and nALM tied to pull-up network. VSSP pins tied to ground.

On the secondary side, the capacitors between VDDH and VDDM, VDDM and VSSS (named C_DIV1 and C_DIV2) are chosen to maintain a ratio of 1:3 (C_DIV2 = 3 × C_DIV1). The current-sense amplifier is powered from VDDM. RESP pin tied to VSSS with a 100kΩ resistor.

### 3.2 INA180-Q1

The INA180-Q1 current-sense amplifier senses voltage drops across current-sense resistors at common mode voltages from −0.2V to +26V, independent of the supply voltage. Integrates a matched resistor gain network in four fixed-gain device options: 20V/V, 50V/V, 100V/V, or 200V/V.

For this design: selected gain of 20V/V, powered from VDDM pin with 100nF input capacitance. The output serves as the alarm signal for the overcurrent detection circuit and feeds the resistor divider for the fault signal.

### 3.3 TPSI2140-Q1

The TPSI2140-Q1 is an isolated solid-state relay designed for high-voltage automotive and industrial applications. Uses TI's capacitive isolation technology with internal back-to-back MOSFETs to form a completely-integrated design requiring no secondary-side power supply.

In this design: used as an isolated switch for discharging the capacitors after the precharge cycle. The switch is in series with a high-ohmic resistor to provide a low-power discharge (about two minutes to reach less than 60V).

## 4. Hardware, Testing Requirements, and Test Results

### 4.1 Hardware Requirements

The reference design PCB measures **140mm × 100mm** and is about **55mm** in height.

External hardware required:
1. High-voltage enclosure
2. Power supply: 5V DC source; high-voltage supply capable of at least 800V/25A, preferably 1000V/30A
3. Oscilloscope
4. Isolated probes
5. External load resistor ~50Ω
6. External capacitor bank ~2mF

### 4.2 Test Setup

1. Connect a 5V power supply to VDDP, EN_PRCHG, and EN_DSCHG banana jacks, negative lead to VSSP.
2. Before placing in enclosure or connecting HV supply, power the TPSI3100-Q1 and verify all voltages on primary and secondary side.
3. Perform step 2 with TPSI2140-Q1, verifying internal FETs are on by measuring resistance between S1 and S2.
4. Turn off 5V power supplies.
5. Place board in enclosure, attach precharge resistor leads to J2 and J3.
6. Attach capacitor positive terminal to J3, negative to J4.
7. Attach HV power supply positive to J1, negative to J4.
8. Connect isolated probe to S1-HV to measure capacitor voltage.
9. Connect isolated probe to VDRV-VSSS to show drive pin step.
10. Close enclosure and energize HV power supply.
11. Power the 5V supply and observe the cycle, powering off after a second.
12. Turn off HV supply.
13. Power 5V supply again to energize EN_DSCHG to discharge capacitor. Wait at least 2 minutes before opening the enclosure.

### 4.3 Test Results

- **Precharge cycle:** VDRV (drive pin on secondary side of TPSI3100-Q1) enables, VCAP (voltage across capacitor bank) charges to system voltage.
- **Discharge cycle:** EN_DSCHG enables TPSI2140-Q1, capacitor voltage drops to safe level.
- **Overcurrent protection:** VDRV pin disables after current exceeds 25A limit. After auto-recovery period, drive pin re-asserts. The nFLT pin on primary side reports the fault by pulling down after 30μs, pulled back up after another 30μs.

## 5. Design Files and Documentation Support

- Schematics and BOM available at TIDA-050080.
- PSpice for TI simulation tool available for design and simulation.
- Reference documents:
  - TI: Why Pre-Charge Circuits are Necessary in High-Voltage Systems (Application Brief)
  - TPSI2140-Q1 Data Sheet: 1200-V, 50-mA, Automotive Isolated Switch With 2-mA Avalanche Rating
  - TPSI3100-Q1 Data Sheet: Automotive Reinforced Isolated Switch Driver With 15-V Gate Supply and Dual Isolated Comparators
  - INAx180-Q1 Data Sheet: Automotive, Low- and High-Side Voltage Output, Current-Sense Amplifiers

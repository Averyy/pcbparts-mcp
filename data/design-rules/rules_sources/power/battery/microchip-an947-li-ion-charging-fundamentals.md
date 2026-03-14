---
source: "Microchip AN947 -- Li-Ion Charging Fundamentals"
url: "https://ww1.microchip.com/downloads/en/AppNotes/00947a.pdf"
format: "PDF 16pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 13268
---
# Power Management in Portable Applications: Charging Lithium-Ion/Lithium-Polymer Batteries

Author: Scott Dearborn, Microchip Technology Inc.

## Introduction

Powering today's portable world poses many challenges for system designers. The use of batteries as a prime power source is on the rise. Each application is unique, but one common theme rings true: maximize battery capacity usage. This theme directly relates to how energy is properly restored to rechargeable batteries.

While no single method is ideal for all battery chemistries, an understanding of the charging characteristics of the battery, along with the application's requirements, is essential when designing an appropriate and reliable battery-charging system. Each method has its associated advantages and disadvantages, with the particular application determining the best method to use.

This application note focuses on the fundamentals of charging Lithium-Ion/Lithium-Polymer batteries. A linear, stand-alone solution utilizing Microchip's MCP73841 is explored.

## Battery Overview

A battery is a device that converts the chemical energy contained in its active materials directly into electric energy by means of an electrochemical oxidation-reduction (redox) reaction.

The standard potential of a battery is determined by the type of active materials contained in the battery. It can be calculated from the standard electrode potentials:

    Standard Potential = Anode (oxidation potential) + Cathode (reduction potential)

For example, in a NiCd battery:
- Cathode: 2NiOOH + 2H2O + 2e -> 2Ni(OH)2 + 2OH- = 0.52 V
- Anode: Cd + 2OH- -> Cd(OH)2 + 2e = -0.81 V
- Standard Potential: 0.52 - (-0.81) = 1.33 V

The theoretical capacity of a battery is expressed as the total quantity of electricity involved in the electrochemical reaction: 1 gram equivalent weight of material will deliver 96,487 C or 26.8 Ah.

The maximum energy that can be delivered is based on the types of active materials (determines voltage) and the amount of active materials (determines ampere-hour capacity). In practice, only a fraction of the theoretical energy is realized due to the electrolyte and non-reactive components (containers, separators, seals). The actual energy available under practical discharge conditions is only about 25% to 35% of the theoretical energy.

### Battery Voltage Definitions

- **Open-Circuit Voltage:** Theoretical voltage of a fully charged battery
- **Closed-Circuit Voltage:** Lower than open-circuit voltage when drawing current, due to electrode impedance and reaction rate limitations
- **Nominal Voltage:** Voltage at the "plateau" of the discharge curve (NiCd/NiMH: 1.2 V, Li-Ion: 3.6 V)
- **End Voltage:** Potential at which the system no longer draws current
- **Discharge Cut-off Voltage:** Secondary safety potential, below which the battery can experience irreparable damage

### C-Rate

The C-rate equates to a charge or discharge current:

    I = M x C / n

Where I = charge or discharge current (A), M = multiple or fraction of C, C = numerical value of rated capacity (Ah), n = time in hours at which C is declared.

A battery discharging at a C-rate of 1 delivers its nominally-rated capacity in one hour. Manufacturers typically specify capacity at 5-hour rate (n = 5). In practice, the operating time at 1C will be less than 1 hour due to inefficiencies in the discharge cycle.

### Battery Types

| Primary Cells | Secondary Cells |
|---|---|
| Zinc Carbon | Sealed Lead Acid |
| Alkaline | Nickel Cadmium |
| Lithium | Nickel Metal-Hydride |
| -- | Lithium-Ion |
| -- | Lithium-Polymer |

## Lithium-Ion Batteries

Li-Ion batteries employ lithium intercalation compounds as the positive and negative materials. The positive electrode material is typically a metal oxide (lithium cobalt oxide LiCoO2 or lithium manganese oxide LiMn2O4) on a current-collector of aluminum foil. The negative electrode material is typically a graphite carbon on a copper current-collector.

**Advantages:**
- Superior energy density by weight and volume
- No "memory" effect (low maintenance, no periodic cycling needed)
- Lowest self-discharge of the three main portable rechargeable battery types

**Disadvantages:**
- Higher costs (relative infancy of technology)
- Lose potential capacity even when not in use (aging)
- Relatively high internal resistance, excluding them from high-discharge current applications
- Require protection circuitry in battery packs

### Protection Circuitry

All Li-Ion battery packs employ protection circuitry to meet UL1642 and IEC Secondary Lithium Battery Standards. The protection circuitry consists of two MOSFETs connected in either a common drain or common source configuration:
- In batteries with 2 or more cells in series: P-channel MOSFETs in series with positive electrode
- In single-cell batteries: N-channel MOSFETs in series with negative electrode

**Operating range:** 4.2 V to 2.8 V. Internal safety protection circuits inhibit operation beyond this window.

| Voltage | Significance |
|---|---|
| 4.35 V | Pack protection circuit opens MOSFET (temporary disconnect) |
| 4.2 V | Upper charge voltage |
| 2.8 V | End voltage |
| 2.5 V | Pack protection circuit opens MOSFET (temporary disconnect) |
| 0 V | Anode dissolves: copper shunts form (permanent degradation) |

## Lithium-Ion Charging Algorithms

The preferred charge algorithm is a constant or controlled current, constant-voltage algorithm broken into three stages:

### Stage 1: Trickle Charge

Employed to restore charge to deeply depleted cells. When the cell voltage is below approximately 2.8 V, the cell is charged with a constant current of 0.1C maximum. An optional safety timer can terminate the charge if the cell voltage has not risen above the trickle charge threshold in approximately 1 hour.

### Stage 2: Fast Charge

Once the cell voltage exceeds the trickle charge threshold, the charge current is raised to perform fast charging. The fast charge current should be less than 1.0C. In linear chargers, the current is often ramped-up as the cell voltage rises to minimize heat dissipation in the pass element. An optional safety timer can terminate if no other termination is reached in approximately 1.5 hours from the start of the fast charge stage (at 1C).

### Stage 3: Constant Voltage

Fast charge ends and constant voltage mode is initiated when the cell voltage reaches 4.2 V. The voltage regulation tolerance should be better than +/-1%. It is not recommended to continue to trickle charge Li-Ion batteries.

Charging is typically terminated by one of two methods:
1. **Minimum charge current:** Monitors charge current during CV stage and terminates when current diminishes below approximately 0.07C
2. **Timer:** Determines when the CV stage is invoked and charges for an additional two hours before terminating

Charging in this manner replenishes a deeply depleted battery in roughly 165 minutes.

**Advanced safety features:**
- Charge is suspended if the cell temperature is outside 0 deg C to 45 deg C

## Lithium-Ion Charging Considerations

### Input Source

Many applications use inexpensive wall cubes as the input supply. The output voltage is highly dependent on the AC input voltage and the load current.

In the United States, the AC mains input voltage can vary from 90 V_RMS to 132 V_RMS for a standard wall outlet (nominal 120 V_RMS, tolerance +10%, -25%). The charger must provide proper regulation to the battery, independent of its input voltage.

    V_O = 2 x V_IN x a - I_O x (R_EQ + R_PTC) - 2 x V_FD

Where R_EQ = resistance of secondary winding plus reflected resistance of primary, R_PTC = PTC resistance, V_FD = forward drop of bridge rectifiers.

### Output Voltage Regulation Accuracy

Output voltage regulation accuracy is critical to maximize battery capacity usage. A small decrease in output voltage accuracy results in a large decrease in capacity. However, the output voltage cannot be set arbitrarily high because of safety and reliability concerns.

Key relationships:
- If the battery is undercharged by 1% of 4.2 V (42 mV), approximately 8-10% of capacity is lost
- The capacity loss is approximately linear with undercharge percentage

### Charge Termination Method

Primary and secondary charge termination methods are essential for reliably charging any battery chemistry. Over-charging is the Achilles' heel of Li-Ion cells.

- **Primary termination:** Monitor charge current during constant voltage phase; terminate when current drops to 0.1C to 0.07C rate
- **Secondary termination:** Elapsed charge timer; terminate if battery does not reach full charge within specified time

### Cell Temperature Monitoring

Temperature range for Li-Ion charging: 0 deg C to 45 deg C. Thermistors are included in Li-Ion battery packs to accurately measure the battery temperature. Charging is inhibited when the temperature is outside the specified operating range.

### Battery Discharge Current or Reverse Leakage Current

The charging system should minimize current drain from the battery when input power is not present. Maximum current drain should be below a few microamps or, ideally, below one microamp.

## Design Example Using MCP73841

### Design Parameters

- Input Source: 5 V, +/-5%
- Battery: Single-cell, Lithium-Ion, 1000 mAh
- Fast Charge Rate: 1C or 0.5C
- Regulation Voltage: 4.2 V
- Primary Termination: I_min
- Secondary Termination: Timer, 6 hours
- Charging Temperature: 0 deg C to 45 deg C

### MCP73841 Device Overview

The MCP73841 is a linear charge-management controller using an external pass transistor (MOSFET). It features:
- Charge qualification and preconditioning
- Constant current regulation (fast charge)
- Constant voltage regulation
- Charge cycle completion with automatic re-charge
- Charge status output

| Charge Cycle State | STAT1 Output |
|---|---|
| Qualification | Off |
| Preconditioning | On |
| Constant Current Fast Charge | On |
| Constant Voltage | On |
| Charge Complete | Off |
| Safety Timer Fault | Flashing (1 Hz, 50% duty cycle) |
| Cell Temperature Invalid | Flashing (1 Hz, 50% duty cycle) |

### Sense Resistor

    R1 = V_FCS / I_REG

For 1000 mA fast charge current, a standard value 110 mOhm, 1% resistor provides a typical fast charge current of 1000 mA and maximum of 1091 mA. Worst-case power dissipation: 131 mW.

A larger-value sense resistor decreases fast charge current and power dissipation but increases charge cycle times.

### External Pass Transistor

**Thermal considerations:** Worst-case power dissipation occurs when the input voltage is at maximum and the device has transitioned from preconditioning to constant current phase:

    P_Q1 = (V_DD(MAX) - (V_PTH(MIN) + V_FCS)) x I_REG(MAX)

For this design: P_Q1 = (5.25 V - (2.85 V + 0.120 V)) x 1091 mA = 2.48 W

Using a Fairchild NDS8434 or IRF7404 mounted on a 1 in^2 pad of 2oz copper, junction temperature rise is approximately 99 deg C, allowing maximum operating ambient temperature of 51 deg C.

**Electrical considerations:** Worst-case V_GS and maximum allowable R_DSON:

    V_GS = V_DRV(MAX) - (V_DD(MIN) - V_FCS(MAX)) = 1.0 V - (4.75 V - 120 mV) = -3.63 V

    R_DSON = (V_DD(MIN) - V_FCS(MAX) - V_BAT(MAX)) / I_REG(MAX)
           = (4.75 V - 120 mV - 4.221 V) / 1091 mA = 375 mOhm

### External Capacitors

Minimum capacitance of 4.7 uF recommended to bypass V_BAT pin to V_SS. This provides compensation when there is no battery load and compensates for the inductive nature of the battery pack. A 4.7 uF ceramic, tantalum, or aluminum electrolytic capacitor at the output is usually sufficient for up to 1 A output current.

### Cell Temperature Monitoring (NTC Thermistor)

For 0 deg C to 45 deg C temperature window, using a 10 kOhm (25 deg C) NTC thermistor with beta = 3982:
- Thermistor resistance: 33.56 kOhm at 0 deg C, 4.52 kOhm at 45 deg C

For NTC thermistors:

    R_T1 = (2 x R_COLD x R_HOT) / (R_COLD - R_HOT)

    R_T2 = (2 x R_COLD x R_HOT) / (R_COLD - 3 x R_HOT)

Calculated values: R_T1 = 10.44 kOhm, R_T2 = 15.17 kOhm. Standard values: 10.5 kOhm and 15.0 kOhm provide a temperature window within 1 deg C of desired.

### Safety Timer

A timing capacitor (C_TIMER) between the TIMER pin and V_SS programs three safety timers:

    t_PRECON = (C_TIMER / 0.1 uF) x 1.0 Hours

    t_FAST = (C_TIMER / 0.1 uF) x 1.5 Hours

    t_TERM = (C_TIMER / 0.1 uF) x 3.0 Hours

Design specifies 6-hour charge termination time. A standard 0.22 uF ceramic capacitor is chosen.

### Charge Cycle Comparison: 1C vs 0.5C

When charging at 0.5C instead of 1C:
- Same charging steps are performed
- Takes about one hour longer to reach end of charge
- MCP73841 scales the charge termination current proportionately with the fast charge current
- Result: 36% increase in charge time, with 2% gain in capacity and reduced power dissipation
- Change in termination current from 0.07C to 0.035C increases final capacity from ~98% to ~100%

The system designer has to make a trade-off between charge time, power dissipation and available capacity.

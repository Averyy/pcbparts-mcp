---
source: "TI SLYP089 -- Design Trade-offs for Switch-Mode Battery Chargers"
url: "https://www.ti.com/lit/ml/slyp089/slyp089.pdf"
format: "PDF 17pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 18529
---
# Design Trade-offs for Switch-Mode Battery Chargers

Jose Formenti and Robert Martinez

## Abstract

The design of switching converters as a standalone block is a well-known topic. However, very specific challenges arise when a DC/DC converter is used to charge a battery pack. Understanding the impact of using a battery as a load, and other charger-related system-level details up-front, is a requirement when designing a DC/DC converter targeted at battery-pack charging. This article discusses the most common benefits and challenges faced when using switching converter topologies to charge battery packs, including specific challenges and design tradeoffs faced when using the battery pack as a load.

## I. Introduction

Methods for designing stand-alone switching converters are well-known. However, specific challenges arise when a DC/DC converter is used to charge a battery pack. Understanding up-front the impact of using a battery as a load and other charger-related system-level details enables the designer to incorporate features and functions not present in common DC/DC converters.

This paper discusses the most common benefits and challenges of using switching-converter topologies to charge battery packs. A comparison of distinct switching topologies identifies when each is most advantageous. Subsequent sections focus on buck switching charger design; synchronous versus nonsynchronous operation; power dissipation and switching frequency; the impact of AC adapter voltage range on converter design; MOSFET selection; loop-compensation requirements for battery-pack loads; and safety and fault-protection circuits.

## II. Converter Topology

### A. Overview

There are currently two major topologies used to implement buck converters targeted at battery-pack-charging applications: synchronous and nonsynchronous rectification. These topologies can be implemented with integrated or discrete switching MOSFET devices. The switching devices can be NMOS, PMOS, or a combination of both.

The selection of a specific topology will be dictated by the design boundaries set by the following system requirements:
- Charge-current level
- AC adapter voltage range
- Ambient temperature range
- Converter switching frequency
- Target PCB area
- Availability of system resources dedicated to power-management functions

### B. Basic Buck-Converter Topologies and High-Side FET Selection

Nonsynchronous buck converters represent one of the earliest implementations of switching regulators. A single switch (S1) is closed during a time (t_ON) connecting the AC adapter voltage to the inductor. When the switch opens during the off time (t_OFF), a free-wheeling diode (D1) holds the voltage at a node (N1) while providing a path for inductor (charge) current. The duty cycle is set by internal control circuits and regulation loops that monitor the pack voltage and pack charge current.

The control loops are configured to limit either the charge current or the charge voltage to a programmed value. This scheme enables control of the charge current when the battery voltage is below the target charge voltage, or control of the charge voltage when the battery voltage reaches the regulation voltage.

**High-side MOSFET selection (NMOS vs PMOS):**

- NMOS devices have the advantage of a lower R_DS(ON) for the same package; thus either more load current can be used or the cost can be lower. For the same R_DS(ON), the die size can be smaller, and total gate charge of a discrete NMOS can be lower than that of a discrete PMOS. The lower gate charge lowers the switching losses, allowing a higher switching frequency and lowering the output filter inductor and capacitor requirements. The disadvantage of an NMOS on the high side is that turning it on requires a method to drive the gate with a voltage higher than the input voltage.

- For PMOS high-side FETs, turn-on is simplified because the gate voltage needs to be lower than the input voltage by at least 5 V instead of higher. Devices with a lower voltage rating can be used.

- For implementations where the power MOSFETs are discrete parts external to the control IC, the preferred MOSFET is NMOS to lower system cost and to have high performance with high efficiency.

- For implementations where the power MOSFETs are integrated within the control IC, PMOS is usually preferred over NMOS because of its ease of implementation and because the PMOS/NMOS area trade-off favors the PMOS in integrated MOSFETs. Discrete devices typically have a 2:1 trade-off, whereas integrated lateral devices may have a 1.4:1 trade-off.

### C. Nonsynchronous and Synchronous Topologies

**Nonsynchronous Topologies:**

Nonsynchronous topologies enable designs that simplify controller architecture and system-side power-management functions. To minimize system cost, less complex controllers designed to drive external PMOS devices are the preferred choice for nonsynchronous buck-charger stages. Another advantage of the PMOS is that the duty cycle can be kept indefinitely at 100%.

The use of a free-wheeling diode implements a topology that intrinsically has no problems with cross-conduction on the power stage during switching; it also eliminates any stray paths from battery pack to ground when the high-side switch is off. As a result there is no need for the complex system power-management functions usually required when cross-conduction and battery-pack leakage paths are present.

The downside of nonsynchronous topologies is their power dissipation. With proper PCB thermal design and proper selection of PWM power-stage components, nonsynchronous topologies typically can be used to charge battery packs with maximum charge-current rates in the 3- to 4-A range.

**Synchronous Topologies:**

Synchronous DC/DC converters are a logical choice for application conditions where the nonsynchronous topologies do not meet power dissipation and efficiency requirements. Synchronous converters typically cost more because additional components are required and the controller is more complex. Two basic topologies are commonly used: both use a low-side NMOS switch to minimize losses on the free-wheeling diode. The high-side switch can be either PMOS or NMOS.

The synchronous operation of the high/low-side switches impacts controller complexity. To avoid shoot-through currents during switching, a break-before-make logic function must be added to ensure that the switches are never on at the same time. A dead time is built in to guarantee that no cross-conduction happens; a Schottky free-wheeling diode is required to hold the node N1 voltage during the dead time.

**PMOS/NMOS synchronous topology limitations:** The internal synchronous PWM cannot be run at very high frequencies due to the typically high gate-charge values for PMOS devices and the power-dissipation constraints on the PWM controller IC. This prevents the use of a smaller inductor. Also, PMOS switches cost more than NMOS switches with the same voltage/current ratings.

**NMOS/NMOS synchronous topology:** This limitation can be overcome by using an NMOS/NMOS topology. Three methods to drive the high-side NMOS gate above the adapter voltage:

1. Use a separate, external gate-drive supply rail that is higher than the input voltage rail by at least 5 V.
2. Use a charge pump to generate the higher gate-drive supply rail.
3. Use a bootstrap circuit to provide the required gate-drive voltage from a 5-V external rail every cycle.

The preferred method is usually the bootstrap circuit because it does not require a higher voltage rail and is usually the simplest to implement. The disadvantage is that the bootstrap capacitor needs to replenish its charge loss due to switching and leakage currents, preventing leaving the high-side FET fully on at a 100% duty cycle for long periods. A periodic recharge pulse providing a 99.9x% duty cycle is required.

## III. Power Dissipation and Size versus Switching Frequency

It is common to target an increase in switching frequency to decrease the output inductor and output capacitor values and sizes.

**Output inductor:**

    L = (V_IN - V_OUT) / (dI_L x f_SW) x (V_OUT / V_IN)

Where dI_L is the inductor current ripple.

**Output capacitor:**

    C = (dI_L x V_OUT) / (V_IN x f_SW x dV_C)

Where dV_C is the capacitor output voltage ripple.

A higher switching frequency can decrease the ripple current and voltage proportionately for the same output inductor and capacitor. If the frequency is kept constant and the output inductor or capacitor is decreased, the output ripple current and voltage will proportionately increase.

**Power Loss Equations:**

Total power losses:

    P_TOT = P_CON + P_SW

**Conduction losses:**

    P_CON = P_ON_T + P_ON_B + P_RSENSE + P_L + P_C

    P_ON_T = R_DS(ON)_T x D x I_OUT^2

    P_ON_B = R_DS(ON)_B x {(1 - D) - f_SW x (t_d1 + t_d2)} x I_OUT^2

    P_RSENSE = R_SENSE x I_OUT^2

    P_L = R_DCR x I_OUT^2

    P_C = R_ESR x (D x I_OUT)^2

**Switching losses:**

    P_SW = P_SW_T + P_SW_B + P_SCH + P_GD

    P_SW_T = (Q_GSI_T / (2 x I_G) + Q_GD_T) x V_IN x I_OUT x f_SW

    P_SW_B = (Q_RR_B x V_IN + C_OSS x V_IN^2 / 2) x f_SW

    P_SCH = V_F x I_OUT x (t_d1 + t_d2) x f_SW

    P_GD = V_IN x (Q_GSTOT_T + Q_GSTOT_B) x f_SW

Where V_F is the forward voltage of the Schottky diode, and t_d1 and t_d2 are the dead times.

The total power dissipation is dependent on the switching frequency; however, the values of the output inductor and capacitor are inversely proportional to the switching frequency. For battery chargers, this trade-off is usually optimized to minimize the size and cost of the components while keeping the system power dissipation below the thermal limit.

**Maximum power loss for a package:**

    P_LOSS(max) = (T_J(max) - T_A) / R_thetaJA

## IV. Switching Regulator Trade-offs for Battery-Charging Applications

### A. Can Standard Converters Be Used in a Battery-Charging Environment?

Standard topologies can be implemented with a wide array of DC/DC controllers. However, using standard controllers for synchronous conversion potentially can cause various problems when a battery load is used, unless additional circuits are designed into the solution. Traditional stand-alone controllers are designed to handle loads that have only sink capability; a battery load can both source and sink currents.

**Problems that can happen:**
- The pack is shorted to the AC adapter output if the pack is above the adapter voltage
- The PWM converter does not start when the charger is enabled and a pack is connected
- Battery reverse current flows through the low-side switch during the charge-current taper phase
- The bootstrap circuit cannot be recharged when the adapter voltage is too close to the battery-pack voltage

### B. Avoiding Undesirable Reverse Discharge

A battery is a two-quadrant device: positive voltage but both positive and negative current can flow. Battery chargers need to avoid reverse discharge, which can drain the battery and reduce expected run-time capacity. Two probable paths for reverse discharge within a synchronous buck regulator:

**Path 1 -- Battery to input:** From the battery, through the output inductor, and through the back diode of the high-side power MOSFET to the input. This occurs when the battery is higher than the input voltage. Solutions:
- Series Schottky diode at the input (simple but adds V_F conduction losses)
- Synchronous PMOS FET controlled by a gate signal (lower losses, easier with integrated solutions)

**Path 2 -- Battery to ground:** From the battery, through the output inductor, and through the low-side FET to ground. This occurs through the channel of the FET when the power MOSFET is on and the current reverses through the inductor. Solutions:
- Monitor inductor/MOSFET current and turn off the low-side MOSFET before the inductor current reverses (goes negative)
- Nonsynchronous buck regulators use the Schottky diode instead of a power MOSFET to prevent reverse discharge

Preventing reverse discharge to ground is also important when a charger is started up with a battery connected at the output. If the converter is allowed to conduct negative current through the low-side FET, the current will go negative and will not be able to charge the inductor with positive current, either indefinitely or for a significant amount of time.

### C. Unique-Load Behavior

Battery chargers have a few unique requirements that stand-alone voltage converters do not:
- Besides regulating the output voltage, battery chargers must regulate output current when the battery voltage is below the voltage-regulation value
- The loads are not always the same as in a simple voltage converter

**Load types by application:**
- **Cradle chargers:** Usually have only a battery load. If the battery is removed, the charger detects removal and stops operation.
- **Embedded chargers:** The charger could have a battery load and a constant-power system load at the same time. The combined load behaves more like a constant-power operation than a constant-current operation when the battery voltage is below the voltage-regulation threshold.

**Compensation considerations:** The battery behaves as an energy source or energy sink. The large capacitance plays a key role in large-signal behavior; but the small-signal behavior is dominated by the series inductance and resistance of the pack. This inductive behavior needs to be accounted for in compensation design, as it has a tendency to improve phase margin but reduce gain margin. The low gain margin can allow excessive ringing at frequencies above the crossover frequency.

Ceramic capacitors have very low ESR values that push out the zero frequency to a value too high to assist in canceling a pole. ESR zeros for ceramics are typically at or above the switching frequency.

### D. Control Scheme Affecting Frequency

Control schemes can be divided into two groups: one that maintains constant switching frequency and another that varies the switching frequency.

**Constant-frequency:** Regulates the duty cycle by varying the on time while keeping the frequency constant.

    D = t_ON / T_S

**Constant-on-time:** Keeps the on time constant and varies the off time.

    f_S = D / t_ON

**Constant-off-time:** Keeps the off time constant and varies the on time.

    f_S = (1 - D) / t_OFF

**Hysteretic:** Varies both on time and off time.

    f_S = 1 / (t_ON + t_OFF) = 1 / {L x dI_L x C x (1/V_OUT + 1/(V_IN - V_OUT))}

Constant-frequency control schemes have the benefit of keeping the frequency above critical frequency bands such as the audible noise region (300 Hz to 3 kHz) or the ADSL carrier frequency (900 kHz), which are important design constraints in many portable applications.

Variable-frequency schemes have the disadvantage that the frequency could vary depending on the adapter input voltage, output (battery) voltage, and load-current (charge) conditions. Worst-case minimum frequencies could occur at minimum load (charge) current, such as when the charge cycle is tapering and nearing termination. Frequencies could easily fall into the audible frequency range. Sometimes a "dummy" load is required to bleed the minimum-current limit and avoid falling into low-frequency operation.

## V. Overall System-Design Considerations

### A. Preventing AC-Adapter-Induced Failure Modes

- The DC/DC controller must survive an adapter hot-plug event
- The DC/DC converter application circuit must not affect AC adapter insertion/removal detection

When an already powered adapter is connected to the system, the input voltage rises very fast; the adapter cable inductance and series resistance interact with the input filter capacitor and generate an overshoot pulse. For small input-capacitor values, it is not uncommon to see overshoots in excess of 50% of the adapter regulation voltage. The only practical solution is to dimension the input capacitor to limit the pulse to reasonable values, below the converter maximum ratings for input voltage.

### B. AC Adapter Power Considerations

Most end equipment must maintain normal operation while charging a battery pack. Usually the adapter voltage is kept as close as possible to the target charge voltage to lower adapter power dissipation. This approach has an adverse impact on the rms current as the converter duty cycle increases. A dynamic-power-management (DPM) loop can be added to the standard converter. This third loop effectively reduces the charge current when the adapter current limit is reached, adapting the charge-current value to the system load conditions and AC-adapter limits.

### C. Additional Charger-Startup Issues

Upon initial startup, the error signal generated by the error amplifiers will try to increase the ramp voltage. Some amount of overshoot for the charge current or charge voltage can be expected during power-up if the ramp voltage increases faster than the feedback loop response. A soft-start circuit is usually implemented to decrease the slew rate for the error signal used by the PWM ramp comparator.

### D. Preventing Other Battery-Charger Failure Mechanisms

Failure mechanisms are of special concern when Li-ion packs are being charged. It is a recommended practice to include secondary fault-protection functions in Li-ion charging systems for increased reliability and safety.

| Event | Detection/Action |
|---|---|
| Charge time exceeds normal charging time | Monitor converter on time; End charge |
| Battery-pack temperature is out of range | Monitor pack thermistor; End charge |
| Converter-IC temperature exceeds safe operating range | Monitor junction temperature (thermal shutdown); End charge |
| Charge current exceeds target value while pack is connected | Monitor charge current; End charge |
| Voltage overshoot occurs at pack removal when charger is on | Detect pack removal; End charge |
| Pack cell or terminal is short-circuited; or pack opens | Design PWM loop with ground-compatible common-mode range |
| High-side switch is damaged due to thermal overload and shorts adapter to pack | Monitor charge current; Add additional on/off switch in series with high-side device to isolate pack from adapter |
| Overvoltage condition occurs | Detect output voltage above target voltage; End charge |

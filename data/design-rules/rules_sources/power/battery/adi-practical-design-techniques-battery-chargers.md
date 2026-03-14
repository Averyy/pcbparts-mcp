---
source: "ADI -- Practical Design Techniques: Battery Chargers"
url: "https://www.analog.com/media/en/training-seminars/design-handbooks/Practical-Design-Techniques-Power-Thermal/Section5.pdf"
format: "PDF 25pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 11600
---
# Battery Chargers

Walt Kester, Joe Buxton

## Introduction

Rechargeable batteries are vital to portable electronic equipment such as laptop computers and cell phones. Fast charging circuits must be carefully designed and are highly dependent on the particular battery's chemistry. The most popular types of rechargeable batteries in use today are the Sealed-Lead-Acid (SLA), Nickel-Cadmium (NiCd), Nickel-Metal-Hydride (NiMH), and Lithium-Ion (Li-Ion). Li-Ion is fast becoming the chemistry of choice for many portable applications because it offers a high capacity-to-size (weight) ratio and a low self-discharge characteristic.

## Battery Fundamentals

### C-Rate Definition

Battery charge and discharge currents are expressed (normalized) in terms of C-Rate:
- C-Rate = C / 1 hour, where C is the battery capacity in A-hr or mA-hr
- Example: A 1000 mA-h battery has a C-Rate of 1000 mA
- 1C = 1000 mA, 0.1C = 100 mA, 2C = 2000 mA
- For a given cell type, the behavior of cells with varying capacity is similar at the same C-Rate

### Rechargeable Battery Technologies

| Property | SLA | NiCd | NiMH | Li-Ion | Li-Metal |
|---|---|---|---|---|---|
| Average Cell Voltage (V) | 2 | 1.20 | 1.25 | 3.6 | 3.0 |
| Energy Density (Wh/kg) | 35 | 45 | 55 | 100 | 140 |
| Energy Density (Wh/l) | 85 | 150 | 180 | 225 | 300 |
| Cost ($/Wh) | 0.25-0.50 | 0.75-1.5 | 1.5-3.0 | 2.5-3.5 | 1.4-3.0 |
| Memory Effect? | No | Yes | No | No | No |
| Self-Discharge (%/month) | 5-10 | 25 | 20-25 | 8 | 1-2 |
| Discharge Rate | <5C | >10C | <3C | <2C | <2C |
| Charge/Discharge Cycles | 500 | 1000 | 800 | 1000 | 1000 |
| Temperature Range (deg C) | 0 to +50 | -10 to +50 | -10 to +50 | -10 to +50 | -30 to +55 |
| Environmental Concerns | Yes | Yes | No | No | No |

**Memory effect** occurs only in NiCd batteries and is relatively rare. It can occur during cyclic discharging to a definite fixed level and subsequent recharging. Memory usually disappears if the cell is almost fully discharged and then recharged a time or two.

**Discharge profiles:** NiCd, NiMH, and SLA batteries have a relatively flat profile at 0.2C, while Li-Ion batteries have a nearly linear discharge profile.

## Battery Charging

### Slow Charging (> 12 hours)

Requires much less sophistication; can be accomplished using a simple current source.

| Property | SLA | NiCd | NiMH | Li-Ion |
|---|---|---|---|---|
| Current | 0.25C | 0.1C | 0.1C | 0.1C |
| Voltage (V/cell) | 2.27 | 1.50 | 1.50 | 4.1 or 4.2 |
| Time (hr) | 24 | 16 | 16 | 16 |
| Temp. Range | 0/45 deg C | 5/45 deg C | 5/40 deg C | 5/40 deg C |
| Termination | None | None | Timer | Voltage Limit |

A safe trickle charge current for NiMH batteries is typically 0.03C.

### Fast Charging (< 3 hours)

Requires much more sophisticated techniques. The most difficult part is to correctly determine when to terminate charging. Undercharged batteries have reduced capacity, while overcharging can damage the battery, cause catastrophic outgassing of the electrolyte, and even explode the battery.

| Property | SLA | NiCd | NiMH | Li-Ion |
|---|---|---|---|---|
| Current | >= 1.5C | >= 1C | >= 1C | 1C |
| Voltage (V/cell) | 2.45 | 1.50 | 1.50 | 4.1 or 4.2 +/- 50 mV |
| Time (hours) | <= 1.5 | <= 3 | <= 3 | 2.5 |
| Temp. Range (deg C) | 0 to 30 | 15 to 40 | 15 to 40 | 10 to 40 |
| Primary Termination | I_min, delta_TCO | -delta_V, dT/dt | dT/dt, dV/dt = 0 | I_min @ Voltage Limit |
| Secondary Termination | Timer, delta_TCO | TCO, Timer | TCO, Timer | TCO, Timer |

### NiCd/NiMH Charge Termination

NiCd has a distinct peak in cell voltage immediately preceding full charge. A popular termination method is -delta_V: charge is terminated after the cell voltage falls 10 to 20 mV after reaching its peak.

For NiMH, the voltage peak is much less pronounced. The change in temperature with respect to time (dT/dt) is most often used as a primary charge termination method.

**NiCd Primary Termination:** -delta_V, dT/dt threshold
**NiCd Secondary Termination:** TCO (Absolute Temperature Cutoff), Timer

**NiMH Primary Termination:** dT/dt threshold, Zero dV/dt
**NiMH Secondary Termination:** TCO (Absolute Temperature Cutoff), Timer

### Li-Ion Charging

The ideal charging source for Li-Ion is a current-limited constant voltage source (CC-CV). A constant current is applied until the cell voltage reaches the final battery voltage (4.2 V +/- 50 mV for most cells). At this point, the charger switches from constant-current to constant-voltage, and the charge current gradually drops due to internal cell resistance. Charge is terminated when the current falls below a specified minimum value (I_MIN).

- Approximately 65% of total charge is delivered during constant current mode
- Final 35% is delivered during constant voltage mode
- Secondary termination: timer or absolute temperature cutoff (TCO)

**Li-Ion batteries are extremely sensitive to overcharge!** Even slight overcharging can result in a dangerous explosion or severely decrease battery life. Final charge voltage must be controlled to within about +/-50 mV of the nominal 4.2 V value.

**Effect of undercharge on capacity:** If the battery is undercharged by only 100 mV, 10% of the battery capacity is lost.

**Multiple-cell packs:** Require matched cells and voltage equalizers. Each cell's voltage is monitored within the pack, and cells with higher voltage are discharged through shunt FETs. If any cell exceeds 4.2 V, charging must be terminated. Under no circumstances should a multiple-cell Li-Ion battery pack be constructed from individual cells without providing voltage equalization!

## ADP3810/3811 Battery Charger Controller

### Key Features

- Programmable Charge Current
- Battery Voltage Limits: 4.2 V, 8.4 V, 12.6 V, 16.8 V (+/-1% accuracy, ADP3810); Adjustable (ADP3811)
- Overvoltage Comparator (6% Over Final Voltage)
- Input Supply Voltage Range 2.7 V to 16 V
- Undervoltage Shutdown for V_CC less than 2.7 V
- High Gain GM Stages for Sharp Current to Voltage Control Transition
- SO-8 Package with Single Pin Compensation

### Operation

The ADP3810 has precision resistors (R1 and R2) trimmed for standard Li-Ion cell/multiple cell voltages. The charging current is controlled by the voltage applied to the V_CTRL input pin. The charging current is monitored by the voltage at the V_CS input pin, derived from a low-side sense resistor.

**Charge current formula:**

    I_CHARGE = (1 / R_CS) x (R3 / 80 kOhm) x V_CTRL

Typical values: R_CS = 0.25 Ohm, R3 = 20 kOhm, gives I_CHARGE = 1.0 A for V_CTRL = 1.0 V.

**Final battery voltage:**

    V_BAT = 2.000 V x (R1/R2 + 1)

The current control loop and voltage control loop work together: as the battery approaches its final charge voltage, the voltage control loop takes over, becoming a voltage source that floats the battery at constant voltage.

Note: Because of the low-side sensing scheme, the ground of the circuits in the system must be isolated from the ground of the DC-DC converter.

## Off-Line, Isolated, Flyback Battery Charger

The ADP3810/3811 are ideal for isolated off-line chargers because the output stage can directly drive an optocoupler for feedback across an isolation barrier.

A current-mode flyback converter topology is used:
- Single diode for rectification, no filter inductor required
- Diode prevents battery from back driving the charger when input power is disconnected
- PWM frequency set around 100 kHz as a compromise between component sizes, switching losses, and cost
- Primary side has cycle-by-cycle current limit (R_LIM resistor) for safety if secondary circuit fails
- Output stage drives photodiode of optocoupler directly (up to 5 mA)

**V_CC bootstrapping:** A connection from the battery maintains V_CC above 2.7 V. A boosting circuit using a rectifier and 3.3 V zener diode keeps V_CC above 2.7 V as long as battery voltage is at least 1.5 V with 0.1 A programmed charge current.

The high gain of internal amplifiers ensures a sharp transition between current-mode and voltage-mode regardless of the charge current setting.

## Linear Battery Charger (ADP3820)

The ADP3820 linear regulator controller accurately charges single-cell Li-Ion batteries. Its output directly controls the gate of an external p-channel MOSFET. Required external components: MOSFET, sense resistor, input and output capacitors.

**Key Specifications:**
- +/-1% accuracy over -20 deg C to +85 deg C
- 4.2 V / 4.1 V final battery voltage options
- Low quiescent current, shutdown current < 1 uA
- Externally programmable current limit

**Efficiency trade-off:** The linear charger is very simple with minimal external components, but efficiency is poor, especially with a large difference between input and output voltages. Power loss in the MOSFET = (V_IN - V_BAT) x I_CHARGE.

## Switch Mode Dual Charger (ADP3801/ADP3802)

Complete battery charging ICs with on-chip buck regulator control circuits.

### Key Specifications

- Programmable Charge Current with High-Side Sensing
- +/-0.75% End-of-Charge Voltage
- Pin Programmable Battery Chemistry and Cell Number Select: 4.2 V (1 Li-Ion), 8.4 V (2 Li-Ion), 12.6 V (3 Li-Ion), 4.5 V (3 NiCd/NiMH), 9.0 V (6 NiCd/NiMH), 13.5 V (9 NiCd/NiMH)
- Battery voltage adjustable by up to +/-10% for different Li-Ion manufacturers
- On Chip LDO Regulator (3.3 V, up to 20 mA)
- Drives External PMOS Transistor
- PWM Oscillator: ADP3801 at 200 kHz, ADP3802 at 500 kHz
- End-of-Charge Output Signal
- Internal multiplexer for alternate charging of two separate battery stacks
- Under Voltage Lock-Out (UVLO) circuit
- SO-16 Package

### Charge Current

    I_CHARGE = V_ISET / (10 x R_CS)

For R_CS = 100 mOhm, V_ISET = 1.0 V gives I_CHARGE = 1.0 A.

### End-of-Charge Detection

When charge current drops below 80 mA (for R_CS = 0.1 Ohm), the EOC output pulls low. The EOC threshold:

    I_MIN = 8 mV / R_CS

The internal EOC comparator monitors V_CS. It is only enabled when V_BAT is at least 95% of its final value (to prevent false triggering during start-up due to soft start).

Recommended operation: Continue charging for 30 minutes after EOC signal, then shutdown the charger. Li-Ion manufacturers recommend not leaving the battery in trickle charge mode indefinitely.

### Dual Battery Selection

The ADP3801/3802 can charge two separate battery packs (different chemistries and cell counts). A two-channel MUX with "break before make" ensures the two batteries are not shorted together when switching.

## Universal Charger for Li-Ion, NiCd, and NiMH

For applications requiring charging of multiple battery types, a microcontroller is used with the ADP3801 to:

1. **Identify the battery:** Read the value of the in-pack thermistor. Different thermistor values identify Li-Ion vs NiCd/NiMH.
2. **Pre-qualify the battery:** Check voltage and temperature are within charging range.
3. **Program charge parameters:** Use PWM outputs with RC filters on BAT_PRG and I_SET pins.
4. **Monitor charge termination:**
   - For NiCd/NiMH: Monitor voltage and temperature for -delta_V or dT/dt criteria, then set to trickle charge. Program final battery voltage higher than maximum expected charging voltage.
   - For Li-Ion: Monitor EOC pin. Optionally continue charging for 30-60 minutes after EOC to top off the battery, then shutdown to prevent constant trickle charging.

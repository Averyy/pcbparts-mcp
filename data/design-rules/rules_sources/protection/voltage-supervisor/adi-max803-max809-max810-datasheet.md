---
source: "Analog Devices (Maxim) -- MAX803/MAX809/MAX810 3-Pin Microprocessor Reset Circuits"
url: "https://www.analog.com/media/en/technical-documentation/data-sheets/MAX803-MAX810Z.pdf"
format: "PDF 8pp (19-0344 Rev 11, 10/17)"
method: "fetchaller"
extracted: 2026-11-06
chars: 3011
---

# MAX803/MAX809/MAX810 3-Pin Microprocessor Reset Circuits (19-0344 Rev 11, 10/17)

Excerpts: description, ratings, output specifications and the applications sections on pull-ups and RESET below VCC = 1 V.

## General Description

The MAX803 has an open-drain output stage, while the MAX809/MAX810 have push-pull outputs. The MAX803's open-drain RESET output requires a pullup resistor that can be connected to a voltage higher than VCC. The MAX803/MAX809 have an active-low RESET output, while the MAX810 has an active-high RESET output. The reset comparator is designed to ignore fast transients on VCC, and the outputs are guaranteed to be in the correct logic state for VCC down to 1V.

Benefits and Features: Guaranteed Reset Valid to VCC = +1V.

## Absolute Maximum Ratings

RESET (open drain) ... -0.3V to +6.0V
Output Current, RESET, RESET ... 20mA

## Electrical Characteristics

| PARAMETER | CONDITIONS | MAX | UNITS |
| --- | --- | --- | --- |
| RESET Output Voltage Low (MAX803 and MAX809) | VCC = VTH (min), ISINK = 1.2mA, MAX803R/S/T/Z, MAX809R/S/T/Z | 0.3 | V |
|  | VCC = VTH (min), ISINK = 3.2mA, MAX803L/M, MAX809J/L/M | 0.4 | V |
|  | VCC > 1.0V, ISINK = 50µA | 0.3 | V |
| RESET Open-Drain Output Leakage Current (MAX803) | VCC > VTH, RESET deasserted | 1 | µA |

## Detailed Description

The MAX803 uses an open-drain output, and the MAX809/MAX810 have a push-pull output stage. Connect a pullup resistor on the MAX803's RESET output to any supply between 0 and 6V.

## Ensuring a Valid Reset Output Down to VCC = 0V

When VCC falls below 1V, the MAX809 RESET output no longer sinks current—it becomes an open circuit. Therefore, high-impedance CMOS logic inputs connected to RESET can drift to undetermined voltages. This presents no problem in most applications since most μP and other circuitry is inoperative with VCC below 1V. However, in applications where RESET must be valid down to 0V, adding a pull-down resistor to RESET causes any stray leakage currents to flow to ground, holding RESET low (Figure 2). R1's value is not critical; 100kΩ is large enough not to load RESET and small enough to pull RESET to ground.

A 100kΩ pullup resistor to VCC is also recommended for the MAX810 if RESET is required to remain valid for VCC < 1V.

(Figure 2, "RESET Valid to VCC = Ground Circuit", shows the push-pull MAX809 with R1 = 100kΩ from RESET to GND.)

## MAX803 Open-Drain RESET Output Allows Use with Multiple Supplies

Generally, the pullup connected to the MAX803 will connect to the supply voltage that is being monitored at the IC's VCC pin. However, some systems may use the opendrain output to level-shift from the monitored supply to reset circuitry powered by some other supply (Figure 4). Note that as the MAX803's VCC decreases below 1V, so does the IC's ability to sink current at RESET. Also, with any pullup, RESET will be pulled high as VCC decays toward 0. The voltage where this occurs depends on the pullup resistor value and the voltage to which it is connected.

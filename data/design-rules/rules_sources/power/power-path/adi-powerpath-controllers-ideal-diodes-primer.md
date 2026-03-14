---
source: "ADI -- PowerPath Controllers/Ideal Diodes Primer"
url: "https://www.analog.com/en/resources/technical-articles/primer-on-powerpath-controllers-ideal-diodes-prioritizers.html"
format: "HTML"
method: "readability"
extracted: 2026-02-16
chars: 9690
---

# Primer on PowerPath Controllers, Ideal Diodes & Prioritizers

Electronic systems powered by multiple DC sources are commonplace - they include handheld devices (USB port and battery), portable instruments (wall adapter and battery), and high-availability servers (main and redundant/auxiliary supply rails). Selecting the correct input supply to power the system is not a trivial task, as an improper implementation oscillates between supplies, causes power brownouts, or damages the input supplies by allowing reverse current. Analog Devices' PowerPath™ controllers simplify this task of dynamic supply selection.

## PowerPath Controllers

A multi-input power system has switches multiplexing the input supplies to a common output load. A PowerPath controller is basically what the name hints—it selects and controls the path on which power flows to the system. The controller selects the input source based on highest voltage or highest priority; the former type is called an ideal diode, while the latter is called a prioritizer. PowerPath controllers employ integrated or external, single or back-to-back, P- or N-channel MOSFET switches to multiplex up to three input supplies to the common output load. More than three supplies are multiplexed by employing multiple controllers.

Figure 1. A PowerPath Controller for Multiple Power Supply Inputs

## Ideal Diodes

Ideal diodes are MOSFETs with a control circuit around them (Figure 2), turning on with a low voltage drop (below 50mV) in the forward bias condition (input voltage greater than output voltage) and turning off when reverse biased (input voltage less than output voltage). Ideal diodes (aka active diodes) reduce voltage and power losses by a factor of ten or more when compared to power Schottky diodes. Heat sinking requirements are minimized, yielding a compact solution. Low voltage supply (5V, 3.3V, or lower) applications gain increased voltage headroom. Ideal diodes also include additional monitoring and protection features not available with standard diodes. Like conventional diodes, ideal diodes combine (diode-OR) supplies together to provide redundancy in the event of input failure or short-circuit. Additionally, they can be used for output supply holdup during input brownouts, reverse battery protection (LTC4359), or balancing supply currents (LTC4370).

Figure 2: N-Channel and P-Channel Ideal Diode Controllers

The voltage drop across an ideal diode can be calculated as ILOAD • RDS(ON). For a 5mΩ RDS(ON) MOSFET with 10A load current, the ideal diode voltage drop calculates to 50mV. Table 1 compares this voltage loss to the 500mV typical drop of a power Schottky diode, at different input supply voltages. As shown, a Schottky diode’s voltage drop becomes intolerable at low supply voltages, eating away a significant portion of the operating voltage. An ideal diode is the only feasible solution at low input voltages.

**Table 1. Diode Voltage Loss as a Percentage of Input Voltage**

|  |  |  |
| --- | --- | --- |
| 1.8V | 28% | 2.8% |
| 3.3V | 15% | 1.5% |
| 5V | 10% | 1% |
| 12V | 4.2% | 0.4% |
| 48V | 1% | 0.1% |

Ideal diode power dissipation is calculated as ILOAD2 • RDS(ON), while for the 0.5V Schottky diode it is calculated as 0.5V • ILOAD. Figure 3 compares the power dissipation of these two diodes: the ideal diode power savings increases with load current, eliminating or shrinking heat sinks to save board area.

Figure 3: Schottky Diode and Ideal Diode Power Loss vs. Load Current

## The Ideal Diode in Actual Practice

There are two methods of constructing an ideal diode—one employs comparators, while the other uses a linear servo amplifier. The comparator based technique either allows DC reverse current (possibly damaging power supply) or it oscillates between on and off at light load currents or during supply switchover, injecting noise in to the system. Conversely, linear control of the forward voltage drop across the MOSFET ensures smooth supply switchover without oscillation, even under light loads. Hence, linear servo is the technique used by all Analog Devices ideal diodes. The voltage drop across the N-channel MOSFET source-to-drain is regulated to a small reference voltage by an amplifier. In Figure 4a, a 15mV difference between the input supply voltage (NFET source) and the load voltage (NFET drain) is maintained by controlling the gate voltage (hence the MOSFET resistance) even as the load current changes. As the load increases, the gate voltage will rail out at its maximum value and the MOSFET behaves as a resistor, its forward voltage drop increasing linearly with current. Figure 4b illustrates the resulting IV characteristic of this 15mV ideal diode.

Figure 4a. Linear Servo Amplifier Based Ideal Diode Implementation

Figure 4b. Corresponding Ideal Diode IV Characteristic

## Is the Ideal Diode MOSFET Backwards?

This is a common question when looking at an ideal diode circuit. Let’s consider the N-channel ideal diode in Figure 2. N-channel power MOSFETs have an inherent body diode pointing from source to drain (i.e., anode connected to source and cathode to drain). If the drain pin was connected to the input and source to the output, the body diode allows reverse current flow from load to supply, which is not desired. Therefore, an N-channel MOSFET’s source pin is connected to the input in ideal diode circuits. With this orientation, load current flows through the body diode until the MOSFET gate turns on and current gets diverted through the MOSFET channel.

## Prioritizers

A diode-OR selects the highest voltage input supply to power the output (there is some droop current sharing when the input voltages are close). This is suitable for redundant supplies with similar nominal voltages. In some applications, especially in portable electronics powered by wall adapter and battery, voltage is not the main criteria for powering the system. The wall adapter powers the system as long as it is available, i.e., it has higher priority than the battery. A prioritizer enables the user to select which power source appears at the load, independent of voltage levels. This can be implemented with an ideal diode-OR circuit that monitors the high priority source (12V wall adapter in Figure 5) with a resistive divider (R2A, R2C) and disables the lower priority supply (E2# input) as long as the higher priority supply is available (above 9V threshold). An extra MOSFET (Q3) is needed to block the parallel forward current path through the ideal diode MOSFET (Q2) body diode on the backup supply (4-cell Li-Ion battery).

Figure 5: Prioritizing a 12V Wall Adapter Over a 14.4V 4-Cell Li-Ion Battery

The above implementation works for a 2-input system but gets complicated with 3-inputs. The LTC4417 prioritizer is designed specifically for prioritizing three supplies in the 2.5V to 36V range (Figure 6); it selects the highest priority valid supply among three inputs to power the load. Priority is defined by pin assignment (V1 is highest priority and V3 is lowest priority), while a supply is considered valid after it has been inside a voltage window set by 1.5% accurate undervoltage and overvoltage thresholds for 256ms. The LTC4417 simplifies designs, deriving power from multiple, disparate voltage sources common in handheld and high availability electronics. In such systems, a prioritizer is a better solution than a simple diode-OR, especially when the preferred power source is not the highest voltage. A limited power source such as a battery (V2, 14.8V) can be given lower priority than a wall adapter (V1, 12V), even though the battery voltage is higher, extending battery run time.

Figure 6: LTC4417 Triple Prioritizer Circuit and Operation

## MOSFET Types and Configurations

Both N-channel and P-channel PowerPath controllers are available. In addition, the MOSFET can be integrated, or the controller may require an external MOSFET. Each option provides flexibility in how the circuit operates. N-channel MOSFETs have higher mobility than P-channel MOSFETs and carry more current; for high current applications (above 5A), N-channel MOSFETs may be preferred. However, N-channel controllers require a gate voltage higher than the supply voltage to enhance (turn on) the MOSFET. This is why a charge pump or boost regulator is included inside positive supply N-channel controllers. P-channel controllers pull the MOSFET gate low for turn on, eliminating the need for a charge pump. Integrated MOSFETs provide a compact solution but are limited in current levels; external MOSFET controllers allow the user to optimize the MOSFET for a specific current level, lowest RDS(ON) (including connecting multiple MOSFETs in parallel for high current applications), thermal performance, etc. A single MOSFET allows forward current to flow through its body diode even when the MOSFET channel is turned off by the gate. To provide complete blocking for both forward and reverse currents during gate turn-off, some controllers are capable of driving back-to-back connected MOSFETs (Q2, Q3 in Figure 5).

## Summary

Analog Devices offers a wide array of PowerPath controllers that minimize power dissipation, reduce voltage drop and provide more functionality than a typical diode. These devices are ideal for a wide range of applications, from high-end datacom and server systems to portable battery-powered products.
---
source: "ADI AN-1311 -- Power Supply Sequencing"
url: "https://www.analog.com/en/resources/app-notes/an-1311.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 7746
---
### Introduction

Power supply sequencing is required for microcontrollers, field
programmable gate arrays (FPGAs), digital signal processors
(DSPs), analog-to-digital converters (ADCs), and other devices
that operate from multiple voltage rails. These applications
typically require that the core and analog blocks be powered up
before the digital input/output (I/O) rails, although some
designs may require other sequences. Proper power-up and
power-down sequencing can prevent both immediate damage
from latch-up and long-term damage from electrostatic
discharge (ESD). In addition, sequencing the supplies staggers
the inrush current during power-up, an especially helpful
technique in applications operating from current-limited supplies.

This application note discusses the advantages and disadvantages
of using discrete components to sequence the power supplies
and describes a simple, yet effective, method of achieving
sequencing by using the internal precision enable pins of the
[ADP5134](/en/products/adp5134.html), which combines two 1.2 A buck regulators with two 300 mA low dropout (LDO) regulators. This application note
also describes sequencer ICs that may be useful for applications
that require more accurate and flexible sequencing.

Figure 1 shows an application that requires multiple supply rails.
These rails are the core supply (VCCINT), I/O supply (VCCO),
auxiliary supply (VCCAUX), and system memory supply.

Figure 1. Typical Method for Powering Processors and FPGAs.

For example, the Xilinx® Spartan-3A FPGA has a built-in
power-on reset circuit that ensures that all supplies have reached
their thresholds before it allows the device to be configured.
The power-on reset circuit reduces the strict requirement for
power sequencing; however, to minimize inrush current levels
and to observe sequencing requirements of circuits attached to
the FPGA, the supply rails must be powered up as follows:
VCCINT followed by VCCAUX followed by VCCO. Note that some
applications require specific sequences; therefore, always refer
to the power requirements section of the relevant data sheet.

### Simple Power Supply Sequencing Using Passive Delay Networks

A simple way to sequence power supplies is to delay the signal
going to the enable pin of a regulator with passive components,
such as resistors, capacitors, and diodes, as shown in Figure 2.
When the switch closes, D1 conducts while D2 is left open. C1
charges with the voltage at EN2 rising at a rate determined by
R1 and C1. When the switch opens, C1 discharges to ground
through R2, D2, and RPULL. The voltage at EN2 falls at a rate
determined by R2, RPULL, and C1. Changing the values of R1 and
R2 changes the charging and discharging times, thereby setting
the turn-on and turn-off times of the regulator.

Figure 2. Simple Power Supply Sequencing Method Using Resistors, Capacitors, and Diodes.

This method may be useful for applications that do not require
precise sequencing. Applications where delaying signals is
sufficient may require only the external resistor and capacitor.
The disadvantage of using this method with standard regulators
is that the logic threshold of the enable pins may vary widely
with voltage and temperature. In addition, the delay in the
voltage ramp depends on the values and tolerances of the
resistor and capacitor. A typical X5R capacitor varies by about
±15% over the –55°C to +85°C temperature range and another
±10% due to dc bias effects, making the timing imprecise and
sometimes unreliable.

### Precision Enables Make Sequencing Easy

To achieve stable threshold levels for precise timing control,
most regulators require an external voltage reference. The
ADP5134 overcomes this problem by integrating a precision
reference, saving significant cost and printed circuit board
(PCB) area. Each regulator has an individual enable input.

When the voltage at the enable input rises above the ENx pin
rising threshold (VIH\_EN [0.9 V minimum]), the device comes out
of shutdown, and the housekeeping block is turned on; however,
the regulator is not activated. The voltage at the enable input is
compared to a precise internal reference voltage (0.97 V typical).
When the voltage at the enable pin goes above the precision
enable threshold, the regulator is activated, and the output
voltage starts to rise. The reference varies by only ±3% over
input voltage and temperature corners. This small range ensures
precise timing control, resolving the issues seen with using
discrete components.

When the voltage at the enable input drops 80 mV (typical) below
the reference voltage, the regulator is deactivated. When the voltage
on all enable inputs drops below the ENx falling threshold
(VIL\_EN [0.35 V maximum]), the device enters shutdown mode.
In this mode, the current consumption falls to less than 1 µA.
Figure 3 and Figure 4 demonstrate the accuracy of the ADP5134
precision enable thresholds for BUCK1 over temperature.

Figure 3. Precision Enable Turn-On Threshold over Temperature, 10 Samples.

Figure 4. Precision Enable Turn-Off Threshold over Temperature, 10 Samples.

### Simple Power Supply Sequencing Using Resistor Dividers

Multichannel supplies can be sequenced by connecting an
attenuated version of the output of one regulator to the enable
pin of the next regulator to be powered up, as shown in Figure 5,
where the regulators turn on or off sequentially: BUCK1 to
BUCK2 to LDO1 to LDO2. Figure 6 shows the power-up
sequence after EN1 is connected to VIN1. Figure 7 shows the
shutdown sequence after EN1 is disconnected from VIN1.

Figure 5. Simple Sequencing with the ADP5134.

Figure 6. ADP5134 Start-Up Sequence.

Figure 7. ADP5134 Shutdown Sequence.

### Sequencer ICs Improve Timing Accuracy

In some cases, achieving precise timing is more important than
reducing PCB area and cost. For these applications, a voltage
monitoring and sequencer IC such as the [ADM1184](/en/products/adm1184.html) quad
voltage monitor, which offers ±0.8% accuracy over voltage and
temperature, can be used. Another choice is the [ADM1186](/en/products/adm1186.html) quad
voltage sequencer and monitor with programmable timing; this
device may be useful in applications that require more elaborate

For example, the [ADP5034](/en/products/adp5034.html) 4-channel regulator includes two
3 MHz, 1200 mA buck regulators and two 300 mA LDOs. A
typical sequencing function can be implemented by using the
ADM1184 to monitor the output voltage of one regulator and
to provide a logic high signal to the enable pin of the next
regulator when the output voltage being monitored reaches a
certain level. This method, shown in Figure 8, can be used with
regulators that do not provide a precision enable function.

Figure 8. Sequencing the ADP5034 4-Channel Regulator Using the ADM1184 Quad Voltage Monitor.

### Conclusion

Sequencing using the ADP5134 precision enable inputs is simple
and easy to implement, requiring only two external resistors per
channel. More elaborate sequencing can be achieved by using
the ADM1184 or ADM1186 voltage monitors.

## References

[Augusta, Chris and Martin Murnane. AN-932 Application
Note. *Power Supply Sequencing. Analog Devices, Inc., 2008*](/en/resources/app-notes/an-932.html).

*Xilinx DS529 Spartan-3A FPGA Family Data Sheet*. Xilinx, Inc.,
2010.

In addition, refer to the [power management](/en/product-category/power.html) web page and the
[power management/sequencing](/en/product-category/power-system-managers-sequencers.html) web page for more information.

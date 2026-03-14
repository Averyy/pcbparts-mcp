---
source: "ADI -- Low IQ Ideal Diode Controller (LTC4357/LTC4359)"
url: "https://www.analog.com/en/resources/technical-articles/low-iq-ideal-diode-controller-with-reverse-input-protection.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 13047
---

# Low IQ Ideal Diode Controller with Reverse Input Protection for Automotive and Telecom Power Solutions

Blocking diodes are widely used in power supplies to solve a variety of problems. In automotive systems, a series blocking diode protects against accidental reverse battery connections when the battery is replaced or the car is jump started. High availability systems and telecom power distributions employ blocking diodes to achieve redundancy by paralleling power supplies. Diodes are also used to prevent discharge of reservoir capacitors in situations where some temporary holdup of output voltage is necessary to ride through input dropouts or noise spikes, or to allow the load to gracefully power down when the input supply abruptly fails.

While blocking diodes are easy to understand and apply, their forward drop results in significant power dissipation, making them unsuitable in both low voltage and high current applications. In low voltage applications, the forward voltage drop becomes a limiting factor for a circuit’s operating range, even when using a Schottky barrier diode. At least 500mV of supply headroom is lost across a series diode—a substantial degradation in 12V automotive systems where the supply can drop to as low as 4V during cold crank.

Since diodes operate at a fixed voltage drop of 400mV to 700mV minimum, regardless of current rating, power dissipation becomes an issue in the 1A–2A range, for surface mount applications. In applications greater than 5A, power dissipation becomes a major issue, requiring elaborate thermal layouts or costly heat sinks to keep the diode cool. Circuit designers need a better solution.

One solution is to replace diodes with MOSFET switches. The MOSFET is connected so that its body diode points in the same direction as the diode it replaces, but during forward conduction the MOSFET is turned on, shorting the body diode with a low loss path through the MOSFET channel. When the current reverses, the MOSFET is turned off, and the body diode blocks the flow of current, thus maintaining the diode behavior. The forward drop and power dissipation are reduced by as much as a factor of 10. This forms the basis of an “ideal” diode, when compared to conventional p-n or Schottky barrier diodes.

The [LTC4357](/en/products/ltc4357.html) and [LTC4359](/en/products/ltc4359.html) are ideal diode controllers, designed to drive N-channel MOSFETs in a wide variety of power supply reverse blocking, ORing and holdup applications. MOSFETs with RDS(ON) specifications as low as 1mΩ are readily available, so ideal diodes can be built to handle currents in excess of 50A using a single pass device while maintaining voltage and power loss levels 10 times better than any diode solution.

The LTC4357 and LTC4359 both replace a diode, but the latter has a wider operating range down to 4V and its quiescent current is a quarter of the former. The LTC4359’s /SHDN pin reduces the quiescent current and turns the LTC4359 solution into a load switch, a feature the LTC4357 and diode solutions do not have. Table 1 highlights the features of the LTC4357 and LTC4359.

The LTC4359 is a low quiescent current controller with a wide operating range of 4V–80V. The 4V end of the operating range is particularly important in low voltage applications, where the diode drop is not tolerable, while the 80V rating allows it to operate and survive transients in 48V telecom systems and automotive environments. The LTC4359 protects downstream circuitry from reverse inputs down to −40V, seen when battery terminals are misconnected.

When operating from a battery, minimizing discharge current is important in normal operation, and becomes crucial when the load is off. The LTC4359 features a low quiescent current of 155µA typical, which can be further reduced to 14µA when placed in shutdown. Although the MOSFET is turned off in shutdown, its body diode can still conduct forward current. Some applications require the ability to turn on/off a load or to control the delivery of power independent of supply voltage. The LTC4359 accomplishes this by driving two N-channel MOSFETs as a load switch to block forward and reverse current.

Table 1. Ideal diode controllers

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| LTC4357 | 9V–80V | 650µA | 20µA | 0.5µs turn-off time with 2A gate pull-down |
| LTC4359 | 4V–80V | 155µA | 10µA | Low IQ shutdown mode, reverse input protection to −40V, controls single or back-to-back MOSFETs |

## How It Works

The LTC4359 controls an N-channel MOSFET, shown as Q1 in the block diagram of Figure 1. The MOSFET source is connected to the input supply and acts like the anode of the diode, while the drain is the cathode. When power is first applied, the load current initially flows through the body diode of the MOSFET. The LTC4359 senses the voltage drop from IN-OUT and drives the MOSFET on. The internal amplifier (GATE AMP) and charge pump try to maintain 30mV drop across the MOSFET. If the load current causes more than 30mV of voltage drop, the MOSFET is driven fully on, and the forward drop increases according to RDS(ON) • ILOAD.

Figure 1. Block diagram of the LTC4359

If the load current is reduced, the GATE AMP drives the MOSFET gate lower to maintain a 30mV drop. If the forward current is reduced to a point where 30mV cannot be supported, the GATE AMP drives the MOSFET off. This prevents DC reverse current and allows smooth switchover without oscillation in redundant power supply applications.

In the event of an input short, the current quickly reverses and is supplied by output capacitance or another supply. The fast pull-down comparator (FPD COMP) senses reverse current by measuring the drop across the MOSFET between IN and OUT. When there is more than −30mV across the MOSFET, the FPD COMP comparator responds by pulling the MOSFET gate low in less than 500ns.

The SHDN pin controls the IC and the external MOSFETs. Pulling /SHDN pin low turns off the IC and external MOSFETs, while reducing the current to a mere 14µA. To turn the IC on, the /SHDN pin can either be left floating or driven high. If left floating, an internal 2.6µA current source pulls up /SHDN.

## Better Than a Schottky Diode

A MOSFET based diode solution reduces the power dissipation and forward voltage drop over a Schottky diode, and is more versatile, with a vast selection of MOSFETs available for virtually any voltage and current combination. Figures 2 and 3 compare the power dissipation and forward voltage drop of an SBG2040CT Schottky diode to a BSC028N06NS MOSFET. At 20A, the BSC028N06NS 2.8mΩ MOSFET dissipates only 1W, saving 8W of power dissipation over the SBG2040CT Schottky diode. The MOSFET’s greatly reduced forward voltage drop of RDS(ON) • ILOAD = 56mV, compared to 450mV with the Schottky diode, enables circuits to operate at a lower voltage.

Figure 2. Power dissipation vs load current

Figure 3. Load current vs forward voltage drop

## 12V/20A Automotive Diode With Reverse Input Protection

Figure 4 shows a typical 12V, 20A application that can handle reverse inputs to −40V. The forward drop is a mere 56mV at full load current, due to the MOSFET’s low on-resistance of 2.8mΩ.

Figure 4. 12V/20A ideal diode with reverse input protection

During input shorts, potentially destructive transients can appear at the IN, SOURCE and OUT pins. D1 and D2 protect IN and SOURCE by clamping the voltage transients to less than −40V. Q1, a 60V BVDSS MOSFET with avalanche rating of 50A, absorbs the inductive energy and prevents IN, SOURCE and OUT from exceeding their absolute maximum ratings.

Downstream circuitry, such as DC/DC converters and linear regulators require protection against voltages seen by reverse inputs and misconnected battery terminals. The LTC4359’s input pins are rated to −40V. To keep the MOSFET off, an internal NEGATIVE COMP comparator senses when the SOURCE pin is negative with respect to VSS by at least 1.7V, and pulls down on the GATE pin. With the MOSFET off, the negative voltage is prevented from reaching the load. Reverse input protection is limited to about −40V by the dissipation in R1.

## Diode as a Load Switch

The LTC4359 can be used as a switch to control delivery of power to the load. A diode, whether it’s a Schottky diode or the circuit of Figure 4, always conducts forward current. In shutdown, the LTC4359 turns off the MOSFET, but its body diode still conducts forward current.

To block forward current, an additional MOSFET, Q2, is added as shown in Figure 5. The /SHDN pin serves as the control signal to turn on/off the load switch. Pulling /SHDN low turns off both MOSFETs: Q2 blocks forward current, while Q1 prevents reverse current. The MOSFET body diodes point in opposite directions, which blocks forward and reverse current flow. Floating or driving /SHDN high turns on the IC and enables diode behavior in the MOSFETs. During turn-on, inrush current can be limited by controlling the slew rate at the GATE pin with the gate capacitor, C1, and the LTC4359’s controlled gate current.

Figure 5. 28V load switch and ideal diode with reverse input protection

For multiple power supplies, duplicating Figure 5 enables active power source selection regardless of relative source voltage. This is in contrast to a passive selection scheme where strict diode behavior simply selects the input source with the highest voltage supply.

## Paralleling Supplies

Multiple LTC4359s can be used to combine the outputs of two or more supplies for redundancy or for droop sharing, as shown in Figure 6. For redundant supplies, the supply with the highest output voltage sources most or all of the load current. If the supply’s output is shorted to ground while delivering load current, the current temporarily reverses, flowing backward through the MOSFET. The LTC4359 senses this reverse current and activates the fast pull-down comparator (FPD COMP) and turns off the MOSFET in 500ns.

Figure 6. Redundant power supplies

If the other, initially lower, supply is not delivering any load current at the time of the fault, the output falls until the body diode of its ORing MOSFET conducts. Meanwhile, the LTC4359 charges the MOSFET gate with 10µA until the forward drop reduces to 30mV. If this supply is sharing load current at the time of the fault, its associated ORing MOSFET simply drives the MOSFET gate harder in an effort to maintain a drop of 30mV.

Droop sharing can be accomplished if both power supply output voltages and output impedances are nearly equal. The 30mV regulation technique ensures smooth load sharing between outputs without oscillation. The degree of sharing is a function of MOSFET RDS(ON), the output impedance of the supplies and their initial output voltages, as prescribed by Ohm’s law.

## Extending Reverse Input Protection Range

Figure 7 shows the LTC4359 configured as a 48V ideal diode protected against reverse input voltage. R2 is added to extend the VIN–VOUT range to −100VDC with the effect of reducing the forward regulation by 10mV. In applications where the output is held up at +48V by a second supply or by charged capacitors, Q1 will block a reversed 48V input supply. In non-redundant applications where the output can be expected to fall to zero when the input supply is removed or accidently reversed, inputs of up to −100VDC are successfully blocked from reaching the output.

Figure 7. 48V ideal diode with reverse input protection

R2 is a pulse-rated component so that VIN–VOUT transients in excess of −100V are easily tolerated. Q1 was selected for its combination of 250V BVDSS and exceptionally low RDS(ON) of 20mΩ, but its avalanche rating is a modest 320mJ with 47A maximum avalanche current. In the event the reverse current exceeds the MOSFET avalanche current rating, D6 can be added to protect Q1 by absorbing any avalanche energy, and this limits the peak VIN–VOUT voltage to −150V. Beyond this point D6 breaks down and passes transient current pulses through to the output.

## Conclusion

The LTC4359 ideal diode controller replaces Schottky diodes, and also can drive a load switch. At currents of 1A–2A or more, the LTC4359 is superior to Schottky diode solutions. With its wide 4V–80V operating range and reverse input capability, the LTC4359 maintains low forward drop in low voltage applications through automotive cold crank, and protects the load from reverse battery connections. Shutdown mode further reduces the already low quiescent current of 155µA down to 14µA and can be used as an on/off control signal for a load switch. The LTC4359 is an excellent fit for automotive as well as telecom and redundant power supply applications.
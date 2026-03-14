---
source: "ADI -- LTC4412 Ideal Diode Controller"
url: "https://www.analog.com/en/resources/technical-articles/ideal-diode-controller-eliminates-energy-wasting-diodes-in-power-or-ing-applications.html"
format: "HTML"
method: "readability"
extracted: 2026-02-16
chars: 10573
---

# Ideal Diode Controller Eliminates Energy Wasting Diodes in Power OR-ing Applications

## Introduction

Many modern electronic devices need a means to automatically and smoothly switch between power sources when prompted by the insertion or removal of any source. The [LTC4412](/en/products/ltc4412.html) permits low loss OR-ing of multiple power sources for extended battery life and low self-heating. The LTC4412 controls external P-channel MOSFET power switches to create a near ideal diode function for power switchover applications or load sharing PowerPath™ management applications. When conducting, the voltage drop across the MOSFET is typically only 20mV. It also provides power monitoring circuitry and external control for integration with other parts of the power management system. The low component count results in a low overall system cost and, with its ThinSOT™ 6-pin package, a compact design solution. It’s versatile enough to be used in a variety of diode OR-ing applications.

For battery powered applications that also can be powered from a wall adapter or other “auxiliary” power source, the load is automatically disconnected from the battery when the auxiliary source is connected, so that no current is drawn from the battery. When the auxiliary source is disconnected, operation reverts back to the battery. An AC adapter present signal is available. The LTC4412 also has built in reverse supply protection. Multiple LTC4412s can be ganged together to provide load sharing between multiple batteries, or to allow multiple batteries to be charged from a single battery charger. The precisely controlled ideal diode behavior of the LTC4412 is crucial to maintain current balance when multiple batteries are discharged or charged while connected to a single load or source.

The advantages of the LTC4412 ideal diode PowerPath controller are shown in Figure 1. The forward voltage drop of the ideal diode is far less than that of a conventional diode and the reverse current leakage can be smaller for the ideal diode as well. The tiny forward voltage drop lowers power losses and self-heating, resulting in extended battery life. The very low reverse leakage, when compared to Schottky diodes, is also beneficial in some applications.

Figure 1. LTC4412 Ideal diode controller vs Schottky diode characteristics.

The wide supply operating range of 2.5V to 28V supports operation with one to six Li-Ion batteries in series. The types of power sources that can be used include all those that are within the supply operating range. The low quiescent current of 11µA with a 3.6V supply is independent of the load current. The LTC4412 also features a status pin that can be used to enable an auxiliary MOSFET power switch for additional power savings when an auxiliary input is utilized. It may also be used to indicate to a microcontroller that an auxiliary supply, such as a wall adapter, is present. A control input pin is provided to extend applications to those that can benefit from external control, such as from a microcontroller.

Applications include anything that must take power from several inputs, including cellular phones, portable computers, PDAs, MP3 players and electronic video and still cameras, USB peripherals, wire-ORed multi-powered equipment, uninterruptible power supplies for alarm and emergency systems, systems with standby capabilities, systems that use load sharing between two or more batteries, multi-battery chargers, and logic controlled power switches.

## How It Works

Figure 2 shows a circuit that automatically switches the power supply between a battery and a wall adapter (or other types of power inputs). The supply inputs are slowly ramped, as seen in Figure 3, to illustrate operation of the circuit. For the sake of this discussion the load is purely resistive, and the terms primary and auxiliary are arbitrary and interchangeable.

Figure 2. Automatic power switching between a battery and a wall adapter.

Figure 3. Operation waveforms.

First the battery primary input, which powers the VIN pin, is ramped up from 0V while the auxiliary input is absent. At about 0.6V the drain-source diode of the P-channel MOSFET transistor begins to forward bias and pulls the output up (time B1). Once the primary input reaches a voltage sufficient to drive the MOSFET gate and power the LTC4412, the forward regulation mode is achieved (B2). Now the output voltage is regulated to typically 20mV (10mV min) below the input. If the load current varies, the GATE pin voltage is controlled to maintain 20mV unless the load current exceeds the P-channel MOSFET’s ability to deliver the current with a 20mV VDS. If the RON is not low enough to maintain forward regulation then the gate voltage reaches ground or clamps 7V below the higher of the voltages on the VIN or SENSE pins. Once clamped the MOSFET behaves as a constant low value resistor, and the forward voltage increases slightly. During this forward regulation mode of operation the STAT pin is an open circuit and the 470k resistor pulls the voltage up to the VCC supply, which can be as high as 28V.

When a wall adapter or other supply connected to the auxiliary input is applied the SENSE pin voltage rises. The battery voltage also rises slightly from being unloaded. As the SENSE voltage pulls above VIN – 20mV the LTC4412 pulls the GATE voltage up to turn off the P-channel MOSFET (A1). When the voltage on SENSE exceeds VIN + 20mV the STAT pin sinks 10µA of current to indicate that an AC wall adapter is present. The system is now in the reverse turn off mode. Power to the load is being delivered through the external diode and no current is drawn from the battery. Should the primary input now be removed there is no effect (A2). When the primary input is applied and the auxiliary input is removed the circuit reverts to battery operation (B3).

The external diode is used to protect against auxiliary input faults. A silicon diode could be used instead of the Schottky, but will result in higher power dissipation and heating due to the higher forward voltage drop. The wall adapter voltage must be high enough to overcome the diodes forward voltage drop. Note that the external MOSFET is wired so that the drain to source diode will reverse bias when a wall adapter input is applied. If the control input (CTL pin) is asserted high the GATE voltage is forced to the higher of the voltages on the VIN pin or the SENSE pin turning the MOSFET off. Also the STAT pin will sink 10µA of current if connected. This feature is useful for forced switching of the load between two power sources. The drain to source diode inherent in MOSFETs require that series back to back MOSFETs, with gates tied together, be used to fully isolate a power source.

## Lowest Loss Automatic PowerPath Control

Figure 4 illustrates an application circuit for automatic switchover of load between a battery and a wall adapter that features lower power loss in the auxiliary path than the circuit of Figure 2. Operation is similar to Figure 2 except that a P-channel MOSFET (Q2) replaces the diode. The STAT pin is used to turn on Q2 once the SENSE pin voltage exceeds the battery voltage by 20mV. When the wall adapter input is applied the drain-source diode of Q2 turns on first to pull up the SENSE pin and load voltages, followed by Q2’s gate turning on. Once Q2 has turned on, the voltage drop across it can be very low depending on the MOSFET’s characteristics.

Figure 4. Lowest loss automatic power switching between a battery and a wall adapter.

## Load Sharing

Figure 5 illustrates an application circuit for dual battery load sharing with automatic switchover of power between batteries and a wall adapter. Whichever battery can supply the higher voltage provides the load current until it is discharged to the voltage of the other battery. Then, the load is shared between the two batteries with the higher capacity battery providing proportionally higher current to the load. When a wall adapter input is applied both MOSFETs turn off and no load current is drawn from the batteries. The STAT pins provide information as to which input is supplying the load current. This concept can be applied to as many power inputs as are needed.

Figure 5. Dual battery load sharing with automatic switchover of power from batteries to wall adapter.

## Multiple Battery Charging

Figure 6 shows an application circuit for automatically charging two batteries from a single charger. Whichever battery has the lower voltage receives the charging current until both battery voltages are equal then both will be charged. When both are charged simultaneously the higher capacity battery receives proportionally higher current from the charger. For Li-Ion batteries both batteries achieve the float voltage of the battery charger minus the forward regulation voltage of 20mV. This concept can apply to more than two batteries. The STAT pins provide information as to which batteries are being charged.

Figure 6. Automatic dual battery charging from single charging source.

## High Side Power Switch

Figure 7 illustrates an application circuit for a logic controlled high side power switch using the control input pin. When the CTL pin is a logical low the LTC4412 turns on the MOSFET. Because the SENSE pin is grounded the LTC4412’s internal controller functions as an open-loop comparator and applies maximum gate drive voltage to the MOSFET. When the CTL pin is a logical high the LTC4412 turns off the MOSFET by pulling its gate voltage up to the supply input voltage, therefore denying power to the load. The MOSFET is connected with its source connected to the power source. This prevents the drain-source diode from supplying voltage to the load when the MOSFET is off.

Figure 7. Logic controlled high side power switch.

## Conclusion

The LTC4412 provides a simple and efficient way to implement a low loss ideal diode controller that extends battery life and significantly reduces self-heating. The low external parts count translates directly to low overall system cost and its ThinSOT 6-pin package makes for compact design solutions. It’s versatile enough to be used in a variety of diode OR-ing applications covering a wide range of supply voltages.
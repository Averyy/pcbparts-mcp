---
source: "TI SLVAF35 -- Driving High-Voltage Contactors in EV and HEVs"
url: "https://www.ti.com/lit/pdf/slvaf35"
format: "PDF 8pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 17545
---

Technical White Paper
Driving High-Voltage Contactors in EV and HEVs
Shuangbing Dong Powertrain Automotive Systems
ABSTRACT
This article provides a general introduction of the high-voltage contactors in EV and HEVs, and presents several
approaches on how to drive the high-voltage contactors.
Table of Contents
1 Introduction.............................................................................................................................................................................2
2 Contactors Distribution in EVs and HEVs............................................................................................................................2
3 Power-Up Sequence...............................................................................................................................................................3
4 Coil Types and Control Requirements..................................................................................................................................3
5 Coil Driving Implementation..................................................................................................................................................4
5.1 Pulse Width Modulation Current Generation......................................................................................................................5
5.2 Adjustable Supply Voltage Approach.................................................................................................................................6
6 Summary ................................................................................................................................................................................6
7 Revision History......................................................................................................................................................................7
List of Figures
Figure 2-1. Contactors Distribution in EV and HEVs...................................................................................................................2
Figure 3-1. Power-Up Sequence With Main Contactors and Pre-Charge Contactor...................................................................3
Figure 4-1. Coil Current With Three Phases ...............................................................................................................................3
Figure 5-1. Implementation Example of Coil Driving Circuit........................................................................................................4
Figure 5-2. Pulse Width Modulation Current Generation.............................................................................................................5
Figure 5-3. Current Generation With Adjustable Supply Voltage.................................................................................................6

SLVAF35A – FEBRUARY 2021 – REVISED JULY 2024 Driving High-Voltage Contactors in EV and HEVs 1

1 Introduction
A high-voltage contactor, also called a high-voltage relay without distinction in the industry, is widely used in
electric vehicles (EV) and hybrid electric vehicles (HEV). It is an electromechanical switching device with a coil to
generate a magnetic force that mechanically operates an electric contact. However, it is more common to use a
high-voltage contactor to represent high-power applications in EV and HEVs.
As a key safety device in new energy vehicles, a high-voltage contactor needs basic functions that are resistant
to high voltage, load, shock, strong arc extinguishing, and breaking capacity. An appropriate current is applied to
the coil such as using an IC, such as DRV3946, to ensure proper force to drive the contacts for robust operation.
Even though there are many different types of contactors for different functions in a vehicle, the driving current
profiles of all the contactor coils are similar.
2 Contactors Distribution in EVs and HEVs
The battery and the traction inverter are electrically isolated by main contactors when the vehicle is switched
off for safety reasons. The main positive contactor is between the positive battery pole and the traction inverter
while the main negative contactor is between the negative battery pole and the traction inverter. Both these
contactors are required for safety robustness. The pre-charge contactor with a series current-limiting resistor is
in parallel with the main positive contactor and used to charge the initially discharged DC link capacitor before
closing the main contactors to avoid the high inrush current which might damage the battery, power contactors,
and DC link capacitor. The two main contactors and one pre-charge contactor comprise an indispensable
configuration for full HEVs.
Motor
retrevnI
Fast DC Auxiliary
Charger
AC/DC
AC/DC: Onboard charger
yrettaB

(1)
(2)
(5)
(3)
(1) Main contactors
(2) Pre-charge contactor
(3) DC charge contactors
(4) AC charge contactors
(5) Auxiliary contactor (e.g. heater)
(4)
Figure 2-1. Contactors Distribution in EV and HEVs
In plug-in HEVs, a pair of additional AC charge contactors is inserted to establish a connection between the
traction battery and the onboard charger. The onboard charger of the vehicle gets power from an AC charger,
converts that AC power to DC to charge the battery.
For battery EVs, another pair of DC fast charge contactors is inserted to establish a connection between the
traction battery and the DC fast-charge equipment. The DC fast charging is essential for long distance driving
and large battery EV fleets. An auxiliary contactor like the electric heater for the passenger compartment is
mandatory because there is no waste heat available from a combustion engine.
Main contactors, pre-charge contactors, and DC charge contactors are mostly located in the battery junction box
(or battery disconnect unit). AC charge contactors are likely to be placed in the battery power distribution unit
which is adjacent to the onboard charger.
2 Driving High-Voltage Contactors in EV and HEVs SLVAF35A – FEBRUARY 2021 – REVISED JULY 2024

3 Power-Up Sequence
The traction inverter motor control system must integrate a large bank of filter capacitors, typically called DC link
capacitors, which generates a huge inrush current once the main contactors are closed while the capacitors are
fully discharged. Therefore, a pre-charge function is mandatory to limit the inrush current during the power-up
procedure. A contactor combined with a current-limiting resistor is the simplest implementation of the pre-charge
function.
A process example during the power-up sequence follows:
1. Close the main negative contactor after power-up command is received.
2. Close the pre-charge contactor.
3. Close the main positive contactor until the voltage at the DC link capacitor reaches 90%–95% of battery
pack voltage.
4. Open the pre-charge contactor after the main positive contactor is fully closed.
Main Positive
Contactor
ON
Main Negative
Contactor OFF
R ON
Pre-charge Pre-charge
Resistor DC Link Contactor OFF OFF
Pre-charge
Capacitor Motor
Contactor ON
Main Positive
Contactor OFF
DC Link
Main Negative
Voltage
Contactor
Figure 3-1. Power-Up Sequence With Main Contactors and Pre-Charge Contactor
Additionally, no contact can be stuck and no insulation leakage failure is allowed before closing the contactors.
Contactor status diagnosis and insulation detection must be implemented in the system-level design.
4 Coil Types and Control Requirements
The coil is a crucial component of high-voltage contactors as it provides the driving force to close the contacts.
The current through the coil generates a magnetic field which attracts the moving core to close the contacts,
and on the contrary open the contacts. Even though there are several high-voltage contactor vendors in the
market, such as TE, Panasonic, GIGAVIC, and so on, the driving current requirements of all the contactor coils
are similar. The current profile can be divided into three phases, as shown in Figure 4-1. The first phase is
known as pickup phase, the current should be large enough and keep long enough to ensure the contactor is
closed during the phase. The second phase is the hold phase, where a smaller current is kept to efficiently close
the contactor and keep it closed. The last phase is current fast decay, during this phase the current drops very
quickly to quench the contacts opening. Figure 4-1 shows the three phases requirement of the current curve, the
actual currents in the pickup phase and hold phase could be PWM signals with maximum and minimum values.
Current Pickup Current
Hold Current
Fast Decay
Current
Pickup Phase Hold Phase
Time
Fast Decay
Figure 4-1. Coil Current With Three Phases
SLVAF35A – FEBRUARY 2021 – REVISED JULY 2024 Driving High-Voltage Contactors in EV and HEVs 3

Generally, the contactor vendors provide two contactor coil types: one is an economized coil with an internal
economizer and the other is a non-economized coil that requires external economization. The economized coil
integrates an internal economizer with one of several methods such as a two coil economizer, pulse-width
modulation with voltage feedback, and pulse-width modulation with current feedback. It is only needed to power
the two terminals of the coil and the desired current waveform is generated by itself with this internal economizer.
The non-economized coil stands for this is only a coil without any internal circuit and needs external circuits to
generate the desired current waveform.
5 Coil Driving Implementation
It is more preferable from the system perspective to use both high-side and low-side switches to drive the
contactor coil for safety reasons. The coil will always be energized and cannot be shut off when short-circuit
failure happens if only the high- or low-side switch is used. The failure is in line with a short circuit to the battery
on the high-side switch and short circuit to ground on the low-side switch. A large current flows through the coil
and cannot be switched off, thus the coil might be damaged due to high power dissipation.
BAT
High-side
ON/OFF
Diagnosis
Fast decay
Freewheeling Coil
Diagnosis
Current sense Shunt
Low-side
PWM
Inside Controller Outside Controller
Figure 5-1. Implementation Example of Coil Driving Circuit
Implementing an elaborate design is indispensable to achieve the current profile. Otherwise, the current through
the coil reaches the maximum value determined by the applied voltage divided by coil resistance. Generally,
the maximum and minimum current for both pickup phase and hold phase are stipulated in each specification
to ensure the proper operation of the contactor. Some vendors prefer to stipulate the minimum effective current
in each phase. These currents are much smaller than the current determined by the supply voltage and coil
resistance. This not only helps save energy consumption, but also extends contactor operation lifetime.
4 Driving High-Voltage Contactors in EV and HEVs SLVAF35A – FEBRUARY 2021 – REVISED JULY 2024

Figure 5-1 shows how to drive contactor coils with both high- and low-side switches. It is supplied by the battery
voltage. Both high- and low-side switches can do PWM control, but it is more suitable to use a low-side switch
for high-frequency PWM control up to 25kHz. Here the high-side switch acts as ON/OFF control and protects the
coil while short-circuit failures happen at the low-side terminal. A freewheeling diode is necessary, because the
current through the coil must not interrupt suddenly while turning off the low-side switch. Otherwise, there could
be a very large voltage spike due to the coil inductance and probably damage the components. A fast-decay
diode is added to generate a large reverse voltage across the coil when both high- and low-side switches are
turned off. This large reverse voltage makes the coil current drop to zero quickly. Meanwhile, diagnosis features
at both high- and low-side terminals are necessary for automotive applications.
A fully integrated high-power contactor driver like DRV3946-Q1 simplifies the implementation of the complex
current regulation to achieve the required current profile. This dual-channel device has the ability to program the
pick up and hold phase current making it more robust and efficient way to drive the contactor.
5.1 Pulse Width Modulation Current Generation
It is very common to use pulse width modulation to generate a desired current waveform in the industry. The
duty cycle, which is the ratio of the ON time to the period of the signal, determines the maximum and minimum
currents applied to the coil with the control frequency.
And there are two control methods typically used for the PWM control. The first one is voltage feedback, the
other one is current feedback. The voltage feedback is an open loop control for current. It measures the supply
voltage and sets the duty cycle accordingly. Even though it is a low-cost realization with simple hardware circuit,
the current accuracy is poor and a large margin is always left in order to ensure proper operation. Besides,
additional effort of pre-calibration work is necessary to get a voltage-duty cycle map for different contactors.
BAT BAT
ON ON
Measurement
Current Sense
Determine PWM PWM
Duty Cycle Based
On Supply Voltage Two Point Current PWM
Regulation Determines
PWM Duty Cycle
(a) Voltage Feedback (b) Current Feedback
Figure 5-2. Pulse Width Modulation Current Generation
SLVAF35A – FEBRUARY 2021 – REVISED JULY 2024 Driving High-Voltage Contactors in EV and HEVs 5

The current feedback is a closed loop control for current. It measures the coil current all the time and toggles
the switches according to the current directly. This can ensure high current accuracy and make the coil current
highly consistent with the required current. In addition, voltage-duty cycle map is no longer needed and save
the pre-calibration effort. However, the cost of this current feedback approach is probably more expensive than
the voltage feedback solution. DRV3946-Q1 has integrated current sense which enables the closed loop control
eliminating the cost of the current feedback approach.
5.2 Adjustable Supply Voltage Approach
In above description, battery voltage is supplied to drive the contactor coil. However, the battery voltage is not
a fixed value and has a large range during normal operation. That is why dedicated PWM control is introduced
to obtain desired current. Because the current is determined by the applied supply voltage divided by the coil
resistance, an adjustable supply voltage to the coil is another option. Figure 5-3 shows the adjustable supply
voltage applied to drive the contactor coil. A DC/DC converter is the best solution converting battery voltage to
adjustable supply voltage. And high-side switch can be eliminated if DC/DC converter integrates Enable/Disable
control.
BAT
DC/DC
Adjustable Supply
Figure 5-3. Current Generation With Adjustable Supply Voltage
It is more like moving PWM control from the coil driving switches to the DC/DC converter. The DC/DC output
voltage depends on the coil resistance for a required current. Thus, the output voltages during pickup phase and
hold phase are not same. Meanwhile, it is better to integrate current sense to check whether the current flowing
through the coil equals to the required value.
6 Summary
Contactors are widely used in EV and HEVs to connect and break power supply lines. The required current
curve generated by the coil driving the circuit is mandatory to ensure proper operation of the contactor. Attention
should be paid to EMC issues due to high current and high frequency. In addition, smart contactors with special
controls and diagnosis features are already used by some customers.
Meanwhile, there is a trend that solid-state switches replace electromechanical contactors for low noise, high
reliability, and a long lifetime. In general, the contactors can fail by welding closed while the failure mode of
solid-state switches is mostly open. However, there are also some drawbacks for the solid-state switches. The
cost of solid-state switches is currently high and there is a fixed-value voltage drop on output due to internal
impedance. Also, there is a leakage current even in OFF mode. That is why it is stipulated that at least one
electromechanical contactor must be retained at a pole while a solid-state switch is used in the other pole.
6 Driving High-Voltage Contactors in EV and HEVs SLVAF35A – FEBRUARY 2021 – REVISED JULY 2024

7 Revision History
NOTE: Page numbers for previous revisions may differ from page numbers in the current version.
Changes from Revision * (February 2021) to Revision A (July 2024) Page
• Updated Section 1..............................................................................................................................................2
• Updated Section 5..............................................................................................................................................4
• Updated Section 5.1...........................................................................................................................................5
SLVAF35A – FEBRUARY 2021 – REVISED JULY 2024 Driving High-Voltage Contactors in EV and HEVs 7
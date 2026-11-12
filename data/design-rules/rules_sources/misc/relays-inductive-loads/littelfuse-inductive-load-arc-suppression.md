Source: https://www.littelfuse.com/assetdocs/inductive-load-arc-suppression-application-note?assetguid=67c3a678-da06-4c93-9aa2-d20d951138e2
Retrieved: 2026-11-10

# Application Note: Inductive Load Arc Suppression (Littelfuse, 2016, 2 pages)

## Introduction

When a reed switch or reed sensor is used to control an inductive device (relay coil, solenoid, transformer, small motor, etc.), the energy stored in the inductance in the device will subject the switch contacts to a high voltage when the reed switch opens. When the switch contacts open, the contact gap is initially small. Arcing across this contact gap can occur immediately after the switch opens. This can happen in resistive as well as inductive loads, but inductive loads generate a higher voltage and this causes increased arcing. Increased arcing decreases switch life. Direct current (DC) inductive circuits typically use a diode to prevent the high voltage. The diode in the circuit is called a suppression diode, flyback diode, freewheeling diode, or catch diode. However, a diode cannot be used in an alternating current (AC) circuit. AC arc suppression requires the use of a metal-oxide varistor (MOV), a bidirectional transient voltage suppressor (TVS) diode, or an RC suppression network. An RC suppression network is also called a snubber. The various arc suppression methods have various advantages and disadvantages. Using no suppression is also an option if life is adequate without it. Which method to use is determined by trade-offs between cost, contact life, packaging, etc.

## Considerations (p.1)

RC suppression has the advantage of limiting the switch contact voltage at the time of switch opening when the size of the contact gap is small. RC suppression can also be used to reduce arcing and improve life in resistive loads. With RC suppression, a series connected capacitor and resistor network is placed across (in parallel with) the switch contact. Alternatively, the capacitor and resistor can be placed across the load. Placing the RC snubber across the switch contact is preferred, but this has the disadvantage of providing a current path to the load through the snubber when the switch is open. Placing the snubber across the load eliminates the current, but wiring and source impedance variation may change the effectiveness of the arc suppression.

The values of the resistor and capacitor used in the snubber are by necessity compromises. The resistor value must be large enough to limit the capacitive discharge current when the switch contacts close, but small enough to adequately limit the voltage when the switch contacts open. Larger capacitor values decrease the voltage when the switch contacts open but they cost more and also increase the capacitive discharge energy when the switch contacts close.

The MOV and TVS diode devices conduct current when a threshold voltage is exceeded. These devices are usually placed across (in parallel with) the switch contact. These devices can work well for lower voltages such as 24 VAC and can also work for higher inductance 120 VAC loads. MOV devices have more capacitance than TVS diodes. If an MOV is used, the effect of MOV capacitance should be reviewed. A separate Hamlin application note discusses capacitive loads.

## Selecting values (p.2)

To select an approximate resistor value, use Ohm's law: V = I * R, or in this case R = V / I. Choose R between 0.5 * Vpk / Isw and 3 * Vpk / Isw, where Vpk is the AC peak voltage (VRMS * 1.414) and Isw is the rated switching current of the reed switch or sensor. A lower R decreases the contact wear from arcing. A higher R decreases the contact wear from the capacitive inrush current.

To select an appropriate capacitor value, start with C = 0.1 μF (100 nF) as this is a commonly used and therefore cost-effective value. Increase the value if evaluation of performance shows this to be inadequate.

Performance of the selected snubber values can be evaluated several ways. Some evaluation can be done by calculation or by simulation. However, the inductive and resistive characteristics of the load may not be precisely known – the inductance of electromechanical loads varies as the mechanical components change position.

It is recommended that the voltage waveform across the switch contacts be evaluated with an oscilloscope, particularly during contact opening. The snubber should reduce or eliminate the arcing that occurs between contact-closed and contact-open. After the contact opens, the voltage will rise. The rising voltage should not re-initiate contact arcing. In addition, the maximum voltage across the snubber's capacitor should not exceed the capacitor's voltage rating.

For a reed switch, another good method of evaluating whether or not the snubber is performing effectively is to look at the intensity of the light produced by the arc in the switch contact gap. Less light is a result of less arc energy and indicates longer life will be achieved.

The last and most accurate method of evaluating the performance is to perform a life test. Contact life is related to the number of switching cycles, not to the number of powered or unpowered hours. The maximum recommended number of operations per second for life testing of arcing loads is 5 to 50 operations per second (max. 5 – 50 Hz). The maximum test rate is dependent on the electrical load and the trade-off of expediency versus accuracy.

When determining component specifications for a snubber, there are a few additional items to consider beyond the previously mentioned checks of arc evaluation, maximum capacitor voltage, and life. When the switch contacts are open, a current will be flowing through the snubber network. It should be verified that this "leakage" current does not cause issues in the application and that the power dissipation in the snubber's resistor does not exceed its power rating. In addition, another consideration is that an RC snubber network may be used in combination with a bidirectional TVS diode or MOV. The snubber is more effective in limiting the initial voltage across the opening contacts. The TVS or MOV can be more effective in limiting the peak voltages.

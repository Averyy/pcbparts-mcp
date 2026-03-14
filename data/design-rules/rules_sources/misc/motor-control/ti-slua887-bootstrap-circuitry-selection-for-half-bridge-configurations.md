---
source: "TI SLUA887 -- Bootstrap Circuitry Selection for Half-Bridge Configurations"
url: "https://www.ti.com/document-viewer/lit/html/SLUA887"
format: "HTML"
method: "pdfplumber"
extracted: 2026-02-16
chars: 14097
---

Application Note
Bootstrap Circuitry Selection for Half-Bridge
Configurations
Mamadou Diallo High Power Drivers
ABSTRACT
Driving MOSFETs in half-bridge configurations present many challenges for designers. One of those challenges
is generating bias for the high-side FET. A bootstrap circuit takes care of this issue when properly designed.
This document uses UCC27710, TI's 620V half-bridge gate driver with interlock to present the different
components in a bootstrap circuit and how to properly select them in order to ensure predictable switching
of the power FETs.
Table of Contents
1 Introduction.............................................................................................................................................................................2
2 Basic Operation of Bootstrap Circuit....................................................................................................................................2
3 Bootstrap Components Selection.........................................................................................................................................3
3.1 Bootstrap Capacitor...........................................................................................................................................................3
3.2 VDD Bypass Capacitor......................................................................................................................................................4
3.3 External Bootstrap Diode...................................................................................................................................................4
3.4 Bootstrap Resistor..............................................................................................................................................................6
4 Layout Considerations for Bootstrap Components............................................................................................................7
5 Summary ................................................................................................................................................................................8
6 References..............................................................................................................................................................................8
7 Revision History......................................................................................................................................................................8
List of Figures
Figure 2-1. Bootstrap Charging Path...........................................................................................................................................2
Figure 2-2. Bootstrap Capacitor Discharging Path......................................................................................................................2
Figure 3-1. Reverse Recovery Losses due to Bootstrap Diode Reverse Recovery Time...........................................................4
Figure 3-2. Reverse Recovery Losses due to Bootstrap Diode Reverse Recovery Time (Zoomed Out)....................................5
Figure 3-3. HB_HS Ringing Effects on Switch Node...................................................................................................................5
Figure 3-4. VDD/HB-HS Fast Ramp Up (R = 0Ohms)............................................................................................................6
boot
Figure 3-5. VDD/HB-HS Fast Ramp Up (R = 2.2Ohms).........................................................................................................7
Figure 4-1. Layout Example using UCC27710............................................................................................................................7

1 Introduction
When using half-bridge configurations, it is necessary to generate high-side bias to drive the gate of the
high-side FET referenced to the switch node. One of the most popular and cost effective way for designers to do
so is the use of a bootstrap circuit which consists of a capacitor, a diode, a resistor and a bypass capacitor.
This application report will explain how this circuit works, the key components of the bootstrap circuits and
their impact in the gate drive. This app note will put emphasis on half-bridge gate drives using drivers with no
built-in bootstrap diode, which gives designers flexibility and reduces power dissipation in the gate driver IC.
Additionally, it will discuss the layout considerations for the different components of this circuit.
2 Basic Operation of Bootstrap Circuit
A bootstrap circuit is used in half-bridge configurations to supply bias to the high-side FET. Figure 2-1 shows
the charging path of a bootstrap circuit in a simplified half-bridge configuration using UCC27710, TI's 620V
half-bridge driver with interlock. When the low-side FET is on (high-side FET is off), the HS pin and the switch
node are pulled to ground; the VDD bias supply, through the bypass capacitor, charges the bootstrap capacitor
through the bootstrap diode and resistor.
Figure 2-1. Bootstrap Charging Path
When the low-side FET is turned off and the high-side is on, the HS pin of the gate driver and the switch
node are pulled to the high voltage bus HV; the bootstrap capacitor discharges some of the stored voltage
(accumulated during the charging sequence) to the high-side FET through the HO and HS pins of the gate driver
as shown in Figure 2-2.
Figure 2-2. Bootstrap Capacitor Discharging Path
3 Bootstrap Components Selection
This section discusses each component's role and its impact in the gate drive.
3.1 Bootstrap Capacitor
From a design perspective, this is the most important component because it provides a low impedance path to
source the high peak currents to charge the high-side switch. As a general rule of thumb, this bootstrap capacitor
should be sized to have enough energy to drive the gate of the high-side MOSFET without being depleted
by more than 10%. This bootstrap cap should be at least 10 times greater than the gate capacitance of the
high-side FET. The reason for that is to allow for capacitance shift from DC bias and temperature, and also
skipped cycles that occur during load transients. The gate capacitance can be determined using Equation 1:
(1)
Qg
Cg= VQ1g
where Qg: gate charge MOSFET’s datasheet
VQ1g=VDD−VBootDiode
where VBootDiode: forward voltage drop across the boot diode.
Once the gate charge determined, the minimum value for the bootstrap capacitor can be estimated using
Equation 2:
(2)
Alternati C vbeolyo,t ≥ a m 10 o × re C dgetailed calculation of the minimum bootstrap capacitor value can be done using Equation
3:
(3)
Qtotal
Cboot≥ ∆VHB
Dmax IHB
Qtotal=QG+IHBS× fsw + fsw
where:
·QG=Total MOSFET gate charge MOSFET’s datasheet
·IHBS=HB to VSS leakage current gate driver′s datasheet
·Dmax=Maximum duty cycle
·IHB=HB Quiescent current Gate driver’s datasheet
And
∆VHB=VDD−VDH−VHBL
where:
·VDD=Supply voltage of the gate driver IC
·VDH=Bootstrap diode forward voltage drop Bootstrap diode datasheet
·VHBL=HB UVLO falling threshold Gate driver datasheet
It is important to note that values below the minimum required bootstrap capacitor value could lead to activation
of the driver's UVLO therefore prematurely turning off the high-side FET. On the flip side, higher values of the
bootstrap capacitor lead to lower ripple voltage and longer reverse recovery time in some conditions (when
initially charging the bootstrap cap or with a narrow bootstrap charging period) as well as higher peak current
through the bootstrap diode. Equation 4 relates the bootstrap cap and the peak currents through the bootstrap
diode.
(4)
dv
Ipeak=Cboot× dt
It is generally recommended to use low ESR and ESL surface mount multi-layer ceramic capacitors (MLCC) with
good voltage ratings (2xVDD), temperature coefficients and capacitance tolerances.
3.2 VDD Bypass Capacitor
The charge to replenish the bootstrap capacitor must come from some larger bypass capacitor, usually the VDD
bypass capacitor. As a rule of thumb, this bypass capacitor should be sized to be at least 10 times larger than
the bootstrap capacitor so that it is not completely drained during the charging time of the bootstrap capacitor.
This allows the bootstrap capacitor to be properly resplenished during the charging sequence. This 10x ratio
results in 10% maximum ripple on the VDD capacitor in worst case conditions.
(5)
3.3 ExteCVrnDDal≥ B1o0o×tCsBtoroatp Diode
In order to minimize losses associated with the reverse recovery properties of the diode and ground noise
bouncing, a fast recovery diode or Schottky diode with low forward voltage drop and low junction capacitance is
recommended. Using Schottky diodes reduce the risk associated with charge supplied back to the gate driver
supply from the bootstrap capacitor and minimize leakage current. Figure 3-1, shows the reverse recovery
losses when using diodes with reverse recovery times on HB-HS(Ch1). We can observe large amount of over
and undershoot on the HB-HS pin which can trigger the driver's UVLO and shutdown the gate driver.
When the HS pin (switch node) is pulled to a higher voltage, the diode must be able reverse bias fast enough
to block any charges from the bootstrap capacitor to the VDD supply. This bootstrap diode should be carefully
chosen such that it is capable of handling the peak transient currents during start-up; and such that its voltage
rating is higher than the system DC-link voltage with enough margins.
Figure 3-1. Reverse Recovery Losses due to Bootstrap Diode Reverse Recovery Time
Figure 3-2 below shows a reverse recovery condition created (channel 1) by setting up the timing to specifically
force the switch node high with the diode current flowing.
Figure 3-2. Reverse Recovery Losses due to Bootstrap Diode Reverse Recovery Time (Zoomed Out)
Figure 3-3 shows the effects of the losses on the HB-HS pin which can trigger the switch node and potentially
damage the driver.
Figure 3-3. HB_HS Ringing Effects on Switch Node
3.4 Bootstrap Resistor
The role of the bootstrap resistor is to limit the peak currents at the bootstrap diode during start-up, it should
therefore be carefully selected as it introduces a time constant with the bootstrap capacitor given by Equation 6:
(6)
RBoot×CBoot
τ= Duty Cycle
This time constant occuring during the high-side off time explains the dependency on duty cycle. This duty
cycle being constant, the bootstrap resistor and bootstrap capacitor should be tuned appropriately to achieve the
desired start-up time. Increasing the bootstrap resistor values will increase the time constant leading to slower
start-up time.
Additionally, the bootstrap resistor chosen must be able to withstand high power dissipation during the first
charging sequence of the bootstrap capacitor. This energy can be estimated by Equation 7:
(7)
1 2
This ene 2 rg × y C is b o d o i t s × si V p C abtoeodt during the charging time of the bootstrap capacitor and can be estimated using
Equation 8:
(8)
This resi E st ≅ or 3 is × e C sbosoetn × tia R lb oino tlimiting the peak currents through the bootstrap diode at start-up and limiting the dv/dt
of HB-HS (high-side floating supply to the return high-side floating supply). The peak current through this resistor
can be calculated using Equation 9:
(9)
VDD−VBootDiode
Figure 3 I - p 4 k s = hows th R ebo foatst ramp up on VDD (CH4) and HB-HS (CH1) when using a 0-Ohm resistor which leads to
undesired change in voltage on LO(CH3) and HO(CH2).
Figure 3-4. VDD/HB-HS Fast Ramp Up (R = 0Ohms)
Figure 3-5 shows how using slightly higher resistor value (R = 2.2Ohms) solve this issue. It is important to
note that the bias rising rate observed in Figure 3-5 does not apply to all drivers.
Figure 3-5. VDD/HB-HS Fast Ramp Up (R = 2.2Ohms)
4 Layout Considerations for Bootstrap Components
Once all bootstrap components appropriately selected, it is important to carefully place these components in
order to minimize parasitic inductances and reduce high current trace length. This high current path includes
the bootstrap capacitor, the bootstrap diode, the ground-referenced VDD bypass capacitor of the driver, and the
low-side power switch. It is therefore important to reduce that path and keep that loop as small as possible. The
bootstrap capacitor and bypass capacitor should be placed as closed as possible to the gate driver supply pins.
Figure 4-1 below shows a good layout example using UCC27710 with all bootstrap components located near the
gate driver IC minimizing any effects of parasitic inductances and reducing the high peak currents path of the
bootstrap circuit. It is also important to separate high voltage power and low voltage signal traces.
Figure 4-1. Layout Example using UCC27710
5 Summary
This application report used UCC27710, TI's 600V family of half-bridge drivers to discuss the basic operation
of a bootstrap circuit in a half-bridge configuration. It also discussed the role and importance of each bootstrap
components required to generate bias for the high-side FET in half-bridge configurations. It showed a detailed
calculation method as well as a general rule of thumb estimation for the bootstrap capacitor. Additionally, it
discussed how to properly place these components on a PCB layout once all the components are appropriately
selected.
6 References
• UCC27710 Product Folder
• UCC27710 Datasheet
• UCC27710 Evaluation Module
• Half-bridge Driver Products
• Fundamentals of MOSFET and IGBT Gate Driver Circuits
7 Revision History
Changes from Revision * (August 2018) to Revision A (September 2023) Page
• Updated the numbering format for tables, figures, and cross-references throughout the document.................1
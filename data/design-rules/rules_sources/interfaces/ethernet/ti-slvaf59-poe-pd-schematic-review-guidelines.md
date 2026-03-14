---
source: "TI SLVAF59 -- PoE PD Schematic Review Guidelines"
url: "https://www.ti.com/document-viewer/lit/html/SLVAF59"
format: "HTML"
method: "ti-html"
extracted: 2026-02-16
chars: 29341
---

# 1 Introduction

The following document provides a step-by-step
procedure to review Power over Ethernet designs for the Powered Device side of the
cable, and the accompanying DCDC. The best advice is to find an EVM or reference design
that most closely matches the design. For example, if the design is a 5-V output
synchronous flyback with a 48-V adapter on the primary with the TPS23758, use the
TPS23758EVM-080 to compare. Check every component and note the differences. The
following is a detailed process for reviewing schematics. Some components will have more
details than others since some are typically changed or changing them has known effects.
Others typically remain the same. Following the IEEE standard for PoE (802.3) is
normally recommended because that enables interoperability. There are certain components
that cannot be changed or the tolerance is minimal to meet the standard. However, many
TI parts also integrate a DCDC controller, where there is more freedom to choose parts.
Please consider the guidance with standards as immoveable and guidance to DCDC as
advice.

# 2 PoE

## 2.1 PoE Input

Find the RJ45 input jack. This should connect the
twisted pairs with both the data and the power to the Ethernet PHY transformer. This
transformer separates the data from the power. Ensure that the pairsets are correct
for PoE. The pairsets are 1 and 2, 3 and 6, 4 and 5, 7 and 8. Note that two pairsets
do not have to connect to the transformer the two pairs can connect to the diode
bridge directly. Ensure that the power side and the data side of the transformer are
correct. Sometimes the inductor is not included on the data side. Also note that two
pairs does not have to connect to the data transformer, they can connect to the
diode bridge directly. Also check they have the power side and the data side of the
transformer correct. Backwards will not support the current, some will not have the
inductors on the data side. Review the data sheet of the Ethernet PHY.

Figure 2-1 Input Transformer

Terminate the pairsets with [Bob-Smith terminations](https://www.ti.com/lit/an/slua469/slua469.pdf?ts=1613488928783&ref_url=https%253A%252F%252Fwww.google.com%252F). Without them, the PoE will probably not work with detection. Connect the Bob-Smith (BS) plane to Earth ground; if Earth ground is not available, then connect it to secondary ground. If it is connected to secondary ground, there should be a provision for a common mode choke on the input. If it is connected to secondary ground, there should be a provision for a common mode choke on the input.

Figure 2-2 Bob-Smith Terminations

Ensure the data lines are properly terminated. This guide is focused on the power portion of the cable. How these are terminated should be in the PHY transformer data sheet, but it will normally be pulled up to a 3.3-V rail; this information is in the data sheet.

Figure 2-3 Input Transformer Data Lines Terminations

Follow the input pairsets to their respective
rectifier. This can be discrete diodes as shown in [Figure 2-4](GUID-E2A56D35-11FA-4287-A36B-85CE7AD4C215.html#GUID-2638E47F-B8DD-4930-BF88-DD23B91B1A20), it can be an integrated FET bridge, integrated diode bridge, discrete FET/diode
combination (called a hybrid). For 13-W designs, typically a discrete diode bridge
is best since it is lowest cost. Since this is the lowest power design, there is low
losses in the diodes since there is low current. As we move to 25-W, 51-W, and 71-W
of power, the losses in the diodes increase since the input current increases (from
around 250mA to 1.5A). At 25-W, it can be decided if the diodes are acceptable, or
to use FETs or an integrated solution. Usually this is costly for 25-W solution but
it can be done. At 51-W and above, FETs are almost required. A hybrid bridge is used
in the 51W TPS23730EVM-093. At 71-W, an integrated solution is optimal. With this
much power, it also affects thermals with so much current going through these
diodes. In any design, ensure the diodes or FETs can handle maximum current (lowest
input voltage, maximum power). Remember that 25-W can be sent through two pairsets
instead of four. The max current would be 676mA – and we double it for the rating –
1.2A or 2A diodes. The DEN resistor will need to change with the input bridge type.
Please see the detection resistor in the PoE Settings Section.

Figure 2-4 Input Rectifying Bridge: Discrete Diode Bridge

There should be some EMI filtering if we are following the power after it is rectified. It is suggested to leave space for an EMI choke. These help with conducted emissions. It is also suggested to have space for ferrite beads that are in series with the EMI choke. These help with radiated emissions. For part selection, ensure they are properly rated for the power. Please also connect the ferrite beads and EMI choke in series to add their properties. If they are in parallel, one can be bypassed so their effects do not add.

Figure 2-5 Input EMI Filter Components

There should also be some input capacitors. These
are required for filtering and for detection. The
IEEE 802.3 detection is an impedance not just a
resistance. So, the maximum input capacitance is
120nF. Please note that the detection will not
work if this is violated.

Figure 2-6 Input Detection Capacitance

Figure 2-7 Input Detection Capacitance Continued

Next check for a TVS diode on the input lines
(VDD-VSS). This diode is critical since it
protects the IC from overvoltage events like ESD
or surge. This diode should be a SMAJ **58.** A
bigger package is needed for outdoor applications.
The **58** is critical. This sets the clamping
voltage, and this is around 92-V. The next size up
is 98-V, but the IC VDD\_VSS abs max is 100V – so a
98-V clamp is too close. Damage has been observed
in the field with this rating. Please give some
margin with the **58** part.

Figure 2-8 TVS Diode: VDD\_VSS

VDD-VSS always requires a small bypass capacitor, usually 0.1uF. This should always be here, and contributes to the 120nF max between VDD and VSS for detection.

Figure 2-9 VDD\_VSS Bypass Capacitor

TVS between VSS\_RTN. This TVS helps protect the internal pass FET during surge and ESD events. It is recommended for outdoor applications, but makes a design more reliable in all applications. Surge is a system level issue, so system level solutions are required. So it is good practice to have space for a TVS between VSS\_RTN just in case three months into the design, it fails surge.

Figure 2-10 TVS Diode: VSS\_RTN

## 2.2 PoE Pin Settings

These pins are simple resistor and
capacitor settings that tell about the PoE settings

1. Check DEN: the resistor should be
   24.9K if a diode bridge. If a hybrid or integrated rectifier, then a higher
   resistance is needed to account for the MOSFET having lower resistance than a
   diode. Use something between 25.5K and 27K as needed.
2. Check the class resistors and
   ensure they are connected to VSS and are the correct class resistors for the
   power needed.
3. If there is SCDIS ensure it is
   set properly as the MCU needs.
4. REF should be a resistor to VSS
   as defined in the data sheet – use an EVM if the value cannot be found.
5. If there is EMPS ensure it is set
   to what is needed: turn on Auto MPS or not.
6. PPD enables wide-Vin applications
   for passive PoE.

Figure 2-11 PoE IC Settings

TPH, TPL, BT, T2P, and APO are all
signals intended for an MCU. They should be connected to an optocoupler with pull
ups to either VCC or VB as appropriate. VDD can also be used.

Figure 2-12 TPH, TPL, and BT
Outputs

# 3 DCDC

## 3.1 DCDC IC Settings

These settings are resistors on the IC
that set characteristics of the DCDC. VCC: needs a bypass capacitor – 0.1uF:

Figure 3-1 VCC Bypass Capacitor

FRS sets the switching frequency. This
is typically set to 250kHz since that has been found to be the optimal switching
frequency to maximize efficiency for the typical PoE input range and output voltage.
Other ranges can be set but ensure the transformer is rated for the appropriate
switching frequency. Each IC as a chart that shows the resistor chosen vs the
switching frequency.

Figure 3-2 FRS Resistor Setting Chart
Example

1. DTHR sets dithering. Ensure that
   it is either enabled (connected to FRS somehow) or disabled (connected to VB).
   Not both
2. DT sets the deadtime (if there
   are two gate drives). For 250kHz switching frequency this should be between 40ns
   and 90ns (typically ). Please note that topologies that do not require a second
   gate drive but the part has one, DT must be connected to VB in order to
   work.
3. I\_STP sets the soft-stop rate (by
   setting the current that drains out of the SST cap). Typically, 499K is
   fine.
4. SST needs a capacitor to set the
   soft-start and soft-start times
5. Vb needs a bypass capacitor –
   usually 0.1uF
6. Vbg needs a capacitor
7. PSRS sets the primary side
   regulation topology – diode or synchronous --- if used at all
8. LineUV sets the IC shutdown
   voltage level – the IC monitors the input voltage through LINEUV. So, set the
   shutdown level to usually 37V. This will set the voltage that soft-stop turns
   on. A divider is usually the same for all designs since the input voltage and
   shutdown voltage do not change

Figure 3-3 LINEUV Resistor
Divider

If PSR is used CP will need a resistor
and cap to clamp the internal FET for sync flybacks.

Figure 3-4 DCDC Pin Settings

## 3.2 Primary Side of the DCDC

The primary side of the DCDC is the left side of the transformer. Most PoE designs use flybacks or active clamp forward topologies to achieve isolation. Typically, the primary side is very similar between designs because the input voltage and power levels are very consistent. With EVM’s and reference designs, if there is one already determined for the power level (example, 51W), then the input current and voltage and therefore power are always going to be the same. Copying an EVM minimizes risk for proper operation.

Input Bulk Capacitor: PoE requires an input bulk
capacitor to provide enough energy for the DCDC. This capacitor requires ESR –
preferably this is an electrolytic cap. However, ceramics can be used, but a 1 ohm
resistor between the cap bank and RTN is strongly recommended for startup. The bulk
capacitance is good in helping with transients (voltage spikes). It is important to
have. The bulk capacitor is recommended to be within the following range for the
appropriate power level as shown in [Table 3-1](GUID-2ED37E62-0817-4DDA-9F29-EBF7AE338498.html#GUID-4C74B40F-B630-478E-B0E0-F6C67EE43E03).

Table 3-1 Input Bulk Capacitor Reference

| Power | Bulk Cap |
| --- | --- |
| 13W | 10-22uF |
| 25W | 33-47uF |
| 50W | 68-100uF |
| 70W | 100uF-200uF |

Figure 3-5 Input Bulk Capacitor

Input Filter. This filter is technically optional but it is strongly suggested. These are the smaller capacitors and inductor on VDD-RTN. These help reduce input ripple and therefore output ripple. There is no requirement here, so the inductor is not required. An inductor can be chosen to not be included in the design, but these capacitors are pretty much needed. These capacitors need to be ceramic. They can be a combination with electrolytic, but then the ripple ratings become an important factor in electrolytic. The [Designing with the TPS23753 Powered-Device and Power Supply Controller application note](https://www.ti.com/lit/an/slva305c/slva305c.pdf?ts=1613499168209&ref_url=https%253A%252F%252Fwww.google.com%252F) includes a section on the calculation for the input inductor and caps. See section 2.7.4

Figure 3-6 Input Filter

VCC power: The IC input power is actually VCC not VDD. So VCC should be connected to the auxiliary winding of the transformer, with some rectification and appropriate capacitance to power the IC. If using the TPS2373x, only a 1uF is required thanks to advanced startup. If using the TPS2375x, (except TPS23755 and TPS23758), something like 22uF is required, preferably electrolytic. Sometimes higher capacitance is needed in active clamp forwards (ACF) for the TPS2375x parts. If a ceramic capacitor is used, please note the effective capacitance needs to be 22uF; so please include the derided value. This is why capacitor type, size, voltage rating and placement are important. Something else to note is that if VCC is powering anything other than the IC, that will drain the capacitor and therefore must be accounted for. As is apparent, essentially every part and power level is different, so please see an EVM for best practice. Active clamp forwards usually have two diodes and an inductor to minimize the ripple. At a minimum 1mH is used but we recommend a 2.2mH inductor.

Figure 3-7 VCC Input: Flyback

Figure 3-8 VCC Input: Active Clamp Forward

Primary side regulation designs will also require an additional cap and resistor. These are there to reduce peak charging since this is used in the feedback loop. What is used in TI designs is the optimal solution.

Figure 3-9 VCC Input: PSR Flyback

Primary side FET(s). There are two if it is an active clamp. The VDS should be 150V. The gate charge should be as low as possible, using the EVM or Reference design MOSFET choice as a baseline. The package of the MOSFET should be at least QFN-8, but certainly not SOT-23. The primary current depends on the primary inductance of the transformer and input power, but usually 2A-3A. For example, the TPS23730EVM-093 is a 51W ACF, and it uses a 3A rated MOSFET. If there is an active clamp, there needs to be an active clamp capacitor -- rated for 250V and usually 0.047uF. This helps set the resonance for the active clamp, so this usually does not need to be changed. The active clamp FET is P-Type and requires similar VDS as the N-FET. The FETs sometimes require pull down circuitry. This is either a diode, or a diode, BJT and resistor. The later is the fastest option. Essentially, the best thing to do is to copy a reference design OR prepare space for all of the options. Additionally, the FET needs a resistor on the gate to slow down the turn on time. This resistor is recommended between 4-50 ohms. If the resistance is too high, it can cause timing issues, but the main concern is that it decreases efficiency.

Figure 3-10 Primary MOSFETs: Active Clamp Forward

Current Sense: the current sense resistor is the <1ohm resistor on the source of the primary FET. Ensure this is a large package (at least 1206).[The resistance value and power level can be calculated](https://www.ti.com/lit/an/slva305c/slva305c.pdf?ts=1613499168209&ref_url=https%253A%252F%252Fwww.google.com%252F) from primary inductance and primary current. Additionally, always leave room for slope compensation. This is a resistor in series with the CS pin and another capacitor. This capacitor provides filtering, but it is not recommended to go above 100pF. This will round off the signal, which makes it difficult to compensate. A good rule is the RC corner frequency created by the resistor and capacitor should be no less than 10x the switching frequency. The resistor is typically 1K-5K ohms for ACFs, and around 1K for flybacks. Please see the reference design for best practice and fine-tuned results. Sometimes [a feed forward resistor](https://www.ti.com/seclit/ml/slup261/slup261.pdf) is used as well.

Figure 3-11 Current Sense and Slope Compensation

Primary FET clamp: If it is a flyback, the [primary side needs a clamp.](https://www.ti.com/seclit/ml/slup261/slup261.pdf)The diode needs to be fast enough to handle the transient (reverse recovery time of 25-50ns). Ensure these components can handle the power going through them. Please note, the [TI Power Stage Designer Tool](https://www.ti.com/tool/POWERSTAGE-DESIGNER) has a specific section for the RCD Snubber Calculation. A TVS diode can be used instead of the resistor and capacitor. The same principles apply of speed, power and voltage ratings.

Figure 3-12 Primary MOSFET RCD Clamp

If it is primary side regulation (PSR), the feedback loop is on the primary side. These components should be close to what we use in our reference designs. The transformer design is a critical part of the functionality of PSR. Since the transformer sets the primary currents, plays an important role in the regulation of the primary loop and sets the auxiliary voltage level, the entire primary side (and secondary side) would need to be redesigned.

Figure 3-13 Primary Side Regulation (PSR) Feedback Components

The Transformer: This is the most critical
component of the DCDC. It sets everything else. The best thing for to do is to use
the exact transformer used in the EVM/reference design. Otherwise, much of the
design will need to be re-calculated. [For flybacks](https://www.ti.com/lit/an/slva305c/slva305c.pdf?ts=1613499168209&ref_url=https%253A%252F%252Fwww.google.com%252F), for [active clamp forwards](https://www.ti.com/lit/an/slua535a/slua535a.pdf?ts=1613509635915&ref_url=https%253A%252F%252Fwww.google.com%252F). For non-PSR transformers, the
transformer can be swapped out, but check: the primary inductance, the turns ratios,
the DCR, leakage inductance, transformer size/footprint, the switching frequency,
and power rating. If these are changed, then other parts of the design will need to
reviewed. PSR regulation is highly dependent on the way the transformer layers are
stacked and wound. The winding has to be spread across the entire bobbin. The
stackup should have the auxiliary between the secondary windings, and the primary
should be split. These are typically not shown in the spec sheet, it is recommended
using transformers in TI EVMs and reference designs. The stackup are as follows:

* ½ pri
* Gate drive
* Secondary
* Bias/aux
* ½ pri

Ensure there are common mode capacitors – they help with EMI and TI recommends them.

Figure 3-14 Common Mode Capacitors

## 3.3 Secondary Side of the DCDC

This will highly depend on what the
topology is.

In all topologies, the output
component will probably need (or should have a footprint for) [a snubber](https://e2e.ti.com/blogs_/b/powerhouse/posts/calculate-an-r-c-snubber-in-seven-steps). The power rating, and thus size, of the
resistor is very important. If the resistor is the incorrect value and size, it will
either become a hot spot thermally, or whatever it is protecting will get hot.
Additionally, the effective resistance may change because of the thermal condition,
and then the snubber is no longer the correct value.

For all topologies, ensure there is
[enough output cap](https://www.ti.com/lit/an/slva305c/slva305c.pdf?ts=1613499168209&ref_url=https%253A%252F%252Fwww.google.com%252F). The combination of ceramic and
electrolytic is preferred. The ESR of an electrolytic or tantalum polymer cap will
help set the dominate pole and zero in opto-feedback designs. This is less prevalent
in PSR flybacks. If an inductor is used for filtering, the electrolytic capacitors
need to be on the output side of the inductor. Only ceramics should be used on the
input side because that side has much higher ripple currents, so the ripple rating
and power rating of the electrolytic capacitors must account for this – but it is
recommended to avoid that by placing them on the output side.

For diode flybacks: ensure the diode
is the proper voltage and current rating for the output voltage and power level.
Best to consult a reference design. But you can use the transformer turns ratio and
output voltage and duty cycle to determine the proper voltage rating. Ensure there
is a snubber across the output diode, and that snubber uses the appropriate
component sizes. Additionally, ensure that the diode has a fast enough reverse
recovery time, otherwise it can lead to lower efficiency.

Figure 3-15 Diode Flyback: Output Diode
(and Snubber)

For sync flybacks: There are [multiple schemes for the grate drive of the FET](https://e2e.ti.com/blogs_/b/powerhouse/posts/maximizing-poe-pd-efficiency-on-a-budget). Some
advice would be to look at a design with similar power and output voltage ratings to
get appropriate parts. Sync flybacks are typically 5V and less. The TPS23753A has
many designs for 13W and less, and the TPS23754/51 have many reference designs for
25W. Even if you are using the TPS2373x in a PSR design, the TPS23754 designs
secondary gate drive is still valuable. For these gate drive components, size (power
ratings, BJT package) and speed (reverse diode recovery time, diode capacitance) are
everything. These gate drives turn off the FET fast which is important in reducing
shoot through. The FET itself needs to be the appropriate Vds rating. The higher the
output voltage, the higher the Vds voltage required (example, 5-V output 30-V-40-V;
12-Vout 60-V-100-V). Additionally, the gate charge needs to be as low as you can
find. Some designs use back to back zeners, while others use a clamp to control the
gate. Find an EVM and or reference design that you know works. If any changes are
made, specially the transformer, then check the gate voltage during normal operation
to see if back-to-back zeners work or if a clamp circuit is needed. If the gate
voltage goes beyond the data sheet limit (usually -20V), then a clamp is suggested.
If unsure, the gate clamp is more robust, but back-to-back zeners are smaller and
less components. Typically the cost is about the same between the two solutions.
Note, wide-Vin solutions might need to use the clamp circuit. If selecting the
MOSFET, use the MOSFET in the EVM and or reference design as a base: the gate charge
should be very similar (example, 21nC and 27nC are similar; 7nC and 18nC are not
similar). Please note, this section does not go over the driven flyback that uses a
pulse transformer to drive the secondary gate. For these designs, please follow the
EVM and or reference design.

Figure 3-16 Synchronous Flyback: Output
MOSFET (and Snubber)

For Active Clamp Forwards: these are
the most complex. This may appear obvious at this point, but the secondary is where
it gets more complicated. The two MOSFETs are critical in the design, as well as the
gate drive circuits. A quick note about the gate drive circuits. In 12-V output
designs, a gate clamp is needed on both MOSFETs. In 5-V designs, the gate clamp is
needed on the parallel. In <5-V designs, it is not needed on either. Since the
two MOSFETs need to be working synchronously, the timing is more important than in a
flyback. Choosing the appropriate MOSFETs and gate drive are important. In ACF
designs, the MOSFETS need to switch very fast. Slow Rdson MOSFETs do not work.
Ensure that the package size is greater than SOT-23, otherwise it will heat up.
Additionally, these MOSFETs might need snubbers as well, ensure there is appropriate
footprints for these components. It is suggested to find a similar reference design
and copy the design. Please note that C31 can be critical for the efficiency and the
turn-off voltage spike of the series MOSFET. In some situations, it helps, but in
others, it does not. The factors of determining this is beyond what can be covered
in this guide, but the suggestion is to strictly follow the presence of the
capacitor if the capacitor is present or not in the reference design used. In [Figure 3-17](GUID-F0341ED9-C97C-4815-8C5E-30EE8740052C.html#GUID-8A732D34-0553-4C41-BC75-67949F9992C6), the dotted boxes are the gate drives, and the solid boxes are the
snubbers/clamps. The green is the parallel FET, and the red is the series FET.

The output inductor is required in the
active clamp forward. [The output inductor can be calculated.](https://www.ti.com/lit/an/slua535a/slua535a.pdf?ts=1613509635915&ref_url=https%253A%252F%252Fwww.google.com%252F)

Figure 3-17 Active Clamp Forward Secondary
Side

## 3.4 Feedback Loop

The feedback loop uses the [current control mode theory](https://www.ti.com/seclit/ml/slup340/slup340.pdf). These contribute to a good
bode plot, which ultimately leads to good startup, shutdown, and load transient
performance.

Note:

If the design is Primary Side
Regulation (PSR), please see the above notes in [Section 3.2](GUID-2ED37E62-0817-4DDA-9F29-EBF7AE338498.html#GUID-2ED37E62-0817-4DDA-9F29-EBF7AE338498).

Check the linear voltage regulator.
High voltage designs >5-V (for example, 12-V) use TL431 parts. Low voltage
designs =<5-v use TL**V**431. [The difference is the lower voltage reference](https://e2e.ti.com/support/power-management/f/power-management-forum/552603/what-difference-between-tlv-lmv-tl431), which
allows a lower voltage turn on of the feedback system.

Figure 3-18 Linear Regulator

Check the voltage divider to ensure it
gives the proper reference voltage for the linear regulator with the output voltage.
If the customer is changing the output voltage (example, from 12-V to 11-V), change
the bottom resistor. The top resistor sets many of the poles and zeros, so changing
the bottom one introduces less change in the system.

Figure 3-19 Feedback Resistor
Divider

Check that there are protection diodes
for these circuits. They provide voltage protection during ESD events. Otherwise
there is no protection for these parts. Ensure these are actual protection diodes
not just regular zeners – they are there to protect against ESD.

Figure 3-20 Protection Diodes

Check the secondary soft-start
circuit. Ensure there is a 10K and 1uF to start. Increasing this cap increases the
soft-start time. Having a soft-start here on the secondary is important for
overshoot on the output. Without it, the risk of overshoot and the potential damage
from that overshoot is increased.

Figure 3-21 Secondary Side Soft
Start

[Check
the pole and zero caps.](https://www.ti.com/seclit/ml/slup340/slup340.pdf) It is suggested to compare against a known
working design. They [can be calculated](https://www.ti.com/lit/an/slva305c/slva305c.pdf?ts=1613499168209&ref_url=https%253A%252F%252Fwww.google.com%252F) (also in the above paper), but Fourier
transforms are required and typically they need to be adjusted on the board also. It
is strongly suggested copying something that works. Calculating feedback components
can be tedious.

Figure 3-22 Feedback Poles and
Zeros

Ensure the opto-biasing resistor is
[set properly.](https://www.ti.com/lit/an/slva305c/slva305c.pdf?ts=1613499168209&ref_url=https%253A%252F%252Fwww.google.com%252F) This resistor sets the current through the
opto, and also sets a gain factor with the resistor on the other side.

Figure 3-23 Optocoupler Biasing
Resistors

The Vb poles and zeros also contribute
to the feedback loop. Same comments as above for calculations

Figure 3-24 Primary Side Poles and
Zeros

80%-160%. Some optocouplers give the
range of 100%-200%, which is also acceptable. All of the feedback is based on this
fact. Otherwise, it must be factored into the gain equation, which usually it is
not. It is strongly advised keeping it this way. Normally, optocuplers come in part
families, with the CTR defined by the last letter (example, -A, -B…-G). Always
ensure it is -A. Confirm with the customer that the CTR chosen is 80%-160%.
Sometimes the -G part is cheaper because the -G is defined at 80%-600% -- for
example, it is untested. If the gain is inconsistent, they will have some boards
work and some boards that do not word. This can be a difficult debug process.

Figure 3-25 Optocoupler

# 4 Adapter Power

Everything needed to know about adapters is included in [Advanced Adapter ORing Solutions using the TPS23753.](https://www.ti.com/lit/an/slva306a/slva306a.pdf?ts=1613520614598&ref_url=https%253A%252F%252Fwww.google.com%252F) Although, a specific IC is mentioned, this document is true for all of TI PoE PD IC’s. Good adapters have EMI filters, input cap filters, they connect to APD and have properly rated diodes. If APD is not used, the APD must be pulled to RTN; otherwise the design does not work.

Figure 4-1 Adapter Input

Another solution to use an adapter with adapter priority is to disrupt the detection resistance. This is Figure 10 in [Advanced Adapter ORing Solutions using the TPS23753](https://www.ti.com/lit/an/slva306a/slva306a.pdf?ts=1619701471473&ref_url=https%253A%252F%252Fwww.google.com%252F). Please note that the resistor divider needs to be the appropriate power size. Note the power rating, component sizes and values.

# 5 Conclusion

To summarize, DCDC design and PoE design are no
simple tasks. This is a guide for the most common design risks for changing the design
from the TI EVM or reference design. The TI designs are tested and validated, so
therefore copying them minimizes risk for the design. [Many designs have been designed by experienced PoE
Designers.](https://e2e.ti.com/blogs_/b/powerhouse/posts/poe-400-and-counting) Most PoE debugs have to do with the DCDC. Checking the schematic
is important to eliminate potential issues from poor part selection.

After the schematic review is completed, the
design will move on to layout. [Please read the following paper for a layout best
practices.](https://www.ti.com/lit/an/slua469/slua469.pdf?ts=1616418098516&ref_url=https%253A%252F%252Fwww.google.com%252F)
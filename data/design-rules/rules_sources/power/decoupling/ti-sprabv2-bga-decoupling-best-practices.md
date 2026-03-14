---
source: "TI SPRABV2 -- BGA Decoupling Best Practices"
url: "https://www.ti.com/lit/an/sprabv2/sprabv2.pdf"
format: "PDF 6pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 18372
---
# BGA Decoupling Best Practices

## Abstract

Much research has been done on decoupling capacitor selection and placement for BGAs. This application report provides the current best practices, and what TI recommends in general for placement and selection of values.

In the past, TI (and many other semiconductor companies) recommended 1 capacitor (cap) per power pin. For DIP packages, this worked great, but other packages like BGAs were developed, this became harder and harder. With any pitch less than 1.0 mm this is nearly impossible, so now TI is trying to take a more realistic approach.

## 1. Overall PDN (Power Distribution Network) Design

The Power Distribution Network (PDN) is the network for getting the power from the power input (AC cord, battery, and so forth) to the circuits it supplies. The components are:

- Power supply and supplies
- Bulk bypassing of the power supply
- Secondary bulk bypassing to recharge the bypass capacitors
- Pin (bypass or decoupling) capacitors
- Planar capacitance (if present)
- Chip, or on-die capacitance
- PCB traces and planes to and from all of the above

All of these elements play a part in the effectiveness of the PDN. They all have different frequencies of response (ranges are approximate):

- 0 to approximately 30 KHz - Power supply response (varies considerably)
- 70 Hz to approximately 40 KHz - Bulk power supply capacitors (works with above)
- 15 KHz to 1 MHz - Secondary bulk capacitors (near the chip)
- 1 MHz to 250 MHz - bypass or decoupling capacitors
- 250 MHz+ - Planar and on-die capacitance

Noise caused by load comes at all different frequencies dependant on the switching frequencies of the buffers and transistors inside the chip, which is dependant on the clock frequencies, software routines, and so forth, so it is important to be able to sustain loads at a wide range of frequencies to avoid having voltage droop at the chip pins.

## 2. General Number and Value of Pin (Bypass) Capacitors Required

TI recommends placing one 0.1 uF cap (in the smallest possible package size, to reduce lead inductance) as close to the chip as possible for every two power pins. Power and ground routes to the BGA should go as directly as possible to the power and ground planes and power and ground traces to and from the caps should also be as short as possible to the power and ground planes. Do not wire the BGA balls to the capacitor before going to the ground and power plane! This increases trace length and reduces the effectiveness of the power distribution network, especially if any planar capacitance is used.

Pay special attention not to put so much bulk capacitance on a supply that it slows the start up voltage ramp enough to change the power sequencing order. Also be sure to verify that the main chip reset is low until after all supplies are at their correct voltage and stable.

The use of inter-plane capacitance is recommended whenever possible (see below section). When using inter-plane capacitance, the requirement for discrete capacitors is drastically reduced. In some situations (after careful analysis), only bulk capacitance is required and the smaller discretes are completely removed. Consider this before deciding on the number of discrete capacitors required for your product.

Note about power sequencing: Power sequencing refers to the order the power supplies come up. This is important because internally the electronics expect a certain order and if it isn't followed, reliability and logic errors may result. Sometimes this causes problems that are difficult to diagnose since they may be sporadic and even temperature dependant. Care should be taken to follow the order recommended on the data sheet for power up and power down.

TI also recommends that at least one bulk (approximately 15 uF or larger) cap be present for every 10 or so power pins. This bulk capacitance recharges the smaller capacitors, but are not low enough inductance to replace them, so both bulk and closer pin decoupling capacitors are necessary. The larger bulk capacitors can be a little farther away, but still should be as close to the part as practical.

For tantalum and electrolytic caps, be sure to select a high enough voltage to take into account the derating over time (which is substantial in most capacitors). In other words you generally want to pick a voltage that is substantially higher (2x) than the voltage being applied to the cap. The derating curve can be found in the data sheet of the capacitor and should be used to validate that a sufficiently high voltage was selected. This can significantly improve MTBF as these kinds of capacitors tend to be a weak link (system wide) over time.

### 2.1 Value For Pin Capacitors

One school of thought suggests that since in the old days capacitor inductance was partially based on capacitor value, capacitors of varying values (usually chosen in logarithmic fashion) should provide the best decoupling (low impedance over a wide frequency range). The larger capacitors would provide the lowest impedance for the PDN at lower frequencies, the middle values at the middle frequencies, and the smaller values at higher frequencies. This made sense when graphing their impedances separately, however, studies have shown that these varying capacitor values do not usually add in a complementary fashion, providing the combined benefits of both, but can resonate considerably at unpredictable frequencies which are hard to control, causing unpredictable rises in impedance at frequencies between the capacitor resonances. Simulations and real life studies have shown this is no longer a good practice.

With the newer ceramic capacitor dielectrics, inductance is related only to the physical size of the capacitor body rather than the value of the capacitor. To verify this, check your capacitor's manufacturer's websites. TDK lists graphs that show this data well for both X7R and other small capacitor dielectrics. When looking at 0.1 uF and 0.01 uF in the same body size (0402 or other small size), both capacitors exhibit the same high frequency slope because the inductance is exactly the same.

Based on the fact that often differing values of capacitors cause more harm than good (because of the resonance possibility listed above), and the fact that with newer capacitor dielectrics, larger value capacitors have the nearly identical high frequency impedance as their smaller value counterparts in the same body size, it is recommended to use just one value, 0.1 uF-0.2 uF, in the smallest package manufacturable by your company (this should be 0402 size or smaller). This will provide the best overall PDN impedance and effectiveness unless the data sheet shows otherwise for that situation. Values larger than 0.1 uF are also useful if they can be ordered in a suitable body size to be placed close to the pin, and don't forget the fact that more capacitors reduces inductance because of their parallel connection.

Simulations on our systems have shown that values lower than 0.1 uF are not very useful in most systems, and instead just take up space that could be more useful otherwise.

## 3. Methods of Placement for Bypass Capacitors

With the smaller pitches that are common on BGAs today, placing caps in between ball vias is usually impossible. That is why via sharing (using just one via for more than one power or ground ball) can be very helpful.

In days past, via sharing was looked down on because theoretically it raises inductance of the system. When 1.0 mm or larger pitches were used, that was true. Now that finer pitches make it impossible to put caps in between multiple rows of vias, two choices are left:

- Keep our "one via per power/ground ball" rule and put the caps the only place they will fit, outside the footprint area.
- Abandon this rule and realize that the distance to the caps, if placed outside the footprint area, introduces a lot more inductance than what it would be if two balls shared a single via and the caps were placed inside the footprint area.

Instead of placing one via per ball inside the power/ground center section of a BGA, skip every other row and share every via with two power or ground balls. This will allow caps to fit directly underneath the part and inductance will be minimized greatly vs. placing the caps outside the footprint area.

Now it is easy to place 0402 caps inside 0.8 mm pitch BGAs, and 0201 caps can even be placed 90 degrees rotated, if desired. This results in more caps underneath the BGA area, much closer to the balls than they would be otherwise, and power distribution network (PDN) integrity is much improved. TI has used this shared via method many times in our own systems, and some of our BGAs are actually designed specifically for this. It is still a good idea to limit the number of power balls shared with one via. As with most engineering problems, the benefits vs. cost (in added inductance) must be weighed.

Sharing more than two power/gnd balls to one via is discouraged because of the extra inductance it causes.

Short capacitor trace length is the most important measure of inductance in most PCB systems. Placement in relation to the BGA is also important, but not as important as trace length.

## 4. Inter-Plane Capacitance

Above approximately 250 MHz, PCB mounted capacitors are not very effective, however, since TI uses some amount of on-die capacitance, they are adequate for our embedded processing chips, but for any high speed system especially systems with more than one processor, inter-plane capacitance is very helpful. Inter-plane capacitance is the capacitance that happens when two PCB layers are brought in very close proximity to each other. Often this requires two extra PCB planes, one power and one ground, that are separated by an extremely thin (<10 mils) layer of dielectric. Since the only "lead" to this giant "capacitor" is the tiny length from the chip's die to the plane and back, inductance is extremely small. This is why planar capacitance can be effective to 10+ GHz, and is invaluable for systems with very high speed PHY chips or other chips that require very high speed decoupling.

The smaller amount of capacitance provided by the planes (vs discretes) is made up for by the reduced inductance of this solution, so the effective capacitance is often increased at the frequencies that are most useful.

Inter-plane capacitance is not required for any current catalog processor, but if your PCB has the possibility of having a ground and power plane in very close proximity to each other, take advantage of it. It will decrease noise substantially and help ensure a good, stable power supply to the processor pins. The benefits are:

- Greatly reduced inductance, which means:
  - Lowered power supply impedance across a very broad range of frequencies
  - Decreased need for discrete capacitors (in some cases the smaller discrete capacitors are completely eliminated)
  - Increased cost of adding two planes can be offset by the reduced cost of discrete capacitors and their assembly as well as the reduced size of the PCB, in some situations resulting in even lower cost (vs using discrete capacitors).

For even more benefit, consider using a special dielectric from 3M, Faradflex, or others that increases the inter-plane capacitance because of the reduced thickness and dielectric constant of the material.

For this to work on boards that have fewer layers, consider pouring copper islands on the signal layers to add capacitance. If the second layer is ground, pouring copper on the top layer (with many vias to the power layer) make more planar capacitance possible, as well as reducing EMI, increasing heat transfer, and reducing power fluctuations. If the second to bottom layer is power consider pouring ground on the bottom layer and realize the same benefits there. Keep isolation between the copper pours and the signals to 15-20 mils minimum to minimize impedance effects on nearby traces.

## 5. Ferrite Bead Recommendations

Ferrite beads are very handy tools to have in your circuit design arsenal. They are, however, not a good idea for all circuit power rails.

Ferrite beads effectively absorb high frequency transients by raising their resistance at higher frequencies. This makes them very good at preventing power supply noise from getting to sensitive circuit sections, however, it also makes them a very bad idea for main digital power.

### 5.1 When to Use Them

Use them on power traces in series with analog circuit sections like composite video or PLLs. These beads effectively shut down power flow in times of high noise transients, allowing the power to be drawn only from the decoupling capacitors that are downstream. This cuts noise to sensitive circuit sections considerably.

### 5.2 How to Use Them

Ferrite beads should be used in between two capacitors to ground. This forms a Pi filter and reduces the amount of noise to the supply considerably. In practice, the capacitor on the chip side should be placed as close to the chip supply ball as possible. The ferrite bead placement and input capacitor placement is not as crucial.

If there is not room for two capacitors to form a Pi filter, the next best thing is to delete the input capacitor. The chip side capacitor should always be there. This is very important. Otherwise the ferrite beads increased high frequency resistance may make things worse instead of better since there will be no local power storage on the chip side and, therefore, no way to get the high peak power pulses to the chip that it so desperately needs.

### 5.3 When Not to Use Them

The above ferrite traits are very handy for those circuit sections that draw power evenly and consistently, but the same traits make them unsuitable for digital power sections. Digital processors need high peak current, because most internal transistors that switch are switching on each clock edge, all the demand occurs at once. Ferrite beads (by definition) will not allow power to flow through them with the high ramp rates required by digital processor logic. This is what makes them perfect for noise filtering on analog (like PLL) supplies.

Since all the power demand in digital system is instant (high frequency), instead of being a slow and steady demand, ferrite beads will block the digital supply during the peaks. Theoretically, the bypass capacitors on the processor side of the bead would supply the peak current, filling in the gaps caused by the ferrites until they were charged after the peak was over, but in reality, the impedance of even the best capacitors is too high above about 200 MHz to supply enough peak power for the processor. In systems without ferrites, the planar capacitance can help to fill in this gap, but if a ferrite is used, it is inserted between the planes and the power pin, so the benefits of planar capacitance are lost. This causes a big instantaneous voltage drop during the period the processor needs it most, causing logic errors and strange behavior if not immediate crashing. This can be avoided by proper design if required for your system (EMI reduction, for example), however, this is beyond the scope of this document.

Is it okay to use a ferrite on supplies that have no planar capacitance? The use of ferrite beads on digital power supplies is still not encouraged. After the bead, the power must flow on traces, which greatly increases the inductance of the connection. This means that the decoupling capacitor connection becomes that much more critical to supply power. If all the decoupling capacitor traces are the very shortest humanly possible, it might still work adequately, but in general, it is not a recommended design practice.

Another disadvantage: segmenting the power planes.

## 6. Summary

- Place a 0.1 uF or higher value capacitor (in the smallest physical package practical for your company, 0402 or 0201) for every two power balls on a BGA embedded processor.
- Be absolutely sure that the traces for decoupling caps are as short as humanly possible. Where you place them in relation to the BGA is a secondary concern to this because planes have very low inductance. Shortening the cap traces to/from the ground/power plane is THE MOST IMPORTANT concern for making a low inductance connection.
- Make sure reset is held low until all power supplies are at their proper level and are stable (with power up and power down sequence correct).
- Use one 15 uF or larger bulk cap for every 10 or so power balls, placed as closely as practical to the chip.
- For tantalum and electrolytic caps, be sure to select a high enough voltage to take into account the derating over time. In other words you generally want to pick a voltage that is substantially higher (2x) than the voltage being applied to the cap. The derating curve can be found in the data sheet of the capacitor and should be used to validate that a sufficiently high voltage was selected. This can significantly improve MTBF.
- Be careful not to place so much bulk capacitance that the power rail will get out of the correct power-up or power-down sequence (this is the order of power supplies starting up and powering down).
- Limited via sharing (using a single via with approximately 2 power or ground balls) is helpful to allow decoupling caps to be placed under the footprint of a BGA, increasing the overall decoupling network effectiveness.
- For the best decoupling, especially for very fast switching interfaces like PCIe, SATA, and USB 2.0, consider pairing power and ground planes close to each other (within 10 mils). This creates interplane capacitance, and GREATLY reduces noise and increases power supply stability at the pins because of the extremely low inductance of this kind of capacitance. The number of discrete capacitors can then be reduced because the effective capacitance is greatly increased and the impedance of the power distribution network is reduced across a very broad frequency range.
- Ferrite beads (especially forming Pi filters) are recommended for analog and PLL power connections.
- Ferrite beads are not recommended for digital power connections.

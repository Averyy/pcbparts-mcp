---
source: "ADI -- A Short Course in PCB Layout for High-Speed ADCs"
url: "https://www.analog.com/en/resources/technical-articles/a-short-course-in-pcb-layout-for-high-speed-adcs.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 15227
---

# A Short Course in PCB Layout for High-Speed ADCs

The intention here is to create the most concise layout guide ever. This goes against our general philosophy of writing to minimize the number of phone calls. This will likely generate a few phone calls because the reasons for the advice are not given. They are the subject of a much longer document for those with longer attention spans, or time. This is meant for those looking for a checklist. Follow these rules for PCB layout, and you should stay out of trouble, at least with [high-speed ADCs](/en/product-category/high-speed-adcs.html).

But first, a few comments:

Using high-speed pipelined ADCs, especially newer generations on lower voltage process technologies, means you are dealing with artifacts that extend further out in frequency, for example to 10 GHz on Analog Devices ADCs using 1.8V processes. This situation persists regardless of the clock rate or the input frequency. Low sample rates reduce the power in these extended artifacts (mixing products reflected into the input path) but they are still there. For RF engineers, the ADC is much like a passive mixer: same mixing products, same procedures.  Reflections from impedance discontinuities matter greatly in the analog input and to a lesser extent in the clock input, and an even lesser extent in the digital outputs – but they still matter. The clock inputs have 2-3 GHz input bandwidth. The clock is often regarded as a logic signal by digital engineers, yet it cannot have any noise margin; it is like the local oscillator in a radio. Higher dV/dt does reduce its sensitivity to noise pick-up to some extent.

1. **No splits in the ground plane across a signal path.**
The ground current should not be viewed as a return current as commonly voiced. The movement of electrons in the ground mirrors the signal propagation in all surrounding metalwork, propagating in concert. The propagation of a wave front in the transmission line induces current flow in the ground. If the ground current has to take a detour due to an interrupted path, there will be potential difference developed across the interruption, and by extension, will be induced in anything grounded to those points. The magnitude of that potential difference is proportional to the frequency content of the signal and the length and impedance of the diverted ground current path. You cannot push high current through a constriction without delay. A wire back to the power supply, or worse, a bead or an inductor is a constriction.

2. **Keep it compact.**
Reduce the distance to points where anything is grounded, including bypass capacitors. Extending traces to a bypass capacitor and then continuing on to ground vias simply creates an antenna. Bypassing to ground on the bottom side of the board involves another plane which may be closely coupled to power planes – more so than the plane under the ADC. In a similar fashion, the ground connection of a balun should be as close as possible to the centerline from the connector, if there is one, and as close as possible to the transmission line, not off on a 90 degree angle like on the schematic.

3. **Don't share vias.**
Well, don’t share vias between signals that are offensive to each other. Supply bypass is offensive to signaling; the analog input is offensive to the reference and the clock, and so on. Assume that all pins on an ADC are offensive to all others.

4. **Ground copper flood every 50 mils.**
If you use copper flood, ground it with vias about every 50 mils around the periphery. Use closer spacing if producing a barrier positioned between potential interferers. Poorly grounded copper will act as an intermediary in crosstalk mechanisms, and as an antenna, and will radiate and receive.

5. **Don't flood too close to signal lines.**
Well, not unless you understand coplanar signal propagation and are able to maintain uninterrupted ground current paths on both sides of the transmission line. Any gaps in these paths must have a cluster of vias on both sides to allow ground current to flow with minimal detour.Coplanar ground current propagation will be sensitive to vias that are too close to the edge, the variation in characteristic impedance producing loss.

6. **Don't flood up to one side only of a differential pair, especially not the analog input!**
The analog input network should be absolutely symmetrical and both lines must behave in an identical fashion for the 2-5 GHz common mode transients that are delivered to the input path. If there is loading from a neighboring element, mirror the details on both sides otherwise it is not truly differential and will radiate, and will translate common mode disturbances with non-linear charge content to differential error, or a loss of SFDR. Even an entirely symmetrical differential pair feeding the analog inputs will radiate the common mode harmonics of the clock, if it is on the surface. For common mode components, the differential pair becomes akin to stripline. These products will be picked up, amplified, frequency translated and become very confusing to identify if you have a mixer in the same compartment. Even LVDS outputs should see symmetrical loading or much like any pair, will reflect common mode digital noise back to the source, and produce common mode current in the destination. Common mode current will induce ground bounce in the substrate of the ADC, which like any silicon device, is only grounded through bond wires. Common mode current in the analog input will tax the abilities of internal virtual grounds, as well as test the common mode rejection of the ADC.

High frequency Common mode rejection, much like any amplifier is limited by positioning and deformation of bond wires during molding, and by features on the PCB, perhaps before limitations of manufacturing to produce matched inputs, switches, capacitors.

7. **Don't put any impedance discontinuities at 100-200 psec (****800 mils to 1.5inch on FR4****) from the ADC.**
That means not in the analog input path, and not even the clock path. By discontinuities, I mean capacitors, or opens (inductors) or even pads that are wider than the transmission lines. If you must place elements such as a shunt capacitor closer than this distance, you should have series resistors at the end with the short. The capacitor is a short at high frequency. If the capacitor is very close to the ADC, the resistors could be 10Ω, or so. If between 100 and 200 psec distant, those resistors should be 49.9Ω, assuming the Zo of the lines is 50Ω/side.

If you have a transmission line transformer, the termination (symmetrical termination to AC ground) should arguably be at the transformer such that the high common mode impedance does not reflect clock transients back to the ADC. The returning clock transients would be skewed slightly due to asymmetry in the construction of the transformer, and as there is non-linear charge involved, will degrade SFDR. Unfortunately, everything is a compromise, so this will also reflect a differential component back to the ADC due to the impedance at the transformer being the termination in parallel with the signal source. As such, the transmission line transformer should not be at the 100-200 psec distance from the ADC, and should generally be as close as possible. If the end termination is far from a transmission line transformer, the transmission pair should not be edge coupled, but two matched lines with some distance between them. Partial termination at the transmission line transformer, with final differential termination at or after the ADC can be considered. In this case, the transmission line transformer should be distant.

A flux coupled transformer with a center-tap is a different situation as it has a low common mode impedance, and the polarity of the return reflection will be reversed. Some ADCs benefit from a low common mode impedance, others do not. Provision for common mode termination, on the center-tap should be made if it is not clear which topology is preferable.

Extending the transmission line and placing end termination after the ADC, truly at the end of a transmission line, as opposed to a point prior to the package pads, prior to bond wires, has been shown produce the best results – again, assuming that the driver/filter/transformer is outside this critical distance. Placing the termination after the ADC requires a layer change at, or very near the input pads. If the input signal is propagated in internal layers, or on the back, the termination can be on the surface facing away from the ADC.

Figure 1. Termination After the ADC

8. **Don't create directional couplers where you don't want them.**
Don't have any signals propagating alongside the encode clock, even other clock lines, putatively in phase or not. An ADC will have ground bounce present and there will be some disturbance reflected into the lines from Miller feedback within the clock receiver. The direction of maximum coupling in a directional coupler is like a reflection from the coupled region, and will be maximized for reflected power from the other ADCs into its neighbors. This is also the case if a clock line is run alongside a data line, power transmitted to the load, the FPGA, will be reflected back into the clock input. There is a popular misconception that the clock is not sensitive at the point where data lines are changing state. Don’t count on it. Any reflections, in the data lines, or in the clock, will preserve it to create a problem. You don't want any signals within 30-50 mils in the same layer for oversampling applications, and nothing except grounded copper in proximity for under-sampling applications, which are more sensitive to clock jitter.

Pay attention to traces in layers above and below the clock traces. Do not run clocks over power planes or in gaps, or near edges between planes.

9. **Keep noisy and sensitive things, including the ADC, away from edges.**
A capacitor grounded at the edge of a plane is not nearly as well grounded as one grounded to the middle of a plane.

10. **Be careful with overlapping power planes.**
Any overlaps are the plates of leadless capacitors. And such capacitors will, at high frequency, have the lowest impedance possible, making any coupled noise very difficult to suppress with capacitors, that do have lead inductance.

11. **Ground bypass capacitors to the same plane as that under the ADC.**
Otherwise, if you must place bypass capacitors on the bottom side, create a small power plane (essentially a leadless capacitor) immediately below the ground plane under the ADC. By immediately below, I mean not more than some 10 mils. This should extend at least some 500 mils around the Vdd or OVdd vias, and should not be shared with other devices. Both Vdd and OVdd can be treated in this manner. If bypass is returned to a plane other than the plane to which the paddle is connected, there must be a significant number of vias to provide a return path to the paddle. Place the bypass on the bottom with the ground rotated towards the ADC.

12. **The bypass capacitors of an output stage should be grounded towards the load.**
This is a general statement that applies to any device, and load. This would appear to conflict with the last statement in item 11, and in some cases there is a conflict. The fact that the ground current path should be no longer than the signal path, should suggest a cluster of vias between OVdd bypass and the load, for minimum ground current path. As ground current “returns” to both the ground pins of a device, and to the point where output bypass is grounded, and as these two grounds could then be at different points, a different path is involved in sourcing or sinking current. The difference in these paths should be minimized, meaning in the case of an ADC, that OVdd should be grounded as close as possible to the ADC’s OGND grounds. If the data bus passes through the board and propagates on the bottom, then OVdd bypass on the back side could be grounded among the data lines on the back side, but incorporating the above mentioned power plane to reduce the high frequency impedance at the OVdd pins. LVDS signaling being differential, does not involve as much ground current as CMOS signaling. As an aside, the points where amplifier output bypass is grounded can carry class AB currents, which is a liability if ground vias are shared.

13. **Ground vias should be interleaved among the data lines at any layer change.**
Any layer change for single ended signaling (e.g. CMOS) should be surrounded by a cluster of vias for ground current.

14. **Don't use thermal relief needlessly in ground vias.**
If a device is to be soldered to ground, use a thermal collector rather than thermal relief that can compromise grounding. This means a plate of copper pour, grounded with perhaps one large via and a distribution of smaller vias such that the heat of reflow will develop an adequate temperature on the pads despite the thermal load of the large via. This can be applied to bypass as well as active devices, and will improve soldering, yet will produce a low inductance connection to ground.

15.**Think about the soldering process.**Be careful to ensure even absorption of heat by all the projections around the ADC, such as with BGAs where the thermal load on all the balls should be similar. Dissimilar temperatures developed during reflow will degrade the soldering process, even producing opens.

16. **A homework assignment.**
Take apart any discarded cell phone that comes into your possession, whether you find it crushed in a parking lot behind an Irish pub, submerged in a puddle outside a home improvement store, or in a thrift store manned, if you will, by elderly ladies. Cell phones are often good examples of using the board as a shield between mutually offensive subsystems, effective use of micro-vias, of performing layer changes with frequency translation, and the art of spoiling antenna efficiency… which is generally what you want around an ADC.

17. **Filter design should take into consideration the distance to the ADC and the distance to the driver.**
A filter needs to be designed with layout in mind, and if layout dictates, filter design may have to change to suit the distance to the ADC.  This is really the subject of a separate article. The filter should be re-simulated once you have extracted parasitic data from the PCB, mentally or with software.

18. **Don’t trust anyone.**
Pay attention to your PCB vendor, CAD services, and signal integrity experts, but be prepared to call them on the carpet. Ask signal integrity experts about the noise margin of the clock inputs if you want to have some fun. Hint: they may assume LVPECL noise margins if you drive the clock with LVPECL.

19. **Vias are cheap.**
Each 10 mil via in an 0.625 inch board has about 1 nH, or 6.28Ω at 1 GHz. Use lots of them.
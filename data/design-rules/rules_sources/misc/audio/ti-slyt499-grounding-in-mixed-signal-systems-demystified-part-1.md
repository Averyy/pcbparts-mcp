---
source: "TI SLYT499 -- Grounding in Mixed-Signal Systems Demystified, Part 1"
url: "https://www.ti.com/lit/an/slyt499/slyt499.pdf"
format: "PDF 6pp"
method: "pdfplumber"
extracted: 2026-03-02
chars: 23960
---

Texas Instruments Incorporated Data Converters
Grounding in mixed-signal systems
demystified, Part 1
By Sanjay Pithadia, Analog Applications Engineer,
and Shridhar More, Senior Analog Applications Engineer
Introduction
Figure 1. AGND and DGND pins in a data converter
Every signal-processing system
requires mixed-signal devices,
Digital Data
such as analog-to-digital converters
(ADCs) and/or digital-to-analog con-
verters (DACs). The need for proc-
essing analog signals with a wide V= Li (di/dt)
dynamic range imposes the require- Digital Li Ri Digital Li Ri
ment to use high-performance ADCs Supply Section DGND
and DACs. Maintaining performance
in a noisy digital environment is Li– Internal inductance
dependent upon using good circuit-
Cstray Cstray Cstray – Stray capacitance
Ri– Internal resistance
design techniques like proper signal
routing, decoupling, and grounding. Analog
Li Ri
Analog
Li Ri
Undoubtedly, grounding is one of Supply Section AGND
the most discussed subjects in system
design. Though the basic concepts are Inside Data Converter
relatively simple, the implementation
is difficult. For linear systems, the Analog Input Signal
ground is the reference against which
the signal is based; and, unfortunately,
it also becomes the return path for the power-supply Interpretation of AGND and DGND pins
current in unipolar supply systems. An improper applica- in mixed-signal devices
tion of grounding strategies can degrade the performance
Digital- and analog-design engineers tend to view mixed-
in high-accuracy linear systems. There is no “cookbook”
signal devices from different perspectives, but every engi-
that guarantees good results, but there are a few things
neer who uses a mixed-signal device is aware of analog
that, if not done properly, can cause issues.
ground (AGND) and digital ground (DGND). Many are
This article is the first of a two-part series that looks
confused about how to deal with these grounds; and, yes,
closely at the grounding techniques used in mixed-signal
much of the confusion comes from how the ADC ground
systems. Part 1 explains typical terminologies and ground
pins are labeled. Note that the pin names, AGND and
planes and introduces partitioning methods. Part 2 explores
DGND, refer to what’s going on inside the component and
techniques for splitting the ground planes, including pros
do not necessarily imply what one should do with the
and cons. It also explains grounding in systems with multi-
grounds externally. Data-converter datasheets usually sug-
ple converters and multiple boards. Part 2 will appear in a
gest tying the analog and digital grounds together at the
future issue of Analog Applications Journal.
device. However, the designer may or may not want the
A term often used in system design is star ground. This
data converter to become the system’s star ground point.
term builds on the theory that all voltages in a circuit are
What should be done?
referred to as a single ground point, or star ground point.
As illustrated in Figure 1, the grounds inside a mixed-
The key feature is that all voltages are measured with
signal IC are typically kept separate to avoid coupling digi-
respect to a particular point in the ground network, not
tal signals into the analog circuits. An IC designer cannot
just to an undefined ground wherever one can clip a probe.
do anything about the internal inductance and resistance
Practically, it is difficult to implement. For example, in a
(negligible compared to the inductance) associated with
star ground system, drawing out all signal paths to mini-
connecting the pads on the chip to the package pins. The
mize signal inter action and the effects of high-impedance
rapidly changing digital currents produce a voltage (di/dt)
signal or ground paths causes implementation problems to
in digital circuits, which inevitably couples into the analog
arise. When power supplies are added to the circuit, either
circuits through the stray capacitance.
they add unwanted ground paths or their supply currents
The IC works well in spite of such coupling. However, in
flowing in the existing ground paths are large enough or
order to prevent further coupling, the AGND and DGND
noisy enough to corrupt the signal transmission.
5
Analog Applications Journal 1Q 2013 www.ti.com/aaj High-Performance Analog Products

Data Converters Texas Instruments Incorporated
pins should be joined together externally to the same low- plane, the analog input signal is going to have digital noise
impedance ground plane with minimum lead lengths. Any summed with it, because it is probably single-ended and
extra external impedance in the DGND connection can referenced to the analog ground plane. Connecting the
cause more digital noise and, in turn, can couple more pins to a quiet analog ground plane can inject a small
digital noise into the analog circuit through the stray amount of digital noise into it and degrade the noise mar-
capacitance. gin of the output logic. This is because the output logic is
now referenced to the analog ground plane and all the
Analog or digital ground plane, or both?
other logic is referenced to the digital ground plane.
Why is a ground plane needed? If a bus wire is used as a However, these currents should be quite small and can be
ground instead of a plane, calculations must be done to minimized by ensuring that the converter output does not
determine the bus wire’s voltage drop because of its imped- drive a large fan-out.
ance at the equivalent frequency of most logic transitions. It is possible that the devices used in a design have
This voltage drop creates an error in the final accuracy of either low digital currents or high digital currents. The
the system. To implement a ground plane, one side of a grounding scheme is different for both cases. Traditionally,
double-sided PCB is made of continuous copper and is data converters may be thought of as low-current devices
used as a ground. The large amount of metal has the low- (such as flash ADC). But today’s data converters with on-
est possible resistance and lowest possible inductance chip analog functions are becoming more and more digi-
because of the large, flattened conductor pattern. tally intensive. Along with the additional digital circuitry
The ground plane acts as a low-impedance return path come larger digital currents and noise. For example, a
for decoupling high-frequency currents caused by fast sigma-delta ADC contains a complex digital filter that adds
digital logic. It also minimizes emissions from electromag- considerably to the digital current in the device.
netic interference/radio-frequency interference (EMI/RFI).
Grounding data converters with
Because of the ground plane’s shielding action, the circuit’s
susceptibility to external EMI/RFI is reduced. Ground low digital currents
planes also permit high-speed digital or analog signals to be As mentioned, a data converter (or any mixed-signal
transmitted via transmission-line (microstrip or stripline) device) is analog. In any system, the analog signal plane is
techniques, where controlled impedances are required. where all the analog circuitry and mixed-signal devices are
As mentioned earlier, the AGND and DGND pins must placed. Similarly, the digital signal plane has all the digital
be joined together at the device. If the analog and digital data-processing circuits. The analog and digital ground
grounds have to be separated, should both be tied to the planes should have the same size and shape as the respec-
analog ground plane, the digital ground plane, or both? tive signal planes.
Remember that a data converter is analog! Thus, the Figure 2 summarizes the approach for grounding a
AGND and DGND pins should be connected to the analog mixed-signal device with low digital currents. The analog
ground plane. If they are connected to the digital ground ground plane is not corrupted because the small digital
Figure 2. Grounding data converters with low internal digital currents
PCB
Analog ground plane’s shape and size Digital ground plane’s
Low digital current
same as for analog signal plane shape and size same as
generates low noise.
for digital signal plane
Keep the local
decoupling capacitor RC Filter
(de-cap) loop as or Ferrite
short as possible. Bead
V A V A V Dig VD
Local
Analog Data De-Cap Digital
Signal Converter for Data
Conditioning Digital Processing
Back-to-back
Schottky diodes
between AGND and AGND DGND
DGND keep maximum
ground-potential
difference at < 0.3 V.
Analog Digital
V
A
Supply Supply VD
To System Star Ground
6
High-Performance Analog Products www.ti.com/aaj 1Q 2013 Analog Applications Journal

Texas Instruments Incorporated Data Converters
transient currents flow in the small loop between V , the The Schottky diodes prevent large DC voltages or low-
Dig
local decoupling capacitor, and DGND (the green line). frequency voltage spikes from developing across the two
Figure 2 also shows a filter between the analog and digital planes. These voltages can potentially damage the mixed-
power supplies. There are two types of ferrite beads: high-Q signal IC if they exceed 0.3 V, because they appear directly
resonant beads and low-Q nonresonant beads. Low-Q between the AGND and DGND pins.
beads are commonly used for power-supply filtering in As an alternative to the back-to-back Schottky diodes, a
series with the power connection. ferrite bead can provide a DC connection between the two
planes but isolate them at frequencies above a few mega-
Grounding data converters with
hertz where the ferrite bead becomes resistive. This pro-
high digital currents
tects the IC from DC voltages between AGND and DGND,
The circuit in Figure 2 depends on the decoupling capaci- but the DC connection provided by the ferrite bead can
tor between V and DGND to keep the digital transient introduce unwanted DC ground loops and may not be suit-
currents isolated in a small loop. However, if the digital able for high-resolution systems. Whenever AGND and
currents are significant enough and have components at DGND pins are separated in the special case of ICs with
DC or low frequencies, the decoupling capacitor may have high digital currents, provisions should be made to con-
to be so large that it is impractical. Any digital current nect them together if necessary.
that flows outside the loop between V and DGND must Jumpers and/or strap options allow both methods to
flow through the analog ground plane. This may degrade be tried to verify which gives the best overall system
performance, especially in high-resolution systems. An performance.
alternative grounding method for a mixed-signal device
Isolation or partitioning: Which is important
with high levels of digital currents is shown in Figure 3.
for ground planes?
The AGND pin of the data converter is connected to the
analog ground plane, and the DGND pin is connected to A common concern is how to isolate the grounds so that
the digital ground plane. The digital currents are isolated the analog circuit does not interfere with the digital circuit.
from the analog ground plane, but the noise between the It is a well-known fact that digital circuitry is noisy.
two ground planes is applied directly between the Saturating logic draws large, fast current spikes from its
device’s AGND and DGND pins. The analog and digital supply during switching. Conversely, analog circuitry is
circuits must be well isolated. The noise between AGND quite vulnerable to noise. It is not that the analog circuit
and DGND pins must not be large enough to reduce might interfere with the digital logic. Rather, it is possible
internal noise margins or cause corruption of the internal that the high-speed digital logic might interfere with the
analog circuits. low-level analog circuits. So the concern should be how to
prevent digital-logic ground currents from contaminating
Connecting analog and digital ground planes
the low-level analog circuitry on a mixed-signal PCB. The
Figures 2 and 3 show optional back-to-back Schottky first thought might be to split the ground planes to isolate
diodes connecting the analog and digital ground planes. DGND from AGND. Although the split-plane approach can
Figure 3. Grounding data converters with high internal digital currents
PCB
Analog ground plane’s shape Digital ground plane’s shape
same as for analog signal plane same as for digital signal plane
V A V A V D VD
Data
Signal Data
Converter
Conditioning Processing
Back-to-back
Schottky diodes
between AGND and AGND DGND
DGND keep maximum
ground-potential
difference at < 0.3 V.
V
A
Supply Supply VD
To System Star Ground
7
Analog Applications Journal 1Q 2013 www.ti.com/aaj High-Performance Analog Products

Data Converters Texas Instruments Incorporated
be made to work, it has many problems--especially in
Figure 4. Distribution of return current
large, complex systems.
There are two basic principles of electromagnetic com-
patibility (EMC): w
ε
1. Currents should be returned to their sources locally and r
as compactly as possible. If not, a loop antenna should t
be created. h
2. A system should have only one reference plane, as two
references create a dipole antenna.
During EMC tests, most problems are observed when i (A/cm)
traces are routed across a slot or a split in a ground or
power plane. Since this routing causes both radiation and
crosstalk issues, it is not recommended.
D
It is important to understand how and where the ground
currents in a split plane actually flow. Most designers think
only about where the signal current flows and ignore the
For reference planes, it is important that the clearance
path taken by the return current. The high-frequency sig-
sections of vias do not interfere with the return current’s
nals have a characteristic of following the path of least
path. In the case of an obstacle, the return current finds a
impedance (inductance). The path’s inductance is deter-
way around it, as shown in Figure 5. However, this rerout-
mined by the loop area that the path encloses. The larger
ing will most likely cause the current’s electromagnetic
the area that the current has to travel to return to the
fields to interfere with the fields of other signal traces,
source, the larger the inductance will be. The smallest
introducing crosstalk. Moreover, this obstacle adversely
inductance path is directly next to the trace. So, regard-
affects the impedance of the traces passing over it, leading
less of the plane--power or ground--the return current
to discontinuities and increased EMI.
flows on the plane adjacent to the trace. The current
Part 2 of this two-part article series will discuss the pros
spreads out slightly in the plane but otherwise stays under
and cons involved in splitting the ground planes and will
the trace. The actual distribution is similar to a Gaussian
also explain grounding in systems with multiple converters
curve in nature. Figure 4 illustrates that the return-current
and multiple boards.
flow is directly below the signal trace. This creates the
path of least impedance. References
The current-distribution curve for the return path is
1. H. W. Ott, “Partitioning and layout of a mixed-signal
defined by
PCB,” Printed Circuit Design, pp. 8–11, June 2001.
I 1 2. “Analog-to-digital converter grounding practices affect
i (A/cm) = O × ,
πh  D 2 system performance,” Application Report. Available:
1+   www.ti.com/sbaa052-aaj
 h 
Related Web sites
where I is the total signal current (A), h is the height of
O
Data Converters:
the trace (cm), and D is the distance from the trace (cm).
www.ti.com/dc-aaj
From this equation it can be concluded that digital ground
currents resist flowing through the analog portion of the For examples of grounding for precision data converters,
ground plane and so will not corrupt the analog signal. visit: www.ti.com/e2egrounding-aaj
Subscribe to the AAJ:
www.ti.com/subscribe-aaj
Figure 5. Return current with and without slot
Circuit Trace Load Ground-Plane
Disruption
Driving
Gate
High-Speed
Return Path
Return Current
Around Obstacle
8
High-Performance Analog Products www.ti.com/aaj 1Q 2013 Analog Applications Journal

TI Worldwide Technical Support
Internet
TI Semiconductor Product Information Center
Home Page
support.ti.com
TI E2E™ Community Home Page
e2e.ti.com
Product Information Centers
Americas Phone +1(512) 434-1560 Asia
Phone
Brazil Phone 0800-891-2616
International +91-80-41381665
Mexico Phone 0800-670-7544 Domestic Toll-Free Number
Note: Toll-free numbers do not support
Fax +1(972) 927-6377 mobile and IP phones.
Internet/Email support.ti.com/sc/pic/americas.htm Australia 1-800-999-084
China 800-820-8682
Europe, Middle East, and Africa
Hong Kong 800-96-5941
Phone
India 1-800-425-7888
European Free Call 00800-ASK-TEXAS
Indonesia 001-803-8861-1006
(00800 275 83927)
Korea 080-551-2804
International +49 (0) 8161 80 2121
Malaysia 1-800-80-3973
Russian Support +7 (4) 95 98 10 701
New Zealand 0800-446-934
Philippines 1-800-765-7404
Note: The European Free Call (Toll Free) number is not active in
Singapore 800-886-1028
all countries. If you have technical difficulty calling the free call
number, please use the international number above. Taiwan 0800-006800
Thailand 001-800-886-0010
Fax +(49) (0) 8161 80 2045 Fax +8621-23073686
Internet www.ti.com/asktexas Email tiasia@ti.com or ti-china@ti.com
Direct Email asktexas@ti.com Internet support.ti.com/sc/pic/asia.htm
Japan Important Notice: The products and services of Texas Instruments
Incorporated and its subsidiaries described herein are sold subject to TI’s
Phone Domestic 0120-92-3326 standard terms and conditions of sale. Customers are advised to obtain the
most current and complete information about TI products and services
Fax International +81-3-3344-5317 before placing orders. TI assumes no liability for applications assistance,
customer’s applications or product designs, software performance, or
Domestic 0120-81-0036 infringement of patents. The publication of information regarding any other
company’s products or services does not constitute TI’s approval, warranty
Internet/Email International support.ti.com/sc/pic/japan.htm or endorsement thereof.
Domestic www.tij.co.jp/pic
A090712
E2E is a trademark of Texas Instruments. All other trademarks are the property of
their respective owners.
© 2013 Texas Instruments Incorporated SLYT499

IMPORTANT NOTICE
Texas Instruments Incorporated and its subsidiaries (TI) reserve the right to make corrections, enhancements, improvements and other
changes to its semiconductor products and services per JESD46, latest issue, and to discontinue any product or service per JESD48, latest
issue. Buyers should obtain the latest relevant information before placing orders and should verify that such information is current and
complete. All semiconductor products (also referred to herein as “components”) are sold subject to TI’s terms and conditions of sale
supplied at the time of order acknowledgment.
TI warrants performance of its components to the specifications applicable at the time of sale, in accordance with the warranty in TI’s terms
and conditions of sale of semiconductor products. Testing and other quality control techniques are used to the extent TI deems necessary
to support this warranty. Except where mandated by applicable law, testing of all parameters of each component is not necessarily
performed.
TI assumes no liability for applications assistance or the design of Buyers’ products. Buyers are responsible for their products and
applications using TI components. To minimize the risks associated with Buyers’ products and applications, Buyers should provide
adequate design and operating safeguards.
TI does not warrant or represent that any license, either express or implied, is granted under any patent right, copyright, mask work right, or
other intellectual property right relating to any combination, machine, or process in which TI components or services are used. Information
published by TI regarding third-party products or services does not constitute a license to use such products or services or a warranty or
endorsement thereof. Use of such information may require a license from a third party under the patents or other intellectual property of the
third party, or a license from TI under the patents or other intellectual property of TI.
Reproduction of significant portions of TI information in TI data books or data sheets is permissible only if reproduction is without alteration
and is accompanied by all associated warranties, conditions, limitations, and notices. TI is not responsible or liable for such altered
documentation. Information of third parties may be subject to additional restrictions.
Resale of TI components or services with statements different from or beyond the parameters stated by TI for that component or service
voids all express and any implied warranties for the associated TI component or service and is an unfair and deceptive business practice.
TI is not responsible or liable for any such statements.
Buyer acknowledges and agrees that it is solely responsible for compliance with all legal, regulatory and safety-related requirements
concerning its products, and any use of TI components in its applications, notwithstanding any applications-related information or support
that may be provided by TI. Buyer represents and agrees that it has all the necessary expertise to create and implement safeguards which
anticipate dangerous consequences of failures, monitor failures and their consequences, lessen the likelihood of failures that might cause
harm and take appropriate remedial actions. Buyer will fully indemnify TI and its representatives against any damages arising out of the use
of any TI components in safety-critical applications.
In some cases, TI components may be promoted specifically to facilitate safety-related applications. With such components, TI’s goal is to
help enable customers to design and create their own end-product solutions that meet applicable functional safety standards and
requirements. Nonetheless, such components are subject to these terms.
No TI components are authorized for use in FDA Class III (or similar life-critical medical equipment) unless authorized officers of the parties
have executed a special agreement specifically governing such use.
Only those TI components which TI has specifically designated as military grade or “enhanced plastic” are designed and intended for use in
military/aerospace applications or environments. Buyer acknowledges and agrees that any military or aerospace use of TI components
which have not been so designated is solely at the Buyer's risk, and that Buyer is solely responsible for compliance with all legal and
regulatory requirements in connection with such use.
TI has specifically designated certain components as meeting ISO/TS16949 requirements, mainly for automotive use. In any case of use of
non-designated products, TI will not be responsible for any failure to meet ISO/TS16949.
Products Applications
Audio www.ti.com/audio Automotive and Transportation www.ti.com/automotive
Amplifiers amplifier.ti.com Communications and Telecom www.ti.com/communications
Data Converters dataconverter.ti.com Computers and Peripherals www.ti.com/computers
DLP® Products www.dlp.com Consumer Electronics www.ti.com/consumer-apps
DSP dsp.ti.com Energy and Lighting www.ti.com/energy
Clocks and Timers www.ti.com/clocks Industrial www.ti.com/industrial
Interface interface.ti.com Medical www.ti.com/medical
Logic logic.ti.com Security www.ti.com/security
Power Mgmt power.ti.com Space, Avionics and Defense www.ti.com/space-avionics-defense
Microcontrollers microcontroller.ti.com Video and Imaging www.ti.com/video
RFID www.ti-rfid.com
OMAP Applications Processors www.ti.com/omap TI E2E Community e2e.ti.com
Wireless Connectivity www.ti.com/wirelessconnectivity
Mailing Address: Texas Instruments, Post Office Box 655303, Dallas, Texas 75265
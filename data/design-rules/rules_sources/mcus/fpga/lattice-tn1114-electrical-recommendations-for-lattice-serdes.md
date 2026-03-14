---
source: "Lattice TN1114 -- Electrical Recommendations for Lattice SERDES"
url: "https://www.latticesemi.com/~/media/3E4AA60747DC46FC9EC26A9FD2F35894.ashx"
format: "PDF 22pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 43335
---

Electrical Recommendations for
Lattice SERDES
March 2014 Technical Note TN1114
Introduction
LatticeECP3, LatticeECP2/M, and LatticeSC/M SERDES integrates high-speed, differential Current Mode Logic
(CML) input and output buffers. This offers significant advantages in switching speed while providing improved
noise immunity and limited power dissipation. Additional advantages in current-mode design include reduced volt-
age swing operation and significant suppression of power supply noise since the supply current is constant.
The CML differential receivers and drivers incorporate various programmable features and interfaces to other CML
and non-CML logic signals. Off-chip signal interface design and characteristics are the focus of this document.
Detailed interfacing requirements to external high-speed devices with LVDS and LVPECL characteristics are dis-
cussed, as well as the transmission line interconnections between devices which are required because of high data
rates. Practical considerations related to printed circuit boards are also discussed. For more detailed PCB recom-
mendations, refer to TN1033, High-Speed PCB Design Considerations. While nominal resistor and capacitor val-
ues are shown throughout this document, optimal values will vary in each application. HSPICE models with the
interface examples are provided to tune user-specific applications.
CML Buffer Overview
CML buffers are used as the common interface to the SERDES PCS. Internal input and output terminations are
provided to simplify board level interfacing and AC coupling capacitors are available within the CML receiver. A sim-
plified schematic of the serial input and output buffers is shown in Figure 1. The termination resistors and AC cou-
pling capacitors are internal to the buffer.
Figure 1. CML Input and Output Buffer Structure for LatticeECP3, LatticeECP2/M and LatticeSC/M
VDDOB (VCCOB) VDDIB (VCCIB)
1.2V to 1.5V 1.2V to 1.5V
VCC12 (VCCRX) (VCCA)
50/75/2K
50/75/5K (50/60/75
/high)
Zo
5 pF
Zo
A An
VOD typ = 500mV VID min = 80mV
VOCM typ = VDDOB - 0.25V VICM_DC = 0.6 -1.2V
Vbias VICM_AC = 0 -1.5V
(VOD typ = 500mV
VOCM typ = VCCOB - 0.25V) (VID min = 100mV
VICM_DC = 0.5 -1.2V
VICM_AC = 0 -1.5V)
Note: Signal or parameter names and values in parenthesis are for LatticeECP2M and LatticeECP3.
© 2014 Lattice Semiconductor Corp. All Lattice trademarks, registered trademarks, patents, and disclaimers are as listed at www.latticesemi.com/legal. All other brand
or product names are trademarks or registered trademarks of their respective holders. The specifications and information herein are subject to change without notice.
www.latticesemi.com 1 tn1114_02.9

Electrical Recommendations
for Lattice SERDES
SERDES Power Supplies
Generally, Lattice SERDES-based FPGA devices have many similarities. However, there are some differences that
need to be highlighted and understood. This is very important when understanding the power supply definitions
between the LatticeSC, LatticeECP2M, and LatticeECP3 devices. These differences are shown in Table 1.
Table 1. SERDES Power Supplies
LatticeSC SERDES LatticeECP2M SERDES LatticeECP3 Nominal Power Supply
Power Supply Power Supply Power Supply Value Description Tolerance
CML Input Termination
VDDIB[0-3] VCCIB[0-3] VCCIB[0:3] 1.2V to 1.5V +/-5%
Voltage Supply
CML Output Termination
VDDOB[0-3] VCCOB[0-3] VCCOB[0:3] 1.2V to 1.5V +/-5%
Voltage Supply
CML I/O Control Logic
VDDAX25 VCCAUX33 VCCAUX2 2.5V/3.3V/3.3V +/-5%
Power Supply
SERDES/PLL
VCC121 VCCP/VCCRX/VCCTX VCCA 1.2V +/-5%
Analog Supply
1. Internal 1.2V power supply voltage for configuration logic and FPGA PLL, SERDES PLL power supply voltage and SERDES analog supply
voltage.
2. This supply shared with VCCAUX of the FPGA supply for LatticeECP3.
The SERDES design provides separate final stage Rx and Tx power nodes for each CML input and output buffer.
These are identified as VDDIB and VDDOB for LatticeSC, and VCCIB and VCCOB for LatticeECP2M and
LatticeECP3. These allow the receiver input termination (50-, 75-, 2K-ohm) and transmitter output termination (50-,
75-, 5K-ohm) to be biased at different levels, independent of the core VCC voltage. The Rx termination (resistor con-
nected to VCCIB) value can vary based on design requirements.
Lattice devices use several supplies for the analog circuitry blocks of the SERDES. All analog supply pins must be
connected to a voltage supply regardless of whether the channel is used in the application. Unused channels can
be powered off internally to conserve power. The analog supplies should be isolated on the PCB to deliver quiet,
noise-free power supplies. For LatticeSCM devices, this supply is identified as VCC12 and is used to supply analog
power nodes within the SERDES blocks. VCC12 is an analog plane within the device that is shared between the
SERDES and the PLLs. For LatticeECP2M these supplies are VCCP, VCCRX, and VCCTX and should be treated
the same as noted for VCC12. LatticeECP3 also includes VCCA which also is similar to VCC12 and should be
treated the same.
There is a very stringent requirement often overlooked by designers to isolate noise generated by digital compo-
nents. It is necessary to provide a low-noise supply for the sensitive analog portions of the SERDES devices. Noise
due to variations in the power supply voltage can be coupled into the analog portion of the chip and may produce
unwanted fluctuations in the sensitive stages of the device.
There are several power supplies associated with the SERDES/PCS of the device. These supplies need to be
addressed based on the design. As previously mentioned, the analog supplies need to be isolated from any other
noise on the 1.2V PCB supply. All dedicated SERDES supply pins, excluding the VDDIB (VCCIB) and VDDOB
(VCCOB) pins, must be connected regardless of the design. VDDIB (VCCIB) and VDDOB (VCCOB) are used to
supply the input and output terminations used to match the transmission lines. These supplies only need to be con-
nected for the channels used in a design. In situations where only the Rx section is used, it is recommended that
the associated VDDOB (VCCOB) be connected to an appropriate power supply regardless that the Tx section is
not being used. This strategy shields noise from the channel. Likewise, if only the Tx is used, the respective VDDIB
(VCCIB) shall be connected. Similarly, the HDIN and HDOUT pins can be left unconnected in designs not using
particular channels.
In instances where PCB power distribution cannot be sufficiently bypassed, the designer might be tempted to use
several different active devices, such as voltage regulators, to serve as the decoupling stages for these power sup-
plies. Supplying DC power to each stage through a separate inductor or “choke” while also bypassing to ground,
2

effectively accomplishes the same results without the use of active components. In these passive filter network
schemes, the choke offers a high impedance path to any errant signals or noise between stages, while offering a
very low resistance path to the DC power. This technique is appropriate to supply RX and TX termination supplies
(VCCIB/VDDIB/VCCOB/VDDOB).
The example in Figure 2 shows a method for isolating the SERDES analog supplies from the digital noise of the
PCB supply. This technique may be used for the VCCIB/VCCOB (LatticeECP2M and LatticeECP3) and
VDDIB/VDDOB (LatticeSC) power stages on the board.
Figure 2. Passive Filter Network “Quiet Supply” Example
1.2V Board
VCC12
Supply
Power Stage
T
VDDIB/VDDOB
VCCIB/VCCOB
22pF --> 1000pF
1 per pin 10nF 100nF 10nF 100nF 1µF 10-22µF
Located under device
Decoupling caps distributed
evenly as close to device as
possible
Note: The use of Passive-Filter Networks is not recommended for low-impedance power supplies such as VCC Core.
(cid:129) High “Q”, minimum inductance decoupling caps
– SMT or chip capacitors made of ceramic are best. Use several size caps in parallel (e.g., 1ufd, 0.1ufd,
0.01ufd, etc). The reason for this is that each cap with its associated inductance will have its own series res-
onant frequency. Therefore, it is best to have a wide range of capacitor values to provide an overall lower
power supply impedance over the effective frequency range.
(cid:129) Use high “Q” – low “R” Ferrite Bead
– The down-side of ferrite is that it will change inductance as the current or flux changes. In large currents, it
can saturate. Understanding the frequency, AC and DC current requirements is important in choosing the
correct inductor. A good choice is a bead from Murata, BLM41PG471SN1L.
Other options for power distribution systems should also be explored to gain an understanding of the sources of
power supply noise and voltage ripple. Using the before-mentioned passive filter techniques is a good start to post
filter the ripple generated by the power supplies. The filter must sufficiently attenuate the low-frequency harmonics
of the primary switching supply, so an understanding of the specifics of what frequency needs to be cut-off by the
post-supply filter is important. A specific recommendation is to build an LC passive-network that will cut off a
decade below the primary frequency. Typically, high-frequency noise generated by supplies can be easily attenu-
ated. This can commonly be achieved with the use of an additional ceramic decoupling capacitor placed after the
post-filter as shown in Figure 2.
Both linear and switching voltage regulators have advantages and disadvantages when used in Lattice FPGA sys-
tems. Depending on the requirements of the system either may be a suitable choice. Switching regulators are a
better choice when the input voltage is less than or much greater than the desired output, when multiple outputs
are desired, and when power dissipation must be kept low. There’s no argument that switching regulators are more
efficient than low drop-out regulators (LDO). A switching regulator can exhibit 90% efficiency versus 36% for an
LDO. However, a switching regulator may not always meet all the critical needs of the design. Switching Voltage
Regulators have these advantages:
(cid:129) High efficiency (reduces source power requirements and need for heat sinking)
(cid:129) Capable of handling higher power densities
3

(cid:129) Single or multiple output voltages, greater or less than the input voltage
They have these disadvantages:
(cid:129) Greater output noise/ripple, especially at the switching frequency
(cid:129) Slower transient recovery time
Switching regulators are well suited for powering the FPGA core and I/O power supplies where high power require-
ments play a factor in the board power design. The high efficiency reduces heat and power concerns that linear
regulators exhibit. However, the finite ripple generated by switching regulators is not desirable for use with the sen-
sitive analog power supplies. Using post-supply filter networks can attenuate the unwanted ripple. Typically, the
added noise on the output is at the switching frequency. If this frequency is below the bandwidth of the SERDES or
PLLs it will directly affect the associated component jitter. Otherwise, it will be filtered. For SERDES connections,
the receiver being transmitted to will also filter low frequency jitter, as generated by the switching regulator.
In general, linear regulators are a better choice when the input voltage is a few volts higher than the output but not
closer than the regulator’s dropout voltage, and when the load current is less than about 3A. Linear Voltage Regu-
lators have these advantages:
(cid:129) Simple and small board application
(cid:129) Low output ripple voltage
(cid:129) Excellent line and load regulation
(cid:129) Fast response time to load or line changes
(cid:129) Low electromagnetic interference (EMI)
They have these disadvantages:
(cid:129) Low efficiency, especially with higher input voltages
(cid:129) Large space requirement if heatsink is needed
This type of regulation is desired for the quiet analog supplies used in the PLLs and SERDES of the SERDES
devices. These regulators have much better noise properties and faster transient response. They offer a good
amount of noise rejection and generate no ripple. They work well to supply the lower power draw from the analog
circuitry of the FPGA. Using a linear regulator to build quiet supplies provides the analog portions of the FPGA the
needed power supply requirements. Lattice strongly recommends using linear regulators to supply the ana-
log SERDES power supplies.
4

Figure 3. Combined Switching and Linear Regulator Power Scheme for LatticeSC
Intermediate Power Bus
2.5/3.3V 1.2V
Switching Switching
Regulator Regulator
1.2V
Linear
Regulator
Figure 4. Combined Switching and Linear Regulator Power Scheme for LatticeECP2M
5
*BIDDV *BODDV 21CCV OICCV 52XADDV XUACCV
eroC
CCV
*VDDIB and VDDOB should be passively filtered from either 1.2V supply.
*BIDDV *BODDV
*BICCV *BOCCV PCCV XTCCV XRCCV OICCV XUACCV 33XUACCV
*VCCIB and VCCOB should be passively filtered from either 1.2V supply.
*BICCV *BOCCV

Figure 5. Combined Switching and Linear Regulator Power Scheme for LatticeECP3
Combining the use of a switching regulator with a linear regulator is a way to reduce board current drain. An exam-
ple of this is shown in Figure 3. In this design, a switching regulator provides the correct voltage levels while the
use of the linear regulator filters the switching noise. Note that the correct power supply decoupling and filtering is
needed. Switching regulators are most efficient when they’re driving the loads for which they were designed. When
the output voltage is not heavily loaded, however, the current needed to keep the switching regulator switching
becomes more problematic. A linear regulator can be more efficient under these conditions. Using this combination
of regulators is helpful to meet the requirements of high-performance FPGA designs that require distribution of
multiple power supplies. This strategy will meet the needs of both the power and performance demands of the
FPGA system.
General FPGA Recommendations
In general, low noise analog power supply networks are a stringent requirement for the proper operation of embed-
ded SERDES elements. The noise due to variations in the power supply voltage can be coupled into other non-
SERDES analog portions of the device. This is important to understand for the phase-locked loops based inside
the FPGA fabric. These PLLs should also follow the suggested recommendations for providing clean power as
mentioned for SERDES supplies.
Table 2. PLL Supplies Per Device
FPGA PLL Quiet Supply
Device Supply Voltage (Nominal)
LatticeSC VCC12 1.2V
LatticeECP2M VCCPLL_[L:R] 1.2V
LatticeECP3 VCCPLL_[L:R] 3.3V
PCB Design Considerations
Many existing documents provide guidance to prevent the pitfalls of PCB designs with SERDES-based and high-
speed I/O designs. There are still a few underlying issues that often go misunderstood or overlooked. The interac-
tion of an FPGA’s Simultaneously Switching Outputs (SSO) can cause many system-level issues that lead to deg-
radation of the overall SERDES performance.
Lattice FPGA I/Os have enabled the building of many complex systems. These abundant and flexible FPGA I/Os
include many speed and signal interface features such as drive strength and termination options. SSO is noise due
6
*BICCV *BOCCV ACCV OICCV XUACCV
*VCCIB and VCCOB should be passively filtered from either 1.2V supply.
*BICCV *BOCCV

to multiple I/O pins switching at the same time. These changing currents induce voltages inadvertently affecting
other sensitive stages of the device. LatticeSC devices include many innovative methods to overcome specific
device and package sensitivities to SSO and in-package cross talk. This can mostly be corrected by minimizing the
total inductance of return paths, similar to what has been done in Lattice package design. PCB designs need to
apply careful techniques to reduce the likelihood of PCB-related crosstalk and SSO that degrades system perfor-
mance.
The leading causes of PCB-related SERDES crosstalk are related to FPGA outputs located in close proximity to
the sensitive SERDES power supplies. These supplies require cautious board layout to insure noise immunity to
the switching noise generated by FPGA outputs. Guidelines have already been provided to build quiet filtered sup-
plies for these sensitive supplies, however robust PCB layout is required to insure that noise does not infiltrate into
these analog supplies. Although coupling has been reduced in the device packages of the devices where little
crosstalk is generated, the vias within the BGA field of the PCB can cause significant noise injection from any I/O
pin adjacent to SERDES data, reference clock, and power pins as well as other critical I/O pins such as clock sig-
nals.
Many PCB designs include adjacent structures that can create cross-coupling of the FPGA I/O to the analog sup-
ply pins. The crosstalk created by via-to-via coupling can cause noise to attack the analog supplies. The noise
aggressor is the culprit SSO pin potentially impacting the supplies and circumventing any provided PCB supply fil-
tering. This coupled noise on the PCB from the aggressor can cause the SERDES performance to degrade dra-
matically. Enabling amplitude boost mode of the SERDES will typically improve noise immunity for both the Rx and
Tx portions of the SERDES, especially noted at rates above 2.7 Gbps.
The system designer can mitigate this problem by implementing differential signaling standards to and from the
FPGA rather than using single-ended buffers. Where single-ended signals must be used, the PCB designer must
pay attention to via and signal placement when in close proximity to the analog power supplies and avoid routing
the single-ended buses near the high-speed SERDES channels. It is a better practice to use the I/O pins in closer
proximity of SERDES data, reference clock, and analog power pins for static control signals or signals with low-
drive strength, slow-slew rate, and limited capacitive loading (terminated signaling also improves this situation).
The suggested pins to avoid for this purpose, if possible, are shown in Table 3 for each LatticeSC package. For
LatticeECP2/M devices, see TN1159, LatticeECP2/M Pin Assignment Recommendations. LatticeECP3 devices
have similar recommendations listed in TN1189, LatticeECP3 Hardware Checklist.
Table 3. LatticeSC PCB Aggressor I/O Pins
Device Package Package Type Aggressive I/O Pins1
SC15 256-fpBGA Wire-bond E7
SC15/SC25 900-fpBGA Wire-bond F222
SC25/SC40 1020-fpBGA Flip Chip D2, E2, F2, D31, E31, F31
SC40/SC80/SC115 1152-fpBGA Flip Chip D2, D33, F14, F21, G14, G21,H13, H14, H21, H22
F27, G1, G2, G3, J17, J18, G40, G41, G42, K18, M9, N9,
SC80/SC115 1704-fpBGA Flip Chip
N10, N33, N34, M34
1. I/O pins are potential PCB coupled noise sources to analog supplies and recommendations should be followed.
2. F22 is a dual function pin. When using SPI Flash, F22 is used to source the SPI Flash chip select and should not be connected to “soft
ground”.
The best-case scenario is to drive these signals with a “soft ground.” Connecting an active output buffer and driving
a low signal builds an effective “soft ground.” This pin should be connected to the ground plane of the PCB. This
connection serves as a return path and helps create additional noise immunity. Pins are listed that will possibly
influence with the analog supplies on the board as well as pins that are adjacent to high-speed SERDES data pins
that could get coupled on the PCB. Additional recommendations include:
7

(cid:129) Do not route the SERDES supply connections as traces. Rather, use planes or very wide bus structures on other
non-adjacent layers to high-speed signal routing and keep them shielded by adjacent ground layers.
(cid:129) Blind-vias are better than through-hole vias for making connection to the I/Os. This limits the amount of coupling
between vias. If through-hole vias are required, place high frequency decoupling capacitors directly beneath the
device adjacent to the VCC12 power via.
(cid:129) Maintaining the greatest distance between single-ended I/O and the analog supplies is always required. It is
always best to keep the analog supplies and the single-ended traces separated vertically in the PCB stack-up
when working in close proximity on the board.
Figure 6. PCB Via Stack Up Detail for LatticeSC
LatticeSC BGA Device
BGA Pad/
Soft
sysIO sysIO VCC12 Via Detail
Ground
Through ViaS
Decoupling Capacitor
Blind Via
In Figure 6, coupling is caused by the mutual inductance occurring in the area between the I/O signal path and the
VCC12 via. Blinding the signal via and reducing the stub minimizes the capacitive coupling effect. Following recom-
mendations designed to minimize this effect reduces the coupling. I/O pins having close proximity to the VCC12
pins vary in different packages and packaging variations also influences noise immunity. The issues related to
these locations are due to the way the pins escape or route away from the device. Determining the best escape
route from the device’s BGA field is critical to minimizing the effects of coupled noise on the board.
Best Practices for SERDES Power Supply PCB Routing
(cid:129) When possible, do not use specified I/Os directly adjacent to an analog power pin.
(cid:129) Routing should also be kept away from analog power vias when escaping from the device.
(cid:129) It is best practice to shield any routing traces from the analog power pin connections. This can be done with
power and ground planes (ground planes preferred) above and below as well as ground shield routing on the
same layer.
(cid:129) Carefully place same layer shielding as to not create edge-coupling issues. Typically 3W spacing is required to
prevent edge coupling.
(cid:129) Consider keeping quiet SERDES supply connections on the first possible power layer closest to the device side
where is can be shielded by a ground layer.
(cid:129) High-speed I/O signals should escape on the signal layer non-adjacent to the analog supply.
(cid:129) High-speed I/O signals should be routed after all SERDES and analog power is routed. If the quiet supply vias
are blinded, this restriction can be relaxed as long as the quiet power plane is kept close to the device side of the
board as possible.
8

Special Considerations to Reduce Tx Jitter and Increase Jitter Tolerance for the 
LatticeSC
For wire-bond packages, it is also a good practice at any speed to limit the number of single-ended outputs simul-
taneously switching outputs in I/O banks adjacent to the SERDES channels. For the 256-ball fpBGA, this is I/O
Bank #1 and for the 900-ball fpBGA packages, these are I/O Banks #1, #2 and #7. This becomes a priority as the
SERDES rate increases.
At SERDES speeds above 3.2Gbps in wire-bond packages, the single-ended outputs in Bank #1 should be limited
to configuration signals (including up to 8-bit MPI interface connections for the 900-ball fpBGA). For Banks #2 and
#7, the number of single-ended outputs should be limited to 8 or less in the 900-ball fpBGA.
For the 256-ball fpBGA package use Bank #1 for:
(cid:129) Differential I/O or static configuration and control signals
(cid:129) Single ended inputs
(cid:129) Only if necessary, single ended outputs can be used but should be limited to a 4mA drive with slewlim mode
enabled
For the 900-ball fpBGA package, use Banks #1, #2 and #7 for:
(cid:129) MPI pins (8-bit only)
(cid:129) Differential I/O or static configuration and control signals
(cid:129) Single ended inputs
(cid:129) Only if necessary, single ended outputs can be used but should be limited to a 4mA drive with slewlim enabled
It is less critical to limit the number of single-ended outputs in flip-chip packages. However limiting the number of
outputs, reducing drive-strength, enabling slew limited mode and reducing the capacitive loads in Banks #1, #2,
and #7 will also have a small effect on improving SERDES performance. At SERDES speeds greater than 3.2Gbps
this effect becomes larger.
SERDES External Interfaces
The high speed of the serial SERDES I/O makes understanding the interface parameters especially important to
the user. Proper interpretation of the parameters is needed for successful integration within a system. Signal inter-
connection performance, reliability and integrity are closely tied to these characteristics and their variation limits.
This section will summarize and discuss critical serial buffer interface parameters. Correctly specifying the buffer
I/O is a complex process. Methods used include extensive SPICE simulation and laboratory measurements.
All interconnection circuits described in this section should use matched length pairs of 50-ohm transmission lines.
Each should provide characteristic impedance termination of the line to provide maximum signal bandwidth. 50
ohms, an industry standard, provides maximum compatibility and suits present printed circuit board technology
interconnections well for circuit pack and backplane applications. It is also consistent with 100-ohm balanced trans-
mission line interfaces which are becoming popular for high bandwidth shielded pair cable connections. However,
for ease of integration into 75-ohm impedance characteristic systems such as video, Lattice SERDES devices are
optimized to terminate directly in both 50-ohm and 75-ohm applications.
DC Coupling
The SERDES high-speed serial buffers are optimized to interface externally to other similar buffers. For some inter-
faces, a direct interconnection of Lattice SERDES buffers requires no external devices or components at the PCB
level. The advantages of DC coupling include simplified board design and no DC wander issues. It is also useful in
all coded-data streams including SONET and NRZ data applications. Systems with a need for wide bandwidth or
where DC unbalanced code is used, can take advantage of DC coupling.
9

AC Coupling
In some high-speed applications, AC coupling is preferred for various reasons. Lattice CML receivers integrate AC
coupling capacitors. AC coupling is used to change the common-mode voltage level when interconnecting different
physical layers. A capacitor removes the DC component of the signal (common-mode voltage), while passing along
the AC component, or voltage swing. The resistors to RxTerm in Figure 1 represent the internal biasing structure
used to set the common-mode voltage on the line side of the AC coupling capacitor. Biasing structures are either
part of the internal biasing of the receiver or an external resistor pull-up and/or pull-down network. Interconnection
to other vendors’ non-CML buffers is possible, but may require the addition of some passive components. AC cou-
pling generates baseline wander in high-speed serial data transmission because it is non-DC balanced. ANSI fiber
channel 8B/10B encoded data is an example of DC-balanced signaling.
The addition of external capacitors (Cext) for AC coupling requires some careful consideration. The designer
should select a capacitor knowing the requirements of the system. It is important to minimize the pattern-depen-
dent jitter associated with the low-frequency cutoff of the AC coupling network. When NRZ data containing long
strings of identical 1’s or 0’s is applied to this high-pass filter, a voltage droop occurs, resulting in low-frequency,
pattern-dependent jitter (PDJ).
When using off-chip capacitors (Cext), it is possible to use both internal AC coupling or DC coupling modes. For AC
coupling modes it is suggested that when Cext is connected in series to the internal AC coupling Cap. When off-
chip AC coupling is required, recommended capacitor values are shown in Table 4.
Table 4. Off-chip AC Coupling Capacitor
Description Min. Max. Units
8b/10b (XAUI) 20 — nF
SONET 22 — nF
PCI Express 75 200 nF
LVDS Device Interface
LVDS, like CML, is intended for low-voltage differential signal point-to-point transmission. Many commercial LVDS
devices provide internal 100-ohm input terminations. They are typically intended for use with 100-ohm characteris-
tic impedance transmission line connections. Standard LVDS is specified with about 3 mA signal-current that trans-
lates to a nominal signal voltage of approximately 600 mVp-p (differential). Low power LVDS provides about 2 mA
signal current. LVDS input and output parameters are shown in Table 5, as specified in the LVDS Standard.
Table 5. LVDS Specifications
Symbol Parameter Conditions Min Max Units
Driver Specifications
VOH Output voltage high Rload (diff) = 100 ohms — 1475 mV
VOL Output voltage low Rload (diff) = 100 ohms 925 — mV
VOD Output differential voltage Rload (diff) = 100 ohms 250 400 mV
Ro Output impedance, single ended Vcm = 1.0V to 1.4V 40 140 Ohms
Receiver Specifications
Vi Input voltage range 0 2400 mV
Vidth Input differential threshold -100 +100 mV
Vhyst Input differential hysteresis 25 — mV
Rin Receiver differential input impedance 90 110 Ohms
Within common LVDS receivers, an internal or external input differential termination of 100 ohms is typically
needed between the P and N input ports. This termination resistor is usually floating with respect to ground. In the
SERDES CML receiver, the differential input termination resistor is center-tapped and AC coupled to ground or left
10

floating. VDDIB can also be connected to a power supply equal to the common-mode level required for proper
operation of the output buffer. In a common LVDS-to-CML application, a simple direct interface can be used in
many applications. The Lattice CML output drivers and input receivers are internally terminated to 50 ohms in this
application. Figure 7 illustrates a recommended interface between Lattice CML buffers and commercial LVDS input
and output buffers. This interface requires no external components utilizing the internal CML features. The simula-
tion results of the interface are plotted in Figure 8.
Figure 7. DC-Coupled CML to LVDS Interface Diagram
VDDOB (VCCOB)
1.2V to 1.5V
50
Zo = 50
100
LatticeSC VOD default = 500mV
VOCM = VDDOB - 0.25V
LVDS Receiver
CML Driver (Lattice ECP2M and LatticeECP3 VOD default = 500mV
VOCM typ = VCCOB - 0.25V)
VID min = 100mV
VICM_DC = 0 - 2.4V
VDDIB (VCCIB)
1.2V to 1.5V
LatticeSC VID min = 80mV
VICM = 0.6 - 1.2V
LVDS Driver
(Lattice ECP2M and LatticeECP3 VID min = 100mV
CML Receiver VICM = 0.5 - 1.2V)
VOD = 250 - 400mV
VOCM = 1.2V
11

Figure 8. Lattice CML Driver to LVDS Receiver Simulation
Higher common mode noise tolerance may be achieved with alternate AC-coupled LVDS driver to SERDES
receiver connection, as shown in Figure 9. This increases the receiver tolerance to common-mode input noise volt-
age and provide a higher tolerance range to common-mode and system and ground noise.
12

Figure 9. AC-Coupled LVDS Driver to CML Receiver Interface
VDDOB (VCCOB)
1.2V to 1.5V VID min = 100mV
VICM_DC = 0 - 2.4V
2.5V
50 100 100
0.01 - 0.1uF
100 100
LVDS Receiver
CML Driver
VDDIB (VCCIB) = 1.2V to 1.5V
VCC12 (VCCRX)
0.01 - 0.1uF
LVDS Driver
CML Receiver
Internally AC Coupled
LVPECL Device Interface
LVPECL is a differential I/O standard that requires a pair of signal lines for each channel. It is used in longer-haul
electrical transmission. The differential transmission scheme is less susceptible to common-mode noise than sin-
gle-ended transmission methods. LVPECL standards require external termination resistors to reduce signal reflec-
tion. The standard voltage swing for the differential pair is approximately 850mV, and the typical LVPECL VCC is
3.3V.
13

Table 6. Typical LVPECL Specifications
Symbol Parameter Conditions Min Max Units
Outputs terminated with
Voh Output voltage high 2215 2420 mV
50 ohms to Vcco - 2.0V
Vol Output voltage low 1470 1680 mV
Vod Output differential voltage 535 950 mV
Ro Output impedance, single ended Vcm =1.0V to 1.4V 3 10 Ohms
1.1 3.1
Vi Input voltage range, common-mode < 500mVp-p > 500mVp-p V
1.3 3.1
Vin-diff Input voltage range, differential mode 200 >2000 mVp-p
Iih Input HIGH current -150 µA
Iil Input LOW current -600 - µA
Table 6 shows typical LVPECL specifications. The Vcm, common-mode voltage is around 2V, which is higher than
the allowable input common-mode voltage of the CML receiver. AC coupling is required to level shift the Vcm to the
level CML needs.
An AC-coupled solution is shown in Figure 10. This scenario allows higher impedance termination at LVPECL Rx
end, without causing signal distortion. Figure 11 shows the results of the simulation.
Figure 10. AC-Coupled CML to LVPECL Interface Diagram
External to Device
VDDOB (VCCIB) = 1.5V
3.3V
50Ω 50Ω 82Ω 82Ω
0.1 3.3V LVPECL
Rx Input
Zo=50Ω
CML Driver W-element lossy 120Ω 120Ω
T-line model
External to Device
VDDIB (VCCIB) = 1.2
C1
0.01 to 0.1µFd CML Receiver
3.3V LVPECL (typical) C2 Int. 50Ω
Tx Output
Int. AC Coupling
Zo=50Ω
W-element lossy
T-line model
R1=112Ω R2=112Ω
14

Figure 11. AC-Coupled CML to LVPECL Simulation
PCI Express Device Interface
At the electrical level, PCI Express utilizes two uni-directional low voltage differential signaling (LVDS) pairs at
2.5Gbps for each lane. Transmit and receive are separate differential pairs, for a total of four data wires per lane.
The Lattice CML buffers interface well with LVDS, thus allowing interconnection to PCI Express buses. An input
receiver with programmable equalization and output transmitters with programmable pre-emphasis permits optimi-
zation of the link. The PCI Express specification requires that the differential line must be common mode termi-
nated at the receiving end. Each link requires a termination resistor at the far (receiver) end. The nominal resistor
values used are 100 ohms. This is accomplished by using the embedded termination features of the CML inputs as
shown in Figure 12. The specification requires AC coupling capacitors (CTX) on the transmit side of the link. This
eliminates potential common-mode bias mismatches between transmit and receive devices. The capacitors must
be added external to the Lattice CML outputs.
15

Table 7. Differential PCI Express Specifications
Symbol Parameter Min. Nom. Max. Units Comments Location
Z DC Differential TX 80 100 120 Ohm TX DC differential mode low imped- Internal on
TX-DIFF-DC
Impedance ance. ZTX-DIFF-DC is the small sig- chip
nal resistance of the transmitter
measured at a DC operating point that
is equivalent to that established by
connecting a 100 Ohm resistor from
D+ and D- while the TX is driving a
static logic one or logic zero.
Z DC Differential Input 80 100 120 Ohm RX DC differential mode impedance Internal on
RX-DIFF-DC
Impedance during all LTSSM states. When trans- chip
mitting from a Fundamental Reset to
Detect, (the initial state of the LTSSM),
there is a 5ms transition time before
receiver termination values must be
met on all un-configured lanes of a
port.
C AC Coupling Capacitor 75 200 nF All transmitters shall be AC coupled. External to
TX
The AC coupling is required either Lattice
within the media or within the transmit- device
ting component itself.
Figure 12. PCI Express Application Termination
VDDOB (VCCOB) = 1.2V to 1.5V
VDDIB (VCCIB) = 1.2V to 1.5V
75 to 200nF
VTX-DIFF-DC per PCIe Spec VRX-DIFF-DC
CML Driver Zo=50Ω CML Receiver
External to Lattice Device
16

Interfacing to Reference Clock CML Buffers
Some applications may require a reference clock interface. Interfacing to LVPECL requires external components to
provide proper load for the LVPECL drivers and either internal or external AC coupling capacitors as shown in the
following figures. These figures show recommended configurations for Differential LVPECL driving CML and Sin-
gle-Ended LPECL driving CML (AC coupled with either Receiver ended or Source ended termination). The best
practice is to use two center-tapped 50-ohm resistors to ground.
Figure 13. CML Reference Clock Input Buffer For LatticeSC Devices
REFCLKP
5pF
2K 2K
2K 2K
REFCLKN
5pF
Figure 14. CML Reference Clock Input Buffer For LatticeECP2M and LatticeECP3 Devices
REFCLKP
50Ω 1K 2K
5pF VCM
5pF 2K
50Ω 1K 2K
REFCLKN
17

Figure 15. Reference Clock Buffer with External AC Coupling – LVPECL Clock Driver
VCC
130-ohm
Termination
RSERIES Required for LatticeECP3,
+ LatticeECP2M and LatticeSC.
Must be external termination resistors
VCC
82-ohm on LatticeSC. On-chip termination
Termination 50-ohm is available for LatticeECP3 and
LVPECL LatticeECP2M. This option is
130-ohm
user configurable.
Termination 50-ohm
-
82-ohm
RSERIES
Termination
Notes:
1. 150-ohm (or similar) pull-down can typically be substituted in place of a 130/82-ohm Thevenin divider.
2. RSERIES varies based on LVPECL driver characteristics.
3. Reference clock options – LatticeECP2M/LatticeECP3: 50-ohm termination, DC-coupling; LatticeSCM: Hi-Z termination, DC-coupling.
4. Refer to the specific device data sheet for DC specifications.
5. External AC coupling is required for LVPECL clock sources.
Figure 16. Single-Ended PECL Driving CML Reference Clock Buffer (AC, Receiver End Termination)
3.3 V
VDD = 3.3 V
120
LatticeSC = VCC12
LatticeECP2M = VCCP
Transmission Line
0.1μ LatticeECP3 = VCCA
Reference
Clock CML
LVPECL
Buffer
82
82 Reference clock buffer
0.1μ set to DC Coupling
18

Figure 17. Single-Ended PECL Driving CML Reference Clock Buffer (AC, Source End Termination)
VDD = 3.3 V
LatticeSC = VCC12
120 LatticeECP2M = VCCP
Transmission Line
0.1μ LatticeECP3 = VCCA
Reference
Clock CML
LVPECL
Buffer
112 82
82 Reference clock buffer
0.1μ set to DC Coupling
There are special considerations when using LatticeSC devices available in the 900-BGA wire-bonded package.
The electrical performance of the input path to the reference clock input may show undesired qualities when
observed by probing the device pins. These signal imperfections are imposed due to parasitics of the clock path
that are intrinsic to the 900-ball fpBGA package. These reflections do not manifest inside the input buffer of the ref-
erence clock itself. HSPICE models are available for user evaluation and verification.
Simulation Usage Details
Analog simulation of interface circuits is a very useful part of the design process. Simple interfaces can be simu-
lated using HSPICE models for the CML buffers available from Lattice. Two 50-ohm ideal transmission lines of
matched length can be provided between the SERDES and the interconnected device, representing PCB traces.
As shown throughout this document, a random 622 Mbps digital signal pattern was used in the simulation to drive
the SERDES buffer and the resulting signal voltage waveforms can be predicted by simulation. Device package
parasitic-elements can be included. Other parameters and conditions assumed were nominal IC processing
parameters, nominal supply voltage and room temperature
Conclusion
This document discusses the general termination and interface interconnections of Lattice SERDES devices. The
use of Current Mode Logic (CML) input and output buffer structures and their capabilities to interface with other
CML and non-CML devices was also discussed. Lattice SERDES devices offer a variety of input and output termi-
nations that offer a reduction in external components.
References
(cid:129) LatticeSC/M Family Data Sheet
(cid:129) LatticeSC/M Family flexiPCS Data Sheet
(cid:129) LatticeECP2/M Family Data Sheet
(cid:129) LatticeECP3 Family Data Sheet
(cid:129) TN1033, High-Speed PCB Design Considerations
(cid:129) TN1124, LatticeECP2M SERDES/PCS Usage Guide
(cid:129) TN1176, LatticeECP3 SERDES/PCS Usage Guide
(cid:129) TN1159, LatticeECP2/M Pin Assignment Recommendations
19

(cid:129) TN1189, LatticeECP3 Hardware Checklist
(cid:129) Lattice Diamond® Software Documentation
Technical Support Assistance
e-mail: techsupport@latticesemi.com
Internet: www.latticesemi.com
20

Revision History
Date Version Change Summary
July 2006 01.0 Initial release.
December 2006 01.1 Added discussion about Switching Voltage Regulators and Linear Volt-
age Regulators text section.
PCI Express Application Termination figure updated.
April 2007 01.2 Added additional recommendations for PCB layout for LatticeSC.
June 2007 01.3 Added footnote 1 to LatticeSC and LatticeECP2M SERDES Power Sup-
plies table.
July 2007 01.4 Updated Interfacing to Reference Clock CML Buffers section.
January 2008 01.5 Updated Interfacing to Reference Clock CML Buffers section.
January 2008 01.6 Updated PCI Express Device Interface section.
June 2008 01.7 Added footnote to LatticeSC PCB Aggressor I/O Pins table.
Added a reference to TN1159 for LatticeECP2/M pin assignment infor-
mation.
Updated Differential LVPECL Driving CML Reference Clock Buffer (DC)
figure and added a new figure after that (Figure 13 to illustrate CML buf-
fers.
August 2008 01.8 LatticeECP2/M parameter names and values are corrected per data
sheet.
November 2008 01.9 Added a note to Passive Filter Network “Quiet Supply” Example figure.
Added new figures showing CML Ref Clock Input Buffers for 
LatticeSCM and LatticeECP2M.
December 2008 02.0 LatticeECP2M VCOM typical range updated.
February 2009 02.1 Added support for LatticeECP3 FPGA family.
April 2009 02.2 Updated CML Reference Clock Input Buffer For LatticeECP2M and
LatticeECP3 Devices diagram.
June 2009 02.3 Updated Reference Clock Buffer with Internal DC Coupling diagram.
Updated Reference Clock Buffer with Internal AC Coupling diagram.
November 2009 02.4 Added REFCLK DC coupling recommendation.
February 2010 02.5 Updates to power supply diagrams and LVPECL termination scheme.
June 2011 02.6 Updated Reference Clock Buffer with Internal DC Coupling figure.
Removed DC coupling figure (CML to LVPECL).
August 2012 02.7 Updated document with new corporate logo.
Updated Reference Clock Buffer with External AC Coupling diagram.
September 2012 02.8 Added power supply (VCCIB/OB) recommendation for RX only or Tx
only usage.
March 2014 02.9 Updated information in DC Coupling and AC Coupling sections.
Updated Table 4, Off-Chip AC Coupling Capacitor.
Updated information in LVPECL Device Interface AC Coupling section.
Updated typical LVPECL description.
Updated the Interfacing to Reference Clock CML Buffers section intro-
duction.
Added footnote 5 to Figure 15, Reference Clock Buffer with External AC
Coupling – LVPECL Clock Driver.
Removed the DC-Coupled LVPECL to CML Interface Diagram and the
Single-Ended PECL Driving CML Reference Clock Buffer (DC) figures.
Updated Technical Support Assistance information.
21

Appendix A. LatticeSC Devices
An external calibration resistor is connected between the RESP pin and RESPN or between the RESP pins and
board ground for packages not offering the dedicated RESPN pin. Each upper corner requires this resistor, so a
maximum of two resistors are required per device. The value of the external resistor, 4.02K ohms, is an industry
standard “EIA E96 series” value for 1% resistors. This circuitry also requires core VCC to be present and generates
the VBIAS shown in Figure 18.
Figure 18. RESP Connection
RESP
Pin
RESP
4 Kohm 4 Kohm
RESPN
22
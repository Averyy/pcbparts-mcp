---
source: "Lattice FPGA-TN-02006 -- iCE40 Hardware Checklist"
url: "https://0x04.net/~mwk/sbdocs/ice40/FPGA-TN-02006-2-3-iCE40-Hardware-Checklist.pdf"
format: "PDF 24pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 32775
---

iCE40 Hardware Checklist
Technical Note
FPGA-TN-02006-2.3
April 2024

Disclaimers
Lattice makes no warranty, representation, or guarantee regarding the accuracy of information contained in this document or the suitability of its products
for any particular purpose. All information herein is provided AS IS, with all faults, and all associated risk is the responsibility entirely of the Buyer. The
information provided herein is for informational purposes only and may contain technical inaccuracies or omissions, and may be otherwise rendered
inaccurate for many reasons, and Lattice assumes no obligation to update or otherwise correct or revise this information. Products sold by Lattice have
been subject to limited testing and it is the Buyer's responsibility to independently determine the suitability of any products and to test and verify the
same. LATTICE PRODUCTS AND SERVICES ARE NOT DESIGNED, MANUFACTURED, OR TESTED FOR USE IN LIFE OR SAFETY CRITICAL SYSTEMS, HAZARDOUS
ENVIRONMENTS, OR ANY OTHER ENVIRONMENTS REQUIRING FAIL-SAFE PERFORMANCE, INCLUDING ANY APPLICATION IN WHICH THE FAILURE OF THE
PRODUCT OR SERVICE COULD LEAD TO DEATH, PERSONAL INJURY, SEVERE PROPERTY DAMAGE OR ENVIRONMENTAL HARM (COLLECTIVELY, "HIGH-RISK
USES"). FURTHER, BUYER MUST TAKE PRUDENT STEPS TO PROTECT AGAINST PRODUCT AND SERVICE FAILURES, INCLUDING PROVIDING APPROPRIATE
REDUNDANCIES, FAIL-SAFE FEATURES, AND/OR SHUT-DOWN MECHANISMS. LATTICE EXPRESSLY DISCLAIMS ANY EXPRESS OR IMPLIED WARRANTY OF
FITNESS OF THE PRODUCTS OR SERVICES FOR HIGH-RISK USES. The information provided in this document is proprietary to Lattice Semiconductor, and
Lattice reserves the right to make any changes to the information in this document or to any products at any time without notice.
Inclusive Language
This document was created consistent with Lattice Semiconductor’s inclusive language policy. In some cases, the language in underlying tools and other
items may not yet have been updated. Please refer to Lattice’s inclusive language FAQ 6878 for a cross reference of terms. Note in some cases such as
register names and state names it has been necessary to continue to utilize older terminology for compatibility.

Contents
Contents................................................................................................................................................................................ 3
Acronyms in This Document ................................................................................................................................................. 6
1. Introduction .................................................................................................................................................................. 7
2. Power Supply ................................................................................................................................................................ 8
2.1. Recommended Power Filtering Groups and Components .................................................................................. 8
2.2. Analog Power Supply Filter for PLL ..................................................................................................................... 10
2.3. Power-Up Sequence .......................................................................................................................................... 10
2.4. Power Source .................................................................................................................................................... 10
3. Configuration Considerations ..................................................................................................................................... 11
3.1. SPI Flash Requirement in Controller SPI Mode ................................................................................................. 13
4. Clock Inputs ................................................................................................................................................................ 14
5. sysI/O .......................................................................................................................................................................... 15
6. LVDS Pin Assignments (For iCE40LP/HX Devices Only) ............................................................................................... 16
7. Layout Recommendations .......................................................................................................................................... 17
8. Checklist ...................................................................................................................................................................... 18
References .......................................................................................................................................................................... 19
Technical Support Assistance ............................................................................................................................................. 20
Revision History .................................................................................................................................................................. 21

Figures
Figure 2.1. Typical Power Supply Filter ........................................................................................................................................ 9
Figure 3.1. Typical Connection for External Flash Programming ............................................................................................... 12
Figure 3.2. Typical Connection for iCE40 Device Target or NVCM Programming ...................................................................... 13
Figure 4.1. High-Fanout Global Buffer Routing Resources for Clocks ........................................................................................ 14
Figure 5.1. Programmable Input/Output ................................................................................................................................... 15
Figure 6.1. LVDS Termination .................................................................................................................................................... 16
Figure 7.1. Layout Recommendations ....................................................................................................................................... 17

Tables
Table 2.1. Power Supply Description and Voltage Levels ............................................................................................................ 8
Table 2.2. Recommended Power Filtering Groups and Components .......................................................................................... 8
Table 3.1. Configuration Pins ..................................................................................................................................................... 11
Table 5.1. Weak Pull-Up Current Specifications ........................................................................................................................ 15
Table 6.1. Maximum Differential Pair Inputs .................................................................................................................................. 16
Table 8.1. iCE40 Hardware Checklist .......................................................................................................................................... 18

Acronyms in This Document
A list of acronyms used in this document.
Acronym Definition
CRAM Configuration RAM
PLL Phase-Locked Loop
POR Power-on-Reset
NVCM Non-volatile Configuration Memory
SPI Serial Peripheral Interface

1. Introduction
When designing complex hardware using the iCE40™ device family (iCE40 LP/HX, iCE40LM, iCE40 Ultra™, iCE40 UltraLite™,
iCE40 UltraPlus™), you must pay special attention to critical hardware configuration requirements. This technical note steps
through these critical hardware requirements related to the iCE40 device. This document does not provide detailed step-
by-step instructions but gives a high-level summary checklist to assist in the design process.
The iCE40 ultra-low-power, non-volatile devices are available in four versions – the LP series for low-power applications, the
HX series for high-performance applications, and the LM and Ultra/UltraLite/UltraPlus series for ultra-low-power mobile
applications.
This technical note assumes that you are familiar with the iCE40 device features as described in the following documents:
• iCE40LP/HX Family Data Sheet (FPGA-DS-02029)
• iCE40LM Family Data Sheet (FPGA-DS-02043)
• iCE40 Ultra Family Data Sheet (FPGA-DS-02028)
• iCE40 UltraLite Family Data Sheet (FPGA-DS-02027)
• iCE40 UltraPlus Family Data Sheet (FPGA-DS-02008)
This technical note covers the following critical hardware areas:
• Power supplies as they relate to the supply rails and how to connect them to the PCB and the associated system.
• Configuration and how to connect to the configuration mode selection.
• Device I/O interface and critical signals.

2. Power Supply
The V (core supply voltage), VCCIO_2, SPI_VCC and VPP_2.5 V determine the iCE40 device’s stable condition. These supplies
CC
need to be at a valid and stable level before the device can become operational. Refer to the family data sheets for voltage
requirements.
To evenly balance the stress in the solder joints, Lattice recommends that PCB solder pads match the corresponding package
solder pad type and dimensions. If a different PCB solder pad type is used, the recommended pad dimension is based on an
equivalent surface contact area.
Table 2.1. Power Supply Description and Voltage Levels
Supply3, 4 Voltage (Nominal Value) Description
V 1.2 V Core supply voltage
V 1.8 V to 3.3 V Power supply for I/O banks
CCIOx
VPP_2.5 V 1.86 V to 3.3 V Target serial peripheral interface (SPI) configuration
2.5 V to 3.3 V Controller SPI configuration
2.5 V to 3.3 V Configuration from NVCM
2.5 V to 3.0 V NVCM programming
VPP_FAST 1.8 V to 3.3 V, Leave unconnected5 Optional fast NVCM programming supply
SPI_VCC 1.8 V to 3.3 V SPI supply voltage
V 1, 2 1.2 V Analog voltage supply to phase-locked loop (PLL)
CCPLL
Notes:
1. V must be tied to V when PLL is not used.
CCPLL CC
2. External power supply filter required for V and GND .
CCPLL PLL
3. iCE40LM device family do not have VPP_2.5 V and VPP_FAST supplies.
4. iCE40 Ultra/iCE40 UltraLite/iCE40 UltraPlus device families do not have VPP_FAST.
5. VPP_FAST, used only for fast production programming, must be left floating or unconnected in applications, except CM36 and CM49
packages MUST have the VPP_FAST ball connected to VCCIO_0_1 ball externally.
6. VPP_2.5 V can optionally be connected to a 1.8 V (±5%) power supply in Target SPI configuration modes subject to the condition that
none of the HFOSC/LFOSC and RGB LED driver features are used. Otherwise, VPP_2.5 V must be connected to a power supply with a
minimum 2.3 V level.
2.1. Recommended Power Filtering Groups and Components
It is recommended to add filters to every power rail of iCE40 devices. Reliable filters enhance the overall performance of
the system. Table 2.2 shows the recommended filter group.
Table 2.2. Recommended Power Filtering Groups and Components
Power Input Recommended Filter Notes
V 4.7 µF + 100 nF per pin Core logic.
1.2 V
V 4.7 µF + 100 nF per pin I/O banks power supply pin
V Banks 0, 1, 2
1.8 V, 3.3 V
VPP_2.5 V 4.7 µF + 100 nF per pin NVCM programming and operating supply voltage
2.5 V
SPI_VCC 4.7 µF + 100 nF per pin SPI supply voltage
1.8 V, 3.3 V
V 100 Ω + 4.7 µF + 100 nF per pin PLL analog supply voltage
CCPLL1, 2

1.8 V/3.3 V
VCC
4.7 µF 100 nF VCCIOx
xPIN
100 nF 4.7 µF
2.5 V xPIN
VPP_2.5 V
4.7 µF 100 nF
VCCPLLx
1.8 V/3.3 V
100 nF
4.7 µF
xPIN
SPI_VCC GNDPLL*
4.7 µF 100 nF
Figure 2.1. Typical Power Supply Filter
Note: GNDPLL should not be connected to the board’s system ground except when a particular iCE40 device does not have a dedicated
GNDPLL pin. This filter should be applied even if the PLL is not utilized in the design.

2.2. Analog Power Supply Filter for PLL
The iCE40 sysCLOCK™ PLL contains analog blocks, so the PLL requires a separate power and ground that is quiet and stable
to reduce the output clock jitter of the PLL on the device with external V supply pins.
Note: PLL is not offered in some device/package combinations without the V ball. Refer to the data sheet and the
device family Pin List to check the availability of the V ball.
The sysCLOCK PLL has the DC ground connection made on the FPGA, so the external PLL ground connection (GND ) must
PLL
NOT be connected to the board’s ground except when a particular iCE40 device does not have a dedicated GND ball.
2.3. Power-Up Sequence
It is recommended to bring up the voltage in the order described in this section. Note that there is no specified timing delay
between the power supplies, however, there is a requirement for each supply to reach a level of 0.5 V or higher before any
subsequent power supplies in the sequence are applied.
To bring up the voltage, follow these steps:
1. Apply the V CC and V CCPLLx rails. These rails can come from the same source and must comply with the power supply
filtering requirements. V is responsible for powering the core logic, while V is responsible for powering the
CC CCPLLx
internal clock circuitry.
2. Apply the SPI_VCC rail. This rail is responsible for powering the SPI logic circuit used for the NVCM or external flash.
3. Apply the VPP_2.5 V rail. This rail is responsible for powering NVCM.
4. Other supplies (V CCIOx ) do not affect device power-up functionality. Apply these supplies at any time after V CC and V CCPLLx .
When powering iCE40 device rails with the same potential, it is recommended to use the same regulator to help meet
power sequencing.
As an example, V and V are tied together and should still be the first ones to be powered up. Then, if V , V , and
CC CCPLL CCIO0 CCIO2
SPI_VCC are tied, then it should be the next to be applied with power since SPI_VCC should be the next in the sequence.
Then, lastly, VPP_2.5 V to be applied with power.
There is no power-down sequence required. However, when partial power supplies are powered down, it is required that
the above sequence be followed when these supplies are powered up again.
For more information, refer to the Power-Up Supply Sequence section of the iCE40 device data sheet.
2.4. Power Source
It is recommended that the voltage regulators be accurate to within 3% of the optimum voltage to allow power noise
design margin.
When calculating the voltage regulator’s total tolerance, include:
• Regulator voltage reference tolerance
• Regulator line tolerance
• Regulator load tolerance
• Tolerances of any resistors connected to the regulator’s feedback pin that sets the regulator’s output voltage
With a 3% tolerance allocated to the voltage source, the design has a remaining 2% tolerance for noise and layout-related
issues. The 1.2 V rail is especially sensitive to noise, as every 12 mV is 1% of the rail voltage. For PLLs, target less than 0.25%
peak noise.

3. Configuration Considerations
The iCE40 LP/HX/Ultra/UltraLite/UltraPlus devices contain two types of memory, CRAM (Configuration RAM) and NVCM
(Non-volatile Configuration Memory). The iCE40LM device contains only the CRAM. CRAM memory contains the active
configuration. The NVCM provides on-chip storage of configuration data. It is one-time programmable and is recommended
for mass production.
For more information, refer to the iCE40 Programming and Configuration (FPGA-TN-02001).
The configuration and programming of the iCE40 LP/HX/LM/Ultra/UltraLite/UltraPlus devices from external memory uses
the SPI port, both in Controller and Target modes. In Controller SPI mode, the device configures its CRAM from an external
SPI flash connected to it. In Target mode, the device can be configured or programmed using the Lattice Diamond™
Programmer or embedded processor and the Lattice Radiant™ Programmer for iCE40 UltraPlus devices.
On the iCE40LP/HX and iCE40 Ultra/UltraLite/UltraPlus device families, the SPI_SS_B determines if the iCE40 CRAM is
configured from an external SPI (SPI_SS_B=0) or from the NVCM (SPI_SS_B=1). This pin is sampled after Power-on-Reset
(POR) is released or CRESET_B is held low and then goes high.
Table 3.1. Configuration Pins
Pin Name Function Direction External Termination Notes
CRESET_B Configuration Reset Input 10 kΩ pull-up to V . A low on CRESET_B
input, active low. delay’s
configuration.
CDONE Configuration Done Output Pull-up to V . —
output from iCE40. The maximum Rpullup value is calculated as
follows: Rpullup=1/(2 X ConfigFrequency X
CDONETraceCap)
SPI_VCC SPI supply voltage. Supply — —
SPI_SI SPI input to the iCE40, Input — Released to user
in both Controller and I/O after
Target modes. configuration.
SPI_SO SPI output from the Output — Released to user
iCE40, in both I/O after
Controller and Target configuration.
modes.
SPI_SCK SPI clock Input/Output 10 kΩ pull-up to VCC_SPI recommended. Direction based on
Controller or
Target modes.
Released to user
I/O after
configuration.
SPI_SS_B Chip select Input (Target 10 kΩ pull-up to VCC_SPI in Controller mode and Refer to iCE40
mode)/Output a 10 kΩ pull-down in Target mode is Programming and
(Controller mode) recommended if not driven by a processor. Configuration
(FPGA-TN-02001)
for more details.
A typical connection from a host programmer to an iCE40 device with external flash is shown in Figure 3.1 and Figure 3.2.
When programming the external flash, HOST CS is connected to both the CS pins of the flash and the iCE40 device with a
10 kΩ pull-up. Drive CRESET_B is low while programming the external flash. The Host Programmer will be communicating
with the external flash in this configuration, and upon normal operation, the iCE40 device will be fetching data from the
external flash for proper bootup and operation.

To program the iCE40 device in Target mode (CRAM or NVCM), connect the device as shown in Figure 3.2. The HOST CS is
only connected to the iCE40 device without a 10 kΩ pull-up, and the HOST must ensure pin CS is LOW to activate the Target
SPI configuration. Notice that connections of MOSI and MISO are interchanged during the configuration at NVCM, revert to
the original connection, including flash CS, for normal operation.
For ease of prototype programming and debugging, it is recommended that every PCB has easy access to the signals
described in Table 3.1.
Route these signals to a 2.54 mm pitch header to allow easy connection to the Lattice Programming Cable.
If space is limited, other routing options include:
• Smaller pitch header(s)
• Test points for soldering connection wires
• A high-density connector that mates to a break-out board or cable
P R O G
H O
R
H
A
S TM
O S
G P
M E R
T _ M
S T _
I O
O S I
IS O
S C K
C S n
1 . 8 V / 3
1
.
0
3 V
k
. 8
V
/ 3
/
3
. 3 V
1 0 k
1 . 8
1 0
C
S
F
D
P
L
C IO 2
O N E
E S E T
I _ V C C
I _ S I
I _ S 0
I _ S C K
I _ S S _ B
A S H _ S I
A S H _ S 0
A S H _ C S
04ECi
HSALF
Figure 3.1. Typical Connection for External Flash Programming

P R O G
A
S TM
M E R
O S I
IS O
S C K
C S n
1 . 8 V / 3
1 .
8 V
3 .
3 . 3 V
1 0 k
1 . 8
1 0
C C IO 2
D O N E
R E S E T
P I _ V C C
P I _ S I
P I _ S 0
P I _ S C K
P I _ S S _ B
L A S H _ V C
L A S H _ S I
L A S H _ S 0
L A S H _ S C
L A S H _ C S
K
04ECi
HSALF
Figure 3.2. Typical Connection for iCE40 Device Target or NVCM Programming
3.1. SPI Flash Requirement in Controller SPI Mode
You are free to select any industry-standard SPI flash. The SPI flash must support the 0x0B Fast Read command, using a
24-bit start address with eight dummy bits before the PROM provides the first data. For more information, refer to iCE40
Programming and Configuration (FPGA-TN-02001).

4. Clock Inputs
The iCE40 device provides certain pins for use as clock inputs, as described in Figure 4.1. These shared pins can be used
alternately for general-purpose I/O. For the global clock requirements, refer to the External Switching Characteristics
section of the iCE40 device family data sheet.
When these pins are used for clocking purposes, you need to pay attention to minimize signal noise on these pins. For more
information, refer to the iCE40 sysCLOCK PLL Design User Guide (FPGA-TN-02052).
GBIN0
GBIN7
Global
Buffer
3 GBUF71
kna
Global B Buffer O GBUF6 /I
GBIN6
5NIBG
1. GBU F7 and its associated PIO
iC E 4 0 LP /H X
GB
I/O B a n k 0 IN1
G B G G B G u u B l B l o o f f U U f f b b e e F F a a r r 0 1 l l
Global
Buffer
GBUF2
Global Buffer GBUF3
4 5 l l r r a a F F e e b b U U f f o o f f B B u u l l G G G G B B
4N I/O B a n k 2 IBG
are best for direct differential clock inputs.
GBIN2
knaB
O/I
GBIN3
H SSG
iC
GBUF5
GBUF0
G0
E 4
iC E 4 0 L M /iC E 4 0 U ltra /
0 U ltra Lite /iC E 4 0 U ltra
I/O Bank 0 G G 2 7
GBUF2 GBUF7
GBUF1 GBUF3
G G I/O Bank 2 1 3
P lu s
LPSG GBUF4
GBUF6
G6
Figure 4.1. High-Fanout Global Buffer Routing Resources for Clocks

5. sysI/O
The iCE40 device provides certain configurations for each I/O. These pins can be configured as input, output, and tri-state.
Additionally, an internal pull-up resistor can be enabled in the configuration. For more information, refer to the iCE40
device data sheet.
For the value of the pull-up resistor, the implementation on the iCE40 device is through the use of a pull-up current. The
values are shown in Table 5.1.
Table 5.1. Weak Pull-Up Current Specifications
Condition Min Max Unit
V = 1.8 V, 0 ≤ V ≤ 0.65 V –3 –31 μA
CCIO IN CCIO
V = 2.5 V, 0 ≤ V ≤ 0.65 V –8 –72 μA
V = 3.3 V, 0 ≤ V ≤ 0.65 V –11 –128 μA
O U
O
T
I NIN
E
iC EH
E n a b le d
D is a b le d
O U T C L K
O U T C L K
G A T E
O L D
= S t a t ic
IN
a lly d
D
e
L K
f in e
V C C IO
I/ O B a n k 0 , 1 , 2 , o r 3
V o lt a g e S u p p ly
0 = H i-Z
1 = O u t p u t
E n a b le d
P u ll-u
P u ll- u p
E n a b le
L a t c h in h ib it s
s w it c h in g f o r
lo w e s t p o w e r
G B IN p in s o p t io n a lly
c o n n e c t d ir e c t ly t o a n
a s s o c ia t e d G B U F g lo b a l
b u f fe r
d b y c o n f ig u r a t io n p r o g r a m
p
A D
Figure 5.1. Programmable Input/Output

6. LVDS Pin Assignments (For iCE40LP/HX Devices Only)
Refer to the Pinout files for differential input pins. Differential outputs are supported at all banks. The maximum differential
pair input for each iCE40 device is shown in Table 6.1.
Table 6.1. Maximum Differential Pair Inputs
iCE40HX1K iCE40LP1K iCE40HX4K iCE40LP4K iCE40LP8K iCE40HX8K
11 12 12 20 23 26
LVDS and Sub-LVDS inputs require external termination resistors for proper operation, as shown in Figure 6.1. A
termination resistor (RT) between the positive and negative inputs at the receiver forms a current loop. The current across
this resistor generates the voltage detected by the receiver’s differential input comparator.
LVDS and Sub-VLDS outputs require an external resistor network consisting of two series resistors (RS) and a parallel
resistor (RP). This resistor network adjusts the FPGA’s output driver to provide the necessary current and voltage
characteristics required by the specification.
For more information on the computation for RS and RP, refer to the LVDS and Sub-LVDS Termination section of Using
Differential I/O (LVDS, Sub-LVDS) in iCE40 LP/HX Devices (FPGA-TN-02213).
Figure 6.1. LVDS Termination

7. Layout Recommendations
A good schematic design should translate into a good layout that works without any issues with noise or power distribution.
The following lists some general recommendations for layouts:
• All power should come from power planes to ensure good power delivery and thermal stability.
• Each power pin has its own decoupling capacitor, typically 100 nF, that should be placed as close as possible to each
other.
• The placement of analog circuits must be away from digital circuits or high-switching components.
• High-speed signals should have a clearance of five times the trace width of other signals.
• High-speed signals that transition from one layer to another should have a corresponding transition ground if both
reference planes are grounded. If the reference on the other layer is a V plane, then a stitching capacitor should be
used (ground to V ). Refer to Figure 7.1.
Figure 7.1. Layout Recommendations
• High-speed signals have a corresponding impedance requirement, calculate the necessary trace width and trace gap
(differential gap) according to the desired stack-up. Verify trace dimensions with the PCB vendor.
• For differential pairs, match the length as closely as possible. A good rule of thumb is to match up to ±5 mils.
For more information on layout recommendations, refer to the following documents:
• PCB Layout Recommendations for BGA Packages (FPGA-TN-02024)
• PCB Layout Recommendations for Leaded Packages (FPGA-TN-02160)

8. Checklist
Table 8.1. iCE40 Hardware Checklist
iCE40 Hardware Checklist Item OK N/A
1 Power Supply
1.1 Core supply V at 1.2 V
1.2 I/O power supply V 0-3 at 1.8 V to 3.3 V
CCIO
1.3 SPI_VCC at 1.8 V to 3.3 V
1.4 V uses 1.2 V connected 100 Ω series resistor and 4.7 µF bypass capacitor
(even if PLL is not used).
1.5 GNDPLL must NOT be connected to the board1
1.6 Power-up supply sequence and Ramp Rate requirements are met2
1.7 VPP_2.5 V should not exceed 3.0 V during NVCM programming
2 Power-on-Reset (POR) inputs
2.1 V
2.2 SPI_VCC
2.3 VCCIO_0-3
2.4 VPP_2V5
VPP_FAST
3 Configuration
3.1 Configuration mode based on SPI_SS_B level when CRESET_B transitions high, or
POR completes
3.2 Pull-up on CRESET_B, CDONE pin
3.3 TRST_B is kept low for normal operation
4 I/O pin assignment
4.1 LVDS pin assignment considerations
Notes:
1. An exception is when a particular iCE40 device does not have a dedicated GNDPLL ball.
2. Refer to the iCE40 device family data sheet for the ramp rates under the Power Supply Ramp Rates section.

References
For more information, refer to the following resources:
• iCE40 LP/HX Family Data Sheet (FPGA-DS-02029)
• iCE40LM Family Data Sheet (FPGA-DS-02043)
• iCE40 Ultra Family Data Sheet (FPGA-DS-02028)
• iCE40 UltraLite Family Data Sheet (FPGA-DS-02027)
• iCE40 UltraPlus Family Data Sheet (FPGA-DS-02008)
• iCE40 Programming and Configuration (FPGA-TN-02001)
• iCE40 sysCLOCK PLL Design User Guide (FPGA-TN-02052)
• PCB Layout Recommendations for BGA Packages (FPGA-TN-02024)
• PCB Layout Recommendations for Leaded Packages (FPGA-TN-02160)
• iCE40 LP/HX device family web page
• iCE40 Ultra/Ultra Lite device family web page
• iCE40 UltraPlus device family web page
• Lattice Insights web page Lattice Semiconductor training courses and learning plans

Technical Support Assistance
Submit a technical support case through www.latticesemi.com/techsupport.
For frequently asked questions, refer to the Lattice Answer Database at www.latticesemi.com/Support/AnswerDatabase.

Revision History
Revision 2.3, April 2024
Section Change Summary
All Minor editorial fixes.
Inclusive language Added this section.
Configuration Considerations Reworked the last paragraph of this section and replaced with the following:
• For ease of prototype programming and debugging, it is recommended that every PCB
has easy access to the signals described in Table 3.1.
Route these signals to a 2.54 mm pitch header to allow easy connection to the Lattice
Programming Cable.
If space is limited, other routing options include:
• Smaller pitch header(s).
• Test points for soldering connection wires.
• A high-density connector that mates to a break-out board or cable.
Revision 2.2, January 2024
Configuration Considerations Updated the following figures in this section:
• Figure 3.1. Typical Connection for External Flash Programming
• Figure 3.2. Typical Connection for iCE40 Device Target or NVCM Programming
Revision 2.1, October 2023
Disclaimers Updated the disclaimer.
Introduction Fixed a broken link for the iCE40 UltraPlus Family Data Sheet.
Power Supply • The following changes were made to Table 2.1. Power Supply Description and Voltage
Levels:
• Changed supply name from VCCIO_X to VCCIOx and corrected the voltage value.
• Added voltage values for VPP_2V5.
• Added footnote 6.
• Added the following subsections:
• Recommended Power Filtering Groups and Components
• Power-Up Sequence
• Power Source
• Moved Analog Power Supply Filter for PLL from the main section to the subsection.
• Removed the Isolating PLL Supplies figure.
Configuration Considerations • Moved this subsection to the main section.
• Removed a note from Table 3.1. Configuration Pins.
• Added the following figures and described the routing connections:
• Figure 3.1. Typical Connection for External Flash Programming
• Figure 3.2. Typical Connection for iCE40 Device Target or NVCM Programming
Clock Inputs Added this section.
sysI/O Added this section.
LVDS Pin Assignments (For Added contents including Figure 6.1. LVDS Termination.
iCE40LP/HX Devices Only)
Layout Recommendations Added this section.

Checklist The following changes were made to Table 8.1. iCE40 Hardware Checklist:
• Updated checklist items 1.4 and 3.1.
• Added footnote 2.
References Added this section.
Technical Support Assistance Added a reference to the Lattice Answer Database on the Lattice website.
All • Minor changes in formatting and styles.
• Replaced “Master” and “Slave” terms with “Controller” and “Target” to adhere to
Lattice’s Inclusive Language Guidelines.
Revision 2.0, January 2022
Power Supply Updated footnote 5 in Table 2.1 Power Supply Description and Voltage Levels.
Revision 1.9, July 2021
Analog Power Supply Filter for Updated the footnote in Figure 3.1.
Checklist Updated Table 5.1 iCE40 Hardware Checklist to add 1.7, 1.8 and footnote.
Revision 1.8, April 2020
Disclaimers Added this section.
Acronyms in This Document Added this section.
Power Supply Updated Table 3.1 Configuration Pins.
Changed VCCIO_2 to VCCIO_X and added footnote.
All • Updated document IDs of referenced data sheets and technical notes.
• Minor changes in formatting and styles.
Revision 1.7, December 2016
All • Changed document number from TN1252 to FPGA-TN-02006.
• Updated document template.
Revision 1.6, June 2016
All Added support for iCE40 UltraPlus device family.
Introduction Updated Introduction section. Added reference to FPGA-DS-02008, iCE40 UltraPlus Family
Data Sheet.
Power Supply Updated Power Supply section. Revised Table 2.1, Power Supply Description and Voltage
Levels. Added footnote 5 to VPP_FAST.
Analog Power Supply Filter for Updated Analog Power Supply Filter for PLL section. Revised Figure 3.1, Isolating PLL
PLL Supplies. Changed 100 W to 100 Ohms.
Configuration Considerations Updated Configuration Considerations section. Revised Table 3.1, Configuration Pins.
Updated SPI_SS_B External Termination.
Technical Support Assistance Updated Technical Support Assistance section.

Revision 1.5, January 2015
All Added support for iCE40 UltraLite device family.
Revision 1.4, June 2014
All Added support for iCE40 Ultra device family.
Analog Power Supply Filter for Updated Analog Power Supply Filter for PLL section.
Configuration Considerations Updated Configuration Considerations section. Updated Table 3.1, Configuration Pins.
Changed VCCIO_2 to VCC_SPI in SPI_SCK and SPI_SS_B.
Revision 1.3, October 2013
Configuration Considerations Updated Configuration Considerations section. Updated Table 3.1, Configuration Pins.
Technical Support Assistance Updated Technical Support Assistance information.
Revision 1.2, December 2012
Power Supply Updated Power Supply section. Revised Table 2.1, Power Supply Description and Voltage
Levels. Corrected VCC nominal voltage.
Revision 1.1, September 2012
LVDS Pin Assignments (For Updated LVDS Pin Assignments (For iCE40LP/HX Devices Only) text section. Corrected
iCE40LP/HX Devices Only) description of differential input and output support.
Revision 1.0, September 2012
All Initial release.
© 2012-2024 Lattice Semiconductor Corp. All Lattice trademarks, registered trademarks, patents, and disclaimers are as listed at www.latticesemi.com/legal.
All other brand or product names are trademarks or registered trademarks of their respective holders. The specifications and information herein are subject to change without notice.
FPGA-TN-02006-2.3 23

www.latticesemi.com
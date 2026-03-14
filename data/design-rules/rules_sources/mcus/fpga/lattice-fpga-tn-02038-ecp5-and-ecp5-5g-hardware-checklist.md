---
source: "Lattice FPGA-TN-02038 -- ECP5 and ECP5-5G Hardware Checklist"
url: "https://0x04.net/~mwk/doc/lattice/ecp5/FPGA-TN-02038-2-0-ECP5-and-ECP5-5G-Hardware-Checklist.pdf"
format: "PDF 36pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 50755
---

ECP5 and ECP5-5G Hardware Checklist
Technical Note
FPGA-TN-02038-2.0
July 2024

Disclaimers
Lattice makes no warranty, representation, or guarantee regarding the accuracy of information contained in this document or the suitability of its
products for any particular purpose. All information herein is provided AS IS, with all faults, and all associated risk is the responsibility entirely of the
Buyer. The information provided herein is for informational purposes only and may contain technical inaccuracies or omissions, and may be otherwise
rendered inaccurate for many reasons, and Lattice assumes no obligation to update or otherwise correct or revise this information. Products sold by
Lattice have been subject to limited testing and it is the Buyer's responsibility to independently determine the suitability of any products and to test
and verify the same. LATTICE PRODUCTS AND SERVICES ARE NOT DESIGNED, MANUFACTURED, OR TESTED FOR USE IN LIFE OR SAFETY CRITICAL
SYSTEMS, HAZARDOUS ENVIRONMENTS, OR ANY OTHER ENVIRONMENTS REQUIRING FAIL-SAFE PERFORMANCE, INCLUDING ANY APPLICATION IN
WHICH THE FAILURE OF THE PRODUCT OR SERVICE COULD LEAD TO DEATH, PERSONAL INJURY, SEVERE PROPERTY DAMAGE OR ENVIRONMENTAL
HARM (COLLECTIVELY, "HIGH-RISK USES"). FURTHER, BUYER MUST TAKE PRUDENT STEPS TO PROTECT AGAINST PRODUCT AND SERVICE FAILURES,
INCLUDING PROVIDING APPROPRIATE REDUNDANCIES, FAIL-SAFE FEATURES, AND/OR SHUT-DOWN MECHANISMS. LATTICE EXPRESSLY DISCLAIMS
ANY EXPRESS OR IMPLIED WARRANTY OF FITNESS OF THE PRODUCTS OR SERVICES FOR HIGH-RISK USES. The information provided in this document
is proprietary to Lattice Semiconductor, and Lattice reserves the right to make any changes to the information in this document or to any products at
any time without notice.
Inclusive Language
This document was created consistent with Lattice Semiconductor’s inclusive language policy. In some cases, the language in underlying tools and
other items may not yet have been updated. Please refer to Lattice’s inclusive language FAQ 6878 for a cross reference of terms. Note in some cases
such as register names and state names it has been necessary to continue to utilize older terminology for compatibility.

Contents
Contents ............................................................................................................................................................................... 3
Acronyms in This Document ................................................................................................................................................. 6
1. Introduction .................................................................................................................................................................. 7
2. Power Supplies ............................................................................................................................................................. 8
2.1. Power Noise ........................................................................................................................................................ 8
2.2. Power Source ...................................................................................................................................................... 9
3. ECP5 and ECP5-5G SERDES/PCS Power Supplies ........................................................................................................ 10
3.1. Recommended Power Filtering Groups and Components ................................................................................ 10
3.2. Ferrite Bead Selection Notes ............................................................................................................................. 11
3.3. Ground Pins ....................................................................................................................................................... 11
3.4. Clock Oscillator Supply Filtering ........................................................................................................................ 11
3.5. Capacitor Selection ........................................................................................................................................... 12
3.5.1. Dielectric ...................................................................................................................................................... 12
3.5.2. Voltage Rating .............................................................................................................................................. 12
3.5.3. Size ............................................................................................................................................................... 12
3.6. Unused Bank V ............................................................................................................................................ 12
CCIOx
3.7. Unused SERDES DCU ......................................................................................................................................... 12
3.8. Unused SERDES Channel in DCU ....................................................................................................................... 12
4. Power Sequencing ...................................................................................................................................................... 13
5. Power Estimation ....................................................................................................................................................... 14
6. Configuration Considerations ..................................................................................................................................... 15
7. External SPI FLASH ...................................................................................................................................................... 19
8. I/O Pin Assignments .................................................................................................................................................... 20
9. sysI/O .......................................................................................................................................................................... 21
10. Clock Inputs ................................................................................................................................................................ 23
11. Pinout Considerations ................................................................................................................................................ 24
12. LVDS Pin Assignments ................................................................................................................................................. 25
13. HSUL and SSTL Pin Assignments ................................................................................................................................. 26
14. LFE5U to LFE5UM/LFE5UM5G and LFE5UM to LFE5UM5G Migration ....................................................................... 27
15. Layout Recommendations .......................................................................................................................................... 28
16. Checklist ...................................................................................................................................................................... 29
References .......................................................................................................................................................................... 31
Technical Support Assistance ............................................................................................................................................. 32
Revision History .................................................................................................................................................................. 33

Figures
Figure 3.1. Recommended Power Filters ............................................................................................................................ 11
Figure 6.1. Typical Connections for Programming SRAM via JTAG ..................................................................................... 16
Figure 6.2. Typical Connections for Programming SRAM via SPI ........................................................................................ 17
Figure 6.3. Typical Connections for Programming external Flash via JTAG ........................................................................ 18
Figure 9.1 sysI/O Buffer Pair for Left and Right Sides ......................................................................................................... 21
Figure 9.2. sysI/O Buffer Pair for Top and Bottom Sides .................................................................................................... 22
Figure 10.1. Clock Oscillator Bypassing ............................................................................................................................... 23
Figure 10.2. PCB Dual Footprint Supporting HCSL and LVDS Oscillators ............................................................................ 23
Figure 15.1. PCB Layout Recommendation......................................................................................................................... 28

Tables
Table 2.1. ECP5 and ECP5-5G FPGA Power Supplies ............................................................................................................ 8
Table 3.1. Recommended Power Filtering Groups and Components................................................................................. 10
Table 3.2. Recommended Capacitor Sizes .......................................................................................................................... 12
Table 6.1. JTAG Pin Recommendations .............................................................................................................................. 15
Table 6.2. Pull-up/Pull-down Recommendations for Configuration Pins ........................................................................... 15
Table 6.3. Configuration Pins Needed per Programming Mode1 ....................................................................................... 15
Table 9.1. Weak pull up/down current specifications ........................................................................................................ 21
Table 16.1. Hardware Checklist .......................................................................................................................................... 29

Acronyms in This Document
A list of acronyms used in this document.
Acronym Definition
BGA Ball Grid Array
CML Current-Mode Logic
LUT Look Up Table
LVCMOS Low-Voltage Complementary Metal Oxide Semiconductor
LVDS Low-Voltage Differential Signaling
PCB Printed Circuit Board

1. Introduction
When designing complex hardware using the ECP5™ and ECP5-5G™ FPGA, you must pay special attention to critical
hardware configuration requirements. This technical note steps through these critical hardware implementation items
relative to the ECP5 and ECP5-5G device. The document does not provide detailed step-by-step instructions but gives a
high-level summary checklist to assist in the design process.
The device family consists of FPGA LUT densities ranging from 25K to 85K. This technical note assumes that the reader
is familiar with the ECP5 and ECP5-5G device features as described in ECP5 and ECP5-5G Family Data Sheet
(FPGA-DS-02012). The data sheet includes the functional specification for the device. Topics covered in the data sheet
include but are not limited to the following:
• High-level functional overview
• Pinouts and packaging information
• Signal descriptions
• Device-specific information about peripherals and registers
• Electrical specifications
Refer to ECP5 and ECP5-5G Family Data Sheet (FPGA-DS-02012) for details. The critical hardware areas covered in this
technical note are:
• Power supplies as they relate to the ECP5 and ECP5-5G power supply rails and how to connect them to the PCB
and the associated system
• Configuration mode selection for proper power-up behavior
• Device I/O interface and critical signals
Important: You should refer to the following documents for detailed recommendations.
• ECP5 and ECP5-5G sysCONFIG Usage Guide (FPGA-TN-02039)
• ECP5 and ECP5-5G SERDES/PCS Usage Guide (FPGA-TN-02206)
• ECP5 and ECP5-5G sysI/O Usage Guide (FPGA-TN-02032)
• ECP5 and ECP5-5G sysClock PLL/DLL Design and Usage Guide (FPGA-TN-02200)
• ECP5 and ECP5-5G Memory Usage Guide (FPGA-TN-02204)
• ECP5 and ECP5-5G High-Speed I/O Interface (FPGA-TN-02035)
• Power Consumption and Management for ECP5 and ECP5-5G Devices (FPGA-TN-02210)
• ECP5 and ECP5-5G sysDSP Usage Guide (FPGA-TN-02205)
• Electrical Recommendations for Lattice SERDES (FPGA-TN-02077)
• High-Speed PCB Design Considerations (FPGA-TN-02024)
• Power Decoupling and Bypass Filtering for Programmable Devices (FPGA-TN-02210)
• LatticeSC SERDES Jitter (TN1084)
• ECP5 and ECP5-5G-related pinout information can be found on the Lattice website.
• HSPICE SERDES simulation package (available under NDA, contact the license administrator at
lic_admin@latticesemi.com)

2. Power Supplies
The V , V , and V power supplies are monitored to determine the ECP5 and ECP5-5G internal power good
CC CCAUX CCIO8
condition during power-up. These supplies need to be at a valid and stable level before the device can become
operational and be configured. All other VCCIOX are not monitored during power-up, but need to be at valid and stable
level before the device is configured and entered into User Mode. Several other supplies including V , V , V ,
CCA CCAUXA CCHRX
and V are used in conjunction with on-board SERDES on LFE5UM/LFE5UM5G devices. Table 2.1 lists the power
CCHTX
supplies and the appropriate voltage levels for each supply.
Table 2.1. ECP5 and ECP5-5G FPGA Power Supplies
Supply Voltage (Nominal Value) Description
V V (LFE5U/5UM) FPGA core power supply.
CC
V (LFE5UM5G)
V V (LFE5UM) Analog power supply for SERDES blocks (For LFE5UM/LFE5UM5G devices).
CCA
V (LFE5UM5G) Should be isolated and clean from excessive noise.
V 2.5 V Auxiliary power supply
CCAUX
V
CCIO[0-4, 6-8]
1 1.2 V to 3.3 V I/O power supply. Seven (eight on LFE5/LFE5UM5G-85 in 756 and 554 caBGA)
general purpose I/O banks. Each bank has its own V supply:
CCIO
V is used in conjunction with pins dedicated and shared with device
CCIO8
configuration, include JTAG.
V , and V are optionally used based on per bank usage of I/O.
CCIO1, 2, 3, 4, 6 CCIO7
V V (LFE5UM) Input terminate voltage supply for SERDES inputs (For LFE5UM/LFE5UM5G
CCHRX
V (LFE5UM5G) devices)
V V (LFE5UM) Output driver/termination voltage supply for SERDES outputs (for
V (LFE5UM5G) LFE5UM/LFE5UM5G devices)
V 2.5 V Auxiliary power supply for SERDES (for LFE5UM/LFE5UM5G devices)
CCAUXA
Note:
1. Bank 4 exists only on the LFE5/LFE5UM5G-85 device in 756 caBGA and 554 caBGA. It is not available in any other
device/package combinations. When migrating LFE5/LFE5UM5G-85 to lower density devices, I/O on Bank 4 cannot be used.
The ECP5 and ECP5-5G FPGA device has a power-up reset state machine that monitors various power supplies.
These supplies should come up monotonically. The on-chip Power-On-Reset (POR) is de-asserted when the following
conditions are met:
• V reaches 0.9 V or above
• V reaches 2.0 V or above
• V reaches 0.95 V or above
Initialization of the device does not proceed until the last power supply above has reached its minimum operating
voltage.
2.1. Power Noise
The power rail voltages of the FPGA allow for a worst-case normal operating tolerance of ±5% of these voltages.
The 5% tolerance includes any noise.

2.2. Power Source
It is recommended that the designed voltage regulators are accurate to within 3% of the optimum voltage to allow
power noise design margin.
When calculating the voltage regulator’s total tolerance, include:
• Regulator voltage reference tolerance
• Regulator line tolerance
• Regulator load tolerance
• Tolerances of any resistors connected to the regulator’s feedback pin, which sets the regulator’s output voltage
• Expected voltage drops due to power filtering the ferrite bead’s ESR x expected current draw
• Expected voltage drops due to the current measuring resistor’s ESR x expected current draw
With a 3% tolerance allocated to the voltage source, the design has a remaining 2% tolerance for noise and layout
related issues. The 1.2 V rail is especially sensitive to noise, as every 12 mV is 1% of the rail voltage. For SERDES
differential power rails, it is recommended to target a maximum 1% peak noise. For PLLs, target less than 0.25% peak
noise.

3. ECP5 and ECP5-5G SERDES/PCS Power Supplies
There are supplies dedicated to the operation of the ECP5 and ECP5-5G device SERDES Blocks. These supplies are also
paired with dedicated ground pins. Providing a quiet supply is critical for these blocks. Supplies should be decoupled
with adequate power filters. Bypass capacitors must be located close to the device package pins with very short traces
to keep inductance low.
For the best jitter performance, use careful pin assignments to keep noisy I/O pins away from sensitive functional pins.
The leading cause of PCB-related crosstalk to sensitive blocks is related to FPGA outputs located in close proximity to
the sensitive power supplies. These supplies require a cautious board layout to ensure noise immunity to the switching
noise generated by FPGA outputs. Guidelines are provided to build quiet-filtered supplies for the analog supplies,
however, a robust PCB layout is required to ensure that noise does not infiltrate into these analog supplies.
3.1. Recommended Power Filtering Groups and Components
Table 3.1. Recommended Power Filtering Groups and Components
Power Input Recommended Filter Notes
V 10 µF x 3 + 100 nF per pin Core and clock logic.
ECP5 1.1 V
ECP5-5G 1.2 V
V 120 Ω FB + 10 µF + 100 nF per pin Auxiliary power supply
2.5 V
V 10 µF + 100 nF per pin Bank I/O.
CCIO[0-8]
Unused banks can replace the 10 µF with a 1.0 µF.
For banks with lots of outputs or large capacitive
loading replace the 10 µF with a 22 µF (or add one
additional 10 µF).
1.2 V to 3.3 V
V 120 Ω FB + 10 µF + 100 nF per pin SERDES Analog Power Supply
ECP5UM 1.1 V
V 120 Ω FB + 10 µF + 100 nF per pin SERDES Input Buffer Power Supply
V 120 Ω FB + 10 µF + 100 nF per pin SERDES Output Buffer Power Supply
V 120 Ω FB + 10 µF + 100 nF per pin SERDES Auxiliary Supply Voltage
2.5 V

E C P 5 : 1 .1 V
E C P 5 -5 G : 1 .2 V
2 .5 V
1 2 0
2 .5 V
E C P 5: 1 .1 V
E C P 5 -5 G : 1 .2 V
1
0
x
µ
3
F
0x
0P
P
nIN
n
IN
IN
I N
C
A
U
U
X
X
V C C
IO [0 -8 ]
C C H R X
C C H T X
1 .2
0 n F
P IN
P IN
P I N
V / 1 .5 V
1 0
/
1 .8 V
/ 2
EE
EE
.5 V / 3 .3 V
C P 5: 1 .1 V
C P 5 -5 G : 1 .2 V
C P 5 : 1 .1 V
C P 5 -5 G : 1 .2 V
Figure 3.1. Recommended Power Filters
3.2. Ferrite Bead Selection Notes
• Most designs work well using ferrite beads between 120 Ω at 100 MHz and 240 Ω at 100 MHz.
• Ferrite bead-induced noise voltage from ESR × CURRENT should be < 1% of rail voltage for non-analog rails and
< 0.25% for sensitive rails.
• Non-PLL rails should use ferrite beads with an ESR between 0.025 Ω and 0.10 Ω depending on the current load.
• PLL rails are low-current, which allows ferrite beads with an ESR ≤ 0.3 Ω.
• Small package size ferrite beads have higher ESR than large package-size ferrite beads of the same impedance.
• High-impedance ferrite beads have a higher ESR than low-impedance ferrite beads in the same package size.
3.3. Ground Pins
• All ground pins need to be connected to the board’s ground plane.
3.4. Clock Oscillator Supply Filtering
When providing an external reference clock to the FPGA from, for example, a single-ended or differential clock
oscillator, proper power supply isolation and decoupling of the clock oscillator are recommended.
When specifying components, choose good-quality ceramic capacitors in small packages and place them as close to the
clock oscillator supply pins as practically possible. Good quality capacitors for bypassing generally meet the following
requirements:

3.5. Capacitor Selection
When specifying components, choose good-quality ceramic capacitors in small packages and place them as close to the
power supply pins as practically possible. Good-quality capacitors for bypassing generally meet the requirements
discussed in the following sections.
3.5.1. Dielectric
Use dielectrics such as X5R, X7R, and similar that have good capacitance tolerance (≤ ±20%) over a temperature range.
Avoid Y5V, Z5U, and similarly poor capacitance-controlled dielectrics.
3.5.2. Voltage Rating
Capacitor working capacitance decreases non-linearly with a higher voltage bias. To maintain capacitance, the
capacitor voltage rating should be at least 80% higher than the voltage rail (maximum). For example, 3.3 V rail bypass
capacitors should use the commonly available 6.3 V rating as a minimum.
3.5.3. Size
Smaller-body capacitors have lower inductance, work at higher frequencies, and improve board layout. For a given
voltage rating, smaller body capacitors tend to cost more than larger body capacitors. Optimizing between market
pricing and size-related inductance, the following capacitor sizes are recommended:
Table 3.2. Recommended Capacitor Sizes
Capacitance Size Preferred Size Next Best
0.1 µF 0201 0402
1.0 µF, 2.2 µF 0402 0603
4.7 µF 0603 0402
10 µF 0603 0805
22 µF 0805 1206
3.6. Unused Bank V
CCIOx
Connect unused V pins to a power rail. Do not leave them open.
3.7. Unused SERDES DCU
Connect VCCA, VCCAUXA, VCCHRX, VCCHTX, REFCLKy_Dx, and Rx Differential Inputs to board ground.
Leave the Tx differential pair outputs open.
3.8. Unused SERDES Channel in DCU
Connect VCCA and VCCHTX to a power rail.
Connect REFCLKy_Dx and Rx Differential Inputs to board ground.
Leave the VCCAUXA, VCCHRX and Tx differential pair outputs open.

4. Power Sequencing
V supplies should be powered up before or together with the V and V supplies.
CCIO CC CCAUX

5. Power Estimation
Once the ECP5 and ECP5-5G device density, package, and logic implementation are decided, power estimation for the
system environment should be determined based on the Power Calculator provided as part of the Lattice Diamond®
design tool. When estimating power, you should keep two goals in mind:
• Power supply budgeting should be based on the maximum power-up in-rush current, configuration current, and
maximum DC and AC current for the given system’s environmental conditions.
• The ability for the system environment and ECP5 and ECP5-5G device packaging to be able to support the specified
maximum operating junction temperature. By determining these two criteria, the ECP5 and ECP5-5G device power
requirements are taken into consideration early in the design phase.

6. Configuration Considerations
The ECP5 and ECP5-5G devices include provisions to configure the FPGA via the JTAG interface or several modes
utilizing the sysCONFIG port. The JTAG port includes a 4-pin interface. The interface requires the following PCB
considerations:
Table 6.1. JTAG Pin Recommendations
JTAG Pin PCB Recommendation
TDI 4.7 kΩ pull-up to V
TMS 4.7 kΩ pull-up to V
TDO 4.7 kΩ pull-up to V
TCK 4.7 kΩ pull-down to GND
Every PCB is recommended to have easy access to FPGA JTAG pins, even if the primary configuration interface is not
using the JTAG port. This JTAG port enables debugging in the final system. For best results, route the TCK, TMS, TDI,
and TDO signals to a common test header along with V and ground.
Using JTAG for configuration, the MODE pins are not used. Using other programming modes requires the use of the
CFG[2:0] input pins. The CFG [2:0] pins include internal weak internal pull-ups. It is recommended that 1–10 kΩ
external resistors be used when using these sysCONFIG modes. Pull-up resistors should be connected to V .
External resistors are always needed if the configuration signals are being used to handshake with other devices.
Recommended 4.7 kΩ pull-up resistors to V and pull-down to board ground should be used on the following pins:
Table 6.2. Pull-up/Pull-down Recommendations for Configuration Pins
Pin PCB Connection
PROGRAMN 4.7 kΩ pull-up to V
INITN 4.7 kΩ pull-up to V
MCLK/CCLK 510 Ω to 1 kΩ pull-up to V serial resistor placing near TX side.
CSSPIN 4.7 kΩ to 10 kΩ pull-up to V
CFG[2:0] 1 kΩ to 10 kΩ pull-up to V
, 0 = GND. See Table 6.3.
Note:
1. Serial resistor value depends on the PCB design, range from 22 Ω to 80 Ω.
2. Strong pull-up resistor is put close to the SPI flash to get enough margin from the rising edge of CSSPIN.
Table 6.3. Configuration Pins Needed per Programming Mode1
Configuration Bus Dedicated Clock
Shared Pins Dedicated Pins
Mode Size CFG[2:0] Pin I/O
SSPI 1 Bit 001 CCLK Input MISO, MOSI, SI, DOUT, PROGRAMN, INITN, DONE
MSPI2 1 Bit 010 MCLK Output MISO, MOSI, CSSPIN, DOUT PROGRAMN, INITN, DONE
2 Bits D[1:0], CSSPIN, DOUT
4 Bits D[3:0], CSSPIN, DOUT
SCM 1 Bit 101 CCLK Input DI, DOUT PROGRAMN, INITN, DONE
SPCM (Parallel) 8 Bits 111 CCLK Input D[7:0], DOUT, CSON, BUSY, PROGRAMN, INITN, DONE
WRITEN, CSN, CS1N
JTAG 1 Bit xxx TCK Input — TCK, TMS, TDI, TDO
Notes:
1. Leave unused configuration ports open.
2. SPI Quad is not supported on the TQFP144 package.

H O
1.2 V /1.5 V /1.8 V /2.5 V
S T P R O G R A M M E
JT A G
G P IO
/3.3 V
R
4.7 k
1.2 V /1.5 V
/1.8 V
/2.5 V /3.3 V
C C IO 8
TD I
TM S
TD O
TC K
V C C IO 8
D O N E
IN ITN
P R O G R A M N
E C P 5
C F G 2
C F G 1
C F G 0
0 k
S E E T A B L E 6 .3
4.7 k 4.7 k
0 k 0 k
Figure 6.1. Typical Connections for Programming SRAM via JTAG

S P I
1 k
C C IO 8
S N
M C LK /C C LK
D 0/M O S I
D 1/M ISO
S E E T A B L E 6 .3
Figure 6.2. Typical Connections for Programming SRAM via SPI

JT A G
TD I
TM S
TD O
TC K
M C
C S SP IN
LK /C C LK
D 0/M O S I
D 1/M ISO
S E E
1.2 V /1.5 V /1.8 V /2.5 V /3.3 V
1 k
F L A S H
T A B L E 6 .3
1.2 V /1.5 V /1.8 V /2.5 V /3.3 V
Figure 6.3. Typical Connections for Programming external Flash via JTAG

7. External SPI FLASH
The flash voltage should match the V voltage.
It is recommended to use an SPI flash device that is supported in Diamond Programmer. To see the supported list of
devices, go to Diamond Programmer, under the Help menu, choose Help, then search for SPI Flash Support.
For SPI flash devices that are not listed in the SPI Flash Support, using the custom flash option may allow a non-
supported device to work.

8. I/O Pin Assignments
The V provides a quiet supply for the SERDES blocks. For the best jitter performance, careful pin assignment keeps
noisy I/O pins away from sensitive pins. The leading cause of PCB-related SERDES crosstalk is related to FPGA outputs
located in close proximity to the sensitive SERDES power supplies. These supplies require cautious board layout to
ensure noise immunity to the switching noise generated by FPGA outputs. Guidelines are provided to build quiet
filtered supplies for the VCCA; however, robust PCB layout is required to ensure that noise does not infiltrate into these
analog supplies.
Although coupling has been reduced in the device packages of ECP5 and ECP5-5G devices where little crosstalk is
generated, the PCB board can cause significant noise injection from any I/O pin adjacent to SERDES data, reference
clock, and power pins, as well as other critical I/O pins such as clock signals. Electrical Recommendations for Lattice
SERDES (FPGA-TN-02077) provides detailed guidelines for optimizing the hardware to reduce the likelihood of crosstalk
to the analog supplies. PCB traces running in parallel for long distances need careful analysis. Simulate any suspicious
traces using a PCB crosstalk simulation tool to determine if they cause problems.
It is common practice for you to select pinouts for their system very early in the design cycle. For the FPGA designer,
this requires detailed knowledge of the targeted FPGA device. You can use a spreadsheet program to initially capture
the list of the design I/O. Lattice Semiconductor provides detailed pinout information that can be downloaded from the
Lattice Semiconductor website in .csv format for you to use as a resource to create pinout information. For example, by
navigating to the pinout.csv file, you can gather the pinout details for all the different package offerings of the device in
the family, including I/O banking, differential pairing, dual function of the pins, and input and output details.

9. sysI/O
ECP5 and ECP5-5G provide the flexibility to configure each I/O according to user requirements. These pins can be
configured as input, output, and tri-state. Additionally, attributes such as PULLMODE, CLAMP, HYSTERESIS, VREF,
OPENDRAIN, SLEWRATE, DIFFRESISTOR, TERMINATION, and DRIVE STRENGTH can also be setup.
For the PULLMODE, pull-up and pull-down resistors can be set. The implementation of these resistors is by using a
constant current that has the following values:
Table 9.1. Weak pull up/down current specifications
Parameter Condition Min Max Unit
I/O weak pull-up
Pull-up 0 ≤ V IN ≤ 0.7 × V CCIO –30 –150 µA
resistor current
I/O weak pull-down
Pull-down V IL (max) ≤ V IN ≤ V CCIO 30 150 µA
resistor current
ECP5 also provides special I/Os that can be used for high-speed communication. Figure 9.1 and Figure 9.2 show the
sysI/O buffer pair.
TRUE TRUE
Pad Pad
A B The PAD C and PAD D pio
pair have the same
configuration logic as
Clamp Clamp PAD A and PAD B, with
O ICC On
O ICC On t
h
o
e
t
h
a
c
v
p
t i
o
r
u
,
t hey do
differential output
kaeWll p u u P - kaeW nw ll o u d P - )tluafeD( DN G kaeWllu pu P - kaeW nw ll o u d P - )tluafeD( DN G
driver.
Programmable (on, off)
100 Differential
Input Termination
Bank VREF
True Differential Drivers only
on AB Pins
V XUA CC V O ICC V CC + XUA
V XUA CC V O ICC V CC +
XUA
d eoitaR d eoitaR ffiD /feR V V O ICC ES REVIRD V O ICC ffiD no revirD sriaP BA V O ICC ES REVIRD P S T
T
t h
r a o
e t
m
g i v c r e a
i
/ n
D m
i y n
m n
io
a a
m b l i e c d eoitaR d eoitaR ffiD /feR
0/7 /1 0 Ω to
Programmable VCCIO/2
Static/Dynamic
Thevenin
Termination
VCCIO/2
A N I A T U O A ST B T U O B ST B N I
Complementary circuitry located
in I/O logic blocks
Figure 9.1 sysI/O Buffer Pair for Left and Right Sides

XUACC
OICC V CC
deoitaR
ANI
deoitaR
C lam p
O O ff, O n
ICCV
p u ka -l e lu W P
OICC
Pro gram m able
Static/D ynam ic
The ven in
Term ination
V CC IO /2
T RP
ATUO
Ua
d
E
kaeW
AOT
nwod-lluP )tluafeD(
DNG
C om p
T R U E
P a d
B
C lam p
O O ff, O n
ICCV
p u ka -l e lu W P
OICC
BTUO
lem e ntary circuitry lo cated
in I/O lo gic blo cks
kaeW
nwod-lluP
BOT
)tluafeD(
XUACC
T h e P A D C a n d P A D D p
p a ir h a v e th e sam e
co n fig u ratio n lo g ic a s
P A D A a n d P A D B .
DNG
O C I C C V C
Pro gram m able d d
e e Static/D ynam ic o o
i i t t The ven in a a
R R
Term ination
V C CIO /2
BNI
io
Figure 9.2. sysI/O Buffer Pair for Top and Bottom Sides

10. Clock Inputs
The ECP5 and ECP5-5G devices provide certain pins for use as clock inputs in each I/O bank. These pins are shared and
can alternately be used for General Purpose I/O.
However, when these pins are used for clocking purposes, noise needs to be minimized on these pins. Refer to
ECP5 and ECP5-5G High-Speed I/O Interface (FPGA-TN-02035).
These shared clock input pins, typically named GPLL and PCLK, can be found under the Dual Function column of the
pinout csv file located on the Lattice website and in the pin assignment tab of Diamond software’s Spreadsheet View.
High-speed differential interfaces (such as MIPI) being received by the FPGA must route their differential clock pair into
a pair of inputs that support differential clocking, labeled PCLKTx_y (+true) and PCLKCx_y (-complement).
When providing an external reference clock to the FPGA, ensure that the oscillator’s output voltage to the FPGA does
not exceed the bank’s voltage. Good power supply decoupling of the clock oscillator is required to reduce clock jitter.
Figure 10.1 shows a typical bypassing circuit.
3 .3 V (t y p ic a l)
6 0 0 Ω
5 0 0 m A
1 µ F 0 .1 µ F
O
C lo c k
s c illa t o
G N D
T o F P G A
Figure 10.1. Clock Oscillator Bypassing
For differential clock inputs to banks with a V voltage of 1.5 V or lower, it is recommended to use an HCSL oscillator
to keep the clock voltage less than or equal to the bank’s V . An LVDS oscillator can also be used if AC is coupled and
then DC is biased at half the VCCIO voltage. Example dual footprint design supporting HCSL and LVDS is shown below in
Figure 10.2.
FPGA_CLK_IN_P VCCIO
HCSL
OSC DNI
DNI
FPGA_CLK_IN_N
Keep termination parts close together
100 nF FPGA_CLK_IN_P VCCIO
LVDS 2.0 k
OSC
100 nF 100 nF 2.0 k
FPGA_CLK_IN_N
Figure 10.2. PCB Dual Footprint Supporting HCSL and LVDS Oscillators

11. Pinout Considerations
The ECP5 and ECP5-5G devices support many applications with high-speed interfaces. These include various rule-based
pinouts that need to be understood prior to the implementation of the PCB design on these high-speed interfaces. The
pinout selection must be completed with an understanding of the interface building blocks implemented in the FPGA
fabric. These include IOLOGIC blocks such as DDR, clock resource connectivity, and PLL and DLL usage. Refer to
ECP5 and ECP5-5G High-Speed I/O Interface (FPGA-TN-02035) for rules pertaining to these interface types.

12. LVDS Pin Assignments
True LVDS inputs and outputs are available on I/O pins on the left and right sides of the devices. Top and I/O banks do
not support the True LVDS standard but can support emulated LVDS outputs. True LVDS input pairing on the left and
right banks can be found under the Differential column in the pinlist csv file. True LVDS output pairs are available on
any A and B pair of the left and right banks.
Emulated LVDS output is available in pairs around all banks, but this requires external termination resistors. This is
described in the ECP5 and ECP5-5G sysI/O Usage Guide (FPGA-TN-02032).

13. HSUL and SSTL Pin Assignments
The HSUL and SSTL interfaces are referenced I/O standards that require an external reference voltage. The VREF pin(s)
should get high priority when assigning pins to the PCB. These pins can be found in the dual function column with the
V label. Each bank includes a separate V voltage. V sets the threshold for the referenced input buffers. Each
REF1 REF REF1
I/O is individually configurable based on the bank’s supply and reference voltages.

14. LFE5U to LFE5UM/LFE5UM5G and LFE5UM to LFE5UM5G
Migration
Besides migrating design from one device to another device (that is, LFE5U-25 to LFE5U-45) on the same package (that
is, caBGA554) within its own family in LFE5U and LFE5UM/LFE5UM5G, you can migrate from the non-SERDES (LFE5U)
device to the SERDES (LFE5UM) device or from LFE5UM device to THE LFE5UM5G device in the same package.
If you anticipate your design, you may use SERDES at a later time on your product. You can first design and make all the
connections to all SERDES circuits on board.
For example, if you anticipate the need to use the two dual SERDES on the LFE5U-85 product, you have to design your
board with LFE5UM, which contains the SERDES ports, to the not-yet-populated SERDES circuit on the board. This
requires all SERDES power pins to be connected to power sources on the board, with the corresponding pins found on
the LFE5U device. Note that these power pins on the ECP5U devices are required to be connected to GND when
migrating to LFE5UM is not considered, but they need to be connected to SERDES power supplies when future
migration is considered. He can still put in the LFE5U-85 device because the two devices are pin compatible, other than
the SERDES pins and SERDES power supply pins. Also, to be taken into account, ensure the SERDES power supplies are
isolated and implemented with different power rails to minimize any noise injection from other supplies.
When designing the board with LFE5UM and planning for future migration to LFE5UM5G to increase the SERDES
throughput to 5G, care has to be taken that the V /V /V /V need to be powered by a 1.2 V nominal supply
CC CCA CCHRX CCHTX
voltage for LFE5UM5G. Voltage regulators with adjustable voltage between 1.1 V and 1.2 V are needed when selecting
to populate the board with either the LFE5UM or LFE5UM5G devices.
The other consideration to migrate between the LFE5UM and LFE5UM5G devices is to ensure the signal quality of the
Rx and Tx traces, which needs to be good for 5 Gbps operation.
Another consideration when migrating between the LFE5UM and LFE5UM5G devices is that if the reference clock
supply comes from a source that cannot be changed, such as a PCIe slot clock (100 MHz), the clock input to the
LFE5UM5G needs the 2X frequency of this clock source. An external clock generator, such as PLL, needs to be used to
double this clock frequency (to 200 MHz) when used with the LFE5UM5G device.

15. Layout Recommendations
A good design from a schematic should also reflect a good layout for the system design to work without any issues with
noise or power distribution. Below are some of the recommended layouts in general.
1. All power should come from power planes; this is to ensure good power delivery and thermal stability.
2. Each power pin has its own decoupling capacitor, typically 100 nF, that should be placed as close as possible to each
other.
3. The placement of analog circuits must be away from digital circuits or high-switching components.
4. High-speed signals should have a clearance of five times the trace width of other signals.
5. High-speed signals that transition from one layer to another should have a corresponding transition ground if both
reference planes are grounded. If the reference on the other layer is a V plane, then a stitching capacitor should
be used (ground to V ).
Figure 15.1. PCB Layout Recommendation
6. High-speed signals have a corresponding impedance requirement; calculate the necessary trace width and trace
gap (differential gap) according to the desired stack-up. Verify trace dimensions with the PCB vendor.
7. For differential pairs, be sure to match the length as closely as possible. A good rule of thumb is to match up to
± mils.
For further information on layout recommendations, refer to:
• PCB Layout Recommendations for BGA Packages (FPGA-TN-02024)
• PCB Layout Recommendations for Leaded Packages (FPGA-TN-02160)

16. Checklist
Table 16.1. Hardware Checklist
Item OK NA
1 FPGA Power Supplies
1.1 V core at 1.1 V ±5% (LFE5U/LFE5UM), at 1.2 V ± 5% (LFE5UM5G).
1.1.1 Use a PCB plane for V core with proper decoupling.
1.1.2 V core sized to meet power requirement calculation from software.
1.2 All V are between 1.2 V to 3.3 V.
1.2.1 V used with configuration interfaces (that is memory devices). Need to match specifications.
1.2.2 V [1:7] used based on user design.
1.3 V at 2.5 V ±5%.
1.4 Power estimation.
2 SERDES Power Supplies
2.1 V and V connected for used SERDES channels.
CCHRX CCHTX
2.2.1 V are at 1.1 V ±5% (LFE5UM), 1.2 V ±5% (LFE5UM5G).
2.2.2 V are from 0.3 V to 1.1 V +5% (LFE5UM), 0.3 V to 1.2 V +5% (LFE5UM5G).
2.3 V at 1.1 V ±5% (LFE5UM), at 1.2 V ±3% (LFE5UM5G).
2.3.1 V at 2.5 V ±5%.
2.3.2 V quiet and isolated.
2.3.3 V pins should be ganged together, and a solid PCB plane is recommended. This plane should not
have adjacent non-SERDES signals passing above or below. It should also be isolated from the V core
power plane.
2.4 If both DCU are not used, V should be connected, and remaining SERDES power supplies can be left
open.
2.5 If only one channel is used, the un-used DCU’s V should be connected, and remaining SERDES
power supplies can be left open.
2.6 If only one channel is used, the un-used channel within the same DCU’s V and V should be
CCA CCHTX
connected, and remaining SERDES power supplies can be left open.
3 Configuration
3.1 Pull-ups and pull-downs on configuration specific pins.
3.2 V bank voltage matches sysCONFIG peripheral devices such as SPI Flash.
4 SERDES
4.1 Dedicated reference clock input from clock source meets the DC and AC requirements.
4.1.1 External AC coupling caps may be required for compatibility to common-mode levels.
4.1.2 Ref clock termination resistors may be needed for compatible signaling levels.
4.2 Maintain good high-speed transmission line routing.
4.2.1 Continuous ground reference plane to serial channels.
4.2.2 Tightly length matched differential traces.
4.2.3 Do not pass other signals on the PCB above or below the high-speed SERDES without isolation.
4.2.4 Keep non-SERDES signal traces from passing above or below the V power plane without isolation.
5 Special Pin Assignments
5.2 V assignments followed for single-ended SSTL inputs.
REF
5.2.1 Properly decouple the V source.
REF
6 Critical Pinout Selection
6.1 Pinout has been chosen to address FPGA resource connections to I/O logic and clock resources per
ECP5 and ECP5-5G High-Speed I/O Interface (FPGA-TN-02035).
6.2 Shared general purpose I/O are used as inputs for FPGA PLL and Clock inputs.
7 External Flash
7.1 Flash voltage should match V CCIO8 voltage.

Item OK NA
8 JTAG
8.1 Pull-down on TCK. See Table 3.1. Recommended Power Filtering Groups and Components
8.2 Pull-up on TDI, TMS, TDO. See Table 3.1. Recommended Power Filtering Groups and Components
9 LPDDR3 and DDR3 Interface Requirements
9.1 DQ, DM, and DQS signals should be routed in a data group and should have similar routing and
matched via counts. Using more than three vias is not recommended in the route between the FPGA
controller and memory device.
9.2 Maintain a maximum of ±50 mil between any DQ/DM and its associated DQS strobe within a DQ
group. Use careful serpentine routing to meet this requirement.
9.3 All data groups must reference a ground plane within the stack-up.
9.4 DDR trace reference must be solid without slots or breaks. It should be continuous between the FPGA
and the memory.
9.5 Provide a separation of 3 W spacing between a data group and any other unrelated signals to avoid
crosstalk issues. Use a minimum of 2 W spacing between all DDR traces excluding differential CK and
DQS signals. (W is the minimum width of the signal trace allowed.)
9.6 Assigned FPGA I/O within a data group can be swapped to allow clean layout. Do not swap DQS
assignments.
9.7 Differential pair of DQS to DQS_N trace lengths should be matched at ±10 mil.
9.8 Resistor terminations (DQ) placed in a fly-by fashion at the FPGA is highly recommended. Stub fashion
terminations, if used, should not include a stub longer than 600 mil.
9.9 LDQS/LDQS_N and UDQS/UDQS_N trace lengths should be matched within ±100 mil.
9.10 Address/control signals and the associated CK and CK_N differential FPGA clock should be routed with
a control trace matching ±100 mil.
9.11 CK to CK_N trace lengths must be matched to within ±10 mil.
9.12 Address and control signals can be referenced to a power plane if a ground plane is not available.
Ground reference is preferred.
9.13 Address and control signals should be kept on a different routing layer from DQ, DQS, and DM to
isolate crosstalk between the signals.
9.14 Differential terminations used by the CLK/CLKN pair must be located as close as possible to the
memory.
9.15 Address and control terminations placed after the memory component using a fly-by technique are
highly recommended. Stub fashion terminations, if used, should not include a stub longer than 600
mils.
10 Unused SERDES
10.1 See Unused SERDES DCU subsection and Unused SERDES Channel in DCU subsection.
11 Layout Recommendations

References
• ECP5 and ECP5-5G devices web page
• ECP5-5G Family Data Sheet (FPGA-DS-02012)
• ECP5 and ECP5-5G sysCONFIG Usage Guide (FPGA-TN-02039)
• ECP5 and ECP5-5G SERDES/PCS Usage Guide (FPGA-TN-02206)
• ECP5 and ECP5-5G sysI/O Usage Guide (FPGA-TN-02032)
• ECP5 and ECP5-5G sysClock PLL/DLL Design and Usage Guide (FPGA-TN-02200)
• ECP5 and ECP5-5G Memory Usage Guide (FPGA-TN-02204)
• ECP5 and ECP5-5G High-Speed I/O Interface (FPGA-TN-02035)
• Power Consumption and Management for ECP5 and ECP5-5G Devices (FPGA-TN-02210)
• ECP5 and ECP5-5G sysDSP Usage Guide (FPGA-TN-02205)
• Electrical Recommendations for Lattice SERDES (FPGA-TN-02077)
• High-Speed PCB Design Considerations (FPGA-TN-02024)
• Power Decoupling and Bypass Filtering for Programmable Devices (FPGA-TN-02210)
• LatticeSC SERDES Jitter (TN1084)
• Boards, Demos, IP Cores and Reference Designs for ECP5 and ECP5-5G
• Lattice Insight for Lattice Semiconductor training series and learning plans

Technical Support Assistance
Submit a technical support case through www.latticesemi.com/techsupport.
For frequently asked questions, refer to the Lattice Answer Database at www.latticesemi.com/Support/AnswerDatabase.

Revision History
Revision 2.0, July 2024
Section Change Summary
All Minor editorial fixes.
Power Supplies Added the Power Noise and Power Source subsections.
ECP5 and ECP5-5G SERDES/PCS Converted this old subsection under Power Supplies into a new section and reworked
Power Supplies section contents.
Power Sequencing Added this new section.
Clock Inputs Moved this section from Section 5 to Section 10 – Clock Inputs and reworked section
contents.
Power Estimation Converted this old subsection under Power Supplies into a new section.
Configuration Considerations Moved this section from Section 3 to Section 6 – Configuration Considerations and reworked
section contents.
External SPI Flash Added this new section.
I/O Pin Assignments Moved this section from Section 4 to Section 8 – I/O Pin Assignments.
sysI/O Added this new section.
Pinout Considerations Moved this section from Section 6 to Section 11 – Pinout Considerations.
LVDS Pin Assignments Moved this section from Section 7 to Section 12 - LVDS Pin Assignments.
HSUL and SSTL Pin Assignments Moved this section from Section 8 to Section 13 - HSUL and SSTL Pin Assignments.
SERDES Pin Configuration Removed this section.
LFE5U to LFE5UM/LFE5UM5G Moved this section from Section 10 to Section 14 - LFE5U to LFE5UM/LFE5UM5G and
and LFE5UM to LFE5UM5G LFE5UM to LFE5UM5G Migration.
Layout Recommendations Added this new section.
Checklist Added this new section.
Revision 1.9, May 2024
Configuration Considerations Table 3.2. Pull-up/Pull-down Recommendations for Configuration Pins:
• updated PCB Connection for MCLK/CCLK pin;
• newly added Note 2.
Revision 1.8, January 2024
Disclaimers Updated this section.
Inclusive Language Added this section.
Configuration Considerations Added the following note for the MSPI configuration mode in Table 3.3. Configuration Pins
Needed per Programming Mode:
SPI Quad is not supported on the TQFP144 package.
References Added this section.
Revision 1.7, April 2023
Power Supplies Updated the ECP5 and ECP5-5G SERDES/PCS Power Supplies subsection to clarify SERDES
power supply pin connections when a DCU is partially or fully unused.
Technical Support Assistance Added reference to the Lattice Answer Database on the Lattice website.
All • Changed SERDES to SERDES.
• Updated table note style.

Revision 1.6, October 2020
Acronyms in This Document Added this section.
Introduction Added link to LatticeSC SERDES Jitter reference document.
Power Supplies • Updated ECP5 and ECP5-5G SERDES/PCS Power Supplies subsection to add V
instance.
• Added information to elaborate SERDES channels on ECP5 and ECP5-5G device.
Clock Inputs Update content to correct information on clock inputs and clock routing.
SERDES Pin Considerations Updated section content.
LFE5U to LFE5UM/LFE5UM5G Updated Table 10.1 to add row for V instance in section 2.
and LFE5UM to LFE5UM5G
Revision 1.5, August 2020
All Updated the document IDs across the technical note.
Disclaimers Added this section.
Clock Inputs Updated section content.
Revision History Updated format.
Revision 1.4, August 2017
Configuration Considerations Updated Table 3.2 Pull-up/Pull-down Recommendations for Configuration Pins. Corrected
MCLK/CCLK, CFG pull-up/pull-down values. Added CSSPIN pull-up recommendation.
All Removed copyright page.
Revision 1.3, June 2017
All • Changed document number from TN1269 to FPGA-TN-02038.
• Updated document template.
• Changed reference to data sheet from DS1044 to FPGA-DS-02012.
• Clarify descriptions on various sections.
Power Supplies Updated Table 2.1 ECP5 and ECP5-5G FPGA Power Supplies changing CFG[0:2] to CFG[2:0].
Configuration Considerations Updated Table 3.1 JTAG Pin Recommendations correcting the value in Dedicated CFG[2:0]
SSPI Configuration Mode to 001.
Power Supplies Update the Power Supplies section to correct SERDES power supply requirements.
LFE5U to LFE5UM/LFE5UM5G Added more details to the LFE5U to LFE5UM/LFE5UM5G and LFE5UM to LFE5UM5G
and LFE5UM to LFE5UM5G Migration section.
Revision 1.2, December 2015
Power Supplies Updated Power Supplies section. Revised Voltage (Nominal Value) for V , V and V
CCA CCHRX CCHTX
in Table 2.1 ECP5 and ECP5-5G FPGA Power Supplies.
LFE5U to LFE5UM/LFE5UM5G • Updated LFE5U to LFE5UM/LFE5UM5G and LFE5UM to LFE5UM5G Migration section.
and LFE5UM to LFE5UM5G • Removed instances of LFE5U5G.
• Revised items 1.2, 2.3.1 and 4.2.4 in Table 10.1 Hardware Checklist.
All • Changed section title.
• Added new paragraph content.

Revision 1.1, November 2015
Power Supplies Added support for ECP5-5G.
LFE5U to LFE5UM/LFE5UM5G • Changed document title to ECP5 and ECP5-5G Hardware Checklist
and LFE5UM to LFE5UM5G • Changed ECP5U and ECP5UM to LFE5U and LFE5UM.
Configuration Considerations Updated Configuration Considerations section. Revised PCB recommendation for TDI, TMS
and TDO in Table 3.1 JTAG Pin Recommendations.
Technical Support Assistance Updated Technical Support Assistance section.
Revision 1.0, March 2014
All Initial release.
© 2017-2024 Lattice Semiconductor Corp. All Lattice trademarks, registered trademarks, patents, and disclaimers are as listed at www.latticesemi.com/legal.
All other brand or product names are trademarks or registered trademarks of their respective holders. The specifications and information herein are subject to change without notice.
FPGA-TN-02038-2.0 35

www.latticesemi.com
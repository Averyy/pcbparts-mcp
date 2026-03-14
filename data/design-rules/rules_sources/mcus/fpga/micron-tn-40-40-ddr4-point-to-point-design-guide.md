---
source: "Micron TN-40-40 -- DDR4 Point-to-Point Design Guide"
url: "https://www.mouser.com/pdfDocs/Micron_DDR4_Design_Guide.pdf"
format: "PDF 34pp"
method: "pdfplumber"
extracted: 2026-03-02
chars: 63105
---

TN-40-40: DDR4 Point-to-Point Design Guide
Introduction
Technical Note
DDR4 Point-to-Point Design Guide
Introduction
DDR4 memory systems are quite similar to DDR3 memory systems. However, there are
several noticeable and important changes required by DDR4 that directly affect the
board’s design:
• New V supply
PP
• Removed V reference input
REFDQ
• Changed I/O buffer interface from midpoint terminated SSTL to V terminated
DD
pseudo open-drain (POD)
• Added ACT_n control
DDR4 added over 30 new features with a significant number of them offering improved
signaling or debug capabilities: CA parity, multipurpose register, programmable write
preamble, programmable read preamble, read preamble training, write CRC, read DBI,
write DBI, V calibration, and per DRAM addressability. It is beyond the scope of
this document to provide an in-depth explanation of these features; however, a success-
ful DDR4 high-speed design will require the use of these new features and they should
not be overlooked. The Micron DDR4 data sheet provides in-depth explanation of these
features.
As the DRAM’s operating clock rates have steadily increased, doubling with each DDR
technology increment, DRAM training/calibration has gone from being a luxury in DDR
to being an absolute necessity with DDR4. For example, if the required V calibra-
tion and data bus write training were not correctly performed, DDR4 timing specifica-
tions would have to be severely derated; but the issue is moot since the specifications
require V calibration and data bus write training.
The first section of this document highlights some new DDR4 features that can help en-
able a successful board operation and debug. These features offer the potential for im-
proved system performance and increased bandwidth over DDR3 devices for system
designers who are able to properly design around the timing constraints introduced by
this technology. The second section outlines a set of board design rules, providing a
starting point for a board design. And the third section details the calculation process
for determining the portion of the total timing budget allotted to the board intercon-
nect. The intent is that board designers will use the first section to develop a set of gen-
eral rules and then, through simulation, verify their designs in the intended environ-
ment.
The suggestions provided in this technical note mitigating tRC, tRRD, tFAW, tCCD, and
tWTR can help system designers optimize DDR4 for their memory subsystems. For sys-
tem designers who find the increases offered by DDR4 are not enough to provide relief
in their networking subsystems, Micron offers a comprehensive line of memory prod-
ucts specifically designed for the networking space. Contact your Micron representative
for more information on these products.
CCMTD-1725822587-10240 1 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.
Products and specifications discussed herein are for evaluation and reference purposes only and are subject to change by
Micron without notice. Products are only warranted by Micron to meet Micron's production data sheet specifications. All
information discussed herein is provided on an "as is" basis, without warranties of any kind.

DDR4 Overview
DDR4 SDRAM is a high-speed dynamic random-access memory internally configured
as an 8-bank DRAM for the x16 configuration and as a 16-bank DRAM for the x4 and x8
configurations. The device uses an 8n-prefetch architecture to achieve high-speed oper-
ation. The 8n-prefetch architecture is combined with an interface designed to transfer
two data words per clock cycle at the I/O pins.
A single READ or WRITE operation consists of a single 8n-bit wide, four-clock data
transfer at the internal DRAM core and two corresponding n-bit wide, one-half-clock-
cycle data transfers at the I/O pins.
This section describes the key features of DDR4, beginning with Table 1, which com-
pares the clock and data rates, density, burst length, and number of banks for the five
standard DRAM products offered by Micron.The maximum clock rate and minimum
data rate are the operating conditions with DLL enabled or normal operation.
Table 1: Micron's DRAM Products
Clock Rate (tCK) Data Rate Prefetch
(Burst Number
Product Max Min Min Max Density Length) of Banks
SDRAM 10ns 5ns 100 Mb/s 200 Mb/s 64–512Mb 1n 4
DDR 10ns 5ns 200 Mb/s 400 Mb/s 256Mb–1Gb 2n 4
DDR2 5ns 2.5ns 400 Mb/s 800 Mb/s 512Mb–2Gb 4n 4, 8
DDR3 2.5ns 1.25ns 800 Mb/s 1600 Mb/s 1–8Gb 8n 8
DDR4 1.25ns 0.625ns 1600 Mb/s 3200 Mb/s 4–16Gb 8n 8, 16
Density
The JEDEC® standard for DDR4 SDRAM defines densities ranging from 2–16Gb; howev-
er, the industry started production for DDR4 at 4Gb density parts. These higher-density
devices enable system designers to take advantage of more available memory with the
same number of placements, which can help to increase the bandwidth or supported
feature set of a system. It can also enable designers to maintain the same density with
fewer placements, which helps to reduce costs.
Prefetch
As shown in Table 1, prefetch (burst length) doubled from one DRAM family to the next.
With DDR4, however, burst length remains the same as DDR3 (8). (Doubling the burst
length to 16 would result in a x16 device transferring 32 bytes of data on each access,
which is good for transferring large chunks of data but inefficient for transferring small-
er chunks of data.)
Like DDR3, DDR4 offers a burst chop 4 mode (BC4), which is a psuedo-burst length of
four. Write-to-read or read-to-write transitions get a small timing advantage from using
BC4 compared to data masking on the last four bits of a burst length of 8
(BL = 8) access; however, other access patterns do not gain any timing advantage from
this mode.
CCMTD-1725822587-10240 2 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Frequency
The JEDEC DDR4 standard defines clock rates up to 1600 MHz, with data rates up to
3200 Mb/s. Higher clock frequencies translate into the possibility of higher peak band-
width. However, unless the timing constraints decrease at the same percentage as the
clock rate increases, the system may not be able to take advantage of all possible band-
widths. See DRAM Timing Constraints for more information
Error Detection and Data Bus Inversion
Devices that operate at higher clock and data rates make it possible to get more work
done in a given period of time. However, higher frequencies also make it more complex
to send and receive information correctly. As a result, DDR4 devices offer:
• Two built-in error detection modes: cyclic redundancy cycle (CRC) for the data bus
and parity checking for the command and address bits.
• Data bus inversion (DBI) to help improve signal integrity while reducing power con-
sumption.
• Both of these features will most likely be used for development and debug purposes.
CCMTD-1725822587-10240 3 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

CRC Error Detection
CRC error detection provides real-time error detection on the DDR4 data bus, improv-
ing system reliability during WRITE operations. DDR4 uses an 8-bit CRC header error
control: X8+X2+X+1 (ATM-8 HEC). High-level, CRC functions include:
• DRAM generates checksum per write burst, per DQS lane: 8 bits per write burst (CR0–
CR7) and a CRC using 72 bits of data (unallocated transfer bits are 1s).
• DRAM compares against controller checksum; if two checksums do not match,
DRAM flags an error, as shown in the CRC Error Detection figure
• A CRC error sets a flag using the ALERT_n signal (short low pulse; 6–10 clocks)
Figure 1: CRC Error Detection
DRAM controller DRAM
Data Data
CRC engine Data CRC code CRC engine
CRC code CRC code
Compare
CRC
Table 2: CRC Error Detection Coverage
Error Type Detection Capability
Random single-bit errors 100%
Random double-bit errors 100%
Random odd count errors 100%
Random multi-bit UI error detection 100%
(excluding DBI bits)
CCMTD-1725822587-10240 4 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Parity Error Detection
Command/address (CA) parity takes the CA parity signal (PAR) input carrying the parity
bit for the generated address and command signals, and matches it to the internally-
generated parity from the captured address and command signals. High-level, parity er-
ror-detection functions include:
• CA parity provides parity checking of command and address buses: ACT_n, RAS_n,
CAS_n, WE_n and the address bus (Control signals CKE, ODT, CS_n are not checked)
• CA parity uses even parity; the parity bit is chosen so that the total number of 1s in
the transmitted signal—including the parity bit—is even
• The device generates a parity bit and compares with controller-sent parity; if parity is
not correct, the device flags an error as shown in the Command/Address Parity Oper-
ation
• A parity error sets a flag using the ALERT_n signal (long low pulse; 48–144 clocks)
Figure 2: Command/Address Parity Operation
DRAM controller DRAM
Command/address Command/address
Even parity Command/address Even parity
GEN Even parity bit GEN
Even parity bit
Compare
parity
bit
Data Bus Inversion
New to DDR4, the data bus inversion (DBI) feature enables these advantages:
• Supported on x8 and x16 configurations (x4 is not supported)
• Configuration is set per-byte: One DBI_n pin is for x8 configuration; UDBI_n, LDBI_n
pins for x16 configuration
• Shares a common pin with data mask (DM) and TDQS functions; Write DBI cannot be
enabled at the same time the DM function is enabled
• Inverts data bits
• Drives fewer bits LOW (maximum of half of the bits are driven LOW, including the
DBI_n pin)
• Consumes less power (power only consumed by bits that are driven LOW)
• Enables fewer bits switching, which results in less noise and a better data eye
• Applies to both READ and WRITE operations, which can be enabled separately (con-
trolled by MR5)
CCMTD-1725822587-10240 5 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Table 3: DBI Example
Read Write
If more than four bits of a byte lane are LOW: If DBI_n input is LOW, write data is inverted
– Invert output data – Invert data internally before storage
– Drive DBI_n pin LOW
If four or less bits of a byte lane are LOW: If DBI_n input is HIGH, write data is not inverted
– Do not invert output data
– Drive DBI_n pin HIGH
Figure 3: DBI Example
No DBI
Controller Data Bus Memory
DQ0 0 1 0 0 1 1 0 1 0 1 0 0
DQ1 1 1 0 0 0 1 0 1 1 1 0 0
DQ2 0 0 0 0 1 0 0 1 0 0 0 0
DQ3 0 1 1 0 1 1 1 1 0 1 1 0
DQ4 0 1 0 0 1 1 0 1 0 1 0 0
Minimum zeros DBI
DQ5 1 0 1 0 0 0 1 1 1 0 1 0
DQ6 1 1 1 0 0 1 1 1 1 1 1 0
DQ7 0 0 1 0 1 0 1 1 0 0 1 0
DBI_n 0 1 1 0
Number of low bits 5 3 4 8 4 3 4 1
Banks and Bank Grouping
DDR4 supports bank grouping:
• x4/x8 DDR4 devices: four bank groups, each comprised of four sub-banks
• x16 DDR4 devices: two bank groups, each comprised of four sub-banks
CCMTD-1725822587-10240 6 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Figure 4: Bank Groupings—x4 and x8 Configurations
Bank 3 Bank 3 Bank 3 Bank 3
Bank 2 Bank 2 Bank 2 Bank 2
Bank 1 Bank 1 Bank 1 Bank 1
Bank 0 Bank 0 Bank 0 Bank 0
Memory Array Memory Array Memory Array Memory Array
Bank Group 0 Bank Group 1 Bank Group 2 Bank Group 3
CMD/ADDR CMD/ADDR
register
Sense amplifiers Sense amplifiers Sense amplifiers Sense amplifiers
Local I/O gating Local I/O gating Local I/O gating Local I/O gating
Global I/O gating
Data I/O
Figure 5: Bank Groupings—x16 Configuration
Bank 3 Bank 3
Bank 2 Bank 2
Bank 1 Bank 1
Bank 0 Bank 0
Memory Array Memory Array
Bank Group 0 Bank Group 1
CMD/ADDR CMD/ADDR
register
Sense amplifiers Sense amplifiers
Local I/O gating Local I/O gating
Global I/O gating
Data I/O
Bank accesses to a different bank group require less time delay between accesses than
bank accesses within the same bank group. Bank accesses to different bank group can
use the short timing specification between commands, while bank accesses within the
same bank group must use the long timing specifications.
Different timing requirements are supported for accesses within the same bank group
and those between different bank groups:
• Long timings (tCCD_L, tRRD_L, and tWTR_L): bank accesses within the same bank
group
• Short timings (tCCD_S, tRRD_S, tWTR_S ): bank accesses between different bank
groups
CCMTD-1725822587-10240 7 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Figure 6: Bank Group: Short vs. Long Timing
Bank 2 Bank 3 Bank 2 Bank 3
Bank group 0 Bank group 1
Bank 0 Bank 1 Bank 0 Bank 1 Bank 2 Bank 3
Long timings
Short timings
Bank 0 Bank 1
Bank 2 Bank 3 Bank 2 Bank 3
Bank group 2 Bank group 3 Bank group 1
Bank 0 Bank 1 Bank 0 Bank 1
The tables below summarize the differences between DDR3 and DDR4 short and long
bank-to-bank access timings tCCD, tRRD, and tWTR for DDR4-1600 through
DDR4-2400. Refer to the DDR4 data sheet for timings above DDR4-2400. It is recom-
mended the memory system utilize a tCCD_L of 5.8ns; system performance impact is
likely to be negligible, if any. Accommodating a tCCD_L of 5.8ns enables the system to
be backward-compatible as well as facilitate future DRAM timing adjustments.
To maximize system performance, it is important that bank-to-bank accesses are to dif-
ferent bank groups. If bank accessing is not controlled properly, it is possible to get less
performance with a DDR4-based system versus a DDR3-based system.
Table 4: DDR3 vs. DDR4 Bank Group Timings – tCCD
Product Parameter 1600 1866 2133 2400
DDR3 tCCD 4CK 4CK 4CK N/A
DDR4 tCCD_S 4CK 4CK 4CK 4CK
DDR4 tCCD_L 5CK or 6.25ns 5CK or 5.355ns 6CK or 5.355ns 6CK or 5ns
Table 5: DDR3 vs. DDR4 Bank Group Timings – tRRD
DDR3 tRRD (1KB) 4CK or 5ns 4 CK or 5ns 4CK or 5ns N/A
DDR4 tRRD_S (1/2KB, 1KB) 4CK or 5ns 4 CK or 4.2ns 4CK or 3.7ns 4CK or 3.3ns
DDR4 tRRD_L (1/2KB, 1KB) 4CK or 6ns 4CK or 5.3ns 4CK or 5.3ns 4CK or 4.9ns
DDR3 tRRD (2KB) 4CK or 7.5ns 4CK or 6ns 4CK or 6ns N/A
DDR4 tRRD_S (2KB) 4CK or 6ns 4CK or 5.3ns 4CK or 5.3ns 4CK or 5.3ns
DDR4 tRRD_L (2KB) 4CK or 7.5ns 4CK or 6.4ns 4CK or 6.4ns 4CK or 6.4ns
CCMTD-1725822587-10240 8 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Table 6: DDR3 vs. DDR4 Bank Group Timings – tWTR
DDR3 tWTR 4CK or 7.5ns 4CK or 7.5ns 4CK or 7.5ns N/A
DDR4 tWTR_S 2CK or 2.5ns 2CK or 2.5ns 2CK or 2.5ns 2CK or 2.5ns
DDR4 tWTR_L 4CK or 7.5ns 4CK or 7.5ns 4CK or 7.5ns 4CK or 7.5ns
Manufacturing Features
DDR4 has three features that help with manufacturing: Post package repair, multi-
plexed address pins and connectivity test mode.
Post Package Repair (PPR): The Micron DDR4 SDRAM has one additional row available
for repair per bank (16 per x4/x8, eight per x16) even though JEDEC only requires one
additional row be available for repair per bank group (four per x4/x8, two per x16). PPR
enables the end user to replace one suspect row in each bank with one good spare row.
Multiplexed Command Pins: To support higher density devices without adding addi-
tional address pins, DDR4 defined a method to multiplex addresses on the command
pins (RAS, CAS, and WE). The state of the newly-defined command pin (ACT_n) deter-
mines how the pins are used during an ACTIVATE command. High-level multiplexed
command/address pin functions include:
• ACT_n along with CS_n LOW = the input pins RAS_n/A16, CAS_n/A15, and WE_n/A14
used as address pins A16, A15, and A14, respectfully.
• ACT_n HIGH along with CS_n LOW = the input pins RAS_n/A16, CAS_n/A15, and
WE_n/A14 used as command pins RAS_n, CAS_n, and WE_n, respectfully for READ,
WRITE and other commands defined in the command truth table.
Connectivity Test Mode: Connectivity test (CT) mode is similar to boundary scan test-
ing, but is designed to significantly speed up testing of the electrical continuity of pin
interconnections between the DDR4 device and the memory controller on a printed cir-
cuit board.
Designed to work seamlessly with any boundary scan device, CT mode is supported on
all x4, x8, and x16 Micron DDR4 devices. JEDEC specifies CT mode for x4 and x8 devices
and as an optional feature on 8Gb and above devices.
Contrary to other conventional shift register-based boundary scan testing, where test
patterns are shifted in and out of the memory devices serially during each clock, the
DDR4 CT mode allows test patterns to be entered on the test input pins in parallel and
the test results to be extracted from the test output pins of the device in parallel. This
significantly increases the speed of the connectivity check.
When placed in CT mode, the device appears as an asynchronous device to the external
controlling agent. After the input test pattern is applied, the connectivity test results are
available for extraction in parallel at the test output pins after a fixed propagation delay
time
CCMTD-1725822587-10240 9 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Table 7: Connectivity Test Mode Pins
Pin Type (CT Mode) Normal Operation Pin Names
Test Enable TEN
Chip Select CS_n
BA0-1, BG0-1, A0-A9, A10/AP, A11, A12/BC_n, A13, WE_n/A14, CAS_n/A15,
RAS_n/A16, CKE, ACT_n, ODT, CLK_t, CLK_c, Parity
Test Inputs DML_n, DBIL_n, DMU_n/DBIU_n, DM/DBI
ALERT_n
RESET_n
Test Outputs DQ0–DQ15, UDQS_t, UDQS_c, LDQS_t, LDQS_c
Logic Equations
Test input and output pins are related to the following equations, where INV denotes a
logical inversion operation and XOR a logical exclusive OR operation.
MT0 = XOR (A1, A6, PAR)
MT1 = XOR (A8, ALERT_n, A9)
MT2 = XOR (A2, A5, A13)
MT3 = XOR (A0, A7, A11)
MT4 = XOR (CK_c, ODT, CAS_n/A15)
MT5 = XOR (CKE, RAS_n,/A16, A10/AP)
MT6 = XOR (ACT_n, A4, BA1)
MT7 = x16: XOR (DMU_n / DBIU_n , DML_n / DBIL_n, CK_t)
........ = x8: XOR (BG1, DML_n / DBIL_n, CK_t)
....... = x4: XOR (BG1, CK_t)
MT8 = XOR (WE_n / A14, A12 / BC, BA0)
MT9 = XOR (BG0, A3, RESET_n, TEN)
Output Equations for a x16 DDR4 device:
DQ0 = MT0 DQ10 = INV DQ2
DQ1 = MT1 DQ11 = INV DQ3
DQ2 = MT2 DQ12 = INV DQ4
DQ3 = MT3 DQ13 = INV DQ5
DQ4 = MT4 DQ14 = INV DQ6
DQ5 = MT5 DQ15 = INV DQ7
DQ6 = MT6 LDQS_t = MT8
DQ7 = MT7 LDQS_c = MT9
DQ8 = INV DQ0 UDQS_t = INV LDQS_t
DQ9 = INV DQ1 UDQS_c = INV LDQS_c
CCMTD-1725822587-10240 10 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

DDR4 Key Changes
As previously noted, there are at least four important changes in DDR4 that require at-
tention when developing a DDR4 motherboard:
• New V supply
• Removed V reference input
• Changed I/O buffer interface from midpoint terminated SSTL to V terminated
pseudo open-drain (POD)
• Added ACT_n control
V Supply
The V supply was added, which is a 2.5V supply that powers the internal word line.
Adding the V supply facilitated the V transition from 1.5V to 1.2V as well as provi-
PP DD
ded additional power savings, approximately 10%. Although JEDEC does not state I
and I current limits, initial DDR4 parts have demonstrated I current usage in the
PP PP
ranges of a) 2mA to 3mA when in standby mode, b) 3mA to 4mA when in the active
mode, and c) 10mA to 20mA during refresh mode. It is worth keeping in mind these I
values are average currents and actual current draw will be narrow pulses in nature, in
the range of 20mA to 60mA. Failure to provide sufficient power to V will prevent the
DRAM from operating correctly.
CCMTD-1725822587-10240 11 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Figure 7: Ipp Current Profile
V Calibration
The V reference input supply was removed from the package interface and V
REFDQ REFDQ
is now internally generated by the DRAM. This means the V can be set to any value
over a wide range; there is no specific value defined. This means the DRAM controller
must set the DRAM’s V settings to the proper value; thus, the need for V cali-
bration.
JEDEC does not provide a specific routine on how to perform V calibration; how-
ever, JEDEC states allowed commands and how to enter and exit the mode. Each system
will need to determine the routine to implement that provides it the best performance.
Although not to be construed as a detailed explanation of V calibration process
and the most optimum methodology to employ when implementing V calibra-
tion, a general overview of how to look at the process is provided as a preview to a de-
tailed studying of the DDR4 device specifications.
CCMTD-1725822587-10240 12 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

V Calibration Settings: The V can be set to either range 1 (between 60% and
92.5% of V ) or range 2 (between 40% and 77.5% of V ). Range 1 was defined with
DDQ DDQ
the intent of providing the choice range for module-based systems, while range 2 was
defined with the intent of providing the choice range for point-to-point-based systems.
Once the range is set, the internal V can be adjusted in 0.65% V ticks. Although
REF DDQ
there are specifications on tolerance of range settings, in reality these are of minimal in-
terest when performing V calibration, as a specific value is not what is sought but
rather the setting that provides the most optimum performance. Additionally, when us-
ing per DRAM addressability each DRAM may have a unique setting for its internal
V .
V Calibration Script: The following script is a reasonable platform to develop a
V calibration routine around:
• Entering V calibration
• If range 1 then MR6 [7:6] 10* MR6 [5:0] XXXXXXX
• If range 2 then MR6 [7:6] 11* MR6 [5:0] XXXXXXX
– Legal commands while in V calibration mode: ACT, WR, WRA, RD, RDA, PRE,
DES, and MRS ** to set V values and exit V calibration mode
– Subsequent V cal MR commands are MR6 [7:6] 10/1* MR6 [5:0] VVVVVV
• To exit V calibration, the last two V calibration MR commands are:
– MR6 [7:6] 10/1* MR6 [5:0] VVVVVV’ note VVVVV’ = desired value for V
– MR6 [7:6] 00/1* MR6 [5:0] VVVVVV’ note exit V DRAM must be in idle state
when exiting
*Range may only be set/changed when entering V calibration mode; changing
range while in or exiting V calibration mode is illegal.
V Calibration Requirements: The goal is to find the best V setting that sets
the internal V level to be the same as the DRAM’s V level. Essential-
REFDQ CENT_DQ(pin mid)
ly, this requires the calibration process to determine what setting provides the largest
optimal level for a DQ and lowest optimal level for a DQ for a given DRAM and use the
setting half-way in between, as shown below.
Figure 8: V with V
REFDQ CENT_DQ(pin mid)
DQx DQy DQz
(smallest V REFDQ Level) (largest V REFDQ Level)
V CENTDQx V CENTDQz
V
CENTDQ,midpoint
V
CENTDQy
V variation
REF
(component)
V Calibration Discussion: The following example is not to construe that there is a
possible relaxation of the requirement that V calibration must be performed on
each DRAM; rather, to show how much error can be induced if V calibration is not
performed for each DRAM individually.
CCMTD-1725822587-10240 13 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

The first step is to determine the theoretical ideal V . This is based on the
CENT_DQ
DRAM’s ODT termination value used and the DRAM controller’s driver impedance.
Let's assume V = 1.2V, the controller’s R = 34W, and the DRAM’s ODT = 60W. This
DDQ ON
would make a LOW at 434mV and thereby want the internal V set half way, which is
434mV+(1.2V - 434mV)/2 or 816mV, and is achieved setting the V setting at 0.68
V , as shown below.
DDQ
Figure 9: Theoretical V
CENT_DQ(pin mid)
V V
V = 1.2V
R = 34Ω ODT
ON
ODT = 64Ω
Initial MR6 setting = 0.68 V
= 816mV RXer
Vx
R ON V REFDQ
(internal)
At this point, if the V register is set to 0.68 × V , then the V internal input is
REFDQ DDQ REF
set to 816mV; however, V is left undefined. That is, without full calibra-
tion, V is not the same as the programmed value for V . Although
CENT_DQ(pin mid) REFDQ
undefined in the JEDEC specifications (since the condition is not allowed), setting the
V setting at its theoretical ideal setting alone will only have the V program-
med value within about ±7.5% of the correct V setting.
If subsequent reads and writes are performed to a rank of DRAMs at the same time
when determining the largest and smallest V values, the final V program-
CENT_DQ REFDQ
med value will be within about ±4.0% of the correct V setting. However, if
subsequent reads and writes are performed to a specific DRAM when determining the
largest and smallest V values, the final V programmed value will then be
CENT_DQ REFDQ
the correct V setting.
CCMTD-1725822587-10240 14 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Figure 10: V Ranges
Initial MR6 setting Only rank Per DRAM
No V calibration V calibration V calibration
REFDQ REFDQ REFDQ
1200
1100
1000
900
±7.5% ±4%
mV 800 error error
700
600
500
400
60Ω 60Ω 60Ω
ODT setting ODT setting ODT setting
POD I/O Buffers
The I/O buffer has been converted from push-pull to pseudo open drain (POD), as seen
in the figure below. By being terminated to V instead of 1/2 of V , the size of and
center of the signal swing can be custom-tailored to each design’s need. POD enables
reduced switching current when driving data since only 0s consume power, and addi-
tional switching current savings can be realized with DBI enabled. An additional benefit
with DBI enabled is a reduction in crosstalk resulting in a larger data-eye.
Figure 11: DDR4 I/O Buffer vs. DDR3 I/O Buffer
DDR3 – Push-Pull DDR4 – Pseudo Open Drain
Driver Channel Driver Channel
Receiver
Receiver
ACT_n Control
To help alleviate the demand for allocating pins after adding so many new features,
DDR4 has for the first time multiplexed some of its address pins. The ACT_n determines
whether RAS_n/A16, CAS_n/A15, and WE_n/A14 are to be treated as control pins or as
address pins. As the nomenclature might suggest, ACT_n is an Active control when reg-
CCMTD-1725822587-10240 15 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Command Bus and Address Bus Options
istered LOW; Activates are for latching the row address, which means when ACT_n is
LOW, the three inputs RAS_n/A16, CAS_n/A15, and WE_n/A14 are treated as A16, A15,
and A14, respectively. Conversely, when ACT_n is HIGH, the three inputs RAS_n/A16,
CAS_n/A15, and WE_n/A14 are treated as RAS_n, CAS_n, and WE_n, respectively.
Command Bus and Address Bus Options
Two options are available for the command bus and address bus, each providing the fol-
lowing advantages and disadvantages:
Table 8: Bus Options
Advantages and Disadvantages
Bus Characteristics Tree Bus Daisy Chain Bus
Routing Difficult Easy
Performance Excellent, but offers low bandwidth Good, but offers high bandwidth
Load handling Difficult and sensitive to large loads Easy and unaffected by large loads
Timing skews Minimal issues Issues require leveling
For more details about command and address bus, see the DDR3 Point-to-Point Design
Support technical note (TN 41-13) available on micron.com.
DDR4 Layout and Design Considerations
Layout is one of the key elements of a successfully designed application. The following
sections provide guidance on the most important factors of layout so that if trade-offs
need to be considered, they may be implemented appropriately.
Decoupling
Micron DRAM has on-die capacitance for the core as well as the I/O. It is not necessary
to allocate a capacitor for every pin pair (V :V , V :V ); however, basic decou-
DD SS DDQ SSQ
pling is imperative.
Decoupling prevents the voltage supply from dropping when the DRAM core requires
current, as with a refresh, read, or write. It also provides current during reads for the
output drivers. The core requirements tend to be lower frequency. The output drivers
tend to have higher frequency demands. This means that the DRAM core requires the
decoupling to have larger values, and the output drivers want low inductance in the de-
coupling path but not a significant amount of capacitance.
One recommendation is to place enough capacitance around the DRAM device to sup-
ply the core and to place capacitance near the output drivers for the I/O. This is accom-
plished by placing four capacitors around the device on each corner of the package.
Place one of the capacitors centered in each quarter of the ball grid, or as close as possi-
ble (see Decoupling Placement Recommendations Figure 12). Place these capacitors as
close to the device as practical with the vias located to the device side of the capacitor.
For these applications, the capacitors placed on both sides of the card in the I/O area
may be optimized for specific purposes. The larger value primarily supports the DRAM
core, and a smaller value with lower inductance primarily supports I/O. The smaller val-
ue should be sized to provide maximum benefit near the maximum data frequency.
CCMTD-1725822587-10240 16 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Figure 12: Decoupling Placement Recommendations
Note: 1. VDD= purple, VSS = green
Table 9: Decoupling Guidance
Pin Description
V 25uF of capacitance can be provided for each DRAM device placement. Small-value capacitors with more place-
ments are preferred because they can be placed physically closer to the DRAM device, therefore, decoupling
more of the routing. Additionally, smaller capacitors contain lower ESL/inductance and do not counteract the de-
sired high-pass filter as with some larger capacitors. Capacitors can be shared between device placements, mean-
ing that the capacitors between the devices can be counted as total decoupling for the device on either side of
the capacitor. These guidelines can apply to SDP, DDP, and 3DS DRAM packages.
V 3uF of capacitance can be provided for each DRAM device placement. Small 1.0uF capacitors placed near the V
PP PP
pins of the device may be sufficient to satisfy high-frequency current requirements.
V A minimum of one 1.0uF capacitor must be used for every two termination resistors on the CA bus.
TT
V One 0.1uF capacitor per DRAM device may be connected between V and ground or V depending on
REFCA REFCA DD
CMD/ADR/CTRL/CK reference. V is referenced to V on DRAM modules designed to JEDEC specifications.
REFCA DD
V does not consume power, so these capacitors provide AC decoupling rather than bulk decoupling.
REFCA
Power Vias and Sharing
A DRAM device has five supply pin types: V and V (power the core), V and V
DD SS DDQ SSQ
(present only for the output drivers), and V . The substrate for the device typically
maintains isolation from the package balls all the way to the die where isolation is also
maintained. This isolation is intended to keep I/O noise off of the core supply and core
CCMTD-1725822587-10240 17 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

noise off of the I/O drivers. It is good practice, but not an absolute requirement, to use
separate vias for V and V as well as for V and V .
SS SSQ DD DDQ
There is a compromise position. Where a via connects to a V ball on one side of the
SS
card and a V ball on the other side of the card, the actual path being shared is mini-
SSQ
mized.
The path from the planes to the DRAM balls is important. Providing good, low induc-
tance paths provides the best margin. Therefore, separate vias where possible and pro-
vide as wide of a trace from the via to the DRAM ball as the design permits.
Where there is concern and sufficient room, multiple vias are a possibility. This is gener-
ally applied at the decoupling cap to make a low impedance connection to the planes.
Return Path
If anything is overlooked, it will be the current return path. This is most important for
terminated signals (parallel termination) since the current flowing through the termina-
tion and back to the source involves higher currents. No board-level (2D) simulators
take this into account. They assume perfect return paths. Most simulators interpret that
an adjacent layer described as a plane is the perfect return path whether it is related to
the signal or not. Some board simulators take into account plane boundaries and gaps
in the plane to a degree. A 3D simulator is required to take into account the correct re-
turn path. These are generally not appropriate for most applications.
Most of the issues with the return path are discovered with visual inspection. The cur-
rent return path is the path of least resistance. This may vary with frequency, so resist-
ance alone may be a good indicator.
Trace Length Matching
Prior to designing the card, it is useful to decide how much of the timing budget to allo-
cate to routing mismatch. This can be determined by thinking in terms of time or as a
percentage of the clock period. For example, 1% (±0.5%) at 800 MHz clock is 6.25ps
(1250ps/200). Typical flight times for FR4 PCB are near 6.5 ps/mm. So matching to
±1mm (±0.040 inch) allocates 1% of the clock period to route matching. Selecting 1mm
is completely arbitrary. If the design is not likely to push the design limits, a larger num-
ber can be allocated.
When the design has unknowns, it is important to select a tighter matching approach.
Using this approach is not difficult and allows as much margin as is conveniently availa-
ble to allocate to the unknowns.
Address
For the address, the design will likely use a tree topology with branching. Making the
branches uneven causes some signal integrity issues. For this reason, make all related
branches match to within 1mm within each net. Different nets may have different
branch lengths as long as they are matched within a branch. This is somewhat arbitrary,
but there are many cases to consider, and 1mm should be adequate for all cases. There
may be some exceptions.
CCMTD-1725822587-10240 18 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Data Bus
For DQ, the topology is point-to-point or point-to-two-points where the two points are
close together. For the data bus, the bit rate is the period of interest; that is, 625ps for an
800 MHz clock. Because 1% of this interval is 6.25ps, if the matching is held to a range of
1% (±0.5%), then ±0.5mm is the limit. Again, this is arbitrary.
Other factors to account for are vias, differences in propagation time for routing on in-
ner layers versus outer layers, and load differences.
Propagation Delay
Propagation delay for inner layers and outer layers is different because the effective die-
lectric constant is different. The dielectric constant for the inner layer is defined by the
glass and resin of the PCB. Outer layers have a mix of materials with different dielectric
constants. Generally, the materials are the glass and resin of the PCB, the solder mask
that is on the surface, and the air that is above the solder mask. This defines the effec-
tive dielectric for the outer layers and usually amounts to a 10% decrease in propaga-
tion delay for traces on the outer layers. For the design of JEDEC UDIMMs, a 10% differ-
ence accounts for the differences in propagation of the inner layers versus the outer lay-
ers. If all traces that need to match are routed with the same percentage on the outer
layers versus the inner layers, this difference may be ignored for the purpose of match-
ing timing. Otherwise, this difference should be accounted for in any delay or matching
calculations.
For inner layer propagation, velocity is about 6.5 ps/mm. To match all traces within
10ps, traces must be held within a range of 1.5mm, 60 mils. In most cases, this can be
easily achieved. Most designs tolerate a much greater variation and still have significant
margin. The engineer must decide how much of the timing budget is allocated to trace
matching.
Vias
In most cases, the number of vias in matched lines should be the same. If this is not the
case, the degree of mismatch should be held to a minimum. Vias represent additional
length in the Z direction. The actual length of a via depends on the starting and ending
layers of the current flow. Because all vias are not the same, one value of delay for all
vias is not possible. Inductance and capacitance cause additional delay beyond the de-
lay associated with the length of the via. The inductance and capacitance vary depend-
ing on the starting and ending layers. This is either complex or labor-intensive and is
the reason for trying to match the number of vias across all matched lines. Vias can be
ignored if they are all the same. A maximum value for delay through a via to consider is
20ps. This number includes a delay based on the Z axis and time allocated to the LC de-
lay. Use a more refined number if available; this generally requires a 3D solver.
Timing Budget
Suggested practice is to look at the design from a timing budget standpoint to provide
flexibility in the routing portion of the design, if there is suitable margin. This starts with
simulation. By referencing the eye diagrams in this document, a setup and hold time
can be established. From here, the parameters not included in the simulation must be
added.
CCMTD-1725822587-10240 19 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Typical routing for DDR4 components requires two internal signal layers, two surface
signal layers, and four other layers ( 2 V and 2 V ) as solid reference planes.
DD SS
DDR4 memories have V and V pins, which are both typically tied to the PCB V
DD DDQ DD
plane. Likewise, component V and V pins are tied to the PCB V plane. Each plane
SS SSQ SS
provides a low-impedance path to the memory devices to deliver V . Sharing a single
SSQ
plane for both power and ground does not provide strong signal referencing. With care-
ful design, it is possible for a split-plane design to work adequately:
• Designs should continuously reference data bus signals to V .
• CA bus and clock may reference either V or V and should be continuous.
DD SS
• Signals should never reference V .
CCMTD-1725822587-10240 20 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Drive Strength and Calibration
Matching the driver to the transmission line eliminates reflections that return to the
driver to provide cleaner edges and a more open eye. See the DDR3 Point-to-Point De-
sign Support technical note (TN 41-13) available on micron.com to learn the effects of
mismatching a driver to the transmission line.
• DDR4 drive strengths: 48Ω and 34Ω
• Micron drive strength: 40Ω
Data Bus Topology
The improvements in the controller are reduced skew, improved setup and hold, im-
proved package parasitic, improved calibration, and added adjustment and training
features. Not all controllers have these features.
Improvements in the DRAM device are reduced skew, reduced setup and hold, im-
proved package parasitic, improved calibration, and improved support for training.
The terminations are on-die, either in the controller or the DRAM device, with a termi-
nation resistance near the transmission line impedance.
Signal Optimization
• If the PCB is designed with multiple power planes on the same layer of the PCB, avoid
routing traces on adjacent layers across the splits on the voltage plane.
• Source DRAM power from a separate power supply rather than sharing power rails
with other sub-systems of the design. This will limit the number of outputs on a sup-
ply and reduce the potential for ground bounce and other signal integrity issues
caused by simultaneously switching outputs (SSO).
• Add low-pass V filtering on the controller to improve noise margin.
• Minimize V noise using spacing techniques like those recommended for signals
implementing V . Maintain a single reference (either ground or V ) between the
decoupling capacitor and the DRAM V pin. Do not reference some V pins
REFCA REFCA
to V and others to ground. JEDEC Raw Card designs decouple to V .
DD DD
• Minimize inter-symbol interference (ISI or unwanted signal distortion) by matching
driver impedance with trace impedance.
• Minimize crosstalk by isolating sensitive bits, such as strobes, by maintaining the
same reference plane along the signal path for effective current return. Avoid discon-
tinuous or broken reference planes. Provide adequate spacing adjacent to the sensi-
tive signal paths.
CCMTD-1725822587-10240 21 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Simulations
For a new or revised design, Micron strongly recommends simulating I/O performance
at regular intervals (pre- and post- layout for example). Optimizing an interface through
simulation can help decrease noise and increase timing margins before building proto-
types. Issues are often resolved more easily when found in simulation, as opposed to
those found later that require expensive and time-consuming board redesigns or facto-
ry recalls.
Micron has created many types of simulation models to match the different tools in use.
Component simulation models currently on micron.com include IBIS, Verilog, and
Hspice. Verifying all simulated conditions is impractical, but there are a few key areas to
focus on: DC levels, signal slew rates, undershoot, overshoot, ringing, and waveform
shape.
Also, it is extremely important to verify that the design has sufficient signal-eye open-
ings to meet both timing and AC input voltage levels. For additional general informa-
tion on the simulation process see the DDR4 SDRAM Point-to-Point Simulation Process
technical note (TN 46-11) available on micron.com.
DDR4 Subsystem Attributes and Assumptions
Table 10: DDR4 Bus
Subsystem Component Name Description
Physical Bus
Data DQ/DQS/DM 3200 Mb/s (DDR)
Command/Address CA 1600 Mb/s (SDR)
Clock CK/CK# 1600 MHz
Bus Operations
READ READ –
WRITE WRITE –
Data Bus Topology
Configuration Point-to-point –
Trace Mean length 5, 15, 25, 35, 45, and 60mm
Width (min) ~0.1mm for Zo ~40Ω to 50Ω
Spacing (min) ~0.2mm with a dialectric thickness of 0.08mm (3 mils)
for Zo ~40Ω to 50Ω
PCB Stackup, 8-layer (4 signals) Target: Zo ~45Ω to 55Ω (FR4)
CCMTD-1725822587-10240 22 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Simulation Setup and Models
• Physical bus: Data at 3200 Mb/s DDR
• Bus operation: Read
• Configuration: Point to 1 Point
• PCB model: Hspice frequency dependent W-element model with 10 coupled lines
• PCB target impedance: 50Ω ±10%
• Controller input capacitance load: 1.5pF (value from Controller IBIS model from
MTK)
• Byte simulated: DQ0, DQ1,….DQ7, DQS0/DQS0# which has highest package crosstalk
• Eye measurement method: Aperture DC window ( V ±50mV) with V centering
REF REF
• Pass/Fail criteria: Aperture DC ≥70% UI, voltage margin ≥100mV, overshoot ≤200mV
Typical Configuration
Figure 13: Typical 2GB x 4 Configuration
DDR4 DDR4
4Gb x 8 4Gb x 8
SoC
DDR4 DDR4
4Gb x 8 4Gb x 8
CCMTD-1725822587-10240 23 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

2GB DDR4 Read-Only Subsystem
Figure 14: Data Bus – ~4 DQ Channels of x8 per Component (1 Rank [CS] per Channel)
SoC DDR4 SDP
Read CS0 Read CS2
Read CS1 Read CS3
PCB Stackup
Figure 15: PCB Stackup – Example of 8 Layers (4 Signal, 4 Power Planes)
Signal (microstrips) 1
0V plane 2
Power plane 3
Signal (offset striplines)
4
PCB center line
Signal (offset striplines) 5
Power plane 6
0V plane
7
Signal (microstrips) 8
CCMTD-1725822587-10240 24 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Eye Diagrams With DRAM R = 48Ω, Controller ODT = 120Ω
Figure 16: MB Length = 5mm
Figure 17: MB Length = 10mm
Figure 18: MB Length = 20mm
CCMTD-1725822587-10240 25 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Figure 19: MB Length = 30mm
Figure 20: MB Length = 40mm
Figure 21: MB Length = 50mm
CCMTD-1725822587-10240 26 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Data Read R and ODT Recommendations
Table 11: Recommendations- DRAM Driver Impedance and Controller ODT Settings
DRAM Controller Package-Z Mother Memory
(Driver) R ODT V Memory Controller Board Z PVT
ON DDQ
Mother Board Length: 5 to 10mm
34 34, 40, 48, 60, 80, 120 1.26 54 54 55 Slow
40 34, 40, 48, 60, 80, 120, 240 1.26 54 54 55 Slow
48 34, 40, 48, 60, 80, 120, 240, Off 1.26 54 54 55 Slow
Mother Board Length: 11 to 20mm
Mother Board Length: 21 to 30mm
Mother Board Length: 31 to 40mm
Mother Board Length: 41 to 50mm
Mother Board Length: 51 to 60mm
Notes: 1. Passing criteria: Aperture DC >= 70%; Voltage margin >= 100mV; Overshoot <= 200mV.
2. Based on simulation optimum signal integrity is achieved with controller ODT of 34Ω,
40Ω, 48Ω, 60Ω, or 80Ω.
3. Controller ODT of 120Ω, 240Ω, or Off yields acceptable signal integrity with recommen-
ded drive strength; therefore, these controllers are recommended in case the weaker
ODT is beneficial, such as in the need to minimize power consumption.
CCMTD-1725822587-10240 27 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

4-Layer Design Recommendations
4-Layer Design Recommendations
Figure 22: PCB Stackup—Example of 4 Layers
Signal (microstrips) 1
OV plane 2
Power plane 3
Signal (microstrips) 4
• All high-speed nets (DQ/DM/DQS, Address/Command, Control, Clock) should re-
main on the same reference plane (either power or ground), all the way from the
DRAM pin to the controller pin.
• To help eliminate crosstalk due to vias, place the reference via (power or ground) next
to each high-speed via that transitions to another layer.
• The clock pair should keep the same reference plane, all the way from the controller
pins to the DRAM pins.
• Place decoupling capacitors as close as possible to the device.
• Perform signal integrity simulation to optimize Address/Command, Clock,
DQ/DM/DQS termination and drive strength.
• Perform simulation to optimize on-board decoupling capacitor placement and val-
ues.
• To reduce power impedance at lower frequency, add more capacitors (two capacitors
for each 4 signals is recommended).
• To reduce power impedance at higher frequency, make the V plane tightly coupled
to the ground plane and as large as possible.
• To reduce current and V noise, reduce the controller's drive strength and increase
termination resistor values while adhering to Address/Command bus timing specifi-
cations.
CCMTD-1725822587-10240 28 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Pin Connection Guidance
The following table provides general guidance for the connection of each ball of the
DRAM to the controller. Some balls are not required depending on the design. It is up to
the designer to ensure all the necessary connections are made.
Table 12: Pin Details
Pin Type If Unused If Connected
DM_n I/O x4 DRAM designs: Ensure DM, DBI, and TDQS x4 DRAM designs: Not used
DBI_n are disabled in mode registers and pins are left-
TDQS_t floating. x4 DRAM devices do not use DBI, DM,
LDM_n or TDQS.
LDBI_n x8 DRAM designs: DM, DBI, and TDQS can be x8 DRAM designs: May be connected directly
used on x8 DDR4 DRAM; however, when audit- to the controller. Series R may not be needed.1
ing mode register commands via logic analyzer,
Note: TDQS_t and TDQS_c are only used on x8
Micron has not seen these features used by pop-
devices.
ular controllers. The customer should make their
own determination of the controller's use of
these features. TDQS is often utilized when x4-
and x8-based DIMMs are mixed in a channel. For
a memory-down solution, it is unlikely that
TDQS would be needed. In that case DM, DBI,
TDQS modes should be disabled in the appropri-
ate mode registers and this pin should be left to
float along with TDQS_c. If x4 and x8 devices
are to be mixed in the same channel, TDQS_t
and TDQS_c must be connected and enabled in
mode registers as outlined in the specification.
x16 DRAM designs: UDM_n, LDM_n, UDBI_n, x16 DRAM designs: May be connected directly
and LDBI_n can be utilized on x16 devices. DBI to the controller. Series R may not be needed.1
and DM are not typically used by popular DDR4
memory controllers, as mentioned in the cell
above. Ensure that these modes are disabled in
mode registers and that the pins are left float-
ing.
TDQS_c Output Float if TDQS feature is disabled. TDQS_t and TDQS_c are only used on x8 devices.
PAR Input If the CA parity feature is not used, disable it via If CA parity feature is used, terminate through
MR5 and float pin. 33-39 or 47Ω resistor to V .
TEN Input If the TEN feature is not used, connect directly If the TEN feature is used, connect the pin to
to ground. ground through a 1000Ω pull-down resistor.
CCMTD-1725822587-10240 29 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Table 12: Pin Details (Continued)
ALERT_n Output If CA parity, write CRC and connectivity test If CA parity and write CRC or a connectivity test
modes are not used, ALERT_n may float. Write is used, the ALERT_n pin must be pulled high
CRC should be disabled in MR2 and CA parity through a pull-up resistor. A first-order evalua-
should be disabled in MR5. The TEN pin should tion of the required pull-up resistor value can
be connected directly to ground. be determined based on V ,max of the device
IL
monitoring the ALERT_n pin and the amount of
sinking current at V ,max (available from
IL
ALERT_n curves in the IBIS model for the DRAM
device). ALERT_n is an open-drain output. Multi-
ple devices can be connected together with a
pull-up at the end. When the DRAM device is in
connectivity test mode (TEN), ALERT_n is an in-
put, and test program controller must also be
able to drive this pull-up (as an input, TEN is
CMOS 20%/80%).
ODT Input For a single-rank point-to-point design, the ODT For a multi-rank design, a more complicated
pin may not be necessary. RTT_WR may be suffi- ODT scheme may be needed to use the ODT pin.
cient and will provide termination as set in MR2 Connect ODT balls through 33-39 or 47Ω resistor
during writes regardless of ODT pin status. The to V . See address line recommendations.
ODT pin may float and RTT_nom and RTT_park
can be disabled in MR1 and MR5 respectively.
DQ I/O Unused DQ should be allowed to float. If only See Note 1.
one of two bytes of a x16 device is used, assign
the lower byte for data transfers and allow the
upper byte to float.
DQS I/O Must be connected See Note 1.
UDQS_t I/O The only time a DQS strobe (true and compli- See Note 1.
UDQS_c ment) should not be used is when the upper
byte of a x16 device is not used. When the up-
per DQS strobe is not used, the UDQS_t should
be connected to either V or V / V via a
DDQ SS SSQ
resistor in the 200Ω range. The UDQS_c should
be connected to the opposite rail via a resistor
in the same 200Ω range.
UDM_n Input x16 DRAM designs only: UDM_n, LDM_n, UD- -
UDBI_n I/O BI_n, and LDBI_n can be used on x16 devices.
DBI and DM are not typically used by Intel and
AMD, as mentioned above. Ensure that these
modes are disabled in mode registers and that
the pins are left floating.
C0/CKE1 Input These pins are not used on single-die package For dual-die package (DDP) devices, use
C1/CS1_n (SDP) devices and can be left to float. CKE1,CS1_n, and ODT1 as directed by the data
C2/ODT1 sheet. For 3DS-2H, use C0 and float C1 and C2.
For 3DS-4H, use C0 and C1 and float C2. For
3DS-8H, use C0, C1, and C2. Terminate through
33-39 or 47Ω resistor to V . See address.
CCMTD-1725822587-10240 30 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Table 12: Pin Details (Continued)
RESET_n Input N/A RESET_n must be maintained at 0.2 x V while
power rails ramp up; therefore, RESET_n must
be tied to V through a pull-down resistor.
LDQS I/O x16 DRAM designs only: LDQS_t and LDQS_c -
are only available on x16 devices and should al-
ways be connected.
V Supply V should be generated via a voltage divider -
REFCA REFCA
rather than a termination regulator. Although
using a termination regulator may be adequate,
a voltage divider on V ensures that any
change in V is met with the same change in
V .
Address Input N/A Each address line in a multi-device configuration
RAS should use fly-by routing with series termina-
CAS tion to V at the end of the net. Termination
WE resistor values between 30-39 or 47Ω should be
CS_n adequate. If lower or higher values occur, Mi-
BA cron requires the customer to simulate the
BG method used to obtain that value to ensure op-
ACT_n timum termination.
CKE
CK_t Input N/A If simulations determine that AC termination is
CK_c needed, terminate CK_t and CK_c through ap-
proximately 36Ω series resistors and a .01uF ca-
pacitor to V . A single approximately 36Ω resis-
tor in parallel across CK_t and CK_c may also be
adequate.
ZQ Reference Must be connected Must be connected to an external 240Ω ±1% re-
sistor
Note: 1. Series resistors on DQ and DQS are meant to dampen reflections due to channel stubs.
• If a single DRAM device is on a DQ, no series resistor is required.
• If two DRAM devices are mounted in alignment with balls facing each other on oppo-
site sides of a PCB, the via is adjacent to the DQ pin and the mirrored DQ pin of the
secondary side. A series resistor may not be required.
• If two devices are adjacent on the same side of a PCB, the DQ should be a T topology
where the length from "T" to the via at the DRAM pin is matched to each side. A ser-
ies resistor may not be required because the stub should be relatively short.
– If the stubs from the split are long or of different length, simulations must be per-
formed to quantify data eyes at the controller and DRAM device in order to deter-
mine the necessity of termination and the values of the resistors.
CCMTD-1725822587-10240 31 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

JEDEC DDP – Single Rank x16
A DDP composed of two x8s in a single rank improves the internal timing performance
of the x16 configuration device. Some pins differ between the SDP and the DDP pack-
ages, but board design recommendations below support both SDP and DDP devices.
Figure 23: Device Performance – Two ×8s in a Board Space of One ×16
Byte 1
(×× Meg ×8, ×16 Banks)
Byte 0
(×× Meg ×8, ×16 Banks)
CS_n CK_t
UDM_n/ UZQ RAS_n/A16 BG[1:0] CK_c LZQ LDM_n/
UDBI_n CAS_n/A15 BA[1:0] CKE LDBI_n
WE_n/A14 A[13:0] ODT
UDQ[7:0] ACT_n TEN LDQ[7:0]
UDQS_t PAR RESET_n LDQS_t
UDQS_c V ALERT_n LDQS_c
Table 13: JEDEC ×16 DDP Pin-Out
DDP and SDP Symbols DDP and SDP Symbols DDP Symbols (x16) SDP Symbols (x16)
Pin 1 2 3 4 5 6 Pin 7 8 9 7 8 9
A V V UDQ0 – – – A UDQS_c V V UDQS_c V V
DDQ SSQ SSQ DDQ SSQ DDQ
B V V V – – – B UDQS_t UDQ1 V UDQS_t DQ9 V
PP SS DD DD DD
C V UDQ4 UDQ2 – – – C UDQ3 UDQ5 V DQ11 DQ13 V
DDQ SSQ SSQ
D V V UDQ6 – – – D UDQ7 V V DQ15 V V
DD SSQ SSQ DDQ SSQ DDQ
E V UDM_n/ V – – – E LDM_n/ V UZQ LDM_n/ V V
SS SSQ SSQ SSQ SS
UDBI_n LDBI_n LDBI_n
F V V LDQS_c – – – F LDQ1 V LZQ DQ1 V ZQ
SSQ DDQ DDQ DDQ
G V LDQ0 LDQS_t – – – G V V V V V V
DDQ DD SS DDQ DD SS DDQ
H V LDQ4 LDQ2 – – – H LDQ3 LDQ5 V DQ3 DQ5 V
SSQ SSQ SSQ
J V V LDQ6 – – – J LDQ7 V V DQ7 V V
DDDLL DDQ DDQ DD DDQ DD
K V CKE ODT – – – K CK_t CK_c V CK_t CK_c V
SS SS SS
L V WE_n/ ACT_n – – – L CS_n RAS_n/ V CS_n RAS_n/ V
DD DD DD
A14 A16 A16
M V BG0 A10/AP – – – M A12/ CAS_n/ BG1 A12/ CAS_n/ V
REFCA SS
BC_n A15 BC_n A15
N V BA0 A4 – – – N A3 BA1 TEN A3 BA1 TEN
P RESET_n A6 A0 – – – P A1 A5 ALERT_n A1 A5 ALERT_n
R V A8 A2 – – – R A9 A7 V A9 A7 V
DD PP PP
T V A11 PAR – – – T V A13 V NC A13 V
SS SS DD DD
CCMTD-1725822587-10240 32 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Figure 24: Optimum Layout – DDP ×16 and SDP ×16 Compatibility
Controller
Optimum BG1
E9 L1 Re9 L1
SDP x16 DDP x16 SDP x16 DDP x16
E9 V UZQ Re9 Re9 0 480
M9 V SS BG1 L3 Rm9 open 0
M9 Rm9b 0 open
Rm9
L2 0 resistors should be low ESL
BG1 should be approx 5ps shorter
L1 Rm9b L1
L1 < 0.1mm
L2 < 0.25mm
Rm9b L3 < 2mm
Note: 1. Mitigates V SS offset; Parallel resistors when connecting to V SS reduces inductance.
Figure 25: Alternate One Layout – DDP ×16 and SDP ×16 Compatibility
Controller
Alternate 1 BG1
E9
SDP x16 DDP x16 Re9 SDP x16 DDP x16
E9 V UZQ Re9 0 240
M9 V SS BG1 L3 Rm9 open 0
M9 Rm9b 0 open
Rm9
L2 0 resistors should be low ESL
BG1 should be approx 5ps shorter
L1 Rm9b L1
L1 < 0.1mm
L2 < 0.25mm
Rm9b L3 < 2mm
Note: 1. Mitigates V SS offset on M9 ball.
CCMTD-1725822587-10240 33 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.

Schematic Checklist
Schematic Checklist
The following checklist outlines the basic things to verify and consider when complet-
ing a schematic review:
1. Ensure that the ZQ pin is connected to a 240Ω ±1% resistor.
2. Verify that the differential clock signals are terminated. Simulations should be
used to determine the method and exact component values. See Table 12 for more
information.
3. Check the remaining pin connections between the controller and the DRAM de-
vice following the guidance provided in Table 12.
4. Ensure adequate decoupling methodology has been implemented. Refer to Table
9.
5. RESET_n requires a pull-down circuit. Ensure the pull-down circuit is adequate
for the number of loads.
6. If TEN is not used, ensure it is connected directly to ground. If TEN is used, it re-
quires a pull-down circuit; ensure the pull-down circuit is adequate for the num-
ber of loads.
7. Micron highly recommends that V tracks at V /2 by using a voltage divider
on V rather than a fixed 0.6V V supply.
DD REFCA
8. Determine the maximum clock speed of the memory bus. Timing margins de-
crease as frequency increases. Ensure adequate margins are designed for through
proper routing and termination.
9. If the following features are being used, ensure the mode registers are properly
configured:
a. Cyclic redundancy cycle (CRC) for the data bus
b. Parity checking of command/address bus
c. Data bus inversion
10. Carefully consider the host's workload, use cases, and environment. A controller
that can strategically pull in and postpone REFRESH commands and/or utilize
temperature-controlled refresh mode can increase the efficiency of the data bus,
which improves throughput.
11. Consider using post package repair, which can be useful in increasing the reliabili-
ty and longevity of systems with soldered-down DRAM devices because they can-
not be replaced like a DRAM module can.
8000 S. Federal Way, P.O. Box 6, Boise, ID 83707-0006, Tel: 208-368-4000
www.micron.com/products/support Sales inquiries: 800-932-4992
Micron and the Micron logo are trademarks of Micron Technology, Inc.
All other trademarks are the property of their respective owners.
CCMTD-1725822587-10240 34 Micron Technology, Inc. reserves the right to change products or specifications without notice.
tn4040_ddr4_point_to_point_design_guide.pdf - Rev. H 08/2020 EN © 2020 Micron Technology, Inc. All rights reserved.
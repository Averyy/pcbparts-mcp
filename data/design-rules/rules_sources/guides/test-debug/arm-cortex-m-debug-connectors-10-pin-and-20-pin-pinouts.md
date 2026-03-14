---
source: "ARM -- Cortex-M Debug Connectors (10-pin and 20-pin pinouts)"
url: "https://documentation-service.arm.com/static/5fce6c49e167456a35b36af1"
format: "PDF 5pp"
method: "pdfplumber"
extracted: 2026-03-02
chars: 7728
---

Cortex-M Debug Connectors
Overview
The debug connectors for Cortex microcontrollers will be migrating to new debug connectors.
Currently the KEIL ULINK2 already supports one of the new debug connector arrangements and the
coming ULINK-Pro supports both new debug connector arrangements. A number of Cortex
microcontroller evaluation boards from KEIL already support the new connectors.
This document covers the basic information of these debug connectors. This is for general
information only and should not be used as a specification. The details covered in this document are
taken from various ARM and KEIL documents / web sites. Additional details are covered in
specifications documents listed in the Reference section.
Why change?
Most existing ARM products use a 20-pin IDC connector for JTAG debug, and 38-pin Mictor
connectors for trace. However, there are a number of issues with the existing arrangement:
- 20-pin IDC connectors are too big for today’s microcontroller boards.
- 20-pin IDC connectors do not support trace.
- The 0.05” micro header in the new connector arrangement has a lower cost for trace.
Since the Cortex-M3 trace port only requires 5 signals (4 bit data and trace clock), the trace signals
can easily be merged into a 20-pin debug connector. For microcontroller products that do not
require trace (e.g. Cortex-M0 or Cortex-M3 without trace), an even smaller connector can be used.
The new connectors are called:
- Cortex Debug Connector (10-pin)
- Cortex Debug+ETM Connector (20-pin)
The new connectors are based on the Samtec 0.05” micro header (reference 1).

Cortex Debug Connector
The Cortex Debug Connector has only 10 pins.
1 2
VCC SWDIO / TMS
GND SWDCLK / TCK
GND SWO / TDO
KEY NC / TDI
GNDDetect nRESET
9 10
The Cortex Debug Connector supports JTAG debug, Serial Wire debug and Serial Wire Viewer (via
SWO connection when Serial Wire debug mode is used) operations.
Cortex Debug+ETM connector
The Cortex Debug+ETM Connector has 20 pins.
1 2
VCC SWDIO / TMS
GND SWDCLK / TCK
GND SWO / TDO / EXTa / TRACECTL
KEY NC/EXTb/TDI
GNDDetect nRESET
GND/TgtPwr+Cap TRACECLK
GND/TgtPwr+Cap TRACEDATA[0]
GND TRACEDATA[1]
GND TRACEDATA[2]
GND TRACEDATA[3]
19 20
The Cortex Debug+ETM Connector supports JTAG debug, Serial-Wire debug, Serial Wire Viewer (via
SWO connection when Serial Wire debug mode is used) and instruction trace operations.
Definition of the signals can be found in the CoreSight Components Technical Reference Manual
(reference 2).

Legacy connectors
The legacy connectors can still be used, and there will be adaptors for the 20-pin IDC connectors. But
for new designs, the Cortex Debug connector and the Cortex Debug+ETM connectors are
recommended. The following diagram shows the 20-pin IDC JTAG connector compared to a 10-pin
Cortex Debug connector.
1 2
VCC VCC (optional)
TRST GND
NC/TDI GND
SWDIO / TMS GND
SWDCLK / TCK GND
RTCK GND
SWO / TDO GND
nRESET GND
NC/DBGRQ GND
NC/DBACK GND
19 20
Another legacy connector is the 38-pin Mictor connector (type 5767054-1 or compatible). The
specification for the signal arrangement is documented in the ETM Architecture Specification
(reference 3). The following diagram shows the pin assignment for the Mictor connector when used
with the Cortex-M3 Trace Port Interface Unit. The Mictor connector can be used for JTAG (and Serial
Wire Debug) as well as trace.
1 NC NC 2
3 NC NC 4
5 GND TRACECLK 6
7 Pulldown Pulldown 8
9 NC/ nSRST Pulldown 10
1 2
11 TDO/SWV Pullup (Vref) 12
13 RTCK VSupply 14
15 TCK/SWCLK 0 / TRACEDATA[7] 16
17 TMS/SWIO 0 / TRACEDATA[6] 18
19 TDI 0 / TRACEDATA[5] 20
21 nTRST 0 / TRACEDATA[4] 22
23 0 / TRACEDATA[15] TRACEDATA[3] 24
25 0 / TRACEDATA[14] TRACEDATA[2] 26
27 0 / TRACEDATA[13] TRACEDATA[1] 28
37 38
29 0 / TRACEDATA[12] 0 30
31 0 / TRACEDATA[11] 0 32
33 0 / TRACEDATA[10] 1 34
35 0 / TRACEDATA[9] 0 / TRACECTRL 36
37 0 / TRACEDATA[8] TRACEDATA[0] 38

The Mictor connector is still the recommended trace connector for other ARM processors including
ARM7, ARM9, Cortex-R and Cortex-A processors, and other applications that require wider trace
widths (e.g multiple processors).
There are additional legacy connectors for ARM microcontrollers. A number of them can be found
on the KEIL web site (reference 4). They are less common and are not used for ARM Cortex
microcontrollers.
Which connector to use?
There are multiple choices of connector. Normally the Cortex Debug+ETM connector should cover all
requirements. But in some cases you might want to include more than one debug connector to allow
different debuggers to be used (e.g. evaluation board for different customers).
Cortex Debug Connector (10-pin)
- Small board space and low trace bandwidth requirement (simple data trace or event trace).
- Supported by ULINK2, ULINK-Pro and most third party debuggers.
Cortex Debug+ETM Connector (20-pin)
- Small board space and higher trace bandwidth requirement (instruction level trace and
higher amount of data trace).
- Instruction trace supported by ULINK-Pro and some third party debuggers.
Legacy 20-pin JTAG IDC connector
- Required when traditional debug tools are used (e.g. ARM RealView-ICE), or the
debugger/emulator unit is powered by target board via the IDC connector. Usually this can
be avoided by using adaptors.
- Required when a physically stronger/robust connector is needed.
Mictor connector
- Required when traditional trace tools are used (e.g. ARM RealView-Trace). Usually
traditional trace tools can be connected to the new Cortex connector via adaptors.
- Required for other ARM processors (ARM7, ARM9, Cortex-R/A processors).
- Required for multiple processor systems which require trace port with more than 4-bit wide.
Additional information on Cortex microcontroller debug and trace can be found on the KEIL web site
(reference 5) and ARM web site (reference 2).
Adaptors
For users of existing ARM RealView Development tools like RealView-ICE and RealView-Trace, you
can connect to target systems with new Cortex Debug connectors by using the CoreSight High

Density Probe (reference 6). Example setup of using the CoreSight High Density Probe with the new
connectors can be found on the ARM web site (reference 7).
For users of Keil ULINK2 or ULINKPro products there is no need to use any adaptor.
For users of Segger J-Link or J-Trace, these products support the 20-pin IDC connector, 38-pin Mictor
connector as well as the Cortex Debug+ETM connector. A number of adaptors are also included.
For users of Signum JTAGJet-Trace-CM3 product, the unit comes with Cortex Debug+ETM connector,
an optional Mictor-38 adaptor cable is also available.
Reference:
Document
1 Samtech FTSH-110 and FTSH-105 micro header
http://www.samtec.com/ftppub/pdf/ftsh_mt.pdf
2 CoreSight Components Technical Reference Manual
(Cortex debug connector detailed specification is in appendix C)
http://infocenter.arm.com/help/topic/com.arm.doc.ddi0314h/DDI0314H_coresight_component
s_trm.pdf
http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.ddi0314h/Chdcdggc.html
3 ETM Architecture Specification
(Physical trace connector description in chapter 8)
http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.ihi0014o/index.html
4 ULINK2 supported connectors
http://www.keil.com/support/man/docs/ulink2/ulink2_hw_connectors.htm
5 Cortex microcontroller debug and trace
http://www.keil.com/peripherals/coresight/default.asp
6 What is the CoreSight High Density Probe?
http://infocenter.arm.com/help/topic/com.arm.doc.faqs/ka13519.html
7 How do I trace the MCBSTM32E using the CoreSight High Density Probe?
http://infocenter.arm.com/help/topic/com.arm.doc.faqs/ka13520.html
8 CoreSight Debug and Trace Connectors for Cortex-M devices
http://www.keil.com/peripherals/coresight/connectors.asp
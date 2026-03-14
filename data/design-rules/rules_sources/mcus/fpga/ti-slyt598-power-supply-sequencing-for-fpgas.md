---
source: "TI SLYT598 -- Power Supply Sequencing for FPGAs"
url: "https://www.ti.com/lit/pdf/slyt598"
format: "PDF 5pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 7315
---

Analog Applications Journal Communications
Power-supply sequencing for FPGAs
By Sami Sirhan
Analog Systems Engineering
Sureena Gupta
Applications Engineer
Introduction
Figure 1. Cascading PGOOD pin into enable pin
Power-supply sequencing is an important aspect to con-
sider when designing with a field programmable gate array
(FPGA). Typically, FPGA vendors specify power-sequenc- V
IN
ing requirements because an FPGA can require anywhere
from three to over ten rails. V OUT1
By following the recommended power sequence, exces- V OUT2
TPS62085
sive current draw during startup can be avoided, which in
TPS62085
turn prevents damage to devices. Sequencing the power
EN
supplies in a system can be accomplished in several ways.
This article elaborates on sequencing solutions that can be PGOOD EN
implemented based on the level of sophistication needed
by a system.
Sequencing solutions addressed in this article are:
1. Cascading PGOOD pin into enable pin
2. Sequencing using a reset IC Method 2: Sequencing using a reset IC
3. Analog up/down sequencers Another simple option to consider for power-up sequenc-
4. Digital system health monitors with PMBus interface ing is a reset IC with time delay. With this option, the reset
IC monitors the power rails with tight threshold limits.
Method 1: Cascading PGOOD pin into enable pin Once the power rail is within 3% or less of its final value,
A basic, cost-effective way to implement sequencing is to the reset IC enters the wait period defined by the solution
cascade the power good (PG) pin of one power supply before powering up the next rail. The wait period can be
into the enable (EN) pin of the next sequential supply programmed into the reset IC using EEPROM or be set by
(Figure 1). The second supply begins to turn on when the external capacitors. A typical multi-channel reset IC is
PG threshold is met, usually when the supply is at 90% of shown in Figure 2. The advantage of using a reset IC for
its final value. This method offers a low-cost approach, but power-up sequencing is that the solution is monitored.
timing cannot be eas-
ily controlled. Adding Figure 2. Power-up sequencing with a multi-output reset IC
a capacitor to the EN
pin can introduce tim-
ing delays between VCC4
VIN DC/DC LDO
stages. However, this VCC3
method is unreliable DC/DC LDO VCC2
during temperature EN4 VCC1
variations and repeated
power cycling. DC/DC LDO VCC TPS386000 VCC1 VCC2 VCC3 VCC4
SENSE1 RESET1 RESET
Also, this method EN3 DSP
SENSE2 RESET2 CPU
does not support s
power-down DC/DC LDO vi d
er
SENSE3 RESET3 CLK
FPGA
sequencing. EN2 EN Di SENSE4L RESET4
SENSE4H WDI
CT1 CT2 CT3 CT4 GND
CT1 CT2 CT3 CT4
Sequence:
VIN VCC4 VCC3 VCC2 VCC1

Each rail is confirmed to be within regulation before
Figure 3. Implementation of an
releasing the next rail and there is no need for a PGOOD
analog up/down sequencer
pin on the power converter. The drawback of using a
reset-IC solution for sequencing is that it does not imple-
ment power-down sequencing. Input
Supply
Device 1
Method 3: Analog up/down sequencers
VCC
Implementing power-up sequencing can be easier than Enable
LM3880
implementing power-down sequencing. To achieve power-
up and power-down sequencing, there are simple analog FLAG 1 Device 2
sequencers (Figure 3) that can reverse (Sequence 1) or Enable EN
FLAG 2 Enable
even mix (Sequence 2) the power-down sequence relative
to the power-up sequence. Upon power up, all the flags FLAG 3 Device 3
are held low until EN is pulled high. After EN is asserted,
GND
each flag goes open drain (pull-up resistor is required) Enable
sequentially after an internal timer has elapsed. The
power-down sequence is the same as power up, but in
reverse order. Input EN
Cascading multiple sequencers
FLAG1
Sequencers can be cascaded together to support many ut
power rails, as well as provide fixed and adjustable delay ut p FLAG2
times between enable signals. In Figure 4, two sequencers O FLAG3
cascade together to achieve six sequenced rails. Upon
power up, the AND gate ensures that the second
sequencer does not trigger until it has received both an FLAG1
EN signal and rail C has triggered. On power down, the
FLAG2
AND gate ensures that the second sequencer sees the EN
falling edge, irrespective of output C. The OR gate ensures FLAG3
that the first sequencer is triggered with the EN rising
edge. Upon power down, the OR gate ensures that the
first sequencer can’t see the EN falling edge until D has
fallen. This guarantees power-up and power-down Figure 4. Cascading multiple analog sequencers
sequencing, but does not offer a monitored sequence.
Monitored up/down sequencing Rails
Monitored sequencing can be added to the circuit in LM3880 A
#1
Figure 4 by simply adding a couple of AND gates between B
the FlagX output and the PG pin as shown in Figure 5. In EN C
this example, PS2 is enabled only if PS1 is greater than
90% of its final value. This method offers a low-cost, moni- LM3880 D
tored sequencing solution. #2 E
EN F
Method 4: Digital system health monitors with
PMBus interface
If a system requires the utmost flexibility, a good solution
is a PMBus/I2C-compatible, digital-system health monitor
such as the UCD90120A. Such solutions offer maximum Figure 5. Adding monitored sequencing to a
control for any sequencing need by allowing the designer simple time-based sequencer
to configure ramp up/down times, on/off delays, sequence
dependencies, and even voltage and current monitoring.
FLAG1
PS1
Dual AND
FLAG2
LM388x
PS2
PWRGD PS1
FLAG3
PS3
PWRGD PS2
1
ecneuqeS
2
ecneuqeS
1 2 3 4 5 6
y y y y y y
a a a a a a el el el el el el
D D D D D D

Figure 6. Example of power up sequencing using the UCD90120A GUI
Digital-system health monitors come with a graphical
Figure 7. Example of a FPGA
user interface (GUI) that can be used to program power-
power-logic sequence
up and power-down sequencing along with other system
parameters (Figure 6). Some digital system health moni-
tors also have non-volatile-error and peak-value logging
Block
that helps with system-failure analysis in case of a brown- Core RAM Auxiliary I/O
Supply Supply Supplies
out event. Supply
FPGA sequencing requirements examples
FPGA vendors such as Xilinx or Altera provide either a
recommended or required power-up sequence in their Related Web sites
datasheets that are easily accessible online. Sequencing
www.ti.com/4q14-LM3880
requirements vary between vendors and vary from one
vendor’s FPGA family to another. Also listed in datasheets www.ti.com/4q14-TPS62085
are timing requirements for ramp-up and shutdown. The www.ti.com/4q14-TPS386000
recommended power-down sequence is typically the
www.ti.com/4q14-UCD90120A
reverse order of the power-up sequence. An example of
Subscribe to the AAJ:
power-up sequencing is shown in Figure 7.
www.ti.com/subscribe-aaj
Conclusion
There are several sequencing solutions that can be utilized
to follow the requirements specified by FPGA vendors.
System requirements may include power monitoring in
addition to power-up and power-down sequencing, but the
optimal power solution for an FPGA will depend on sys-
tem complexity and specifications.

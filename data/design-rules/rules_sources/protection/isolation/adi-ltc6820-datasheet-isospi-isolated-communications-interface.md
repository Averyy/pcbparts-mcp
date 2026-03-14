---
source: "ADI LTC6820 Datasheet -- isoSPI Isolated Communications Interface"
url: "https://www.analog.com/media/en/technical-documentation/data-sheets/LTC6820.pdf"
format: "PDF 30pp"
method: "pdfplumber"
extracted: 2026-03-02
chars: 55468
---

LTC6820
isoSPI Isolated
Communications Interface
FEATURES DESCRIPTION
n AEC-Q100 Qualified for Automotive Applications The LTC®6820 provides bidirectional SPI communications
n 1Mbps Isolated SPI Data Communications between two isolated devices through a single twisted-
n Simple Galvanic Isolation Using Standard pair connection. Each LTC6820 encodes logic states into
Transformers signals that are transmitted across an isolation barrier to
n Bidirectional Interface Over a Single Twisted Pair another LTC6820. The receiving LTC6820 decodes the
n Supports Cable Lengths Up to 100 Meters transmission and drives the slave bus to the appropri-
n Very Low EMI Susceptibility and Emissions ate logic states. The isolation barrier can be bridged by
n Configurable for High Noise Immunity or Low Power a simple pulse transformer to achieve hundreds of volts
n Engineered for ISO26262 Compliant Systems of isolation.
n Requires No Software Changes in Most SPI Systems
The LTC6820 drives differential signals using matched
n Ultralow, 2µA Idle Current
source and sink currents, eliminating the requirement
n Automatic Wake-Up Detection
for a transformer center tap and reducing EMI. Precision
n Operating Temperature Range: –40°C to 125°C
window comparators in the receiver detect the differential
n 2.7V to 5.5V Power Supply
signals. The drive currents and the comparator thresholds
n Interfaces to All Logic from 1.7V to 5.5V
are set by a simple external resistor divider, allowing the
n Available in 16-Lead QFN and MSOP Packages
system to be optimized for required cable lengths and
desired signal-to-noise performance.
APPLICATIONS
All registered trademarks and trademarks are the property of their respective owners. Protected
by U.S. patents, including 8908779.
n Industrial Networking
n Battery Monitoring Systems
n Remote Sensors
TYPICAL APPLICATION
Microcontroller to SPI Slave Isolated Interface Data Rate vs Cable Length
MASTER
µC LTC6820
MSTR
SDO MOSI IP
SDI MISO 120Ω
SCK SCK IM
CS CS
100 METERS
TWISTED PAIR
REMOTE
SLAVE IC LTC6820
0
IP
SDI MOSI 1
120Ω CABLE LENGTH (METERS)
SDO MISO
SCK SCK IM
6820 TA01a
Rev C
1
Document Feedback For more information www.analog.com
)spbM(
ETAR
ATAD
1.2
CAT-5 ASSUMED
1.0
0.8
0.6
0.4
0.2
10 100
6820 TA01b

ABSOLUTE MAXIMUM RATINGS
(Notes 1, 2, 3)
Input Supply Voltages (V and V ) to GND ...........6V
DD DDS
Pin Voltages
SCK, CS, EN ...............–0.3V to V + 0.3V (6V Max)
DDS
IBIAS, SLOW, IP, IM .....–0.3V to V + 0.3V (6V Max)
DD
All Other Pin Voltages ..............................–0.3V to 6V
Maximum Source/Sink Current
IP, IM .................................................................30mA
MOSI, MISO, SCK, CS ........................................20mA
PIN CONFIGURATION
TOP VIEW
16 15 14 13
MOSI 1 12 SLOW
MISO 2 11 MSTR 17
SCK 3 10 IP
CS 4 9 IM
5 6 7 8
UD PACKAGE
16-LEAD (3mm × 3mm) PLASTIC QFN
TJMAX = 150°C, θJA = 58.7°C/W
EXPOSED PAD (PIN 17) PCB CONNECTION TO GND IS OPTIONAL
2
For more information www.analog.com
NE
SDDV
SAIBI
LOP
PMCI
AHP
DNG
DDV
Operating Temperature Range
LTC6820I .............................................–40°C to 85°C
LTC6820H ..........................................–40°C to 125°C
Specified Temperature Range
LTC6820I .............................................–40°C to 85°C
LTC6820H ..........................................–40°C to 125°C
Storage Temperature Range ..................–65°C to 150°C
Lead Temperature (Soldering, 10 sec)
MSOP ...............................................................300°C
TOP VIEW
EN 1 16 IBIAS
MOSI 2 15 ICMP
MISO 3 14 GND
SCK 4 13 SLOW
CS 5 12 MSTR
VDDS 6 11 IP
POL 7 10 IM
PHA 8 9 VDD
MS PACKAGE
16-LEAD PLASTIC MSOP
TJMAX = 150°C, θJA = 120°C/W
ORDER INFORMATION
PART MSL SPECIFIED
TUBE (121PC) TAPE AND REEL (2500PC) MARKING* PACKAGE DESCRIPTION RATING TEMPERATURE RANGE
LTC6820IUD#PBF LTC6820IUD#TRPBF LGFM 16-Lead (3mm × 3mm) Plastic QFN 1 –40°C to 85°C
LTC6820HUD#PBF LTC6820HUD#TRPBF LGFM 16-Lead (3mm × 3mm) Plastic QFN 1 –40°C to 125°C
AUTOMOTIVE PRODUCTS**
PART MSL SPECIFIED
TUBE (37PC) TAPE AND REEL (2500PC) MARKING* PACKAGE DESCRIPTION RATING TEMPERATURE RANGE
LTC6820IMS#PBF LTC6820IMS#TRPBF 6820 16-Lead Plastic MSOP 1 –40°C to 85°C
LTC6820IMS#3ZZPBF LTC6820IMS#3ZZTRPBF 6820 16-Lead Plastic MSOP 1 –40°C to 85°C
LTC6820HMS#PBF LTC6820HMS#TRPBF 6820 16-Lead Plastic MSOP 1 –40°C to 125°C
LTC6820HMS#3ZZPBF LTC6820HMS#3ZZTRPBF 6820 16-Lead Plastic MSOP 1 –40°C to 125°C
Contact the factory for parts specified with wider operating temperature ranges.*The temperature grade is identified by a label on the shipping container.
Tape and reel specifications. Some packages are available in 500 unit reels through designated sales channels with #TRMPBF suffix.
**Versions of this part are available with controlled manufacturing to support the quality and reliability requirements of automotive applications. These
models are designated with a #3ZZ suffix. Only the automotive grade products shown are available for use in automotive applications. Contact your
local Analog Devices account representative for specific product ordering information and to obtain the specific Automotive Reliability reports for
these models.

ELECTRICAL CHARACTERISTICS
The l denotes the specifications which apply over the full specified
temperature range, otherwise specifications are at T = 25°C. V = 2.7V to 5.5V, V = 1.7V to 5.5V, R = 2k to 20k unless
A DD DDS BIAS
otherwise specified. All voltages are with respect to GND.
SYMBOL PARAMETER CONDITIONS MIN TYP MAX UNITS
Power Supply
V Operating Supply Voltage Range l 2.7 5.5 V
V IO Supply Voltage Range (Level Shifting) Affects CS, SCK, MOSI, MISO and EN Pins l 1.7 5.5 V
I Supply Current, READY/ACTIVE States R = 2kΩ (I = 1mA) 1/t = 0MHz l 4 4.8 5.8 mA
DD BIAS B CLK
(Note 4) 1/t = 1MHz 7 mA
CLK
R = 20kΩ (I = 0.1mA) 1/t = 0MHz l 1.3 2 2.9 mA
BIAS B CLK
1/t = 1MHz 2.4 mA
Supply Current, IDLE State MSTR = 0V l 2 6 µA
MSTR = V l 1 3 µA
I IO Supply Current (Note 5) SPI Inputs and EN Pin at 0V or V , l 1 µA
DDS DDS
SPI Outputs Unloaded
Biasing
V Voltage on IBIAS Pin READY/ACTIVE State l 1.9 2.0 2.1 V
BIAS
IDLE State 0 V
I Isolated Interface Bias Current (Note 6) R = 2k to 20k l V /R mA
B BIAS BIAS BIAS
A Isolated Interface Current Gain V ≤ 1.6V I = 1mA l 18 20 22 mA/mA
IB A B
I = 0.1mA l 18 20 24 mA/mA
B
V Transmitter Pulse Amplitude V = |V – V | V < 3.3V l V – 1.7V V
A A IP IM DD DD
V ≥ 3.3V l 1.6 V
V Threshold-Setting Voltage on ICMP Pin V = A • V l 0.2 1.5 V
ICMP TCMP TCMP ICMP
I Leakage Current on ICMP Pin V = 0V to V l ±1 µA
LEAK(ICMP) ICMP DD
I Leakage Current on IP and IM Pins IDLE State, V = V = 0V to V l ±2 µA
LEAK(IP/IM) IP IM DD
A Receiver Comparator Threshold Voltage V = V /2 to V – 0.2V, l 0.4 0.5 0.6 V/V
TCMP CM DD DD
Gain V = 0.2V to 1.5V
ICMP
V Receiver Common Mode Bias IP/IM Not Driving (V – V /3 – 167mV) V
CM DD ICMP
R Receiver Input Resistance Single-Ended to IP or IM l 26 35 42 kΩ
IN
Idle/Wake-Up (See Figure 13, 14, 15)
V Differential Wake-Up Voltage t = 240ns l 240 mV
WAKE DWELL
(See Figure 13)
t Dwell Time at V V = 240mV l 240 ns
DWELL WAKE WAKE
t Start-Up Time After Wake Detection l 8 µs
READY
t Idle Time-Out Duration l 4 5.7 7.5 ms
IDLE
Digital I/O
V Digital Voltage Input High, Configuration V = 2.7V to 5.5V (POL, PHA, MSTR, SLOW) l 0.7 • V V
IH(CFG) DD DD
Pins (PHA, POL, MSTR, SLOW)
V Digital Voltage Input Low, Configuration V = 2.7V to 5.5V (POL, PHA, MSTR, SLOW) l 0.3 • V V
IL(CFG) DD DD
Pins (PHA, POL, MSTR, SLOW)
V Digital Voltage Input High, SPI Pins V = 2.7V to 5.5V l 0.7 • V V
IH(SPI) DDS DDS
(CS, SCK, MOSI, MISO) V = 1.7V to 2.7V l 0.8 • V V
V Digital Voltage Input Low, SPI Pins V = 2.7V to 5.5V l 0.3 • V V
IL(SPI) DDS DDS
(CS, SCK, MOSI, MISO) V = 1.7V to 2.7V l 0.2 • V V
V Digital Voltage Input High, EN Pin V = 2.7V to 5.5V l 2 V
IH(EN) DDS
V = 1.7V to 2.7V l 0.85 • V V
V Digital Voltage Input Low, EN Pin V = 2.7V to 5.5V l 0.8 V
IL(EN) DDS
V = 1.7V to 2.7V l 0.25 • V V
V Digital Voltage Output High (CS and SCK) V = 3.3V, Sourcing 2mA l V – 0.2 V
OH DDS DDS
V = 1.7V, Sourcing 1mA l V – 0.25 V
V Digital Voltage Output Low V = 3.3V, Sinking 3.3mA l 0.2 V
OL DDS
(MOSI, MISO, CS, SCK) V = 1.7V, Sinking 1mA l 0.2 V
3

The l denotes the specifications which apply over the full specified
junction temperature range, otherwise specifications are at T = 25°C. V = 2.7V to 5.5V, V = 1.7V to 5.5V, R = 2k to 20k
A DD DDS BIAS
unless otherwise specified. All voltages are with respect to GND.
SYMBOL PARAMETER CONDITIONS MIN TYP MAX UNITS
I Digital Pin Input Leakage Current PHA, POL, MSTR, SLOW = 0V to V l ±1 µA
LEAK(DIG) DD
CS, SCK, MOSI, MISO, EN = 0V to V
C Input/Output Pin Capacitance (Note 9) 10 pF
I/O
Isolated Pulse Timing (See Figure 2)
t Chip-Select Half-Pulse Width l 120 150 180 ns
1/2PW(CS)
t Chip-Select Pulse Inversion Delay l 200 ns
INV(CS)
t Chip-Select Response Delay l 140 190 ns
DEL(CS)
t Data Half-Pulse Width l 40 50 60 ns
½PW(D)
t Data Pulse Inversion Delay l 70 ns
INV(D)
t Data Response Delay (Note 8) l 75 120 ns
DEL(D)
isoSPI™ Timing—Master (See Figure 3, 4)
t SCK Latching Edge to SCK Latching Edge (Note 7) SLOW = 0 l 0.5 µs
SLOW = 1 l 5 µs
t MOSI Setup Time Before SCK Latching Edge (Note 8) l 25 ns
t MOSI Hold Time After SCK Latching Edge l 25 ns
t SCK Low t = t + t ≥ 0.5µs l 50 ns
3 CLK 3 4
t SCK High t = t + t ≥ 0.5µs l 50 ns
4 CLK 3 4
t CS Rising Edge to CS Falling Edge 1MHz isoSPI Slave, t > 1 µs l 0.6 µs
5 CLK
2MHz isoSPI Slave, 0.5µs < t < 1µs l 2.0 µs
t SCK Latching Edge to CS Rising Edge 1MHz isoSPI Slave, t > 1µs l 1 µs
6 CLK
(Note 7) 2MHz isoSPI Slave, 0.5µs < t < 1µs l 0.5 µs
t CS Falling Edge to SCK Latch Edge ADI Stack Monitor isoSPI Slave l 0.5 µs
7
(Note 7) Other isoSPI Slave Devices Including 6820 l 1 µs
t SCK Non-Latch Edge to MISO Valid (Note 8) l 55 ns
8
t SCK Latching Edge to Short ±1 Transmit l 50 ns
9
t CS Transition to Long ±1 Transmit l 55 ns
10
t CS Rising Edge to MISO Rising (Note 8) l 55 ns
11
isoSPI Timing—Slave (See Figure 3, 4)
t isoSPI Data Recognized to SCK (Note 8) SLOW = 0 l 110 145 185 ns
12
Latching Edge SLOW = 1 l 0.9 1.1 1.4 µs
t SCK Pulse Width SLOW = 0 l 90 115 150 ns
13
SLOW = 1 l 0.9 1.1 1.4 µs
t SCK Non-Latch Edge to isoSPI Data Transmit (Note 8) SLOW = 0 l 115 145 190 ns
14
t CS Falling Edge to SCK Non-Latch Edge PHA = 1 SLOW = 0 l 90 120 160 ns
15
t CS Falling Edge to isoSPI Data Transmit SLOW = 0 l 200 265 345 ns
16
SLOW = 1 l 1.8 2.2 2.8 µs
t CS Rising Edge to SCK Latching Edge PHA = 1 SLOW = 0 l 90 120 160 ns
17
t CS Rising Edge to MOSI Rising Edge (Note 8) l 35 ns
18
t Data Return Delay SLOW = 0 l 485 625 ns
RTN
SLOW = 1 l 3.3 4 µs
4

Note 1: Stresses beyond those listed under Absolute Maximum Ratings Note 6: The LTC6820 is guaranteed to meet specifications with R
may cause permanent damage to the device. Exposure to any Absolute resistor values ranging from 2k to 20k, with 1% or better tolerance. Those
Maximum Rating condition for extended periods may affect device resistor values correspond to a typical I that can range from 0.1mA
reliability and lifetime. (for 20k) to 1mA (for 2k).
Note 2: All currents into pins are positive, and all voltages are referenced Note 7: These timing specifications are dependent on the delay through
to GND unless otherwise specified. the cable, and include allowances for 50ns of delay each direction. 50ns
Note 3: The LTC6820I is guaranteed to meet specified performance corresponds to 10m of CAT-5 cable (which has a velocity of propagation of
from –40°C to 85°C. The LTC6820H is guaranteed to meet specified 66% the speed of light). Use of longer cables would require derating these
performance from –40°C to 125°C. specs by the amount of additional delay.
Note 4: Active supply current (I ) is dependent on the amount of time Note 8: These specifications do not include rise or fall time. While fall
that the output drivers are active on IP and IM. During those times I will time (typically 5ns due to the internal pull-down transistor) is not a
increase by the 20 • I B drive current. For the maximum data rate 1MHz, concern, rising-edge transition time t RISE is dependent on the pull-up
the drivers are active approximately 10% of the time if MSTR = 1, and 5% resistance and load capacitance. In particular, t 12 and t 14 require t RISE
of the time if MSTR = 0. See Applications Information section for more < 110ns (if SLOW = 0) for the slave’s setup and hold times. Therefore,
detailed information. the recommended time constant is 50ns or less. For example, if the
total capacitance on the data pin is 25pF (including self capacitance
Note 5: The IO supply pin, V , provides power for the SPI inputs and
C of 10pF), the required pull-up resistor value is R ≤ 2kΩ. If these
outputs, including the EN pin. If the inputs are near 0V or V (to avoid I/O PU
requirements can’t be met, use SLOW = 1.
static current in input buffers) and the outputs are not sourcing current,
then I includes only leakage current. Note 9: Guaranteed by design. Not tested in production.
5

IBIAS Voltage vs Temperature IBIAS Voltage Load Regulation IBIAS Voltage vs Supply Voltage
IBIAS CURRENT (mA)
6
)V(
EGATLOV
NIP
2.010
VDD = 3V
2.005
2.000
1.995
1.990 1.990
0.2 0.4 0.6 0.8 1.0 2.5
SUPPLY VOLTAGE (V)
6820 G08
2.010
2.005 IB = 0.1mA
IB = 1mA
2.000
1.995
1.96
–50 –25 3 3.5 4 4.5 5 5.5
TEMPERATURE (°C)
6820 G09
TYPICAL PERFORMANCE CHARACTERISTICS
V = V , unless otherwise noted.
Input Voltage Threshold
Supply Current (READY/ACTIVE) Supply Current (READY) (Except EN Pin)
vs Clock Frequency vs Temperature vs Supply Voltage (V or V )
FREQUENCY (kHz)
Supply Current (IDLE) Supply Current (IDLE)
vs Supply Voltage vs Temperature
2.04
3 PARTS
2.02
2.00
1.98
IB = 0.1mA
0 25 50 75 100 125
6820 G07
)Am(
TNERRUC
YLPPUS
6 VDD = 5V, IB = 1mA
VDD = 3V, IB = 1mA
VDD = 5V, IB = 0.1mA
2 VDD = 3V, IB = 0.1mA
MSTR = 1
4.8
200 400 600 800 1000 –50 –25
6820 G01
5.3
5.2
VDD = 5V
5.1
5.0
4.9
0 25 50 75 100 125 1.5 2.5
6820 G02
DLOHSERHT
TUPNI
4.0
3.5
ONLY
3.0 SPI PINS HIGH
VIH
2.5
2.0 LOW
1.5
VIL
0.5
2.0 3.0 3.5 4.0 4.5 5.0 5.5
6820 G03
)Aµ(
3.0
SLAVE (MSTR = 0)
2.0
MASTER (MSTR = 1)
3.0 3.5 4.0 4.5 5.0 5.5 –50
6820 G04
)Aµ(
Output Resistance vs Supply
Voltage (V /V )
OH OL
SLAVE (MSTR = 0)
MASTER (MSTR = 1)
–25 0 25 50 75 100 125 1.5
6820 G05
)Ω(
ECNATSISER
TUPTUO
100
80
OUTPUT
SOURCING 2mA CURRENT
60
40
20
OUTPUT SINKING 3.3mA CURRENT
2.5 3.5 4.5 5.5
6820 G19

Driver Current Gain Driver Current Gain
Driver Current Gain vs Amplitude vs IBIAS Current (I ) vs Supply Voltage
PULSE AMPLITUDE VA (V)
Driver Current Gain Driver Common Mode Voltage Driver Common Mode Voltage
vs Temperature vs Temperature vs Pulse Amplitude
)Am/Am(
BIA
NIAG
23
VA(MAX) = 1.6V
22
FOR VDD > 3.3V
21
VDD = 3V VDD = 3V
19 IB = 0.1mA IB = 1mA
VA(MAX) = 1.3V
FOR VDD = 3V
0.5 1.0 1.5 2.0 0
IBIAS CURRENT (mA)
6820 G10
22.0
VA = 1V
21.5
21.0 VDD = 5V
20.5
20.0
19.5
19.0
18.5
18.0
0.2 0.4 0.6 0.8 1.0 2.5
6820 G11
21.0
19.5
18.0
3 3.5 4 4.5 5 5.5
6820 G12
–50
IB = 0.1mA, VDD = 5V
21.0
IB = 1mA, VDD = 5V
IB = 0.1mA, VDD = 3V
19.5 IB = 1mA, VDD = 3V
18.0 0
–25 0 25 50 75 100 125 –50 –25
6820 G13
EDOM
NOMMOC
REVIRD
IB = 0.1mA, VDD = 5V
IB = 0.1mA, VDD = 3V
IB = 1mA, VDD = 3V
0 25 50 75 100 125 0
PULSE AMPLITUDE (V)
6820 G14
EDOM
NOMMOC
REVIRD
5.0
4.5 IB = 0.1mA, VDD = 5V
4.0
3.5
2.5 IB = 0.1mA, VDD = 3V
1.5 IB = 1mA, VDD = 3V
0.5 1.0 1.5 2.0
6820 G15
Comparator Threshold Gain Comparator Threshold Gain Comparator Threshold Gain
vs ICMP Voltage vs Common Mode vs Temperature
ICMP VOLTAGE (V)
)V/V(
DLOHSERHT
ROTARAPMOC
0.56
0.54
0.52
0.50
0.48
0.46
0.44
0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6 1.5 2.0
COMMON MODE VOLTAGE (V)
6820 G16
DLHSERHT
0.52 VICMP = 1V VICMP = 1V
VDD = 3V VDD = 5V
0.48 VI V CM DD P = = 3 0 V .2V VI V CM DD P = = 5 0 V .2V
2.5 3.0 3.5 4.0 4.5 5.0 5.5 –50 –25
6820 G17
DLHSERHT
0.52
0.48
VICMP = 1V
VICMP = 0.2V
0 25 50 75 100 125
6820 G18

Wake-Up Pulse Amplitude
vs Dwell Time Start-Up Time
CS 3.6µs
5V/DIV
IBIAS
2V/DIV
IP-IM
1V/DIV
VDDS = 5V 1µs/DIV 6820 G06
0 MSTR = 1
WAKE-UP DWELL TIME, tDWELL (ns)
RBIAS = 2k
SPI Signal and isoSPI Pulses, MSTR = 1 SPI Signal and isoSPI Pulses, MSTR = 0
CS
SCK CS
5V/DIV 5V/DIV
MOSI SCK
MIS0 MOSI
IP-IM MIS0
2V/DIV 5V/DIV
VDD = 5V 1.2µs/DIV 6820 G21 VDD = 5V 1.2µs/DIV 6820 G22
VDDS = 3.3V VDDS = 5V
PHA = 1 PHA = 0
POL = 1 POL = 0
8
)Vm(
EKAWV
,EDUTILPMA
ESLUP
PU-EKAW
300
GUARANTEED
250 WAKE-UP REGION
200
150
100
50
150 300 450 600
6820 G20

PIN FUNCTIONS
(QFN/MSOP)
MOSI (Pin 1/Pin 2): SPI Master Out/Slave In Data. If con- V (Pin 8/Pin 9): Device Power Supply Input. Connect
nected on the master side of a SPI interface (MSTR pin a bypass capacitor of at least 0.01μF directly between
high), this pin receives the data signal output from the V and GND.
master SPI controller. If connected on the slave side of the
IM (Pin 9/Pin 10): Isolated Interface Minus Input/Output.
interface (MSTR pin low), this pin drives the data signal
input to the slave SPI device. The output is open drain, so IP (Pin 10/Pin 11): Isolated Interface Plus Input/Output.
an external pull-up resistor to V is required.
DDS MSTR (Pin 11/Pin 12): Serial Interface Master/Slave
MISO (Pin 2/Pin 3): SPI Master In/Slave Out Data. If con- Selector Input. Tie this pin to V DD if the device is on the
nected on the master side of a SPI interface (MSTR pin master side of the isolated interface. Tie this pin to GND
high), this pin drives the data signal input to the master if the device is on the slave side of the isolated interface.
SPI controller. If connected on the slave side of the inter-
SLOW (Pin 12/Pin 13): Slow Interface Selection Input. For
face (MSTR pin low), this pin receives the data signal out-
clock frequencies at or below 200kHz, or if slave devices
put from the slave SPI device. The output is open drain,
cannot meet timing requirements, this pin should be tied
so an external pull-up resistor to V is required.
DDS to V . For clock frequencies above 200kHz, this pin
SCK (Pin 3/Pin 4): SPI Clock Input/Output. If connected should be tied to GND.
on the master side of the interface (MSTR pin high), this
GND (Pin 13/Pin 14): Device Ground.
pin receives the clock signal from the master SPI control-
ICMP (Pin 14/Pin 15): Isolated Interface Comparator
ler. This input should not be pulled above V . If con-
Voltage Threshold Set. Tie this pin to the resistor divider
nected on the slave side of the interface (MSTR pin low),
between IBIAS and GND to set the voltage threshold of the
this pin outputs the clock signal to the slave device. The
interface receiver comparators. The comparator thresh-
output driver is push-pull; no external pull-up resistor
olds are set to 1/2 the voltage on the ICMP pin.
is needed.
IBIAS (Pin 15/Pin 16): Isolated Interface Current Bias.
CS (Pin 4/Pin 5): SPI Chip Select Input/Output. If con-
Tie IBIAS to GND through a resistor divider to set the
nected on the master side of the interface (MSTR pin
interface output current level. When the device is enabled,
high), this pin receives the chip select signal from the
this pin is approximately 2V. When transmitting pulses,
master SPI controller. This input should not be pulled
the sink current on each of the IP and IM pins is set to
above V . If connected on the slave side of the interface
20 times the current sourced from pin IBIAS to GND.
(MSTR pin low), this pin outputs the chip select signal
Limit the capacitance on the IBIAS pin to less than 50pF
to the slave device. The output driver is push-pull; no
to maintain the stability of the feedback circuit regulating
external pull-up resistor is needed.
the IBIAS voltage.
V (Pin 5/Pin 6): SPI Input/Output Power Supply Input.
EN (Pin 16/Pin 1): Device Enable Input. If high, this
The output drivers for the SCK and CS pins use the V
pin forces the LTC6820 to stay enabled, overriding the
input as their positive power supply. The input threshold
internal IDLE mode function. If low, the LTC6820 will go
voltages of SCK, CS, MOSI, MISO and EN are determined
into IDLE mode after the CS pin has been high for 5.7ms
by V . May be tied to V or to a supply above or below
DDS DD
(when MSTR pin is high) or after no signal on the IP/IM
V to level shift the SPI I/O. If separate from V , con-
DD DD
pins for 5.7ms (when MSTR pin is low). The LTC6820 will
nect a bypass capacitor of at least 0.01μF directly between
wake-up less than 8µs after CS falls (MSTR high) or after
V and GND.
a signal is detected on IP/IM (MSTR low).
POL (Pin 6/Pin 7): SPI Clock Polarity Input. Tie to V or
Exposed Pad (Pin 17, QFN Package Only): Exposed pad
GND. See Operation section for details.
may be left open or connected to device GND.
PHA (Pin 7/Pin 8): SPI Clock Phase Input. Tie to V or
GND. See Operation section for details.
9

BLOCK DIAGRAM
IB
RB1
RB2
+
–
Rx = +1
RPU Rx = –1
Tx = +1 IP
IDRV RM
CS Tx = –1 IM
Tx • 20 • IB
6820 BD
OPERATION
+
–
EN
VDD CS IDLE TIMEOUT 2V
READY WAKE DETECT
MSTR VDD RBIAS = RB1 + RB2
SLOW
VICMP+
167mV
3 POL
OPEN
PHA WHEN
IDLE 35k
35k
VDDS
VDDS
EN
THRESHOLD 0.5x
MOSI
MISO
SCK
GND
STUPNI
NOITARUGIFNOC
DEREWOP-DDV
NOITALSNART
IPS
DEREWOP-SDDV
CIGOL
NOITACIFILAUQ
ESLUP
GNIMIT
VDD
0.1µF
(TO MOSI IF MSTR = 0)
(TO MISO IF MSTR = 1)
The LTC6820 creates a bidirectional isolated serial port The receiver consists of a window comparator with a
interface (isoSPI) over a single twisted pair of wires, differential voltage threshold, V . When V – V
TCMP IP IM
with increased safety and noise immunity over a non- is greater than +V , the comparator detects a logic
TCMP
isolated interface. Using transformers, the LTC6820 +1. When V – V is less than –V , the comparator
IP IM TCMP
translates standard SPI signals (CS, SCK, MOSI and detects a logic –1. A logic 0 (null) indicates V – V is
IP IM
MISO) into pulses that can be sent back and forth on between the positive and negative thresholds.
twisted-pair cables.
The comparator outputs are sent to pulse timers (filters)
A typical system uses two LTC6820 devices. The first is that discriminate between short and long pulses.
paired with a microcontroller or other SPI master. Its IP
and IM transmitter/receiver pins are connected across an Selecting Bias Resistors
isolation barrier to a second LTC6820 that reproduces the
The adjustable signal amplitude allows the system to trade
SPI signals for use by one or more slave devices.
power consumption for communication robustness, and
The transmitter is a current-regulated differential driver. the adjustable comparator threshold allows the system to
The voltage amplitude is determined by the drive cur- account for signal losses.
rent and the equivalent resistive load (cable characteristic
impedance and termination resistor, R ).
M

ISOLATION BARRIER
MSTR IP IP MSTR
MASTER LTC6820 RM RM LTC6820 SLAVE
SDO MOSI IM IM MOSI SDI
SDI MISO IBIAS TWISTED-PAIR CABLE IBIAS MISO SDO
SCK SCK RB1 WITH CHARACTERISTIC IMPEDANCE RM RB1 SCK SCK
CS CS CS CS
ICMP ICMP
RB2 RB2
6820 F01
Figure 1. Typical System Using Two LTC6820 Devices
The transmitter drive current and comparator voltage isoSPI Pulse Detail
threshold are set by a resistor divider (R = R + R )
BIAS B1 B2 The isoSPI transmitter can generate three voltage levels:
between the IBIAS pin and GND, with the divided voltage
+V , 0V, and –V . To eliminate the DC signal component
A A
tied to the ICMP pin. When the LTC6820 is enabled (not
and enhance reliability, isoSPI pulses are defined as sym-
IDLE), I is held at 2V, causing a current, I , to flow
BIAS B metric pulse pairs. A +1 pulse pair is defined as a +V
A
out of the IBIAS pin. The IP and IM pin drive currents are
pulse followed by a –V pulse. A –1 pulse pair is –V
20 • I . The comparator threshold is half the voltage on
B followed by +V .
A
the ICMP pin (V ).
The duration of each pulse is defined as t . (The total
1/2PW
As an example, if divider resistor R is 1.21k and resistor
B1 isoSPI pulse duration is 2 • t ). The LTC6820 allows
R is 787Ω (so that R = 2k), then:
B2 BIAS for two different t values so that four types of pulses
2V can be transmitted, as listed in Table 1.
I = =1mA
R +R
B1 B2 Table 1. isoSPI Pulse Types
PULSE TYPE FIRST LEVEL SECOND LEVEL ENDING LEVEL
I = I = I = 20 • I = 20mA
DRV IP IM B
Long +1 +V (150ns) –V (150ns) 0V
V =2V• R B2 =I •R =788mV Long –1 –V A (150ns) +V A (150ns) 0V
ICMP B B2
R B1 +R B2 Short +1 +V A (50ns) –V A (50ns) 0V
Short –1 –V (50ns) +V (50ns) 0V
V = 0.5 • V = 394mV
TCMP ICMP
Long pulses are used to transmit CS changes. Short pulses
In this example, the pulse drive current I DRV will be 20mA, transmit data (MOSI or MISO). An LTC6820 detects four
and the receiver comparators will detect pulses with IP-IM types of communication events from the SPI master: CS
amplitudes greater than ±394mV. falling, CS rising, SCK latching MOSI = 0, and SCK latch-
ing MOSI = 1. It converts each event into one of the four
If the isolation barrier uses 1:1 transformers connected
pulse types, as shown in Table 2.
by a twisted pair and terminated with 100Ω resistors on
each end, then the transmitted differential signal ampli-
Table 2. Master Communication Events
tude (±) will be:
SPI MASTER EVENT TRANSMITTED PULSE
R CS Rising Long +1
M
V =I • =1V
A DRV CS Falling Long –1
SCK Latching Edge, MOSI = 1 Short +1
(This result ignores transformer and cable losses, which SCK Latching Edge, MOSI = 0 Short –1
will reduce the amplitude).
11

On the other side of the isolation barrier (i.e., the other end Characteristics table, these specifications are further sep-
of the cable) another LTC6820 is configured to interface arated into CS (long) and Data (short) parameters.
with a SPI slave. It receives the transmitted pulses and
A valid pulse must meet the minimum spec for t and
reconstructs the SPI signals on its output port, as shown
the maximum spec for t . In other words, the half-pulse
INV
in Table 3. In addition, the slave device may transmit a
width must be long enough to pass through the appropri-
return data pulse to the master to set the state of MISO.
ate pulse timer, but short enough for the inversion to begin
See isoSPI Interaction and Timing for additional details.
within the valid window of time.
Table 3. Slave SPI Port Output The response observed at MOSI, MISO or CS will occur
RECEIVED PULSE SPI PORT ACTION RETURN PULSE after delay t from the pulse inversion.
DEL
Long +1 Drive CS High None
Long –1 Drive CS Low Setting Clock Phase and Polarity (PHA and POL)
Short –1 Pulse
Short +1 1. Set MOSI = 1
if MISO = 0 SPI devices often use one clock edge to latch data and
2. Pulse SCK
(No Return Pulse the other edge to shift data. This avoids timing problems
Short –1 1. Set MOSI = 0 if MISO = 1)
2. Pulse SCK associated with clock skew. There is no standard to spec-
ify whether the shift or latch occurs first. There is also no
A slave LTC6820 never transmits long (CS) pulses.
requirement for data to be latched on a rising or falling
Furthermore, a slave will only transmit a short –1 pulse
clock edge, although latching on the rising edge is most
(when MISO = 0), never a +1 pulse. This allows for mul-
common. The LTC6820 supports all four SPI operating
tiple slave devices on a single cable without risk of colli-
modes, as configured by the PHA and POL Pins.
sions (see Multidrop section).
Table 4. SPI Modes
isoSPI Pulse Specifications
MODE POL PHA DESCRIPTION
Figure 2 details the timing specifications for the +1 and 0 0 0 SCK Idles Low, Latches on Rising (1st) Edge
–1 isoSPI pulses. The same timing specifications apply to 1 0 1 SCK Idles Low, Latches on Falling (2nd) Edge
either version of these symmetric pulses. In the Electrical 2 1 0 SCK Idles High, Latches on Falling (1st) Edge
3 1 1 SCK Idles High, Latches on Rising (2nd) Edge
+1 PULSE VA
VTCMP
t1/2PW
VIP – VIM
–VTCMP
tINV
–VA
tDEL
MOSI, MISO OR CS
–1 PULSE VA
tINV
VTCMP
–VTCMP
tDEL
–VA
MOSI, MISO OR CS
6820 F02
Figure 2. isoSPI Differential Pulse Detail
12

If POL = 0, SCK idles low. Data is latched on the rising isoSPI data pulse (M , M , … M ) while simultane-
N N–1 0
(first) clock edge if PHA = 0 and on the falling (second) ously latching the slave’s data bit. As the slave LTC6820
clock edge if PHA = 1. receives each data bit it will set the slave MOSI pin to
the proper state and then generate an SCK pulse before
If POL =1, SCK idles high. Data is latched on the falling
returning the slave’s MISO data (either as a Short –1
(first) clock edge if PHA = 0 and on the rising (second)
pulse, or as a null).
clock edge if PHA = 1.
At the end of communication, the final data bit sent by
The two most common configurations are mode 0 (PHA =
the slave (either as a pulse or null) will be ignored by
0 and POL = 0) and mode 3 (PHA = 1 and POL = 1)
the master controller. (The slave LTC6820 must return a
because these modes latch data on a rising clock edge.
data bit since it cannot predict when communications will
cease.) The master SPI device can then raise CS, which
isoSPI Interaction and Timing
is transmitted to the slave in the form of a Long +1 pulse.
The timing diagrams in Figure 3 and Figure 4 show how The process ends with the slave LTC6820 transitioning
an isoSPI in master mode (connected to a SPI master) CS high, and returning SCK to the idle state if PHA = 1.
interacts with an isoSPI in slave mode (connected to a
SPI slave). Figure 3 details operation with PHA = 0 (and Rise Time
shows SCK signals for POL = 0 or 1). Figure 4 provides
MOSI and MISO outputs have open-drain drivers. The rise
the timing diagram for PHA = 1. Although not shown, it
time t for the data output is determined by the pull-
RISE
is acceptable to use different SPI modes (PHA and POL
up resistance and load capacitance. R must be small
PU
settings) on the master and slave devices.
enough to provide adequate setup and hold times.
A master SPI device initiates communication by lowering
CS. The LTC6820 converts this transition into a Long –1 Slow Mode
pulse on its IP/IM pins. The pulse traverses the isolation
When configured for slave operation, the LTC6820 provides
barrier (with an associated cable delay) and arrives at the
two operating modes to ensure compatibility with a wide
IP/IM pins of the slave LTC6820. Once validated, the Long
range of SPI timing scenarios. These modes are referred
–1 pulse is converted back into a falling CS transition, this
to as fast and slow mode, and are set using the SLOW pin.
time supplied to the slave SPI device. If slave PHA = 1,
When configured for master operation, the SLOW pin set-
SCK will also leave the idle state at this time.
ting has no effect on the LTC6820 operation. In this case,
Before the master SPI device supplies the first latching it is recommended to tie the SLOW pin to GND.
clock edge (usually a rising edge, but see Table 4 for
In fast mode (SLOW pin tied to GND), the LTC6820 can
exceptions), the slave LTC6820 must transmit the initial
operate at clock rates up to 1MHz (t = 1µs). However,
slave data bit S , which it determines by sampling the
N some SPI slave devices can’t respond quickly enough to
state of MISO after a suitable delay.
support this data rate. Fast mode requires a slave to operate
If MISO = 0, the slave will transmit a Short –1 pulse to the with setup and response times of 100ns, as well as 100ns
master. The master LTC6820 will receive and decode the clock widths. In addition, allowances must be made for the
pulse and set the master MISO = 0 (matching the slave). RC rise time of MOSI and MISO’s open-drain outputs. In
However, if the slave MISO=1, the slave does not transmit slow mode (SLOW pin tied to V+), the timing requirement
a pulse. The master will interpret this null response as a 1 are relaxed at the expense of maximum data rate. As indi-
and set the master MISO = 1. This makes it possible to cated in the Electrical Characteristics, the clock pulses and
connect multiple slave LTC6820’s to a single cable with required setup and response times are increased to 0.9µs
no conflicting signals (see Multidrop section). minimum. Accordingly, the minimum t CLK (controlled by
the master) must be limited to 5µs. The SLOW pin setting
After the falling CS sequence, every latching clock edge
has no effect on the master LTC6820 (with MSTR = 1).
on the master converts the state of the MOSI pin into an
13

14
6t
KLCt
7t
SC
5t
3t
4t
)0
=
LOP(
KCS
)1
2t
1t
ISOM
8t
11t
ESIRt
OSIM
01t
)D(LEDt
9t
OSI
BSC
0M
1-NM
NM
DERONGI
2-NS
1-NS
NS
)SC(LEDt
TON
SEOD
EVALS
41t
NTRt
1+
TIMSNART
61t
31t
21t
81t
ELPMAS
0005
0054
0004
0053
0003
0052
0002
0051
0001
005
30F
0286
)sn(
EMIT
AHP(
margaiD
gnimiT
reviecsnarT
.3
erugiF

6t
KLCt
7t
5t
3t
4t
2t
1t
8t
11t
9t
OM
1-NM
NM
DERONGI
2-NS
1-NS
NS
1 T
+ O
N T
I S M
E S O N D A
E R V T ALS
41t
NTRt
)SC(LE
6 D 1 t t
71t
31t
51t
21t
81t
0005
0054
0004
0053
0003
0052
0002
0051
0001
005
40F
0286
)sn(
EMIT
AHP(
margaiD
gnimiT
reviecsnarT
.4
erugiF

Figure 6 demonstrates slow mode, as compared to fast
VDD VDD
mode in Figure 5.
+ – VIC 3 MP+ 167mV
SCK POS OPEN WHEN IDLE
RM
5V/DIV IM
VDD = 5V 200ns/DIV 6820 F05
NEG POS
VDDS = 5V
Figure 5. Fast Mode (SLOW = 0) NEG
20 • IB
6820 F07
2V/DIV Figure 7. Pulse Driver
SCK
VDD = 5V 1µs/DIV 6820 F06
VDDS = 5V
Figure 6. Slow Mode (SLOW = 1)
IP and IM Pulse Driver
The IP and IM pins transmit and receive the isoSPI pulses. 0
The transmitter uses a current-regulated driver (see
VIP OR VIM (V)
Figure 7) to establish the pulse amplitude, as determined
by the IBIAS pin current, I , and the load resistance. The
sinking current source is regulated to 20x the bias current
I . The sourcing current source operates in a current- B
starved (resistive) manner to maintain the sourcing pin’s
voltage near V , as shown in Figure 8 and Figure 9. The
common mode voltage (while driving) is dependent on
bias current and output amplitude.
The output driver will regulate the common mode and
peak swing of IP and IM to the proper levels, allowing for
a broad range of output amplitude with fairly flat gain, as
shown in Figure 10.
16
KNIS/ECRUOS
25
SOURCING OUTPUT
1V AMPLITUDE
SINKING OUTPUT
0.5 1 1.5 2 2.5 3
6820 F08
Figure 8. Drive Source/Sink vs Output Voltage
TUPTUO
SOURCING
2.5 OUTPUT
VCM
SINKING
OUTPUT
6820 F09
Figure 9. Output Voltages and Common Mode vs Amplitude

Figure 10. A Current Gain vs Amplitude
IB
IS = 1mA
–1.5
TIME (ns)
6820 F10
Figure 11. Transmitting and Receiving Data
This type of driver does not require a center-tapped trans-
former, but such a transformer may improve noise immu-
nity, especially if it has a common mode choke. See the
Applications Information section for additional details.
Receiver Common Mode Bias
When not transmitting, the output driver maintains IP and
IM near V with a pair of 35k (R ) resistors to a volt-
DD IN
age of V – V /3 – 167mV. This weak bias net-work DD ICMP
holds the outputs near their desired operating point with-
out significantly loading the cable, which allows a large Figure 12. State Diagram
number of LTC6820’s to be paralleled without affecting
signal amplitude.
Figure 11 shows the differential and single-ended IP and
IM signals while transmitting and receiving data. The
driver forces the common mode voltage it needs while
transmitting, then it returns to the bias level with a time
constant of R • C /2, where C is the sum of the
IN LOAD LOAD
capacitance at the IP and IM pins.
When the LTC6820 is in low power IDLE mode, the bias
voltage is disconnected from the 35k resistors, resulting
in a 70k differential load.
State Diagram
During periods of no communication, a low current IDLE
(or shutdown) state is available to reduce power. In the
IDLE state the LTC6820 shuts down most of the circuitry.
A slave device uses a low current comparator to monitor
for activity, so it has larger IDLE current.
TRANSMIT SHORT +1
IP IM
1.5 RECEIVE SHORT –1
–0.5
–1.0 VDD = 3V
200 400 600 800 1000
6820 F11
IDLE WAKE-UP SIGNAL
TIMEOUT (tREADY)
(tIDLE)
NO ACTIVITY
ON isoSPI TRANSMIT/RECEIVE
PORT
ACTIVE
6820 F12
In the READY state all circuitry is enabled and ready to
transmit or receive, but is not actively transmitting on IP
and IM.
Supply current increases when actively communicating,
so this condition is referred to as the ACTIVE state.
Supply Current
Table 5 provides equations for estimating I in each state.
The results are for average supply current (as opposed
to peak currents), and make the assumption that a slave
is returning an equal number of 0s and 1s (significant
because the slave doesn’t generate +1 data pulses, so the
average driver current is smaller).

Figure 15 demonstrates a simple procedure for waking
Table 5. I Equations
a master (MSTR = 1) LTC6820 and its connected slave
STATE MSTR ESTIMATED I
(MSTR = 0). A negative edge on CS causes the master
IDLE 0 (slave) 2µA
to drive IBIAS to 2V and, after a short delay, transmit a
1 (master) 1µA
long +1 pulse. (If CS remains low throughout t , the
READY 0 or 1 1.7mA + 3 • I READY
LTC6820 would first generate a –1 pulse, then the +1
ACTIVE 0 (slave) 2mA+ ⎛ ⎜ ⎜⎜ 3+20• 100
t
ns•0.5⎟ ⎟⎟ ⎞ •IB pulse when CS returns high). The long pulse serves as a
⎝ CLK ⎠ wake-up signal for the slave device, which responds by
1 (master) 2mA+ ⎛ ⎜ ⎜⎜ 3+20• 1
t
00ns⎞ ⎟ ⎟⎟ •IB driving its IBIAS pin to 2V and entering the READY state.
⎝ CLK ⎠
240mV
IDLE Mode and Wake-Up Detection IP IPAC
240ns DELAY
To conserve power, an LTC6820 in slave mode (MSTR = 0) |IPAC–IMAC| > 240mV (FILTER)
will enter an IDLE state after 5.7ms (t
) of inactivity on 240ns IM IMAC SLAVE
the IP/IM pins. In this condition I is reduced to less MASTER
than 6µA and the SPI pins are idled (CS = 1, MOSI = 1 CS
WAKE-UP
and SCK = POL).
IDLE TIMER
The LTC6820 will continue monitoring the IP and IM pins
using a low power AC-coupled detector. It will wake up EN tREADY READY
when it sees a differential signal of 240mV or greater tIDLE (IBIAS = 2V)
6820 F13
that persists for 240ns or longer. In practice, a long (CS)
Figure 13. Wake-Up Detection and IDLE Timer
isoSPI pulse is sufficient to wake the device up. Once the
comparator generates the wake-up signal it can take up
to 8µs (t ) for bias circuits to stabilize. REJECTS
COMMON MODE
NOISE
Figure 14 details the sequence of waking up a slave LTC6820
(placing it in the READY state), using it to communicate,
IM
then allowing it to return to the low power IDLE state.
tDWELL tIDLE
A LTC6820 in master mode (MSTR = 1) doesn’t use the READY tREADY OK TO COMMUNICATE
wake-up detection comparator. A falling edge on CS will 6820 F14
enable the isoSPI port within t , and the LTC6820 Figure 14. Slave LTC6820 Wake-Up/Idle Timing
will transmit a long (CS) pulse as it leaves the IDLE state.
(The polarity of the pulse matches the CS state at the end
ALLOW >2 • tREADY TO WAKE
of t ). MASTER AND SLAVE
MASTER CS
The master LTC6820 will remain in the READY/ACTIVE
tREADY tIDLE
MASTER
state as long as CS = 0. If CS transitions high and EN = 0
it will enter the IDLE state, but not until t IDLE expires. tDWELL tREADY tIDLE
This prevents the device from shutting down between SLAVE
data packets. SLAVE CS
6820 F15
In either master or slave mode the IDLE feature may be Figure 15. Master and Slave Wake-Up/Idle Sequence
disabled by driving EN high. This forces the device to
remain “ready” at all times.

Multidrop n The SPI slaves must be addressable, because they will
all see the same CS signal (as decoded by each slave
Multiple slaves can be connected to a single master by con-
LTC6820).
necting them in parallel (multidrop configuration)along one
cable. As shown in Figure 16, the cable should be terminated n When not addressed, the slave SDO must remain high.
only at the beginning (master) and the end. In between, the
When a slave is not addressed, its LTC6820 will not trans-
additional LTC6820’s and their associated slave devices will
mit data pulses as long as MISO (the SPI device’s SDO)
be connected to “stubs” on the cable. These stubs should
remains high. This eliminates the possibility for collisions,
be kept short, with as little capacitance as possible, to avoid
as only the addressed slave device will ever be returning
degrading the termination along the cable.
data to the master.
The multidrop scheme is only possible if the SPI slaves
have certain characteristics:
MASTER LTC6820 LTC6820 SLAVE 1
MSTR MSTR
SDO MOSI IP IP MOSI 1 SDI
SDI MISO RM MISO SDO
SCK SCK IM IM SCK SCK
1 1
LTC6820 SLAVE 2
IP 2
MOSI SDI
MISO SDO
IM SCK SCK
2 2
LTC6820 SLAVE 3
IP 3
MOSI SDI
RM
MISO SDO
IM SCK SCK
3 3
6820 F16
Figure 16. Multidropping Multiple Slaves on a Single Cable
19

APPLICATIONS INFORMATION
isoSPI Setup For cables over 50 meters:
The LTC6820 allows each application to be optimized for I = 1mA
power consumption or for noise immunity. The power
V = (20 • I ) • (R /2)
A B M
and noise immunity of an isoSPI system is determined
by the programmed I B current. The I B current can range V TCMP = 1/4 • V A
from 0.1mA to 1mA. A low I reduces the isoSPI power
B V = 2 • V
ICMP TCMP
consumption in the READY and ACTIVE states, while a
R = V /I
high I increases the amplitude of the differential signal B2 ICMP B
voltage V A across the matching termination resistor, R M . ⎛ 2V⎞
⎜ ⎟
R = –R
I is programmed by the sum of the R and R resis-
B1 ⎜⎜
I
⎟⎟ B2
B B1 B2 ⎝ B ⎠
tors connected between the I pin and GND. For most
applications setting I to 0.5mA is a good compromise The maximum data rate of an isoSPI link is determined by
between power consumption and noise immunity. Using the length of the cable used. For cables 10 meters or less
this I setting with a 1:1 transformer and R = 120Ω, R the maximum 1MHz SPI clock frequency is possible. As
B M B1
should be set to 2.8k and R set to 1.2k. In a typical CAT5 the length of the cable increases the maximum possible
B2
twisted pair these settings will allow for communication SPI clock rate decreases. This is a result of the increased
up to 50m. propagation delays through the cable creating possible
timing violations.
For applications that require cables longer than 50m it is
recommended to increase the amplitude V by increasing Cable delay affects three timing specifications, t , t ,
A CLK 6
I to 1mA. This compensates for the increased insertion and t . In the Electrical Characteristics table, each is
B 7
loss in the cable and maintains high noise immunity. So derated by 100ns to allow for 50ns of cable delay. For
when using cables over 50m and, again, using a trans- longer cables, the minimum timing parameters may be
former with a 1:1 turns ratio and R = 120Ω, R would calculated as shown below:
M B1
be 1.4k and R would be 600Ω.
B2 t , t , and t > 0.9µs + 2 • t
CLK 6 7 CABLE
Other I settings can be used to reduce power consump-
tion or increase the noise immunity as required by the Pull-Up Resistance Considerations
application. In these cases when setting V and choos-
ICMP The data output (MOSI if MSTR = 0, MISO if MSTR =
ing R and R resistor values the following rules should
B1 B2 1) requires a pull-up resistor, R . The rise time t is
PU RISE
be used:
determined by R and the capacitance on the pin. R
PU PU
For cables 50 meters or less: must be small enough to provide adequate setup and hold
times. For a slave device, the time constant must be less
I = 0.5mA
B than t and t . In fast mode, 50ns is recommended.
12 14
V = (20 • I ) • (R /2)
A B M R < 50ns/C
PU LOAD
V = 1/2 • V
TCMP A Larger pull-up resistances, up to 5k, can be used in slow
V = 2 • V mode.
ICMP TCMP
R = V /I
B2 ICMP B
⎛ 2V⎞
⎜ ⎟
R = –R
B1 ⎜⎜ ⎟⎟ B2
I
⎝ B ⎠

Table 6. Typical R and R Values
B1 B2
MAX CABLE TURNS TERMINATION READY
LENGTH RATIO RESISTANCE I V V V R R IDRV CURRENT
B A TCMP ICMP B2 B1
100m 1 :1 120Ω 1mA 1.2V 0.3V 0.6V 604Ω 1.4k 20mA 4.7mA
50m 1 :1 120Ω 0.5mA 0.6V 0.3V 0.6V 1.21k 2.8k 10mA 3.2mA
100m 1 :1 75Ω 1mA 0.75V 0.19V 0.38V 374Ω 1.62k 20mA 4.7mA
50m 1 :1 75Ω 0.5mA 0.375V 0.19V 0.38V 750Ω 3.24k 10mA 3.2mA
Transformer Selection Guide For optimal common mode noise rejection, choose a cen-
ter-tapped transformer or a transformer with an integrated
As shown in Figure 1, a transformer or a pair of transform-
common mode choke. The center tap can be tied to a 27pF
ers are used to isolate the IP and IM signals between the
or smaller capacitor (larger will restrict the driver’s abil-
two LTC6820’s. The isoSPI signals have programmable
ity to set the common mode voltage). If the transformer
pulse amplitudes up to 1.6V, and pulse widths of 50ns
has both a center tap and common mode choke on the
and 150ns. To meet these requirements, choose a trans-
primary side, a larger capacitor may be used.
former having a magnetizing inductance ranging from
50µH to 350µH, and a 1:1 or 2:1 turns ratio. Minimizing Table 7 shows a recommended list of transformers for use
transformer insertion loss will reduce required transmit with the LTC6820. 10/100BaseTX Ethernet transformers
power; generally an insertion loss of less than –1.5dB is are inexpensive and work very well in this application.
recommended. Ethernet transformers often include a common mode
choke, which will improve common mode rejection as
compared to other transformers.
Table 7. Recommended Transformers
MANUFACTURER PART NUMBER ISOLATION VOLTAGE TURNS RATIO CENTER TAP CM CHOKE
PCA EPF8119SE 1500V 1:1 Yes Yes
RMS
Halo TG110-AE050N5LF 1500V 1:1 Yes Yes
Pulse PE-68386NL 1500V DC 1:1 No No
Murata 78613/3C 1000V 1:1 Yes No
Murata 78604/3C 1000V 2:1 No No
Pulse HX1188NL 1500V 1:1 Yes Yes
EPCOS B82804A0354A110 1500V DC 1:1 No No
2:1 Transformers
µC LTC6820 LTC6820 LTC2452
MSTR 2:1 1:2 MSTR
SDO MOSI IP IP
SDI MISO 480Ω 480Ω MISO SDO
Single-Transformer Isolation
µC LTC6820 LTC6820 LTC6802
MSTR MSTR
SDO MOSI IP IP MOSI SDI
SDI MISO 120Ω 120Ω MISO SDO
6820 F17
Figure 17. Alternative Isolation Barriers
21

Capacitive Isolation Barrier use a transformer with a center tap and a common mode
choke as shown in Figure 19. The center tap of the trans-
In some applications, where the environment is relatively
former should be bypassed with a 27pF capacitor. The
noise free and only galvanic isolation is required, capaci-
center tap capacitor will help attenuate common mode
tors can be used in place of transformers as the isolation
signals. Large center tap capacitors should be avoided as
barrier. With capacitive coupling, the twisted pair cable
they will prevent the isoSPI transmitters common mode
is driven by a voltage and is subject to signal loss with
voltage from settling.
cable length. This low cost isolated solution can be suit-
able for short distance interconnections (1 meter or less), To improve common mode current rejection a common
such as between adjacent circuit boards or across a large mode choke should also be placed in series with the IP
PCB. The capacitors will provide galvanic isolation, but no and IM lines of the LTC6820. The common mode choke
common mode rejection. This option uses the drivers in will both increase EMI immunity and reduce EMI emission.
a different way, by using pull up resistors to maintain the When choosing a common mode choke, the differential
common mode near V , only the sinking drive current mode impedance should be 20Ω or less for signals 50MHz
has any effect. Figure 18 shows an example application and below. Generally common mode chokes similar to
circuit using a capacitive isolation barrier capable of driv- those used in Ethernet applications are recommended.
ing 1 meter of cable.
Table 8. Recommended Common Mode Chokes
VOLTAGE DIFFERENTIAL COMMON MODE
MANUFACTURER PART NUMBER CAPACITANCE RATING IMPEDANCE AT IMPEDANCE AT
MANUFACTURER PART NUMBER 50MHz 50MHz
Murata GCM188R72A104KA64 100nF 100V
TDK ACT45B-220-2P 20Ω 5000Ω
EMC
When using the LTC6820, for the best electromagnetic
compatibility (EMC) performance it is recommended to
Capacitive Isolation
µC LTC6820 LTC6820 LTC2640
100nF MSTR
SDO MOSI IP IP MOSI SDI
SDI MISO MISO
100nF
6820 F18
Figure 18. Capacitive Isolation Barrier
IP 27pF
IM 120Ω
6820 F19
Figure 19. Connection of Transformer and Common Mode Choke
22

Layout of the isoSPI signal lines also plays a significant injects current into the twisted-pair lines at set levels over
role in maximizing the immunity of a circuit. The following a frequency range of 1MHz to 400MHz. With the mini-
layout guidelines should be followed: mum I current, 0.1mA, the isoSPI serial link has been
shown to pass a 40mA BCI test with no bit errors. A 40mA
1. The transformer should be placed as close to the iso-
BCI test level is sufficient for most industrial applications.
SPI cable connector as possible. The distance should
Automotive applications tend to have a higher BCI require-
be kept less than 2cm. The LTC6820 should be placed
ment so the recommended I is set to 1mA, the maximum
at least 1cm to 2cm away from the transformer to help B
power level. The isoSPI system has been shown to pass a
isolate the IC from the magnetic coupling fields.
200mA BCI test with no transmitted bit errors. The 200mA
2. On the top layer, no ground plane should be placed test level is typical for automotive testing.
under the magnetic, the isoSPI connector, or in
between the transformer and the connector. Software Layer
3. The IP and IM traces should be isolated from sur- The isoSPI physical layer has high immunity to EMI and
rounding circuits. No traces should cross the IP and is not particularly susceptible to bit errors induced by
IM lines, unless separated by a ground plane within noise, but for best results in a high noise environment it
the printed circuit board. is recommended to implement a software layer that uses
an error detection code like a cyclic redundancy check
The isoSPI drive currents are programmable and allow for
or check sum. Error detection codes will allow software
a tradeoff between power consumption and noise immu-
detection of any bit error and will notify the system to retry
nity. The noise immunity of the LTC6820 has been evalu-
the last erroneous serial communication.
ated using a bulk current injection (BCI) test. The BCI test
1.5cm 1cm
IM
CONNECTOR
6820 F20
Figure 20. Example Layout
23

TYPICAL APPLICATIONS
Remote Sensor Monitor with Micropower Shutdown
LTC6820 2.8k
EN IBIAS
ICMP 1.21k
1.21k 2.8k
5V VDDS GND LTC6820
100nF SLOW IBIAS EN
2k VDD 5V ICMP
MSTR 100nF GND CS
MISO POL SLOW SCK
MOSI PHA MSTR MISO
1 16 1 16
SCK IP IP MOSI
CS IM IM
120Ω 2 15 2 15 120Ω PHA
POL
VDD VDDS
3 14 3 14
HX1188NL HX1188NL 3V
LT6656-3
+ 1µF
100nF 3.6V
VREF VCC
+ IN+
TO SENSOR LTC2452 SCK
– IN– CS
6820 TA02
IQ SHUTDOWN = 3.7µA
100 Meter Remote DAC Control
LTC6820 1.4k
EN IBIAS
ICMP 604Ω
604Ω 1.4k
3V VDDS GND LTC6820
100nF SLOW IBIAS EN
2k VDD 5V ICMP
MSTR 100nF GND CS
MISO POL SLOW SCK
MOSI PHA MSTR MISO
1 16 1 16
SCK IP IP
CS IM IM MOSI
120Ω 2 15 2 15 120Ω PHA 2k
POL
VDD VDDS
3 14 3 14
HX1188NL HX1188NL 3V
LT6656-3
+ 1µF
100nF 3.6V
VREF VCC
SDI
VOUT OUT LTC2640 SCK
CS
6820 TA03
GND
24

Interfacing to Addressable Stack of LTC6804-2 Multicell Battery Monitors
VREG LTC6804-2
ISOMD
A3
A2
A1
A0
806Ω
IPA ICMP
120Ω 1.21k
IMA VM
VREG LTC6804-2
A3
A2
A1
A0
1.21k
LTC6820 806Ω
EN IBIAS 1
ICMP 1.21k VREG LTC6804-2
5V VDDS GND ISOMD
100nF SLOW A3
2k VDD 5V A2
MSTR 100nF A1
MISO POL A0
MOSI PHA 0 806Ω
SCK IP IPA ICMP
CS IM 120Ω 1.21k
6820 TA05 0

Battery Monitoring System Using a Multidrop isoSPI Link
LTC6803-2
VSTACK3
1.21k 806Ω GND3
LTC6820 GND3 A3
A2 100Ω
IBIAS EN A1
ICMP MOSI MOSI A0
GND MISO MISO VREG CZT3055
GND3 VDD3 SLOW SCK SCK
MSTR CS CS
2k
IP VDDS
120Ω IM POL 2k
VDD PHA
VDD3
LTC6803-2
VSTACK2
1.21k 806Ω GND2
LTC6820 GND2 A3
A2 100Ω
IBIAS EN A1
GND2 VDD2 SLOW SCK SCK
IP VDDS
IM POL 2k
VDD2
LTC6820 806Ω LTC6803-2
VSTACK1
EN IBIAS 1.21k 806Ω LTC6820 GND1 A3 GND1
ICMP 1.21k A2 100Ω
5V VDDS GND IBIAS EN A1
100nF SLOW
2k VDD 5V
MSTR 100nF GND1 VDD1 SLOW SCK SCK
MISO POL
MOSI PHA
SCK IP IP VDDS
CS IM 120Ω IM POL 2k
VDD1
6820 TA04
26

PACKAGE DESCRIPTION
UD Package
16-Lead Plastic QFN (3mm × 3mm)
(Reference LTC DWG # 05-08-1700 Rev A)
Exposed Pad Variation AA
0.70 ±0.05
3.50 ±0.05 1.65 ±0.05
2.10 ±0.05 (4 SIDES)
PACKAGE OUTLINE
0.25 ±0.05
0.50 BSC
RECOMMENDED SOLDER PAD PITCH AND DIMENSIONS
BOTTOM VIEW—EXPOSED PAD
R = 0.115 PIN 1 NOTCH R = 0.20 TYP
3.00 ±0.10 0.75 ±0.05 TYP OR 0.25 × 45° CHAMFER
(4 SIDES) 15 16
PIN 1 0.40 ±0.10
TOP MARK
(NOTE 6) 1
1.65 ±0.10 2
(4-SIDES)
(UD16 VAR A) QFN 1207 REV A
0.200 REF 0.25 ±0.05
0.00 – 0.05 0.50 BSC
NOTE:
1. DRAWING CONFORMS TO JEDEC PACKAGE OUTLINE MO-220 VARIATION (WEED-4)
2. DRAWING NOT TO SCALE
3. ALL DIMENSIONS ARE IN MILLIMETERS
4. DIMENSIONS OF EXPOSED PAD ON BOTTOM OF PACKAGE DO NOT INCLUDE
MOLD FLASH. MOLD FLASH, IF PRESENT, SHALL NOT EXCEED 0.15mm ON ANY SIDE
5. EXPOSED PAD SHALL BE SOLDER PLATED
6. SHADED AREA IS ONLY A REFERENCE FOR PIN 1 LOCATION
ON THE TOP AND BOTTOM OF PACKAGE
27

PACKAGE DESCRIPTION
MS Package
16-Lead Plastic MSOP
(Reference LTC DWG # 05-08-1669 Rev A)
0.889 ±0.127
(.035 ±.005)
5.10
3.20 – 3.45
(.201)
(.126 – .136)
MIN
4.039 ±0.102
0.305 ±0.038 0.50 (.159 ±.004)
(.0120 ±.0015) (.0197) (NOTE 3) 0.280 ±0.076
TYP BSC
16151413121110 9 (.011 ±.003)
RECOMMENDED SOLDER PAD LAYOUT REF
DETAIL “A” 3.00 ±0.102
0.254 4.90 ±0.152
(.118 ±.004)
(.010) 0° – 6° TYP (.193 ±.006) (NOTE 4)
GAUGE PLANE
0.53 ±0.152
1234567 8
(.021 ±.006) 1.10 0.86
(.043) (.034)
DETAIL “A”
MAX REF
0.18
(.007)
SEATING
PLANE 0.17 – 0.27 0.1016 ±0.0508
(.007 – .011) (.004 ±.002)
TYP 0.50
NOTE: (.0197) MSOP (MS16) 0213 REV A
1. DIMENSIONS IN MILLIMETER/(INCH) BSC
2. DRAWING NOT TO SCALE
3. DIMENSION DOES NOT INCLUDE MOLD FLASH, PROTRUSIONS OR GATE BURRS.
MOLD FLASH, PROTRUSIONS OR GATE BURRS SHALL NOT EXCEED 0.152mm (.006") PER SIDE
4. DIMENSION DOES NOT INCLUDE INTERLEAD FLASH OR PROTRUSIONS.
INTERLEAD FLASH OR PROTRUSIONS SHALL NOT EXCEED 0.152mm (.006") PER SIDE
5. LEAD COPLANARITY (BOTTOM OF LEADS AFTER FORMING) SHALL BE 0.102mm (.004") MAX
28

REVISION HISTORY
REV DATE DESCRIPTION PAGE NUMBER
A 06/13 Web hyperlinks added. 1 to 30
Note 8 added to Electrical Characteristics section. 5
B 01/17 Patent Information added. 1
Web Links updated. All
C 05/19 Specifications for isoSPI Timing-Master modified to support operation up to 2Mbps 4
Information furnished by Analog Devices is believed to be accurate and reliable. However, no responsibility is assumed by Analog 29
Devices for its use, nor for any infringements of patents or other rights of third parties that may result from its use. Specifications
subject to change without notice. No license Fiso gr rmanoterde biny fiomrpmlicaattiioonn owr wotwhe.arwniasleo ugn.cdeorm any patent or patent rights of Analog Devices.

TYPICAL APPLICATION
Interfacing to Daisy-Chained Stack of LTC6804-1 Multicell Battery Monitors
LTC6804-1
VREG
IPB
IMB IBIAS
GND4
VREG
120Ω
IMB IBIAS
LTC6820 806Ω
EN IBIAS GND3
ICMP 1.21k
5V VDDS GND VREG
100nF SLOW ISOMD
2k VDD 5V
120Ω
MSTR 100nF
MISO POL IMB IBIAS
MOSI PHA 806Ω
SCK IP IPA ICMP
CS IM 120Ω 120Ω 1.21k
6820 TA06 GND2
RELATED PARTS
PART NUMBER DESCRIPTION COMMENTS
LTC6803-2/ Multicell Battery Stack Monitor with an Individually Functionality Equivalent to LTC6803-1/LTC6803-3, Allows for Parallel
LTC6803-4 Addressable SPI Interface Communication Battery Stack Topologies
LTC6803-1/ Multicell Battery Stack Monitor with Daisy-Chained Functionality Equivalent to LTC6803-2/LTC6803-4, Allows for Multiple
LTC6803-3 SPI Interface Devices to Be Daisy Chained
LTC6903 1kHz to 68MHz Programmable Silicon Oscillator with Frequency Resolution of 0.01%. No External Components Required.
SPI Interface Operates on 2.7V to 5.5V
LTC6804-1/ Multicell Battery Stack Monitor with Built-In isoSPI Includes isoSPI Interfaces for Communication with Master LTC6820
LTC6804-2 Interface and to other LTC6804 Devices
05/19
30 www.analog.com
For more information www.analog.com  ANALOG DEVICES, INC. 2012-2018
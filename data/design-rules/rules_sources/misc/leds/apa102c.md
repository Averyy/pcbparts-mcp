Source: https://www.lcd-module.de/eng/pdf/zubehoer/APA102C.pdf
Retrieved: 2026-11-09

[PDF: 12 pages.]

2018/10/11


400-800
APA-102C

1100-2000

-NEW-260

200-800


-40°C~+70°C


5.1 MHz


CKO compared with CKI


# APA


APA ELECTRONIC CO., LTD.


#### Three-way constant current 256-level lantern driver chip


Overview
AP A102 is a full color point source LED driver
chip
It uses a CMOS process to provide three
constant current drives. The three-wire
transmission scheme (DATA, CLOCK and GND)
is used for built-in regeneration to increase the
transmission distance. It is used to drive display
light conversion, various character
transformations, and color animation patterns.
Offline or online operation according to
different controller and customer different form
requirements.
This product has excellent performance, clear
visual effect, simple cascading mode, and is most
suitable for applying large-scale point source
pixel screen; stable data transmission and strong
anti-interference ability.


Provide DIE package.


Pin map


Characteristics: IC input voltage is
4.5V~5.5V & led light is off by default
when led chip is powered initially;

Built-in fixed constant current and
external feedback mode optional,
three-way drive
Moving, each drive current is 18mA;


256 levels of grayscale adjustable;
Built-in ring vibration (5.1MHZ) supports

supports uninterrupted FREE-RUN
modulation output to maintain the picture
still function;
Maximum serial input data clock
PWM :20KHz,frequency 30MHZ (lighting
application When the clock frequency is
controlled below 2MHz)

Data signal phase-locked regeneration,
cascaded at 1MHZ data transmission speed
Point source can reach 1000;


Adopt special global clock latching
mode to make the picture more consistent;


APA102(DIE) R: RED  G: GREEN B: BLUE


# APA

NO sign


1 DOUT Serial data output。


2 COUT Serial clock output。


APA ELECTRONIC CO., LTD.
Function Description


3 VOUT Internal working voltageVCC>4.5V时，4.5VRegulated output，VCC<4.5V ，Vout=VCC


，External 0.1uF capacitor to ground。


4 VCC voltage，4.5-5.5V。


5、6、7 R、G、B Constant current output port


8 GND GRAND。
10 CIN Serial clock input, built-in pull-up。


11 DIN Serial data input, built-in pull-up。

### Functional framework:


5.1 APA102 Functional block diagram

### Communication protocol and timing：


1. The first 32 bits of "0" are the start frame, which is entered at the rising edge of Cin, and the


timing DIN is preceded by CIN;


2 **.** T flag is three "1"


3 **.** D D3, D2, D1 and D0 are 32-level brightness adjustment, D4 is the highest position;


4 **.** G y level data should be high first, and it is blue green and red.

### Electrical parameter（Ta = 25℃, Vss = 0 V）


APA ELECTRONIC CO., LTD.
# APA

Limit parameter：

UNIT
parameter symbol range


voltage VDD 2.5 ～7.5 V

LED voltage VLED 3～7.5 V
Data clock frequency FCLK 30 MHZ


Maximum LED output current Iomax 18 mA


Channel current deviation DIO 片内<3%，片间<5% %

Power loss PD <400 mW
Welding temperature TM 300(8S) ℃


Operating temperature Topt -30 ～ +85 ℃


Storage temperature Tstg -65 ～ +120 ℃
Recommended working parameters：


parameter symbol range UNIT


voltage VDD 4.5～5.5 V


LED voltage VLED 3～7.5 V


Regulated output voltage VOUT 4.5 ±0.3% V


Input voltage VIN -0.4-VOUT+0.4 V


Data clock frequency FCLK 0-5 MHZ


Clock high width TCLKH >30 ns


Clock low width TCLKL >30 ns


Time when data was created TSETUP >10 ns


Data retention time THOLD >5 ns


Power consumption PD <300 mW


Operating temperature TOP -25～+80 ℃


Timing parameter：(T=25℃,VCC=5V)


parameter symbol range unit


Input signal maximum rise and fall times TR VCC=5V <500 ns


Input signal maximum rise and fall times TF VCC=5V <400 ns


Cascaded output signal maximum rise time and fall time TTHH CL=30pF,RL=1K <15 ns


Cascaded output signal maximum rise time and fall time TTHL CL=30pF,RL=1K <15 ns


Cascaded output signal maximum delay time TPD CL=30pF,RL=1K <15 ns


Cascaded output signal maximum delay time TCO CL=30pF,RL=1K <15 ns


Drive output minimum PWM turn-on width TONMIN IOUT=0~20mA 200 ns


Drive output signal maximum on and off time TON IOUT=0~20mA <80 ns
Logic level normal working range（Ta = -20 ～ +80℃，Vss = 0 V）


parameter symbol Min. typical Max. unit Test Conditions


Logic supply voltage VDD － 5 － V －


High level input voltage VIH 0.7 VDD － VDD V －


Low level input voltage VIL － － 0.3VDD V －


Recommendation: Be sure to bake according to the requirements before use to ensure
quality.



MSL:5a


260
230


260°


230°


**Change History**


## 金建電子有限公司

APA ELECTRONIC CO., LTD


11 OCT 18 REV.01 1st released copy mfg p/n : APA-102C-NEW-260


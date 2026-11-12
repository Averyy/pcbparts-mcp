Source: https://cdn.sparkfun.com/assets/e/1/0/f/b/WS2812C-2020_V1.2_EN_19112716191654.pdf
Retrieved: 2026-11-09

[PDF: 9 pages.]

# **WS2812C-2020**


#### **Intelligent control LED**


#### **integrated light source**


**Features and Benefits**
 The control integrated circuit and the LED share the only power source.
 **5mA** operating current per channel.
 Control circuit and RGB chip are integrated in a package of **2020** components, to form a complete addressable pixel.
 Built-in signal reshaping circuit, after wave reshaping to the next driver, ensure wave-form distortion not accumulate.
 Built-in electric reset circuit and power lost reset circuit.
 Each pixel of the three primary color can achieve 256 brightness display, completed 16777216 color full color display,
and scan frequency is of **2KHz** .
 Cascading port transmission signal by single line.
 Any two point the distance not more than 3m transmission signal without any increase circuit.
 When the refresh rate is 30fps, cascade number are not less than 1024 pixels.
 Send data at speeds of 800Kbps.
 The color of the light is highly consistent, cost-effective..
**Applications**
 Full-color module, Full color soft lights a lamp strip.
 LED decorative lighting, Indoor/outdoor LED irregular screen, game machine and amusement equipment etc.
**General description**

WS2812B-2020 is an intelligent control LED light source, its exterior adopts the latest MOLDING packaging technology,
the control circuit and RGB chips are integrated in a package of **2020** component. Its internal includes intelligent digital port
data latch and signal reshaping amplification drive circuit. Also include a precision internal oscillator and a voltage
programmable constant current control part, effectively ensuring the pixel point light color height consistent.

The data transfer protocol use single NZR communication mode. After the pixel power-on reset, the DIN port receive data
from controller, the first pixel collect initial 24bit data then sent to the internal data latch, the other data which reshaping by the
internal signal reshaping amplification circuit sent to the next cascade pixel through the DO port. After transmission for each
pixel, the signal to reduce 24bit. pixel adopt auto reshaping transmit technology, making the pixel cascade number is not
limited the signal transmission, only depend on the speed of signal transmission.

RESET time **>280μs**, it won't cause wrong reset while interruption, it supports the lower frequency and inexpensive MCU.
Refresh Frequency updates to **2KHz**, Low Frame Frequency and No Flicker appear in HD Video Camera, it improve
excellent display effect.

LED with low driving voltage, environmental protection and energy saving, high brightness, large scattering angle, good
consistency, low power, long life and other advantages. The control chip integrated in LED above becoming more simple
circuit, small volume, convenient installation.
**Mechanical Dimensions**


**1** / **9**
**http://** [www.world-semi.com](http://www.world-semi.com)


# **WS2812C-2020**


#### **Intelligent control LED**


**PIN Configuration**


**PIN Function**


#### **integrated light source**


**NO.** **Symbol** **PIN** **Function description**

1 DO DATA OUT Control data signal output

2 GND GROUND Ground, data & power grounding

3 DI DATA IN Control data signal input

4 VDD POWER SUPPLY Power supply

**Absolute Maximum Ratings**

**Parameter** **Symbol** **Ratings** **Unit**

Power supply voltage VDD +3.7~+5.3 V

Logical Input Voltage VI **-0.3V** ～ **VDD+0.7** V

Operation junction temperature Topt -25～+85 ℃

Storage temperature range Tstg -40~+105 ℃


**Electrical Characteristics** （ TA=25℃, VDD=5V, VSS=0V, unless otherwise specified ）

**Parameter** **Symbol** **Min** **Tpy** **Max** **Unit** **Conditions**

Input current II —— —— ±1 µA VI=VDD/VSS

High Voltage Input VIH **2.7V** —— **VDD+0.7V** V DIN, SET

Low Voltage Input VIL **-0.3V** —— **0.7V** V DIN, SET


**Switching Characteristics** （ TA=25℃, VDD=5V, VSS=0V, unless otherwise specified ）

**Parameter** **Symbol** **Min** **Tpy** **Max** **Unit** **Condition**

Transmission delay time tPLZ —— —— 300 ns CL=15pF, DIN→DOUT, RL=10KΩ

Fall time tTHZ —— —— 120 µs CL=300pF, OUTR/OUTG/OUTB

Input capacity CI —— —— 15 pF ——


**2** / **9**
**http://** [www.world-semi.com](http://www.world-semi.com)


# **WS2812C-2020**


#### **Intelligent control LED**


**LED Characteristics**


#### **integrated light source**


**Quiescent Current:** ＜ **0.5mA** **Test Condition**
**Parameter** **Symbol** **Color**

**Min.** **Typ.** **Max.** **Unit** **(Working current)**

**RED** 50 80 100


Luminous intensity IV


Wavelength λd


**Data Transfer Time**


**GREEN** 200 270 300 mcd 5mA

**BLUE** 50 70 100

**RED** 620 624.6 625

**GREEN** 515 517.8 525 nm 5mA

**BLUE** 460 471.4 465


T0H 0 code, high voltage time 220ns~380ns


T1H 1 code, high voltage time 580ns~1µs


T0L 0 code, low voltage time 580ns~1µs


T1L 1 code, low voltage time 580ns~1µs


RES Frame unit, low voltage time >280µs


**Sequence Chart**


0 code


1 code


RET code


**Cascade Method**


### D1 D2 D3 D4


T0H


T1H


T0L


T1L


DIN DO DIN DO DIN DO


##### PIX1


##### PIX2 PIX3


Treset


**3** / **9**
**http://** [www.world-semi.com](http://www.world-semi.com)


# **WS2812C-2020**


#### **Intelligent control LED**


**Data Transmission Method**


#### **integrated light source**


Note: The data of D1 is send by MCU, and D2, D3, D4 through pixel internal reshaping amplification to
transmit.


**Composition of 24bit Data**

G7 G6 G5 G4 G3 G2 G1 G0 R7 R6 R5 R4 R3 R2 R1 R0 B7 B6 B5 B4 B3 B2 B1 B0

Note: Data transmit in order of GRB, high bit data at first.


**Typical Application Circuit**


Remarks: C1 is the filter capacitor for VDD, its value of 100nF.


**4** / **9**
**http://** [www.world-semi.com](http://www.world-semi.com)


# **WS2812C-2020**


#### **Intelligent control LED**


#### **integrated light source**


**Tape Size (Unit: mm)**

##### Inspector:


LED Taping Position

##### **CARRIER TAPES TEST REPORTS**


UNIT: mm


**SYMBOL** **A0** **B0** **K0** **P0** **P1** **P2** **T** **E** **F** **D0** **D1** **W**


**SPEC** **2.20** **2.40** **1.01** **4.00** **4.00** **2.00** **0.18** **1.75** **3.50** **1.50** **1.00** **8.00**


**Reel Packing Specifications (Unit: mm)**


.


**5** / **9**
**http://** [www.world-semi.com](http://www.world-semi.com)


# **WS2812C-2020**


#### **Intelligent control LED**


**Moistureproof bag packing**

**SPQ: 4500PCS /Reel**


Internal label


#### **integrated light source**


Moisture-proof bag Desiccant External label


## **Top SMD LED Using Instructions**

1. **Summary**

To make the best use of WORLDSEMI’s LED, please refer to the below precautions, they are of same usage
method as other electronic components.


**2.** **Cautions**


2.1. Dust & Cleaning


The surface of the LED is encapsulated with modified epoxy resin because it plays a very good role in protecting
the optical performance and aging resistance. The modified epoxy resin is easy to stick with dust and must be kept
clean. When there’s a certain amount of dust on the surface of the LED, it won’t affect brightness, but dust proof
should be taken care of. Promoting the use of unsealed package in preference to others and the assembled LEDs
should be placed in a clean container.


Avoid using the organic solvents to clean the dust on the LED surface and it’s necessary to confirm whether the
cleaning fluid will dissolve the LED.


Do not clean the LEDs by the ultrasonic. Some parameters affecting the LED performance must be evaluated if
have no alternative but to the ultrasonic cleaning method, such as ultrasonic power, baking time and assembly
conditions, etc.


**6** / **9**
**http://** [www.world-semi.com](http://www.world-semi.com)


# **WS2812C-2020**


#### **Intelligent control LED**


#### **integrated light source**


2.2 Moisture-proof packaging


TOP SMD LEDs are moisture sensitive components. LEDs are packaged in aluminum foil bag to prevent the
from absorbing moisture during transport and storage. A desiccant is placed in the bags to absorb moisture. If the
LED absorbs moisture, then it evaporates and expands when in reflow process, which may break the colloid from
the bracket and damage the optical performance of LED. For this reason, moisture-proof packaging is to prevent the
from absorbing moisture during transport and storage. The moisture resistance rating of WORLDSEMI’s LED is:
**LEVEL 5a** .


**Tabel I - IPC/JEDEC J-STD-020 Moisture/Reflow Sensitivity Classification**


**Workshop Life**
**MSL Level**
**Time** **Conditions**
LEVEL1 Unlimited ≤30℃/85%RH
LEVEL2 1 Year ≤30℃/60%RH
LEVEL2a 4 Weeks ≤30℃/60%RH
LEVEL3 168 Hours ≤30℃/60%RH
LEVEL4 72 Hours ≤30℃160%RH
LEVEL5 48 Hours ≤30℃/60%RH
LEVEL5a 24 Hours ≤30℃/60%RH
LEVEL6 Take-out and Use immediately ≤30℃/60%RH


2.3 Management after unpacking


Moisture-proof sealed storage:20℃~30℃, 25%~60%RH, storage time ≤3 months, can be used directly;


Moisture-proof sealed dry storage: 20℃~30℃, 10%~25%RH, storage time ≤6 months, can be used directly;


It’s recommend to perform SMT assembly as soon as possible after opening the moisture-proof bag,and reflow
soldering should be completed within 4 hours after SMT assembly(ambient temperature <30℃, humidity <60%).


2.4 Management of Dehumidification


LED products exceed the prescribed time limit or damp for other reasons. It is recommended use them after
dehumidification. Demand for dehumidification: 75℃/>24H.


3. **Management of secondary SMT process**

It’s necessary to do moisture-proof treatment when the secondary reflow carried out that followed the first
reflow. Exposed at condition of “＜30 °C/60% RH”, it is recommended to pass the secondary reflow within 2
hours;It can’t be more than 2 hours to be exposed at condition of “<30℃/60%RH” and dehumification operation is
requested for a longer interval reflow. For instance, place in a drying box or a container with desiccant, and
dehumidify it before the secondary reflow(Low temperature baking operation: **70℃-75℃, ≥12 hours** ). For
exposure to “< 30 °C / 60% RH” more than 12 hours after one welding, can't pass the second secondary reflow.

**7** / **9**
**http://** [www.world-semi.com](http://www.world-semi.com)


# **WS2812C-2020**


#### **Intelligent control LED**


#### **integrated light source**


**4.** **SMT Reflow**


Refer to the parameters listed below, the experimental results prove that the TOP SMD LED meets the JEDEC
J-STD-020C standards. As a general guideline, it is recommended to follow the SMT reflow temperature curve
recommended by the solder paste manufacturer.


**Curve Description** **Lead-free**

The lowest preheat temperature (Tsmin) 150℃

The highest preheat temperature (Tsmax) 200℃

Preheating time (Tsmin to Tsmax) (ts) 60-180 S

Average rate of temperature rise (Tsmax to Tp) <3℃/S

LIQUID REGION temperature (TL) 217℃

LIQUID REGION Holding Time (tL) 60-150 S

Peak Temperature (Tp) 240℃

High Temperature Region(Tp=-5℃) Holding <10 S

Cooling Rate <6℃/S

Room Temperature to Peak Holding Time <6 min


Remarks: 1. These general guidelines may not apply to all PCB designs and reflow soldering configurations.


2. All temperatures referred are measured on the surface of the package body.


**5.** **Assembly Precautions**


4.Can not be stored in or

applied in the acidic sites of

PH<7.


1. Clip the LED from its

side.


2. Neither directly touch the

gel surface with the hand or

sharp instrument, it may

damage its internal circuit.


3. Not to be double stacked, it

may damage its internal circuit.


**8** / **9**
**http://** [www.world-semi.com](http://www.world-semi.com)


# **WS2812C-2020**


#### **Intelligent control LED**


#### **integrated light source**


**Modify Record**

**Version №** **Status Bar** **Modify Content Summary** **Date** **Reviser** **Approved**

V1.2 N New-Official release 20190104 Shen JinGuo Yin HuaPing


**Remarks:** Initial version: V1.0；Version number plus "0.1" after each revision;

Status bar: N--New, A--Add, M--Modify, D--Delete.


**9** / **9**
**http://** [www.world-semi.com](http://www.world-semi.com)


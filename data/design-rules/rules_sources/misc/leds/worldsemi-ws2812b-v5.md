Source: https://www.peace-corp.co.jp/data/WS2812B-V5_V1.0_EN.pdf
Retrieved: 2026-11-09

[PDF: 8 pages.]

**Features and Benefits**
 The control circuit and the LED share the only power source.


# **WS2812B-V5**
### **Intelligent control LED** **integrated light source**


 Control circuit and RGB chip are integrated in a package of 5050 components, to form a complete addressable
pixel.

 Built-in signal reshaping circuit, after wave reshaping to the next driver, ensure wave-form distortion not
accumulate.

 Built-in electric reset circuit and power lost reset circuit.

 Each pixel of the three primary color can achieve 256 brightness display, completed 16777216 color full color
display, and scan frequency is of 2KHz.

 Cascading port transmission signal by single line.

 Any two point the distance not more than 5m transmission signal without any increase circuit.

 When the refresh rate is 30fps, cascade number are not less than 1024 pixels.

 Send data at speeds of 800Kbps.

 The color of the light is highly consistent, cost-effective..


**Applications**
 Full-color module, LED full-color soft/hard light bar, LED guardrail tube.
####  LED decorative lighting, LED Screen, Indoor/outdoor LED video irregular screen, various electronic products,

electrical equipment marquee.


**General description**

WS2812B-V5 is a intelligent control LED light source that the control circuit and RGB chip are integrated in a
package of 5050 components.It internal include intelligent digital port data latch and signal reshaping amplification drive
circuit.Also include a precision internal oscillator and a voltage programmable constant current control part, effectively
ensuring the pixel point light color height consistent.
The data transfer protocol use single NZR communication mode. After the pixel power-on reset, the DIN port receive
data from controller, the first pixel collect initial 24bit data then sent to the internal data latch, the other data which
reshaping by the internal signal reshaping amplification circuit sent to the next cascade pixel through the DO port. After
transmission for each pixel, the signal to reduce 24bit. pixel adopt auto reshaping transmit technology, making the pixel
cascade number is not limited the signal transmission, only depend on the speed of signal transmission.

RESET time> **280μs**, it won't cause wrong reset while interruption, it supports the lower frequency and inexpensive
MCU.

Refresh Frequency updates to **2KHz**, Low Frame Frequency and No Flicker appear in HD Video Camera, it improve
excellent display effect.

LED with low driving voltage, environmental protection and energy saving, high brightness, scattering angle is large,
good consistency, low power, long life and other advantages. The control chip integrated in LED above becoming more
simple circuit, small volume, convenient installation.


1 / 8
#### http://www.world-semi.com


**Mechanical** **Dimensions**


**Remarks:** Dimension of 5.0*5.4*1.57mm, default Tolerance of 0.05mm.


**PIN Configuration**


**PIN Function**


# **WS2812B-V5**
### **Intelligent control LED** **integrated light source**


**NO.** **Symbol** **PIN** **Function description**

1 VDD POWER SUPPLY Power supply

2 DOUT DATA OUT Control data signal output

3 VSS GROUND Ground,data & power grounding

4 DIN DATA IN Control data signal input


**Absolute Maximum Ratings**

**Parameter** **Symbol** **Ratings** **Unit**
Power supply voltage VDD +3.7~+5.3 V

Logical Input Voltage VI **VDD-0.3V** ～ **VDD+0.7** V

Operation junction temperature Topt -25～+85 ℃

Storage temperature range Tstg -40~+105 ℃


2 / 8
#### http://www.world-semi.com


# **WS2812B-V5**
### **Intelligent control LED** **integrated light source**
#### Electrical Characteristics （ TA=25℃, VDD=5V, VSS=0V, unless otherwise specified ）

**Parameter** **Symbol** **Min** **Tpy** **Max** **Unit** **Conditions**

Input current II —— —— ±1 µA VI=VDD/VSS

High Voltage Input VIH 2.7V —— VDD+0.7V V DIN，SET

Low Voltage Input VIL -0.3V —— 0.7V V DIN，SET

#### Switching Characteristics （ TA=25℃, VDD=5V, VSS=0V, unless otherwise specified ）

**Parameter** **Symbol** **Min** **Tpy** **Max** **Unit** **Condition**

Transmission delay

tPLZ —— —— 300 ns CL=15pF, DIN→DOUT,RL=10KΩ
time

Fall time tTHZ —— —— 120 µs CL=300pF, OUTR/OUTG/OUTB

Input capacity CI —— —— 15 pF ——


**LED Characteristics**


**Parameter** **Symbol** **Color**


**Quiescent Current: 0.6mA** **Condition**
( **Working current** )
**Mini** **Typ** **Max** **Unit**


**Brightness** IV


**Wavelength** λd


**Data Transfer Time**


Red 300 310 500

Green 600 780 1000 mcd 12mA

Blue 200 215 300

Red 620 -- 630

Green 515 -- 525 nm 12mA

Blue 465 -- 475


T0H 0 code, high voltage time 220ns~380ns

T1H 1 code, high voltage time 580ns~1µs

T0L 0 code, low voltage time 580ns~1µs

T1L 1 code, low voltage time **580ns~1µs**

RES Frame unit, low voltage time >280µs


3 / 8
#### http://www.world-semi.com


**Sequence Chart** **Cascade Method**


# **WS2812B-V5**
### **Intelligent control LED** **integrated light source**


## D1 D2 D3 D4

DIN DO DIN DO DIN DO


PIX1


PIX2 PIX3


**Data Transmission Method**


Note: The data of D1 is send by MCU, and D2, D3, D4 through pixel internal reshaping amplification to transmit.


**Composition of 24bit Data**

G7 G6 G5 G4 G3 G2 G1 G0 R7 R6 R5 R4 R3 R2 R1 R0 B7 B6 B5 B4 B3 B2 B1 B0


Note: Data transmit in order of GRB, high bit data at first.


**Typical Application Circuit: The peripheral circuit don’t need to add filter capacitor.**


4 / 8
#### http://www.world-semi.com


**Packing Standard**


**Packing:** 1K/Reel: 167*12mm

4.5K/Reel: 327*12mm


**Product Label**

#### **Top SMD LED Using Instructions**


1. **Summary**


**Anti-static bag**


# **WS2812B-V5**
### **Intelligent control LED** **integrated light source**

**Carrier** **tape**


**The foam protective layer**


**Guard against damp/ Keep dry**


To make the best use of WORLDSEMI’s LED, please refer to the below precautions, they are of same usage
method as other electronic components.


**2.** **Cautions**


5 / 8
#### http://www.world-semi.com


# **WS2812B-V5**
### **Intelligent control LED** **integrated light source**

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


2.2. Moisture-proof packaging


TOP SMD LEDs are moisture sensitive components. LEDs are packaged in aluminum foil bag to prevent the
from absorbing moisture during transport and storage. A desiccant is placed in the bags to absorb moisture. If the
LED absorbs moisture, then it evaporates and expands when in reflow process, which may break the colloid from
the bracket and damage the optical performance of LED. For this reason, moisture-proof packaging is to prevent the
from absorbing moisture during transport and storage. The moisture resistance rating of WORLDSEMI’s LED is:
**LEVEL 5a.**


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

6 / 8
#### http://www.world-semi.com


# **WS2812B-V5**
### **Intelligent control LED** **integrated light source**

2.4 Management of Dehumidification


LED products exceed the prescribed time limit or damp for other reasons. It is recommended use them after
dehumidification. Demand for dehumidification: 75℃/>24H.


3. **Management of secondary SMT process**

It’s necessary to do moisture-proof treatment when the secondary reflow carried out that followed the first reflow.
Exposed at condition of “＜30 °C/60% RH”, it is recommended to pass the secondary reflow within 2 hours;It can’t
be more than 2 hours to be exposed at condition of “<30℃/60%RH” and dehumification operation is requested for
a longer interval reflow. For instance, place in a drying box or a container with desiccant, and dehumidify it before
the secondary reflow(Low temperature baking operation: **70℃-75℃, ≥12 hours** ). For exposure to “< 30 °C /
60% RH” more than 12 hours after one welding, can't pass the second secondary reflow.


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


7 / 8
#### http://www.world-semi.com


# **WS2812B-V5**
### **Intelligent control LED** **integrated light source**


1. Clip the LED from its

side.


**Modify Record**


2. Neither directly touch the

gel surface with the hand or

sharp instrument, it may

damage its internal circuit.


3. Not to be double stacked, it

may damage its internal circuit.


4. Can not be stored in or

applied in the acidic sites of

PH<7.


**Version №** **Status Bar** **Modify Content Summary** **Date** **Reviser** **Approved**

V1.0 N New WS2812B - V5 20190219 Shen JinGuo Yin HuaPing


**Remarks:** Initial version: V1.0；Version number plus "0.1" after each revision;

Status bar: N--New, A--Add, M--Modify, D--Delete.


8 / 8
#### http://www.world-semi.com


Source: https://cdn.sparkfun.com/assets/e/6/1/f/4/WS2812B-LED-datasheet.pdf
Retrieved: 2026-11-09

[PDF: 10 pages.]

# WS2812B LED

###### Intelligent control LED integrated light source

# **WORLDSEMI CO.,LIMITED**

## **WS2812B Datasheet and Specifications**

### **Intelligent control LED integrated light source** **Jan,2016** **V1.0**

1/9


# WS2812B LED

###### Intelligent control LED integrated light source

**Features and Benefits**
 Intelligent reverse connect protection, the power supply reverse connection does not damage the IC.

 The control circuit and the LED share the only power source.

 Control circuit and RGB chip are integrated in a package of 5050 components, form a complete control of pixel
point.

 Built-in signal reshaping circuit, after wave reshaping to the next driver, ensure wave-form distortion not
accumulate.

 Built-in electric reset circuit and power lost reset circuit.

 Each pixel of the three primary color can achieve 256 brightness display, completed 16777216 color full color
display, and scan frequency not less than 400Hz/s.

 Cascading port transmission signal by single line.

 Any two point the distance more than 5m transmission signal without any increase circuit.

 When the refresh rate is 30fps, cascade number are not less than1024 points.

 Send data at speeds of 800Kbps.

 The color of the light were highly consistent, cost-effective..
**Applications**
 Full-color module, Full color soft lights a lamp strip.

 LED decorative lighting, Indoor/outdoor LED video irregular screen.


**General description**


WS2812B is a intelligent control LED light source that the control circuit and RGB chip are integrated in
a package of 5050 components. It internal include intelligent digital port data latch and signal reshaping ampli
fication drive circuit. Also include a precision internal oscillator and a 12V voltage programmable constant curr
e-nt control part, effectively ensuring the pixel point light color height consistent.
The data transfer protocol use single NZR communication mode. After the pixel power-on reset, the DIN
port receive data from controller, the first pixel collect initial 24bit data then sent to the internal data latch,
the other data which reshaping by the internal signal reshaping amplification circuit sent to the next cascade
pixel through the DO port. After transmission for each pixel，the signal to reduce 24bit. pixel adopt auto resha
-ping transmit technology, making the pixel cascade number is not limited the signal transmission, only depend
on the speed of signal transmission.
LED with low driving voltage, environmental protection and energy saving, high brightness, scattering angl
e is large, good consistency, low power, long life and other advantages. The control chip integrated in LED
above becoming more simple circuit, small volume, convenient installation.


2/9


# WS2812B LED

###### Intelligent control LED integrated light source

**Mechanical** **Dimensions**


**PIN** **configuration**


**PIN function**


**NO.** **Symbol** **Function description**


1 VDD Power supply LED


2 DOUT Control data signal output


3 VSS Ground


4 DIN Control data signal input


3/9


# WS2812B LED

###### Intelligent control LED integrated light source

**Absolute Maximum Ratings**


**Prameter** **Symbol** **Ratings** **Unit**


Power supply voltage VDD +3.5~+5.3 V


Input voltage VI -0.5～VDD+0.5 V

Operation junction
Topt -25～+80 ℃
temperature


Storage temperature range Tstg -40~+105 ℃


**Electrical Characteristics** （ TA=-20～+70℃，VDD=4.5～5.5V,VSS=0V,unless otherwise specified ）


**Prameter** **Smybol** **conditions** **Min** **Tpy** **Max** **Unit**


Input current II VI=VDD/VSS —— —— ±1 µA


Input voltage level


VIH DIN，SET 0.7VDD —— —— V


VIL DIN，SET —— —— 0.3 VDD V


Hysteresis voltage VH DIN，SET —— 0.35 —— V


**Switching characteristics** （ TA=-20～+70℃，VDD=4.5～5.5V,VSS=0V,unless otherwise specified ）


**Prameter** **Symbol** **Condition** **Min** **Tpy** **Max** **Unit**


Transmission delay
tPLZ
time


Fall time tTHZ


CL=15pF,DIN→
—— —— 300 ns
DOUT,RL=10KΩ


CL=300pF,OUTR/OU
—— —— 120 µs
TG/OUTB


Input capcity CI —— —— —— 15 pF


**RGB IC characteristic parameter**


Emitting color Model Wavelength(nm) Luminous intensity(mcd) Voltage(V)


Red 13CBAUP
620-630 550-700 1.8-2.2


Green 13CGAUP
515-530 1100-1400 3.0-3.2


Blue 10R1MUX
465-475 200-400 3.0-3.4


4/9


# WS2812B LED

###### Intelligent control LED integrated light source

**Data transfer time(** TH+TL **=** 1.25µs±600ns)


T0H 0 code,high voltage time 0.4us ±150ns


T1H 1 code,high voltage time 0.85us ±150ns


T0L 0 code, low voltage time 0.85us ±150ns


T1L 1 code,low voltage time 0.4us ±150ns


RES low voltage time Above 50µs


**Sequence chart:**


0 code


1 code


RET code


**Cascade method:**


T0L
T0H


T1L
T1H


Treset


#### D1 D2 D3 D4

DIN DO DIN DO DIN DO


PIX1


PIX2 PIX3


5/9


**Data transmission method** ：


# WS2812B LED

###### Intelligent control LED integrated light source reset code >=50us reset code


###### D1 D2 D3 D4


###### Data refresh cycle 1 Data refresh cycle 2

second second
first 24bit 24bit third 24bit first 24bit 24bit third 24bit


second second
third 24bit third 24bit
24bit 24bit


third 24bit third 24bit


6/9


# WS2812B LED

###### Intelligent control LED integrated light source

Note: The data of D1 is send by MCU,and D2, D3, D4 through pixel internal reshaping amplification to
transmit.

**Composition of 24bit data:**


G7 G6 G5 G4 G3 G2 G1 G0 R7 R6 R5 R4 R3 R2 R1 R0 B7 B6 B5 B4 B3 B2 B1 B0


Note: Follow the order of GRB to sent data and the high bit sent at first.

**Typical application circuit:**


U1


5V

1 4 DIN


1
VDD


4
DIN


C1
104


C2
104


C1
104


DOUT2 3

DOUT VSS


WS2812B


7/9


2 3
DOUT VSS


WS2812B


U2


5V


5V


1
VDD


4
DIN


2 3
DOUT VSS


WS2812B


U1


1
VDD


4
DIN


# WS2812B LED

###### Intelligent control LED integrated light source

##### **WS2812B Products Using Instructions** **MSL=5A Level**

1. Purpose：


WS2812B-Mini LED lamp’s surface use the high hardness silicone resin,can ensure that no
matter customers use PU glue or epoxy resin to do the silicone drop rubber
processing,won’t lead the LED to die;also has a very good anti sulfide capacity. Good
compatibility with bracket, but the silicon resin has a higher requirements on the humidity
and dehumidification process, especially pay attention during wet season,ensure the
production safety.
2. Transport and application area：


All WS2812S/B products during the transportation process, need to maintain a positive
upward, moisture-proof, during the transport process,shall avoid the extrusion, collision
and vibration.
3. Product storage and deadline：


Sealed storage at room temperature: 20 ℃ ~ 30 ℃, 40% ~ 60%RH, the product is valid
for 3 months;
Moisture seal storage: 20 ℃ ~ 30 ℃, 25% ~ 60%RH, the product is valid for 6 months;
After opening the product packaging, suggest using them within 1 hours,(environmental
conditions of temperature <30 ℃, humidity <60%).


4. Dehumidification process:


LED products which is beyond the prescribed time limit,or for getting damp for some other
reasons,we recommend the customer first do the dehumidification process,then use
them.Dehumidification method:under 75 ℃ / 22 ±2 hours.


5. Electrostatic protection:


LED is the electrostatic sensitive devices, although the LED product has excellent
anti-static ability, but after each ESD impact, will cause a certain degree of damage to LED.
Thus in using process of LED products, must do the electrostatic protection measures, such
as anti-static gloves, anti-static Bracelet etc..


6. Manual welding operation instruction


Suggest using the Electric soldering iron whose power is less than 30W, then control the

8/9


# WS2812B LED

###### Intelligent control LED integrated light source

electric soldering iron’s temperature being not higher than 350 ℃, every time when
welding electric iron in the bracket pin,stay time shall be no more than 3 seconds,if
requiring repeat welding,then interval time shall be no less than 2 seconds.Please don’t
touch or extrusion the LED’s surface,in order to avoid damage to the internal LED, at the
same time, please pay attention to avoid the electric iron burns the colloid on the surface of
LED and other injuries.


7. Reflow instructions


Set the reflow parameters, check the following drawing and table for reference.,
recommend using Senju, Alfa, Henkel loctite brand solder paste, recommends customers do
the necessary adjustments according to foundation of material properties provided by the
solder materials suppliers.


**Curve description** **Lead in solder reflow** **SMT LINE**


**The lowest preheat temperature(Tsmin)** **100** ℃ **150** ℃


**The highest preheat temperature(Tsmax)** **150** ℃ **200** ℃


**Preheating time (Tsmin to Tsmax)(ts)** **60-120 S** **60-180 S**


**Average rate of temperature rise(Tsmax to Tp)** **<3** ℃ **/S** **<3** ℃ **/S**


**liquid phase temperature (TL)** **183** ℃ **217** ℃


**Holding time liquid region (tL)** **60-150 S** **60-150 S**


**peak temperature(Tp)** **235** ℃ **250** ℃


**High temperature region (the peak temperature**
**-5** ℃ **) residence time (tp)**


**<10 S** **<10 S**


**Decreasing temperature rate** **<6** ℃ **/S** **<6** ℃ **/S**


**Stay time from room temperature to the peak**
**temperature**


8.Notice of Production


**<6 min** **<6 min**


1.All products,during SMT, please carefully check, if the vacuum packaging intact, no


9/9


# WS2812B LED

###### Intelligent control LED integrated light source

leakage phenomenon,Please use directly, can don’t do the bake dehumidification.


2. During use, please open a bag and use a bag,please don’t open many bags at one-time


which shall lead the LEDs absorb moisture in the air since you don’t use them at once.


3. After SMT,please do the reflow soldering furnace immediately,please don’t leave them in


in the pre-reflow for a long time which absorb moisture.Especially


when off work,please use out the LEDs which is out of packaging,please SMT and


reflow,do not let them stay in the air for a long time.


4. Dehumidification process,please under 70-75 ℃, bake for 24 hours. Also note during


using, use the LEDs immediately after taking out of the bake box,please don’t take many


reels at one-time, since it is very hot when taking out,LED in the cooling process more


easily absorb the moisture in the air into the inside of the LED,which shall cause led dead


during reflow.


5.Please pay attention that it is forbidden to secondary reflow soldering.


10/9


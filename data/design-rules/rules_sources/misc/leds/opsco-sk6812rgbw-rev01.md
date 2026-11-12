Source: https://cdn-shop.adafruit.com/product-files/2757/p2757_SK6812RGBW_REV01.pdf
Retrieved: 2026-11-09

[PDF: 15 pages.]

### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**

## **SK6812RGBW**

**SPECIFICATION**
**INTEGRATED LIGHT SOURCE INTELLIGENT CONTROL OF**
**CHIP-ON-TOP SMD TYPE LED**


Document No.: SPC/ SK6812RGBW-XX


Model No.:    SK6812RGBW-XX


Description: 5.5x5.0x1.6mm Top SMD Type 0.25 Watt Power


tegrated light source Intelligent control LED


Rev. No.:      01


Date:         2015-07-31


ELECTROSTATIC
SENSITIVE DEVICES


1 / 15


Document No.: SPC / SK6812RGBW Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


INTEGRATED LIGHT SOURCE INTELLIGENT CONTROL

OF CHIP-ON-TOP SMD TYPE LED

**Model: SK6812RGBW**

**1.** **Product Overview :**


**SK6812RGBW is a smart LED control circuit and light emitting circuit in one controlled LED source,**
**which has the shape of a 5050 LED chip. Each lighting element is a pixel, and the intensities of the**
**pixels are contained within the intelligent digital interface input. The output is driven by patented PWM**
**technology, which effectively guarantees high consistency of the color of the pixels. The control**
**circuit consists of a signal shaping amplification circuit, a built-in constant current circuit, and a high**
**precision RC oscillator.**


**The data protocol being used is unipolar NRZ communication mode. The 32-bit data is transmitted**
**from the controller to DIN of the first element, and if it is accepted it is extracted pixel to pixel. After an**
**internal data latch, the remaining data is passed through the internal amplification circuit and sent out**
**on the DO port to the remaining pixels. The pixel is reset after the end of DIN. Using automatic**
**shaping forwarding technology makes the number of cascaded pixels without signal transmission only**
**limited by signal transmission speed.**


**The LED has a low driving voltage (which allows for environmental protection and energy saving),**
**high brightness, scattering angle, good consistency, low power, and long life. The control circuit is**
**integrated in the LED above.**
2. **Main Application Field:**


- **Full color LED string light, LED full color module, LED super hard and soft lights, LED guardrail tube,**
**LED appearance / scene lighting**


- **LED point light, LED pixel screen, LED shaped screen, a variety of electronic products, electrical**
**equipment etc..**

3. **Description:**


- **Top SMD internal integrated high quality external control line serial cascade constant current IC;**


- **control circuit and the chip in SMD 5050 components, to form a complete control of pixel, color**
**mixing uniformity and consistency;**


- **built-in data shaping circuit, a pixel signal is received after wave shaping and output waveform**
**distortion will not guarantee a line;**


- **The built-in power on reset and reset circuit, the power does not work;**


- **gray level adjusting circuit (256 level gray scale adjustable);**


- **red drive special treatment, color balance;**


- **line data transmission;**


- **plastic forward strengthening technology, the transmission distance between two points over 10M;**


- **Using a typical data transmission frequency of 800 Kbps, when the refresh rate of 30 frames per sec**


4. Mechanical Dimensions:


Notes:
1. All dimensions are in millimeters.
2. Tolerance is ± 0.1mm unless otherwise noted


2 / 15


Document No.: SPC / SK6812RGBW Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


**5.** PIN configuration


**NO.** **Symbol** **Function description**

1 VDD Power supply LED


2 DOUT Control data signal output


3 VSS Ground


4 DIN Control data signal input


**6.** General Information

# **SK6812RGBW-XX**


SK6812RGBW: The default is the chips with IC integration


R:  RED   620-630NM


G:  GREEN  515-525 NM


B:  BLUE   460-470 NM

W : White Color

-xx BW  Blue White 6000-7000K


NW Natural White 4000-4500K


WS  Warm Sunlight 2700-3000K


3 / 15


Document No.: SPC / SK6812RGBW Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


**7.** Absolute Maximum Ratings（Ta=25℃,VSS=0V）:


Parameter Symbol Range Unit


Power supply voltage VDD +3.5 ～ +5.5 V


Logic input voltage VIN -0.5 ～ VDD+0.5 V


Working temperature Topt -40~+85 ℃


Storage temperature Tstg -50~+150 ℃


ESD pressure VESD 4K V


**8.** The electrical parameters (unless otherwise specified, TA=-20 ~ +70 ℃, VDD=4.5 ~ 5.5V,
VSS=0V):


Parmeter Symbol Min Typical Max Unit Test conditions


The chip
VDD --- 5.2 --- V --supply voltage


R/G/B port VDS,M
--- --- 26 V --pressure AX


DOUT drive
capability


The signal
input flip
threshold


DOUT conect ground,
IDOH --- 49 --- mA the maximum drive
current


DOUT conect +, the
IDOL --- -50 --- mA
largest current


VIH 3.4 --- --- V
VDD=5.0V
VIL --- --- 1.6 V


The frequency
FPWM --- 1.2 --- KHZ --of PWM


Static power
IDD --- 1 --- mA --consumption


**9.** The dynamic parameters (Ta=25 ℃):


Parameter Symbol Min Typical Max Unit Test conditions


The speed of data The duty ratio of 67%
fDIN --- 800 --- KHZ
transmission (data 1)


DOUT transmission
delay


IOUT Rise/Drop
Time


4 / 15


TPLH --- --- 500 ns
DIN→DOUT
TPHL --- --- 500 ns


Tr --- --- 40 ns
VDS=1.5
IOUT=9mA
Tf --- --- 80 ns


Document No.: SPC / SK6812RGBW Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


**10.** The data transmission time (TH+TL=1.25µs±600ns):


T0H 0 code, high level time 0.3µs ±0.15µs


T0L 0 code, low level time 0.9µs ±0.15µs


T1H 1 code, high level time 0.6µs ±0.15µs


T1L 1 code, low level time 0.6µs ±0.15µs


Trst Reset code，low level time 80µs


**11.** Timing waveform:


Input code: Connection mode:
###### D1 D2 D3 D4

DIN DO DIN DO DIN DO


PIX1


PIX2 PIX3


**12.** The method of data transmission:


Note: the D1 sends data for MCU, D2, D3, D4 for data forwarding automatic shaping cascade circuit.


5 / 15


Document No.: SPC / SK6812RGBW Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


**13.** The data structure of 32bit:


**R7** **R6** **R5** **R4** **R3** **R2** **R1** **R0** **G7** **G6** **G5** **G4**

**G3** **G2** **G1** **G0** **B7** **B6** **B5** **B4** **B3** **B2** **B1** **B0**

**W7** **W6** **W5** **W4** **W3** **W2** **W1** **W0**


Note: high starting, in order to send data (R7 - R6 - ... ..W0)


**14.** The typical application circuit:


6 / 15


Document No.: SPC / SK6812RGBW Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


15. White Color Temperature Ranks & CIE Color Rank (Refer to CIE 1931 chromaticity diagram **)**


CIE chromaticity coordinates (ANSI Cool White)


C.A X Y C.A X Y C.A X Y C.A X Y
0.3048 0.3207 0.3028 0.3304 0.3115 0.3391 0.3130 0.3290
0.3130 0.3290 0.3115 0.3391 0.3205 0.3481 0.3213 0.3373

C1 C2 C3 C4

0.3144 0.3186 0.3130 0.3290 0.3213 0.3373 0.3221 0.3261
0.3068 0.3113 0.3048 0.3207 0.3130 0.3290 0.3144 0.3186
0.3068 0.3113 0.3005 0.3415 0.3099 0.3509 0.3144 0.3186
0.3144 0.3186 0.3099 0.3509 0.3196 0.3602 0.3221 0.3261

C5 C6 C7 C8

0.3161 0.3059 0.3115 0.3391 0.3205 0.3481 0.3231 0.3120
0.3093 0.2993 0.3028 0.3304 0.3115 0.3391 0.3161 0.3059
0.3215 0.3350 0.3207 0.3462 0.3290 0.3538 0.3290 0.3417
0.3290 0.3417 0.3290 0.3538 0.3376 0.3616 0.3371 0.3490

D1 D2 D3 D4

0.3290 0.3300 0.3290 0.3417 0.3371 0.3490 0.3366 0.3369
0.3222 0.3243 0.3215 0.3350 0.3290 0.3417 0.3290 0.3300
0.3222 0.3243 0.3196 0.3602 0.3290 0.3690 0.3290 0.3300
0.3290 0.3300 0.3290 0.3690 0.3381 0.3762 0.3366 0.3369

D5 D6 D7 D8

0.3290 0.3180 0.3290 0.3538 0.3376 0.3616 0.3361 0.3245
0.3231 0.3120 0.3207 0.3462 0.3290 0.3538 0.3290 0.3180
0.3371 0.3490 0.3376 0.3616 0.3463 0.3687 0.3451 0.3554
0.3451 0.3554 0.3463 0.3687 0.3551 0.3760 0.3533 0.3620

E1 E2 E3 E4

0.3440 0.3427 0.3451 0.3554 0.3533 0.3620 0.3515 0.3487
0.3366 0.3369 0.3371 0.3490 0.3451 0.3554 0.3440 0.3427
0.3366 0.3369 0.3381 0.3762 0.3480 0.3840 0.3440 0.3428
0.3440 0.3428 0.3480 0.3840 0.3571 0.3907 0.3515 0.3487

E5 E6 E7 E8

0.3429 0.3307 0.3463 0.3687 0.3551 0.3760 0.3495 0.3339
0.3361 0.3245 0.3376 0.3616 0.3463 0.3687 0.3429 0.3307


C1 C2 C3 C4


C5 C6 C7 C8


D1 D2 D3 D4


D5 D6 D7 D8


E1 E2 E3 E4


E5 E6 E7 E8


ANSI Blue White Color bin structures


7 / 15


Document No.: SPC / SK6812RGBW Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


CIE chromaticity coordinates (ANSI Natural white)


C.A X Y C.A X Y C.A X Y C.A X Y
0.3530 0.3597 0.3548 0.3736 0.3641 0.3804 0.3615 0.3659
0.3615 0.3659 0.3641 0.3804 0.3736 0.3874 0.3702 0.3722

F1 F2 F3 F4

0.3590 0.3521 0.3615 0.3659 0.3702 0.3722 0.3670 0.3578
0.3512 0.3465 0.3530 0.3597 0.3615 0.3659 0.3590 0.3521
0.3512 0.3465 0.3571 0.3907 0.3668 0.3957 0.359 0.3521
0.359 0.3521 0.3668 0.3957 0.3771 0.4034 0.367 0.3578

F5 F6 F7 F8

0.3567 0.3389 0.3641 0.3804 0.3736 0.3874 0.364 0.344
0.3495 0.3339 0.3548 0.3736 0.3641 0.3804 0.3567 0.3389
0.367 0.3578 0.3702 0.3722 0.3825 0.3798 0.3783 0.3646
0.3702 0.3722 0.3736 0.3874 0.3869 0.3958 0.3825 0.3798

G1 G2 G3 G4

0.3825 0.3798 0.3869 0.3958 0.4006 0.4044 0.395 0.3875
0.3783 0.3646 0.3825 0.3798 0.395 0.3875 0.3898 0.3716
0.367 0.3578 0.3771 0.4034 0.3916 0.4127 0.3783 0.3646
0.3783 0.3646 0.3916 0.4127 0.4064 0.4221 0.3898 0.3716

G5 G6 G7 G8

0.3743 0.3502 0.3869 0.3958 0.4006 0.4044 0.3848 0.3565
0.364 0.344 0.3736 0.3874 0.3869 0.3958 0.3743 0.3502
0.4054 0.4191 0.3941 0.3848 0.3889 0.369 0.3889 0.369
0.4217 0.4273 0.3996 0.4015 0.3941 0.3848 0.4017 0.3751

H6 H2 H1 H5

0.4146 0.4089 0.4146 0.4089 0.408 0.3916 0.3957 0.3596
0.3996 0.4015 0.408 0.3916 0.4017 0.3751 0.384 0.354


F1 F2 F3 F4


F5 F6 F7 F8


G1 G2 G3 G4


G5 G6 G7 G8


H6 H2 H1 H5


ANSI Natural White Color bin structures
#### **OPSCO Natural White Graph**


0.43


0.42


0.41


0.40


0.39


3500K


4000K
##### H6 G7 H2


##### F7


##### G6 G2


0.38


0.37


0.36


0.35


0.34


0.33


8 / 15


4500K

##### F6


##### F3


##### G4


##### G3 H5


##### H1


##### F2


##### G1 F4


##### G8


##### F1 G5


##### F8 F5


X

0.35 0.36 0.37 0.38 0.39 0.40 0.41 0.42 0.43


Document No.: SPC / SK6812RGBW Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


CIE chromaticity coordinates (ANSI Warm White)


C.A X Y C.A X Y C.A X Y C.A X Y
0.4082 0.3922 0.4146 0.4089 0.4299 0.4165 0.4221 0.3984
0.3941 0.3848 0.3996 0.4015 0.4146 0.4089 0.4082 0.3922

H1 H2 H3 H4

0.3889 0.3690 0.3941 0.3848 0.4082 0.3922 0.4017 0.3752
0.4017 0.3752 0.4082 0.3922 0.4221 0.3984 0.4147 0.3814
0.4344 0.4032 0.4430 0.4212 0.4562 0.4260 0.4465 0.4071
0.4221 0.3984 0.4299 0.4165 0.4430 0.4212 0.4344 0.4032

K1 K2 K3 K4

0.4147 0.3814 0.4221 0.3984 0.4344 0.4032 0.4260 0.3853
0.4260 0.3853 0.4344 0.4032 0.4465 0.4071 0.4373 0.3893
0.4586 0.4103 0.4687 0.4289 0.4813 0.4319 0.4700 0.4126
0.4465 0.4071 0.4562 0.4260 0.4687 0.4289 0.4586 0.4103

L1 L2 L3 L4

0.4373 0.3893 0.4465 0.4071 0.4586 0.4103 0.4483 0.3918
0.4483 0.3918 0.4586 0.4103 0.4700 0.4126 0.4593 0.3944


H1 H2 H3 H4


K1 K2 K3 K4


L1 L2 L3 L4


ANSI Warm White Color bin structures


9 / 15


Document No.: SPC / SK6812RGBW Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


16. Standard LED Performance Graph:


Typical Relative Luminous Flux vs. Forward Current
Forward Voltage vs. Forward Current


150%


120%


100%


80%


60%


40%


20%


0.00

0 10


15 20 50 150 0.0


BLUE/GREEN


~~RED~~





~~RED~~


~~BLUE\GREEN~~


1.0 2.0 3.0 4.0


5.0


1.0 2.0 3.0


Forward Current(mA)


Thermal Pad Temperature vs. Relative Light Output


120%


100%


80%


60%


40%


20%


0.00


BLUE GREEN


Forward Voltage(V) Tj=25 °C


Wavelength Characteristics


RED


BLUE\GREEN

100%


80%


60%

RED


40%


20%


0.00

0 20 40 60 80 100

Thermal Pad Temperature (T=25°C)


120 400 450 500 550 600 650

Wavelength (nm)


WS

NW
BW


700 750 800


Thermal Pad Temperature vs. Forward Current








0 20 40 60 80 100


Thermal Pad Temperature (°C)



Typical Radiation Pattern  120°



30°


60°


90°

90 75 60 45 30 15 0 0.2 0.4 0.6 0.8 1.0

Radiation Angle


Document No.: SPC / SK6812RGBW Rev. No.: 01


10 / 15


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


17. Packaging Standard:

**S K 6 8 1 2 R G B W -X X**


C A T H O D E ID E N T IF IC A T IO N


T A P E F E E D D IR E C T IO N


R E E L (1 7 8 x1 2 m m )

(IN N E R 1 0 0 0 p c s L E D M A X )


E S D P O L Y E T H Y L E N E B A G


C A R D B O A R D (IN N E R 4 5 B A G M A X .)


C A R R IE R T A P E


C O V E R T A P E


S M D
P R O D U C T N O .: S K 6 8 1 2 R G B W -W S


Q U A N T IT Y .: 1 0 0 0 P C S


L o t N o .: L W 2 0 1 5 0 7 0 9 0 2 -1 0


W S : 2 7 0 0 -3 2 0 0 K


D A T E :2 0 1 5 -0 8 -0 4

L A B E L S K E T C H IN G


The reel pack is applied in SMD LED. The LEDs are packed in cardboard boxes after packaging in normal or antielectrostatic bags. cardboard boxes will be used to protect the LEDs from mechanical shocks during transportation. The
boxes are not water resistant and therefore must be kept away from water and moisture.


11 / 15


Document No.: SPC / SK6812RGBW Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


**TOP SMD LED Application Notes**


1. Features

**The Purposes of making OPSCO’s customers and users to have a clear understanding on the ways how to**


**use the LED** .
2. Description

**Generally. The LED can be used the same way as other general purposed semiconductors. When using**


**OPSCO’s TOP SMD LED, the following precautions must be taken to protect the LED.**


3. Cautions
3.1. Dust & Cleaning

**This emitter has a silicone surface, There are many benefits to the silicone surface in terms of optical**
**properties and improved reliability. However, silicone is a softer material and prone to attract dust. While a**
**minimal amount of dust and debris on the LED will not cause significant reduction in illumination, steps**
**should be taken to keep the emitter free of dust.**


**These include keeping the LEDs in the manufacturer’s package prior to assembly and storing assemblies in**
**an enclosed area after installing the emitters.**


**Surface condition of this device may change when organic solvents such as trichloroethylene or acetone**
**were applied.**


**Avoid using organic solvent, it is recommended that isopropyl be used as a solvent for cleaning the LEDs.**
**When using other solvents, it should be confirmed beforehand whether the solvents will dissolve the**
**package and the resin of not.**


**Do not clean the LEDs by the ultrasonic. When it is absolutely necessary, the influence as ultrasonic**
**cleaning on the LEDs depends on factors such as ultrasonic power. Baking time and assembled**
**condition. Before cleaning, a pre-test should be done to confirm whether any damage to the LEDs will**
**occur.**


3.2. Moisture Proof Package


**In order to avoid the absorption of moisture during transportation and storage, LED are packed in the**
**aluminum envelop, A desiccant is included in the aluminum envelop as it absorbs moisture. When**
**moisture is absorbed into the AMT package it may vaporize and expand during soldering. There is a**
**possibility that this can cause exfoliation of the contacts and damage to the optical characteristics of the**
**LEDs. For this reason, the moisture proof package is used to keep moisture to a minimum in the package.**


3.3. Storage


**In order to avoid the absorption of moisture, It is recommended to store SMD LED (in bulk or taped) in the**
**dry box (or the** **desiccator ) with a desiccant, Otherwise to store them in the following environment as**
**recommended.**


**a. Temperature: 5** ℃ **~30** ℃ **b. Humidity: 60% RH Max**


**It is recommended to solder the LED as soon as possible after unpacking the aluminum envelop, But in case**
**that the LED have to be left unused after unpacking envelop again is requested.**


**The LED should be soldering within 1 hours after opening the package.**


**If baking is required, A baking treatment should be performed as follows:**


**70** ℃± **5** ℃ **for more than 24 hours.**


12 / 15


Document No.: SPC / SK6812RGBW Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


3.4. Reflow Soldering Characteristics

In testing, OPSCO has found S50 LEDs to be compatible with JEDEC J-STD-020C,using the parameters listed below. As a
general guideline OPSCO recommends that users follow the recommended soldering profile provided by the manufacturer
of solder paste used.


Note that this general guideline is offered as a starting point and may require adjustment for certain PCB designs and


Configurations of reflow soldering equipment.


Critical Zone TL to TP


amp-up


L L

s max


MIN

Ramp down


ts
(Preheat)


T 25°C to Peak


13 / 15


Times


**Profile Feature** **Lead-Based Solder** **Lead-Free Solder**


**Average Ramp-Up Rate (Ts max to Tp )** **3** ℃ **/second max.** **3** ℃ **/second max.**


**Preheat: Temperature Min (Ts min)** **100** ℃ **150** ℃


**Preheat: Temperature Min (Ts max)** **150** ℃ **200** ℃


**Preheat: Time ( ts min to ts max )** **60-120 seconds** **60-180 seconds**


**Time Maintained Above: Temperature (TL)** **183** ℃ **217** ℃


**Time Maintained Above: Time (t L)** **60-150 seconds** **60-150 seconds**


**Peak/Classification Temperature (T P)** **215** ℃ **255** ℃


**Time Within 5** ℃ **of Actual Peak Temperature ( tp)** **<10 seconds** **<10 seconds**


**Ramp-Down Rate** **6** ℃ **/second max.** **6** ℃ **/second max.**


**Time 25** ℃ **to Peak Temperature** **<6 minutes max.** **<6 minutes max.**


Note: All temperatures refer to topside of the package, measured on the package body surface.


Document No.: SPC / SK6812RGBW Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


3.5 Heat Generation:


**Thermal design of the end product is of paramount importance. Please consider the heat generation of the**


**LED when making the system design. The coefficient of temperature increase per input electric power is**


**affected by the thermal resistance of the circuit board and density of LED placement on the board, as well as**


**components. It is necessary to avoid in tense heat generation and operate within the maximum rating given in**


**this specification. The operating current should be decided after considering the ambient maximum**


**temperature of LEDs**


3.6 Electrostatic Discharge & Surge Current :


**Electrostatic discharge (ESD) or surge current (EOS) may damage LED.**


**Precautions such as ESD wrist strap, ESD shoe strap or antistatic gloves must be worn whenever handling of**


**LED.**


**All devices, equipment and machinery must be properly grounded.**


**It is recommended to perform electrical test to screen out ESD failures at final inspection.**


**It is important to eliminate the possibility of surge current during circuitry design.**


3.7 Moisture Proof Package


**Cannot take any responsibility for any trouble that are caused by using the LEDs at conditions exceeding**


**our specifications.**


**The LED light output is strong enough to injure human eyes. Precautions must be taken to prevent looking**


**directly at the LEDs with unaided eyes for more than a few seconds.**


**The formal specification must be exchanged and signed by both parties before large volume purchase begins.**


**The appearance and specifications of the product may be modified for improvement without notice.**


14 / 15


Document No.: SPC / SK6812RGBW Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


**Change History**


**FCN No.** **Date** **Rev. No.** **Changes/Reason of changes**


2015-07-31 01 Initial Document


Note
**Items** **Signatures** **Date**


Prepared by Kevin Zhu 2015-07-31


Checked by


Approved by


FCN#


15 / 15


Document No.: SPC / SK6812RGBW Rev. No.: 01


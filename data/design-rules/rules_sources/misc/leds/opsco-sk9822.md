Source: https://www.pololu.com/file/0J1234/sk9822_datasheet.pdf
Retrieved: 2026-11-09

[PDF: 12 pages.]

### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**

## **SK9822**
#### **SPECIFICATION** **INTEGRATED LIGHT SOURCE INTELLIGENT CONTROL (Double** **line transmission) OF CHIP-ON-TOP SMD TYPE LED**

##### Document No.: SPC/ SK9822 Model No.:    SK9822 Description: 5.5x5.0x1.6mm Top SMD Type 0.2Watt Power Double line transmission tegrated light source Intelligent control LED Rev. No.:      01 Date:         2016-03-18


ELECTROSTATIC
SENSITIVE DEVICES


1 / 12


Document No.: SPC / SK9822  Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


INTEGRATED LIGHT SOURCE INTELLIGENT CONTROL

(Double line transmission) OF CHIP-ON-TOP SMD TYPE LED

#### **Model: SK9822**


**1.** **Product Overview :**


**SK9822 is a two-wire transmission channel three (RGB) driving intelligent control circuit and the light**
**emitting circuit in one of the LED light source control. Products containing a signal decoding module,**
**data buffer, a built-in constant current circuit and RC oscillator; CMOS, low voltage, low power**
**consumption; 256 level grayscale PWM adjustment and 32 brightness adjustment; use the double**
**output, Data and synchronization of the CLK signal, connected in series each wafer output action**
**synchronization.**


2. **Main Application Field:**


- **Full color LED string light, LED full color module, LED super hard and soft lights, LED guardrail tube,**
**LED appearance / scene lighting**


- **LED point light, LED pixel screen, LED shaped screen, a variety of electronic products, electrical**
**equipment etc..**


3. **Description:**


- **Top SMD internal integrated high quality external control line serial cascade constant current IC; 5V**
**application; default on electric lights;**


- **Control circuit and the RGB chip in SMD 5050 components, to form a complete control of pixel,**
**color mixing uniformity and consistency;**


- **The two-wire synchronous control.**


- **The three RGB output control, 8Bit (256) color; 5Bit (32) to adjust the brightness;**


- **The three constant current drive, self detection function specific signal**


- **The maximum frequency of 30MHZ serial data input**


- **The double data transmission, built-in support uninterrupted oscillation PWM output, can maintain a**
**static image.**


4. Mechanical Dimensions:


Notes:
1. All dimensions are in millimeters.
2. Tolerance is ± 0.1mm unless otherwise noted


2 / 12


Document No.: SPC / SK9822  Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


**5.** PIN configuration


Item Symbol Pin Name Function description


1 SDI Data Input control signal Input data


2 CKI CLK Input control signal Input Clock data


The signal and power supply and
3 GND Ground
grounding


4 VCC Power power supply pin


5 CKO CLK Output control signal output Clock data


control signal output data
6 SDO Data Input


**6.** General Information

# **SK9822**


SK9822: The default is RGB chips with IC integration


3 / 12


Document No.: SPC / SK9822  Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


**7.** Absolute Maximum Ratings（Ta=25℃,VSS=0V）:


Parameter Symbol Range Unit


Power supply voltage VDD -0.5 ～ +5.5 V


Logic input voltage VIN -0.3 ～ VDD+0.3 V


Working temperature Topt -20~+80 ℃


Storage temperature Tstg -50~+120 ℃


ESD pressure VESD 4K V


**8.** The electrical parameters (unless otherwise specified, TA=-20 ~ +70 ℃, VDD=4.5 ~ 5.5V,
VSS=0V):


Test
Parmeter Symbol Min Typical Max Unit
conditions


The chip supply voltage VDD --- 5.0 5.3 V --

R/G/B port pressure VDS,MAX --- --- 17 V --

The biggest LED output current Imax --- --- 20 mA --
The clock high level width TCLKH --- --- >30 ns --

The clock low level width TCLKL --- --- >30 ns --

Data set up time TSETUP --- --- >10 ns --

The frequency of PWM FPWM --- 1.2 --- KHZ --

Static power consumption IDD --- 1 --- mA --

**9.** Feature Descriptions:


(1) Series data structure


4 / 12


Document No.: SPC / SK9822  Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


(2) 256 level gray level:


**Data** **Duty Cycle**


**MSB……..LSB**


**0000 0000** **0/256**


**0000 0001** **1/256**


**0000 0010** **2/256**


**-**

**-**

**-**

**-**

**-**


**-**

**-**

**-**

**-**

**-**


**1111** **1101** **253/256**


**1111 1110** **254/256**


**1111 1111** **255/256**


(3) PWM input / output signal relationship:


(4) 5-Bit (level 32) brightness adjustment (simultaneous control of OUTR\OUTG\OUTB three port current):


**Data** **Driving Current**


**MSB……..LSB**


**00000** **0/31**


**00001** **1/31**


**00010** **2/31**


**-**

**-**

**-**

**-**

**-**


**-**

**-**

**-**

**-**

**-**


**11101** **29/31**


**11110** **30/31**


**11111** **31/31**


5 / 12


Document No.: SPC / SK9822  Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


(5) Refresh Rate :


Frame rate (=1/ (64+ (32* points)) *CKI (cycle) unit: frames per second )


Such as: 1024 points, CKI frequency is 1MHZ, is =30 frames per second frame rate.


**10.** The typical application circuit:


6 / 12


Document No.: SPC / SK9822  Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


11. Standard LED Performance Graph:


Typical Relative Luminous Flux vs. Forward Current Forward Voltage vs. Forward Current


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


RED


RED


~~BLUE/GREEN~~





~~BLUE/GREEN~~


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


Forward Voltage(V) Tj=25 °C


Wavelength Characteristics


BLUE GREEN
RED


BLUE/GREEN


100%


80%


60%


40%


20%


0.00


RED


700 750 800


0 20 40 60 80 100


Thermal Pad Temperature (T=25°C)


120 400 450 500 550 600 650


Wavelength (nm)


Thermal Pad Temperature vs. Forward Current








BLUE/GREEN


RED


0 20 40 60 80 100


Thermal Pad Temperature (°C)



Typical Radiation Pattern  120°



30°


60°


90°

90 75 60 45 30 15 0 0.2 0.4 0.6 0.8 1.0

Radiation Angle


Document No.: SPC / SK9822  Rev. No.: 01


7 / 12


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


12. Packaging Standard:

###### **S K 9822**


C ATH O DE ID E NTIFIC ATIO N


TA P E FE ED D IR EC TIO N


R EE L(178x12m m )

(IN N ER 1000pcs LED M AX)


E SD P O LY ETH YLEN E BAG


C AR D BO AR D (IN N ER 40 BAG M AX.)


C A R R IER TAPE


C O VER TAPE


S M D
P R O D U C T N O .: SK9822


Q U A N TITY.: 1000 PC S


Lot N o.: LW 2016030902-10


D ATE :2016-03-12


LABE L S KETC H IN G


The reel pack is applied in SMD LED. The LEDs are packed in cardboard boxes after packaging in normal or antielectrostatic bags. cardboard boxes will be used to protect the LEDs from mechanical shocks during transportation. The
boxes are not water resistant and therefore must be kept away from water and moisture.


8 / 12


Document No.: SPC / SK9822  Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**

#### **TOP SMD LED Application Notes**


1. Features

**The Purposes of making OPSCO’s customers and users to have a clear understanding on the ways how to**
**use the LED** .


2. Description

**Generally. The LED can be used the same way as other general purposed semiconductors. When using**
**OPSCO’s TOP SMD LED, the following precautions must be taken to protect the LED.**


3. Cautions
3.1. Dust & Cleaning

**This emitter has a silicone surface, There are many benefits to the silicone surface in terms of optical**
**properties and improved reliability. However, silicone is a softer material and prone to attract dust. While**
**a minimal amount of dust and debris on the LED will not cause significant reduction in illumination, steps**
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


**In order to avoid the absorption of moisture during transportation and storage, LED are packed in**
**the aluminum envelop, A desiccant is included in the aluminum envelop as it absorbs moisture.**
**When moisture is absorbed into the AMT package it may vaporize and expand during soldering.**
**There is a possibility that this can cause exfoliation of the contacts and damage to the optical**
**characteristics of the LEDs. For this reason, the moisture proof package is used to keep**
**moisture to a minimum in the package.**


3.3. Storage


**In order to avoid the absorption of moisture, It is recommended to store SMD LED (in bulk or taped) in the dry**
**box (or the** **desiccator ) with a desiccant, Otherwise to store them in the following environment as**
**recommended.**


**a. Temperature: 5** ℃ **~30** ℃ **b. Humidity: 60% RH Max**


**It is recommended to solder the LED as soon as possible after unpacking the aluminum envelop, But in case**
**that the LED have to be left unused after unpacking envelop again is requested.**


**The LED should be soldering within 1 hours after opening the package.**


**If baking is required, A baking treatment should be performed as follows:**


**70** ℃± **5** ℃ **for more than 24 hours.**


9 / 12


Document No.: SPC / SK9822  Rev. No.: 01


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


10 / 12


Times


**Profile Feature** **Lead-Based Solder** **Lead-Free Solder**


**Average Ramp-Up Rate (Ts max to Tp )** **3** ℃ **/second max.** **3** ℃ **/second max.**


**Preheat: Temperature Min (Ts min)** **100** ℃ **150** ℃


**Preheat: Temperature Min (Ts max)** **150** ℃ **200** ℃


**Preheat: Time ( ts min to ts max )** **60-120 seconds** **60-180 seconds**


**Time Maintained Above: Temperature (TL)** **183** ℃ **217** ℃


**Time Maintained Above: Time (t L)** **60-150 seconds** **60-150 seconds**


**Peak/Classification Temperature (T P)** **215** ℃ **240** ℃


**Time Within 5** ℃ **of Actual Peak Temperature ( tp)** **<10 seconds** **<10 seconds**


**Ramp-Down Rate** **6** ℃ **/second max.** **6** ℃ **/second max.**


**Time 25** ℃ **to Peak Temperature** **<6 minutes max.** **<6 minutes max.**


Note: All temperatures refer to topside of the package, measured on the package body surface.


Document No.: SPC / SK9822  Rev. No.: 01


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


11 / 12


Document No.: SPC / SK9822  Rev. No.: 01


### 东莞市欧思科光电科技有限公司

DONGGUANG OPSCO OPTOELECTRONICS CO., LTD


**Dongguang Factory :** Side of fast in the east, Yucai Road, Dongshan Country, Qishi Town, Dongguan City.
**Dongguan Tel: (769)82632725      Dongguan Fax: (769)82632735**


**Change History**


**FCN No.** **Date** **Rev. No.** **Changes/Reason of changes**


2016-03-18 01 Initial Document


Note
**Items** **Signatures** **Date**


Prepared by Kevin Zhu 2016-03-18


Checked by


Approved by


FCN#


12 / 12


Document No.: SPC / SK9822  Rev. No.: 01


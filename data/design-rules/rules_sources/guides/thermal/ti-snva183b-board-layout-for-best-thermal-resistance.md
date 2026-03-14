---
source: "TI SNVA183B -- Board Layout for Best Thermal Resistance"
url: "https://www.ti.com/lit/an/snva183b/snva183b.pdf"
format: "PDF 15pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 33559
---
# AN-1520 A Guide to Board Layout for Best Thermal Resistance for Exposed Packages

# **ABSTRACT**

This thermal application report provides guidelines for the optimal board layout to achieve the best thermal resistance for exposed packages. The thermal resistance between junction-to-ambient ( $\theta_{JA}$ ) is highly dependent on the PCB (Printed Circuit Board) design factors. This becomes more critical for packages having very low thermal resistance between junction-to-case, such as exposed pad TSSOP (e-TSSOP), exposed pad QFP (e-QFP), and LLP.

A case study of the LM2652 in a 28-lead e-TSSOP package demonstrates the PCB design impact on  $\theta_{JA}$ , and generates design recommendations to improve the thermal performance. Five different PCBs were manufactured with various layouts of ground planes based on a 3"x3" size and 4-layer design. The new PCBs reduced  $\theta_{JA}$  from the range of 40~50°C/W down to 25~30°C/W. Finite Element Analysis (FEA) modeling was used for sensitivity analysis to identify the key PCB parameters.

|           | 1       | Introduction                                                                                                                                                  | 3  |
|-----------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|----|
|           | 2       | DOE of PCB (Printed Circuit Board) Design                                                                                                                     | 3  |
|           | 3       | Test Methodology                                                                                                                                              | 4  |
|           | 4       | Test Results                                                                                                                                                  |    |
|           |         | 4.1 Thermal Resistance $\theta_{JA}$                                                                                                                          | 6  |
|           |         | 4.2 Thermal Resistance                                                                                                                                        |    |
|           | 5       | Modeling                                                                                                                                                      |    |
|           |         | 5.1 Parametric Study                                                                                                                                          |    |
|           |         | 5.2 Results and Discussion                                                                                                                                    |    |
|           | 6       | PCB Design Recommendations                                                                                                                                    |    |
|           | 7       | Conclusion                                                                                                                                                    | 14 |
|           |         | List of Figures                                                                                                                                               |    |
|           | 1       | Cross Section View of Thermal Test PCB Assembled With Package                                                                                                 | 3  |
|           | 2       | Manufactured PCB's                                                                                                                                            | 4  |
|           | 3       | Top View of 28L TSSOP EXP PAD                                                                                                                                 | 5  |
|           | 4       | Pins Showing Diode Characteristics                                                                                                                            | 5  |
|           | 5       | LM2652 Diode Voltage vs. Junction Temperature                                                                                                                 | 6  |
|           | 6       | (a) The Image Of IR Camera for the Temperature Distribution Near Package and (b) the Temperature Plot Along the Package Middle Line                           | 7  |
|           | 7       | (a), (b) And (c) for the Three Types of PCB Boards Analyzed Using FEA, and (d) Shows FEA Mesh for the Effect of the Dummy Regions Outside the Dog Bone Region | 8  |
|           | 8       | Temperature Distributions of the Board "Ideal" With 28L TSSOP EXP PAD                                                                                         | 10 |
|           | 9       | Temperature Distributions of the Board "4-Layer JEDEC" With 28L TSSOP EXP PAD                                                                                 | 11 |
|           | 10      | Effects of Airflow (a) and Device Power (b) on the Thermal Resistance $\theta_{JA}$                                                                           | 11 |
|           | 11      | Effects of Die Size (a) and Die Attach Material (b) on the Thermal Resistance $\theta_{JA}$                                                                   | 12 |
|           | 12      | Effect of Solder Coverage (a), Diameter of Thermal Vias (b), and Thermal Via Distribution (c) on the Thermal Resistance $\theta_{JA}$                         | 12 |
|           | 13      | Thermal Via Distribution on the Thermal Resistance $\theta_{JA}$                                                                                              | 13 |
| 1 | DOE of Test PCB                                                                       | 4 |
|---|---------------------------------------------------------------------------------------|---|
| 2 | $	heta_{JA}$ Results On DOE of Test Boards and Different Power and Airflow Conditions | 6 |
| 3 | $oldsymbol{\Psi}_{JT}$ Results Under The Device Power 2W And 3W                      | 7 |
#### 1 Introduction

It is well known that the thermal resistance of the package, especially, theta JA or  $\theta_{JA}$ , (thermal resistance between junction-to-ambient) is highly dependent on the PCB in which the parts are mounted for thermal testing. The effect of the PCB is more critical when the package has extremely low theta JC ( $\theta_{JC}$  or thermal resistance between junction-to-case) because the thermal resistance between case to PCB, and PCB to ambient air, becomes more dominant than that between die to package case.

This is the main reason why both  $\theta_{JC}$  and  $\theta_{JA}$  have been typically used to compare the thermal performance of the package excluding the PCB effect. Nevertheless,  $\theta_{JA}$  is still considered as the most popular and important specification in the data sheet. The system engineer needs  $\theta_{JA}$  values when designing his system based on the operating temperature, not on the temperature on the package case. The condition of the test PCB for  $\theta_{JA}$  measurement should be similar with that in the real application in terms of size and number of layers of the PCB.

The goal of this application report is to improve  $\theta_{JA}$  measurement and thermal performance by improving the test PCB, and suggest guidelines for designing the PCB for  $\theta_{JA}$  measurement of exposed packages. The application engineer needs to refer to this guideline for designing the evaluation boards, especially for high power devices since the PCB will critically affect the thermal performance, including device power efficiency, SOA (safe operating area), and reliability.

LM2652 in a 28-lead e-TSSOP (Exposed Pad Thin Shrink Small Outline Package) was selected as a case study. Five different PCBs were manufactured with various layouts of ground plane in the size of 9 square inch and 4-layer configuration with 2oz/1oz/1oz/2oz Cu.

 $\theta_{JA}$  results and PCB design recommendations presented in this application report can be applied to other packages with exposed DAP (die attach paddle), such as e-QFP (exposed Quad Flat Pack) and LLP (Leadless Leadframe Package) with different pin numbers.

# 2 DOE of PCB (Printed Circuit Board) Design

The test boards are 9 square inch (2.65"x3.4") with a 4-layer Cu configuration of 2oz/1oz/1oz/2oz. As shown in Figure 1, thermal vias connect the DAP landing pattern on the top layer, the first interlayer which is also assigned as ground, and the bottom layer. Five different thermal test boards were designed to demonstrate the thermal effects of different layout parameters as summarized in Table 1. The layout factors include the size of the top ground area called "dog bone" area, connection to the DAP landing pattern, number of thermal vias on ground plane near the package (called dog bone via, 0.018" diameter), and the solder resist covering the top and bottom layers. The dog bone area is 0.0663 inch square for Real#1 board, and Real#2 has 2 times larger dog bone area than Real#1. The number of vias in the DAP landing pattern (DAP via, 0.008" diameter) is fixed. Excluding the ideal and modified JEDEC board, the rest of the top and bottom layers contain the cross-hatched Cu lines with 50% Cu area density. Figure 2 shows the top view pictures of the five different PCBs manufactured.

Figure 1. Cross Section View of Thermal Test PCB Assembled With Package

#### Table 1. DOE of Test PCB

| PCB ID                 | Description                                                                                            |
|------------------------|--------------------------------------------------------------------------------------------------------|
| Ideal                  | Maximize Cu ground area for all layer<br>(Note: The text seems to continue on a new line in the image) |
| Real#1                 | Dog bone ground in top & bottom; Full Cu planes in 1st and 2nd interlayer                              |
| Real#2                 | 2 times dog bone area than Real#1 on top & bottom                                                      |
| Real#3 (Real#2 + SR)   | Cover Solder Resist on top and bottom; Rest is same with Real#2                                        |
| Modified JEDEC 4 layer | No GND on top and bottom other than DAP landing; Thermal via connected 1st interlayer                  |

Ideal Board

Real#1 Board

Real#2 Board

Real#3 Board

Modified JEDEC Board

Figure 2. Manufactured PCB's

# 3 Test Methodology

Thermal resistance is defined as the difference in temperature between two closed isothermal surfaces divided by the total heat flow between them. In case of  $\theta_{\text{JA}}$  measurement:

$$\theta_{JA}$$
 = (Tj – Ta)/ $P_{diss}$

where, Tj is the temperature measured at the semiconductor junction and Ta is the ambient temperature, which is measured in a test environment and fixed at  $20\sim25^{\circ}$ C.  $P_{\text{diss}}$  is the power dissipated by the device. There are two ways to power the device to generate heat, which are substrate diode powering and active powering. Substrate diode powering is used for this test, in which the isolated diodes are found by curve tracing. Those diodes are used for heating the device and sensing the temperature by measuring the forward voltage drop of the diode depending on the junction temperature. The active powering test is to measure the junction temperature and  $\theta_{\text{JA}}$  with the device on evaluation boards. Passive components are required. Active powering has the advantage that  $\theta_{\text{JA}}$  is measured while the device is in operation, but the results can be more easily interrupted by electrical interference.

Figure 3 shows the top view of the LM2652 devices with pin ids. Figure 4 shows the diodes found through curve tracing or simple diode check. The internal drain-to-source body diode of the PGND and PVIN is used for monitoring the junction temperature by measuring forward voltage drop, while SW and PVIN path is used for heating the device with supplying current. Figure 5 shows the plot of diode voltage vs. junction temperature measured from PGND and PVIN, which shows good linear relationship.

Figure 3. Top View of 28L TSSOP EXP PAD

Figure 4. Pins Showing Diode Characteristics

Figure 5. LM2652 Diode Voltage vs. Junction Temperature

#### 4 Test Results

#### 4.1 Thermal Resistance $\theta_{\mu}$

The measurement results of thermal resistance  $\theta_{JA}$  are shown in Table 2 for high performance and modified JEDEC boards. Four different heating powers and two airflow conditions were applied. Also,  $\theta_{JA}$  measured with the same LM2652 package, but with a 2-layer PCB test board (explained under ) is also listed for comparison.

Table 2.  $\theta_{JA}$  Results On DOE of Test Boards and Different Power and Airflow Conditions

| PCB description     |        | 0.5W | 1W   | 1.5W | 2W   | 1W @ 200 LFPM | 1W @ 400 LFPM |
|---------------------|--------|------|------|------|------|---------------|---------------|
|                     | Ideal  | 27.7 | 26.7 | 25.9 | 25.5 | 18.3          | 16.8          |
| High<br>Performance | Real#1 | 28   | 27.8 | 27.8 | 27.7 | 19.4          | 19.9          |
| PCB                 | Real#2 | 27.3 | 27.1 | 26.7 | 26.3 | 20.6          | 19.1          |
|                     | Real#3 | 26.4 | 25.9 | 25.4 | 25   | 20            | 18.9          |
| JEDEC (modified)    |        | 33.5 | 32.4 | 31.3 | 30.3 | 27            | 25.5          |
| Old PCB (1)         |        | 47.6 | 44.7 |      | 43.4 |               |               |

<sup>(1)</sup> Old PCB: 2-layer – 1oz/1oz, 2 inch square ground plane on backside of PCB, DAP on the top layer connected to the bottom layer with thermal vias.

Aside from the well-known large effect of the airflow condition and the moderate effect of device power on  $\theta_{JA}$  as shown in Table 2, the effects of board design factors are also addressed. Based on the results of the 2W heating condition in Table 2, the effects of some board design factors on the thermal resistance  $\theta_{JA}$  are summarized as follows.

- Effect of PCB: It is obvious that a high performance multi-layer PCB helps to reduce  $\theta_{JA}$  significantly. For example,  $\theta_{JA}$  is 43.4°C/W and 25°C/W on the 2-layer PCB and the "Real#3" board, respectively. It decreases about 42%.
- Effect of ground planes: The result of the modified JEDEC board shows about 21% higher  $\theta_{JA}$  than that of the high performance PCB. The reason is that the modified JEDEC board does not have ground planes on the top and bottom layers for heat sinking effects.
- Effect of copper coverage: The thermal resistance  $\theta_{JA}$  of the boards "Ideal" and "Real#2", as shown in Table 2, are 25.5 and 26.3°C/W. The thermal resistance increases 3.1% when the copper area on the top and bottom layers decreases to about 50% for the board "Real#2" from the maximum copper area for the board "Ideal".
- Effect of solder resist covering:  $\theta_{JA}$  is 26.3°C/W and 25°C/W on the "Real#2" and "Real#3" boards,

respectively. The solder resist covering reduces  $\theta_{JA}$  by 4.9% due to better thermal radiation.

• Effect of dog bone region:  $\theta_{JA}$  is 27.7°C/W and 26.3°C/W on the "Real#1" and "Real#2" boards, respectively. The larger dog bone region with more vias on the "Real#2" boards reduces  $\theta_{JA}$  by 5%. The effect of the dog bone region depends on the copper layers and vias of the PCB. For the case of less copper layers and less number of vias, the effect of the dog bone region will become larger. In other words, the dog bone region can significantly improve the thermal performance of a low effective thermal conductivity PCB.

# 4.2 Thermal Resistance

Power

3W

21.9

21.6

 $\Psi_{JT}$  is defined as  $\Psi_{JT} = (T_j - T_{top})/P_{diss}$  where  $T_j$  and  $T_{top}$  are the junction temperature and the temperature at the top center of the package, respectively.  $\Psi_{JT}$  is often used to predict the junction temperature at the end user environment based on the temperature  $T_{top}$ . The temperature  $T_{top}$  can be measured by a thermocouple located at the top center of the package.  $\Psi_{JT}$  is dependent on the PCB. The PCB with higher effective conductivity will give a lower value of  $\Psi_{JT}$ . Also, it is dependent on the device power and power distribution called "Chip Power Map". Table 3 shows the measured values of  $\Psi_{JT}$  of the LM2652 package on the "Real#3" board under the device power at 2W and 3W.

Ambient Temp. Junction Temp. Temp. at package top center  $\Psi_{JT}$

67.5

88.4

2.95

3.3

Table 3.  $\Psi_{\text{JT}}$  Results Under The Device Power 2W And 3W.

73.4

98.3

When  $\Psi_{JT}$  is known, the junction temperature can be easily predicted based on the temperature at the top center of the package, which can be measured by using a thermocouple or based on the image from an IR camera. Figure 6 shows the measurement using an IR camera for the same sample used in Table 3 under 2W device power. Figure 6(a) is the IR image and Figure 6(b) shows the temperature plot along the middle line through the package top. The temperature at the top center of the package is about 68°C, which is close to the value 67.5°C in Table 3 using thermocouple. Based on the top center temperature 68°C and  $\Psi_{JT}$  2.95°C/W, the junction temperature is evaluated as 73.9°C based on the formula  $T_j = \Psi_{JT} \times P_{diss} + T_{top}$  which is close to the measured value of the junction temperature in Table 3.

Figure 6. (a) The Image Of IR Camera for the Temperature Distribution Near Package and (b) the Temperature Plot Along the Package Middle Line

# 5 Modeling

 $\theta_{JA}$  is used to characterize the heat dissipation ability of a package/board system from the die through the PCB board to the ambient environment. As the thermal resistance from PCB board to ambient is much larger than that from die to board, it is more significant to study the effect of the PCB board design on the thermal resistance  $\theta_{JA}$  in detail.

The thermal conductivities of die, die attach, mold compound, leadframe, bonding wire, copper trace, FR4, Pb/Sn solder material, and solder mask used in FEA models for the comparison study are 111, 1.1, 0.92, 370, 317, 377, 0.35, 57.3, and 0.3 in unit W/m-K. Other parameters including the ambient temperature, airflow, power and emissivity are listed in Table 4 together with the results of thermal resistances.

# 5.1 Parametric Study

The PCBs analyzed by FEA models are shown in Figure 7, where the details of the copper structures of the top layers are displayed. Figure 7(a) is for modeling the board "Ideal", Figure 7(b) with corresponding effective conductivities of the top and bottom layers is for modeling the boards "Real#1", "Real#2" and "Real#3", Figure 7(c) for modeling the modified JEDEC 4-layer board, and Figure 7(d) for modeling the effect of the dummy regions outside the dog bone region.

Figure 7. (a), (b) And (c) for the Three Types of PCB Boards Analyzed Using FEA, and (d) Shows FEA Mesh for the Effect of the Dummy Regions Outside the Dog Bone Region

In addition to those PCB design factors summarized in the preceding section, some other factors involved in packages and boards were also studied using FEA based on the thermal performance of a 28L e-TSSOP package on various PCB boards. Simulation results of LLP packages are also used to show the effects of solder layer and the thermal via designs underneath the exposed pad of packages. All the parameters studied include:

- · Vias on the dog bone region
- · Vias on the dummy region outside the dog bone region
- Composite die (10 micron thick copper on Si)
- Airflow
- Die size
- Device power
- · Die attach materials
- Bonding wire materials (gold or copper)
- Solder coverage between exposed pad and board
- · Thermal via design

### 5.2 Results and Discussion

Comparison among PCB boards: The FEA results are listed in Table 4. The thermal radiation is not lumped into the effective heat transfer coefficient of the surfaces of packages and boards, but modeled separately. It is seen that the emissivity value has large effects on the predicted thermal resistance  $\theta_{JA}$ . Compared to the measurement results, the finite element model gives 4.8% smaller  $\theta_{JA}$  for the board "Real#3". As the same emissivity 0.5 is used, the 4.9% difference between the "Real#2" and "Real#3" boards that is observed in the measurement is not captured by the model. For other PCB design factors, the model is agreeable with the measurement results, including the effects of ground planes, copper coverage and dog bone region. Also, the effect of the dummy region as shown in Figure 7(d) is small.

Table 4. Comparison Among The Thermal Performances Of The Various PCB Boards

| $\begin{array}{c} \text{with Radiation} \\ \epsilon_{\text{Board}} = 0.5 \\ \epsilon_{\text{pkg}} = 0.7 \end{array}$ | 0 m/s Results |        |        |                                          |                                          |                           |  |  |  |
|----------------------------------------------------------------------------------------------------------------------|---------------|--------|--------|------------------------------------------|------------------------------------------|---------------------------|--|--|--|
| Board Type                                                                                                           | Ideal         | Real#1 | Real#2 | Real#3 $(\epsilon_{\text{Board}} = 0.5)$ | Real#3 $(\epsilon_{\text{Board} = 0.9})$ | Modified JEDEC<br>4–Layer |  |  |  |
| Power (W)                                                                                                            |               | 1.84   |        |                                          |                                          |                           |  |  |  |
| Ambient<br>Temperature<br>TA (°C)                                                                                    |               | 25     |        |                                          |                                          |                           |  |  |  |
| Junction<br>Temperature<br>TJ (°C)                                                                                   | 68.5          | 69.4   | 68.7   | 68.7                                     | 63                                       | 73                        |  |  |  |
| Package Top<br>Surface<br>Ttop (°C)                                                                                  | 67.9          | 68.8   | 68.1   | 68.1                                     | 62.4                                     | 72.2                      |  |  |  |
| Board Top<br>Surface<br>Tbrd (°C)                                                                                    | 58            | 59.9   | 59.3   | 59.3                                     | 53.6                                     | 58.2                      |  |  |  |
| θJA (°C/W)                                                                                                           | 23.6          | 24.1   | 23.8   | 23.8                                     | 20.7                                     | 26.1                      |  |  |  |
| ΨJT (°C/W)                                                                                                           | 0.326         | 0.326  | 0.326  | 0.326                                    | 0.326                                    | 0.435                     |  |  |  |
| ΨJT (°C/W)                                                                                                           | 5.7           | 5.2    | 5.1    | 5.1                                      | 5.1                                      | 8.0                       |  |  |  |
| without<br>Radiation                                                                                                 |               |        |        |                                          |                                          |                           |  |  |  |
| Junction<br>Temperature<br>TJ (°C)                                                                                   | 84.4          | 85.3   | 84.6   | 84.6                                     |                                          | 85.5                      |  |  |  |

Table 4. Comparison Among The Thermal Performances Of The Various PCB Boards (continued)

| $\begin{array}{c} \text{with Radiation} \\ \epsilon_{\text{Board}} = 0.5 \\ \epsilon_{\text{pkg}} = 0.7 \end{array}$ | \varepsilon_{\rm pkg}=0.7 | 0 m/s Results |       |       |       |
|----------------------------------------------------------------------------------------------------------------------|---------------------------|---------------|-------|-------|-------|
| Package Top<br>Surface<br>Ttop (°C)                                                                                  | 83.7                      | 84.7          | 84.0  | 84.0  | 84.8  |
| Board Top<br>Surface<br>Tbrd (°C)                                                                                    | 73.8                      | 75.7          | 75.2  | 75.2  | 70.7  |
| \theta_{JA} (°C/W)                                                                                                   | 32.3                      | 32.8          | 32.4  | 32.4  | 32.9  |
| \Psi_{JT (°C/W)}                                                                                                     | 0.380                     | 0.326         | 0.326 | 0.326 | 0.380 |
| \Psi_{JT} (°C/W)                                                                                                     | 5.8                       | 5.2           | 5.1   | 5.1   | 8.0   |

Figure 8 and Figure 9 show the temperature distribution near packages on the "Ideal" and JEDEC boards. While the copper coverage is important to achieve an optimized thermal performance requires keeping good heat dissipation paths in all directions. Since the board area in the vicinity of the package will see the most heat, it is imperative to design boards with good thermal conductivity near the assembled package. For example, for the board designed for the experimental test shown in Figure 2 Real#3 board, if the copper traces were extended as far as possible, the thermal resistance would be reduced up to 10% or up to 2°C/W.

Figure 8. Temperature Distributions of the Board "Ideal" With 28L TSSOP EXP PAD

Figure 9. Temperature Distributions of the Board "4-Layer JEDEC" With 28L TSSOP EXP PAD

Effect of other parameters: Of the ten parameters mentioned previously, the airflow and device power are associated with the experimental measurement conditions, while the other eight are associated with the designs of package and PCB. The FEA simulation does not model the airflow directly. Airflow is included by assuming an effective heat transfer coefficient. With a properly validated heat transfer coefficient, the model can give consistent results with experimental measurement for a certain airflow velocity. As the radiation boundary condition is directly used in the FEA model, the dependence of the thermal resistance  $\theta_{JA}$  on the power is simulated. The effects of airflow and device power are shown in Figure 10(a) and Figure 10(b), which is agreeable with the measurement trend.

Figure 10. Effects of Airflow (a) and Device Power (b) on the Thermal Resistance  $\theta_{1A}$

Four factors without importance: Of the other eight parameters associated with the designs of package and PCB board, FEA simulations show that the effect of the following four parameters is small:

- Vias on the dog bone region
- Vias on the dummy region outside the dog bone region
- · Composite die (10 micron thick copper on Si)
- Bonding wire materials

For example, varying from 0 to 24 dog bone vias causes the thermal resistance  $\theta_{JA}$  to decrease by 0.5%, while the effect of the other three parameters is less than 0.1%.

Four factors with importance: The die size and die attach material have significant effects on the thermal resistance  $\theta_{JA}$ , as shown in Figure 11(a) and Figure 11(b). Based on Figure 11(b), using a film die attach (conductivity of 0.36 W/m-K) to replace a liquid die attach material (conductivity of 1.1 W/m-K) will significantly increase the thermal resistance  $\theta_{JA}$ .

Figure 11. Effects of Die Size (a) and Die Attach Material (b) on the Thermal Resistance  $\theta_{JA}$

Figure 12(a) shows the effect of solder coverage between exposed pad and board on the thermal resistance  $\theta_{JA}$ . Full solder coverage is labeled as 100% solder coverage in Figure 12(a). The smaller solder coverage assumed in FEA simulation for Figure 12(a) is located underneath the middle of the exposed pad. When solder coverage decreases to 50%, 20%, 10% and 5%, the thermal resistance  $\theta_{JA}$  will increase by about 4%, 13%, 19%, and 34%, respectively. The 10% solder coverage is a critical point. Once solder coverage becomes less than 10%,  $\theta_{JA}$  drastically goes up. However, the critical point is dependent on the packages and boards. For example, for a 44L LLP on a 4L JEDEC board, the critical point is 20%. In general, the change of the thermal resistance  $\theta_{JA}$  will be less than 5% for the solder coverage larger than 50%.

Figure 12. Effect of Solder Coverage (a), Diameter of Thermal Vias (b), and Thermal Via Distribution (c) on the Thermal Resistance  $\theta_{JA}$

Figure 12(b) shows the effect of the thermal via diameter on the thermal resistance  $\theta_{JA}$ . Two thermal via diameters (0.33 mm and 0.2 mm) are investigated. The percent change of  $\theta_{JA}$  on the y-axis of Figure 12(b) is defined as the change of  $\theta_{JA}$  as the via diameter changes from 0.33 mm to 0.2 mm divided by  $\theta_{JA}$  associated with 0.33 mm via diameter. The maximum number of vias is determined based on the pad size and 1.2 mm distance between vias. The simulation is based on 4L JEDEC board. The 0.2 mm via diameter may increase the  $\theta_{JA}$  by about 15~25% for packages with a small exposed pad (maximum number of vias is 4 or less). On the other hand, for packages with a large exposed pad (maximum number of vias is 9 or more), the effect of via diameter is not so significant, generally less than 10%.

Figure 13 shows the effect of the number and distribution of vias on  $\theta_{JA}$  based on a 36L LLP with 7mm x 7mm exposed pad on 4L JEDEC board. Two die sizes are simulated.  $\theta_{JA}$  variation due to the number and distribution of the vias shown in Figure 13 is generally valid for other packages with large exposed pads.

Figure 13. Thermal Via Distribution on the Thermal Resistance  $\theta_{JA}$

#### 6 PCB Design Recommendations

The following recommendations can be used as guidelines for designing PCB for thermal testing or functional evaluation.

- Use large and multi-layer PCB boards (at least 4 layers, 3"x3", 2oz/1oz/1oz/2oz).
- Use thermal vias connecting the DAP landing pattern on the top layer, inter GND, and bottom GND layer in both DAP landing pattern and ground plane.
- Make the thermal vias near the periphery of the exposed DAP if the maximum number of vias is not applicable.
- Use 0.33 mm diameter of vias if possible, especially for packages with small exposed pad, which may reduce  $\theta_{JA}$  about 15~25%.
- Generate as large a GND plane as allowable on the top and bottom layers, especially right near the package.
- Connect the top GND pattern with the DAP landing pattern underneath the package.
- Gather the same functional pins together in die design, such as for GND, PVIN, POUT in the power device. This will allow maximizing the Cu area right near the package by eliminating the needs for isolating each lead pattern on the PCB.
- Make the traces as long as possible so that a better thermal conductivity near the package is achieved.

#### 7 Conclusion

For packages having exposed DAP such as e-TSSOP, e-QFP, and LLP, the thermal resistance from junction-to-ambient,  $\theta_{\text{JA}}$ , is critically dependent on the configuration of the test PCB. Therefore, it is necessary to use large high thermal performance PCBs with multiple layers of thick Cu, thermal vias, and as large a ground plane as allowable. The thermal vias should be used to connect the DAP landing pattern, internal ground plane, and bottom ground plane. It is critical to have a large ground plane on the top and bottom layers and connection to the DAP landing pattern for thermal dissipation. For high power devices, it is recommended that the same functional pins be shorted electrically, so to form a solid landing pattern on the top layer maximizing the Cu area right near the package.

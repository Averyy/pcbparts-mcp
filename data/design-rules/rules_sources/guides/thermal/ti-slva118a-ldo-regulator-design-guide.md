---
source: "TI SLVA118A -- LDO Regulator Design Guide"
url: "https://www.ti.com/lit/an/slva118a/slva118a.pdf"
format: "PDF 25pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 39658
---
# *Linear Regulator Design Guide For LDOs*

*Bruce Hunter and Patrick Rowland PMP Portable Power*

# **1 Purpose**

The purpose of this application report is to explore the thermal considerations in using linear regulators. When finished, the reader will understand the following:

- Why thermal considerations are important for every linear regulator design
- The thermal equations governing a linear regulator
- How to evaluate/choose linear regulators for a design

In addition, this document provides a *summary of approach and equations* in Chapter 6. This chapter is designed as a one page reference for the reader.

# **2 The Basics**

The first considerations for choosing a linear regulator are input voltage (VI), output voltage (VO), and output current (IO). These are necessary for selecting the appropriate linear regulator for an application. Other very necessary, although often over looked, considerations in linear regulator selection are the application specific thermal considerations. These thermal considerations are the topic of this application report.

For a short review on the theory of operation, a linear regulator has a pass element that is managed by the controller portion of the IC. The controller monitors the feedback and either opens or restricts the pass element to maintain a constant output voltage over variation in the input voltage and the output current required by the load. A helpful analogy is to think of the control portion of the regulator as a lamp dimmer switch or potentiometer.

Where altering a dimmer switch varies the amount of light, a linear regulator alters the pass element to maintain a constant output voltage. We know that Ohm's law states V = I ×R. If a linear regulator maintains a constant output voltage (V) over varying input voltage and output current into the load, it follows that R is what is being controlled by the regulator. So that is how we maintain the output voltage, but where does the heat come from?

The difference between the input voltage and output voltage with a fixed load current is energy that is dissipated by the linear regulator. Nearly all of this energy is converted to heat. How to calculate and manage this heat is the topic of this application report.

# **3 Power Dissipation in the Linear Regulator**

To help us understand the power dissipation requirements at a high level, we use the potentiometer model shown in Figure 1.

**Figure 1. Potentiometer Model of a Linear Regulator**

While regulating, the pass element is always on in a linear regulator. Using the potentiometer model as a guide and remembering Kirchoff's current law, we can see how the input current must be equal to the output current. Armed with that knowledge, we can look at power and power dissipation in our system.

Since our system must observe physics and the conservation of energy, we can use our knowledge of VI, VO, and current to identify how power is distributed in our model. We start with the power placed into our system:

$$P_{l} = I_{l} \times V_{l} \tag{1}$$

Following the same thought process, the power delivered to the load is:

$$P_{O} = I_{O} \times V_{O} \tag{2}$$

Now, looking back at Figure 1 we remember that II roughly equals IO. The difference between PI and PO is the power that is burned or dissipated by the regulator. The quantity of dissipated power (PD) can be extracted by the following equation:

$$P_{D} = P_{I} - P_{O} \tag{3}$$

PD is almost entirely heat dissipated by the linear regulator thus PD is precisely what we are concerned with thermally when selecting a package. If we use equation 3 to arrive at a maximum PD for an application, we refer to that variable as PD(max). Making this distinction becomes useful in later equations.

Before moving on, we should take a moment to look at equation 3 in slightly more detail. Equation 3 can be rewritten from before as:

$$P_{I} = P_{O} + P_{D} \tag{4}$$

In most applications, the approximation of assuming II = IO is sufficient for thermal calculations. The model we have used up to now has ignored the quiescent current of the linear regulator. If we add the quiescent power (PQ) required by the linear regulator, equation 4 changes to:

$$P_{I} = P_{O} + P_{D} + P_{Q} \tag{5}$$

PQ is derived by multiplying the input voltage by the quiescent current of the regulator. Thermally, PQ is usually insignificant, as it is orders of magnitude smaller than the output current. For example, the TPS789xx series of 100 mA (or 0.1 A) low dropout regulators (LDO) has a typical IQ of 17 µA (or 0.000017 A). In an example where the TPS78925 is used with VI = 3.3 V, VO = 2.5 V, and IO = 100 mA we can see how PQ (56 µW) is substantially smaller than PD (80 mW). Thus, out of practicality and for simplicity we examine the thermal considerations for linear regulators based on equation 4 ignoring quiescent current.

Quiescent current can have a significant impact on efficiency in power sensitive applications. This is covered briefly in *Other Useful Items* (Chapter 8) and in more detail in the *Efficiency* portion of TI application reports SLVA079 – *Understanding the Terms and Definitions of Low-Dropout Voltage Regulators* and SLVA072 – *Technical Review of Low Dropout Voltage Regulator Operation and Performance,* as listed in Appendix B.

Another topic that warrants a brief commentary is steady state verses transient or pulsed current demand of a load from its power supply. In many applications, an LDO supplies both steady-state and pulsed load current. A given design may have low duty cycle load transient currents in addition to the steady-state load. The current transients can approach the internal fixed current limit of the LDO, which is normally between 2 and 4 times the continuous current rating of the device. However, if we have an excessive junction temperature rise, thermal shutdown is activated. The thermal shutdown junction temperature typically occurs at 150°C. Whether the thermal design is based upon the average load current or designed to handle the maximum peak current depends upon the duration and frequency of occurrence of the load transient. In either case we are safe if we do not exceed the absolute maximum junction temperature rating of the device.

Returning to PD, the power ratings of LDOs are normally based upon steady state operating conditions. Steady-state conditions between junction and case are typically achieved in less than 10 seconds where several minutes may be required to achieve steady-state junction to ambient. Transient thermal impedance illustrates the thermal response to a step change in power. This information is provided for discrete power devices and normally not for integrated circuits. The transient thermal response is a function of die size, die attach, and package. We limit the scope of our discussion to steady-state thermal resistance.

By utilizing the thermal equations that follow in Chapter 4, we ensure that the junction temperature of our linear regulator remains within acceptable limits. A semiconductor's long term reliability is affected by its operating junction temperature; therefore, it is important to maintain a junction temperature that falls below the manufacturers absolute maximum operating junction temperature. This restriction limits the device's power dissipation capability. To do this, we need to calculate the maximum allowable dissipation, PD(max), and the actual dissipation, PD, which must be less than or equal to PD(max). How to make these calculations is what we explore next.

Factors which influence thermal performance include PCB design, component placement, interaction with other components on the board, airflow, and altitude. There is no substitute for a system level thermal analysis to ensure a successful design.

# 4 Thermal Equations—Will My Part Work?

With an understanding of  $P_D$ , now we can examine the thermal considerations  $P_D$  generates. The following equation links  $P_D$  to the thermal specifications for a linear regulator:

$$P_{D} = (T_{J} - T_{A})/\theta_{JA} \tag{6}$$

Where

 $\theta_{JA}$  = theta ja (junction to ambient) – °C/W

 $T_J$  = junction temperature rating –  $^{\circ}$ C

 $T_A$  = ambient temperature –  $^{\circ}C$

P<sub>D</sub> = power dissipated in watts – W

Equation 6 enables us to relate power dissipation with the thermal characteristics of the die/package combination and ambient temperature. It is useful to manipulate equation 6 to:

$$\theta_{\mathsf{JA}} = (\mathsf{T}_{\mathsf{J}} - \mathsf{T}_{\mathsf{A}})/\mathsf{P}_{\mathsf{D}} \tag{7}$$

Equation 7 is useful as  $T_J$ ,  $T_A$ , and  $P_{D(max)}$  (see equation 3) are often known quantities in an application. By using these three known values, equation 7 will tell us what value of  $\theta_{JA}$  is necessary in order to have enough thermal conductance or thermal dissipation capability for our linear regulator in a particular application. Having the appropriate thermal conductance ensures that the  $P_{D(max)}$  does not exceed the  $P_D$  that the linear regulator is capable of supporting. Exceeding the  $P_D$  that the regulator can support creates extreme junction temperatures which in turn impact the reliability of the design. For the remainder of this application note, if we use  $P_{D(max)}$  in equation 7 to determine a maximum  $\theta_{JA}$  for an application, we are referring to it as  $\theta_{JA(max)}$ .

In looking at equation 7,  $\theta_{JA}$  decreases with an increase in  $T_A$  or  $P_D$ . It follows that the lower  $\theta_{JA}$  is from equation 7, the more challenging the thermal requirements. Additionally, the lower a  $\theta_{JA}$  is specified in a data sheet, the better thermal conductance a device exhibits.

Most vendors specify  $\theta_{JA}$  in a linear regulator data sheet as the thermal specification. At TI, this was the case until recently and is still the case for higher power, higher output current linear regulators. To make regulator selection easier, TI has moved to a different way of representing the same information. As an example, data sheet examples have been provided below. (NOTE: xx is the voltage option. For example: TPS77618 is the 1.8 V option in the family). Figure 2 and Figure 3 show power dissipation ratings based on package, airflow, ambient temperature, and in the case of the PowerPAD<sup>TM</sup> package, copper area underneath the device. In this case, instead of looking for a  $\theta_{JA}$ , we can simply compare  $P_{D(max)}$  from equation 3 to these tables so long as we cross-reference the appropriate package, ambient temperature, copper area, and airflow. Figure 4 is from page 13, of the REG103 data sheet. It demonstrates how drastically factors such as airflow or copper area, as in this case, can alter the thermal properties of a linear regulator.

# **5 Thermal Equations—What to Do if My Part Does not Work?**

In situations where a device or package is thermally insufficient, the first step is to look at other package options. This is one significant reason why vendors often offer linear regulators in multiple package options and why the smallest package is not always the appropriate choice. It is also possible that, if the original device does not have an appropriate package option, an engineer needs to look at a linear regulator with higher output current than is required by the application to obtain the necessary θJA to ensure reliable operation. Linear regulators with higher output current generally have a larger die and come in larger, more thermally efficient, packages. Both of these items lead to better, lower θJA or higher PD(max), ratings. The following figure shows a list of packages relative to thermal efficiency.

**Figure 5. Thermal and Area Comparison of Packages**

θJA for a package varies between different parts and different vendors. Variables that affect θJA include the copper properties of a board, the number of layers of a board, the airflow over a board, and whether a high K or low K model was used (see TI application note SCAA022A – *K−Factor Test Board Design Impact on Thermal Impedance Measurements*), etc. Figure 5 is an estimate for comparison purposes only. Always consult the data sheet to obtain θJA or PD(max) for a given device and package option.

There is some overlap and minor variation in packages depending on pin count and die size, but Figure 5 is a starting point for comparison of common packages. Also included in the list is TI's patented PowerPAD™ packaging technology. PowerPAD footprints and dimensions remain standard while the exposed thermal pad greatly enhances the thermal capabilities of the PowerPAD MSOP, TSSOP, and SOIC packages. For more information about PowerPAD, see TI application brief (http://www−s.ti/com/sc/techlit/slma004), *PowerPAD Made Easy*, and/or application note, (http://www−s.ti/com/sc/techlit/slma002), *PowerPAD Thermally Enhanced Package*. Both of these documents are listed in Appendix B.

Where thermal considerations are challenging, another approach is to look at a switching regulator. Often, the additional efficiency that can be possible with a switching design can alleviate thermal issues faced when using a linear regulator approach. There are many considerations in migrating from a linear to a switching design that are beyond the scope of this application report.

Continuing with linear regulators, if by using equation 7 we arrive at a θJA that indicates that we have no package options to meet the thermal dissipation, the addition of a heatsink is an alternative. While often a last resort, a heatsink adds thermal mass that improves the thermal conductivity of a regulator. This effectively lowers θJA of the system and enables the linear regulator to dissipate a higher PD(max). A helpful analogy is to think of our thermal system in terms of resistance as shown in Figure 6.

**Figure 6. Steady State Thermal Equivalent Model**

In this example, we are referring to:

θJA = theta JA (junction to ambient) − °C/W

θJC = theta JC (junction to case) − °C/W

θCS = theta CS (case to heatsink) − °C/W

θSA = theta SA (heatsink to ambient) − °C/W

**NOTE:** θCS is the thermal interface between the device case and the sink whether it is air, PCB/solder, or any other kind of heatsink.

Our simplified steady state heat transfer model is analogous to Ohm's law. Power dissipation is analogous to current, θ is analogous to electrical resistance, and ambient temperature is analogous to ground potential or our reference point. We have used θJA up to now as we were depending on the package for a complete thermal system from junction to ambient. Since a heatsink has been added, it is necessary to break the system down into more granular components.

Adding a heatsink achieves a system θ junction to ambient low enough to meet the system thermal requirements. A heatsink accomplishes this by offering a better thermal interface to air versus the package alone. Thus, we require the following to be met:

$$\theta_{\text{JA}(\text{max})} \ge \theta_{\text{JC}} + \theta_{\text{CS}} + \theta_{\text{SA}}$$
 (8)

Where θJA(max) is the max acceptable thermal rating that meets the system requirements. This equation can be manipulated to:

$$\theta_{SA} \le \theta_{JA(max)} - \theta_{JC} - \theta_{CS}$$
 (9)

If we refer back to equation 7, we can substitute (TJ – TA)/PD for θJA to obtain a θJA(max) and arrive at:

$$\theta_{SA} \leq [[(T_J - T_A)/P_{D(max)}] - \theta_{JC} - \theta_{CS}$$
(10)

Equation 10 gives the designer one equation of what are normally known variables and yields the maximum allowable value for a heatsink in an application.

The value of θCS depends upon the interface material and device mounting. In the case of a PowerPAD or a TO-263 package where the exposed pad is soldered directly to the bare printed-circuit board copper, θCS is essentially 0°C/W. For a TO-220 package, which is mounted to a heatsink with a bolt or clip, a thermal interface material is used to fill voids between the tab and heat sink. The interface thermal resistance depends upon the material used and is effected by the mounting pressure, material thickness, and flatness of each surface. Typical values of common interface material range between 0.1°C/W and 1°C/W and if no interface material is used could be as high as 5°C/W.

The user should consult the interface or heat sink vender to determine a suitable material to meet the desired design goals.

By solving equation 10, we arrive at the required thermal impedance of the heatsink. Some packages, such as the TO-220, TO-263, or DDPAK better lend themselves to using heatsinks. Packages such as the SC70 and SOT23 due to their physical size, are not generally considered for use with heatsinks. Appendix A has a short list of some thermal management vendors. The vendors listed do offer various solutions for different package types. TI does not endorse one vendor over another and there are many other thermal management vendors not listed.

Having read this far, the reader should have a basic understanding of the following:

- Why thermal considerations are important in linear regulator design
- Thermal equations for a linear regulator
- How to thermally evaluate different regulators for a design

The subsequent chapters of this applications report include a summary, real world examples, items to look out for, and appendixes including reference material, and additional useful information on linear regulators and TI PowerPAD packaging technology.

# **6 Summary of Approach and Equations**

This chapter is a one page summary engineers can use to quickly evaluate a linear regulator.

With VI, VO, and IO (max) in hand, calculate PD(max) with:

$$P_{D(max)} = P_I - P_O$$
 (3)
=  $(V_I - V_O) \times I_O$  (11)

**NOTE:** The IQ of the linear regulator is ignored due to its relative small size to IO. Thus, we assume lI = lO.

Then, take PD(max) and consult the data sheets of all perspective linear regulators. If the data sheet has power dissipation tables in watts, use PD(max) and compare the package with the rating associated with the appropriate ambient temperature, copper area, and airflow. If the data sheet only offers a θJA for the package, calculate θJA(max) using:

$$\theta_{\text{JA}(\text{max})} = (T_{\text{J}} - T_{\text{A}})/P_{\text{D}(\text{max})} \tag{7}$$

If PD(max) is less than the power noted in the power dissipation table or θJA in the data sheet is less than the θJA(max) calculated in equation 7, the package is thermally acceptable. Otherwise, the package is not acceptable and an alternative should be found. Also, always be sure to reference θJA or PD(max) with the appropriate copper area and airflow for the application when reading a data sheet.

In the case where the initial linear regulator is thermally insufficient, the easiest alternative is to look for a different package. [Figure 5](#page-7-0) is a reasonable reference to help start such a search. It is possible a linear regulator with more output current capability than required by the application may be necessary to obtain the appropriate thermal properties.

If no package can be found to meet the thermal needs for the application, the next step is to consider the addition of a heatsink or move to a switching power solution. When looking for a heatsink, use θJA calculated in equation 7 and substitute it into equation 9:

$$\theta_{SA} \le \theta_{JA(max)} - \theta_{JC} - \theta_{CS}$$
 (9)

This yields the θSA required for the heatsink. The other major considerations in choosing a heatsink are form factor and mounting options for the linear regulator package.

# **7 Things Often Overlooked**

Included in this chapter are answers to common questions and items that are often overlooked.

## **7.1 Differences Between Vendors**

In making a thermal comparison between linear regulator vendors, always check the data sheet. Different manufacturers are more or less aggressive in specifying θJA and the maximum recommended junction temperature for a given package type. In addition, different vendors make different assumptions on things such as airflow or copper area under a device. Lead frame options such as TI's PowerPAD can also drastically alter the thermal capabilities of a package.

Never assume similar parts have similar thermal capabilities, particularly when they come from different vendors, and always be aware of what assumptions or conditions the specifications assume.

## **7.2 The Math Does Not Work... But the Part Does**

It is not uncommon to find situations where the thermal equations indicate a potential problem but a part seems to work. Recall equation 7:

$$\theta_{\mathsf{JA}} = (\mathsf{T}_{\mathsf{J}} - \mathsf{T}_{\mathsf{A}})/\mathsf{P}_{\mathsf{D}} \tag{7}$$

does not take into account airflow or the potential benefits of heatsinking into the PCB copper. In addition, manufacturers build headroom into their specifications. The cumulative headroom this provides could allow a part to work outside what is covered in the data sheet and this document.

If additional factors such as heatsinking into the PCB copper cannot account for why a part works, it is not advised to continue to use it in a design. Violating the thermal ratings on a device can reduce the long-term reliability of the design.

The flip side to this is the situation where the original circuit was over-engineered for prototyping and exceeds what current the application requires. While the temptation is to leave the circuit as is, technically and financially it is often worth re-examining an over-engineered LDO. It can be possible to obtain advantages in both cost and space with a minimal amount of work to populate the function with a properly sized LDO.

### **7.3 Derating**

Often, in demanding applications, companies have a policy of derating the integrated circuits they use. Depending on the project or end equipment this can be done in a variety of ways. From a thermal perspective, one often derates the absolute maximum junction temperature (TJ) for specific system reliability considerations when derating is necessary. This, in turn, decreases θJA(max) in equation 6, which causes the application's thermal design to be more demanding and operation more robust.

It is up to the user to determine device suitability for a given application. It is important that the device operate within the manufacturers operating conditions stated in the data sheet. Device operation at or above the absolute maximum ratings, which includes temperature, voltage, and current causes premature device failure.

Several reliability prediction standards are used to assess product life such as MIL-HDBK-217F and Bellcore TR-NWT-000332. Mil-HDBK-217F defines two prediction methods; a part stress analysis and parts count reliability prediction.

Common stresses that are known to accelerate device failure mechanisms include temperature, voltage, current, humidity, and temperature cycling. Temperature accelerates many chemical or physical processes that may shorten the usable life of a semiconductor device.

The Arrhenius model is commonly used for semiconductor reliability prediction. The model assumes that device failure rate is linear with time and that the acceleration factor is a function of device junction temperature. The mean time between failure (MTBF) is defined as the inverse of the acceleration factor (f). Equation 12 shows the acceleration factor expressed as the ratio of a time to fail at one temperature to a time to fail at a different temperature.

Acceleration factor
$$f = \frac{t1}{t2} = \exp\left[\frac{Ea}{K}\left(\frac{1}{T1} - \frac{1}{T2}\right)\right]$$
 (12)

Where:

Ea = Activation energy (ev)

K = Boltzmans constant 8.6 x 10E-5 ev/°K

t1 = Time between failure at temperature T1

t2 = Time between failure at temperature T2

T1 = Junction temperature (°K) at time t1

T2 = Junction temperature (°K) at time t2 where T2 >T1

We can use this equation to illustrate the effect on the MTBF by derating the maximum allowable junction temperature of the device. For this exercise we assume an activation energy of 0.9 ev. The manufacturers maximum operating junction temperature is found in the absolute maximum ratings table in the data sheet. Many low dropout regulators are specified with an absolute maximum rating of 125°C. If we reduce the maximum allowable junction temperature by 10°C for a given design we see that the MTBF approximately doubles.

In many applications it is unnecessary to derate components. This discussion was provided as an example of one common way to derate components when necessary.

#### 8 Other Useful Items

Included in this chapter are quick references to a few useful items regarding linear regulators.

### 8.1 Linear Regulator Efficiency

Efficiency of any power regulator is:

$$Eff = P_O/P_I \times 100\% = (V_O \times I_O)/(V_I \times I_J) \times 100\%$$
 (13)

If we make the assumption as we did before that  $I_1 = I_0$  for a linear regulator discounting  $I_0$  due to its relative size compared with  $I_0$ , this can be simplified to:

$$Eff = V_O/V_I \times 100\% \tag{14}$$

This is a good rule of thumb, but remember, this only holds for a linear regulator design. Switching power supplies cannot be analyzed in this way.

There are applications that need to take into account the  $I_Q$  of the linear regulator. To consider  $I_Q$ ,  $I_O$  no longer equals  $I_I$  and thus equation 14 is invalid. To consider  $I_Q$ , we examine equation 5:

$$P_{I} = P_{O} + P_{D} + P_{Q} \tag{5}$$

Since quiescent power dissipation, PQ, is also derived from the input voltage, equation 13 can be manipulated to:

$$Eff = (V_O \times I_O)/[(V_I \times I_I) + (V_I \times I_Q)] \times 100\%$$
(15)

Assuming IQ comes from the same source, VI, as does II. An example where this is not the case is the UC382 as it has a bias supply input, VB, which draws IQ. The UC382 aside and assuming both II and IQ come from the same source, we return to our potentiometer module from Chapter 3, and we conclude that:

$$Eff = (V_O \times I_O)/[V_I \times (I_O + I_Q)] \times 100\%$$
 (16)

Again, remember these equations only apply to a linear regulator design. One example of an application where this granularity could be important is in portable end equipments where the load is *asleep* for the majority of the time. With a very small load current for a significant amount of time, IQ can become a significant factor in efficiency and product run time. This is why companies such as TI have low IQ families of linear regulators. For comparison, the TPS761xx family of LDO's has a typical quiescent current of 2.6 mA where the TPS769xx family has a typical quiescent current of 0.017 mA. Both are 100-mA LDOs, but the TPS769xx was designed for power sensitive applications as are other TI LDOs which offer even lower IQ than the TPS769xx.

With regard to IQ, we must also keep in mind what the relationship is between IQ and output current. PMOS linear regulators are generally load independent.

**Figure 7. Comparison of 100-A lQ PMOS and PNP LDOs**

As illustrated in Figure 7, the PMOS linear regulators IQ is essentially constant as a function of load current. In contrast, bipolar linear regulators have IQ characteristics that are load dependent. This can be important to take into account before deciding that IQ is negligible. Particularly for bipolar linear regulators, it is good practice to consult the graphs in the data sheet if they are provided.

# **8.2 Input Voltage, Dropout Voltage (VDO), and Low Dropout Regulators (LDO's)**

Dropout voltage for linear regulators is often misunderstood. As discussed previously, the difference between VI and VO is the voltage drop across the linear regulator. The lower the difference between the input and output voltage, the lower the power dissipation for a given load current. The dropout voltage is defined as the minimum difference required between VI and VO for the regulator to operate within specification. A subset of linear regulators called *low dropout regulators* (or *LDO*) exhibits small dropout specifications. This can be an advantage when:

- VI and VO are close in value
- VI can be manipulated to be close to VO thus reducing PD and increasing efficiency
- A battery is the VI source, thus allowing the regulator to draw voltage from the battery and regulate over a wider range

Figure 8 demonstrates what a dropout voltage specification means visually.

**Figure 8. Dropout Voltage Example**

To highlight the difference between a standard linear regulator and what is considered an LDO, look at the VDO specification on both the TPS77601 and the LM317M. TI considers anything with a VDO < 1 V to be an LDO and anything with VDO > 1 V to be a *standard* linear regulator. In summary, the minimum input voltage as shown in Figure 8 is the greater value of either VO + VDO or the minimum specified input voltage.

The ultimate combination is an LDO that has both a low dropout and an input voltage range that extends to relatively low voltages. An example of this is the TPS721xx (150 mA), TPS722xx (50 mA), and TPS725xx (1 A) series. This series is the first LDO in the industry to allow VI down to 1.8 V and a very small VDO which allows these parts to run directly off batteries in portable applications or off other core voltages for point-of-use needs. As a side note, this family of LDOs also features stability with any output capacitor providing even more flexibility in designs.

# **9 Real World Examples**

Included in this chapter are four real world examples to further illustrate the thermal concepts presented in this application report.

### **Example 1:**

We need to power a C5409 DSP core with a small amount of additional logic at 1.8 V. The application calls for a 100 mA solution at 1.8 V and this rail needs to be created from 5 V. The maximum ambient temperature is 70°C, and we assume zero airflow. The TPS76318 and REG101-A linear regulators are under consideration. Which device(s) and package options are acceptable?

#### Answer:

As a side note, if we take a quick look at efficiency with equation 14:

Eff =
$$V_O/V_I \times 100\%$$

Eff = 1.8 V/5 V × 100% = ~36%

Obviously, a linear regulator is not the optimal solution for efficiency in this case but we assume efficiency is not a primary design goal in this application.

Both the TPS76318 and REG101-A have an acceptable input voltage range, output voltage range, and output current capability. The potential pitfall in this application are the thermal considerations.

Ignoring the IQ of the linear regulator, at 100 mA output current we calculate the input and output power:

```
Output Power: P = I × V = 100 mA × 1.8 V = 180 mW
Input Power: P = I ×V = 100 mA × 5 V = 500 mW
PD = PI – PO
PD(max) = 500 mW – 180 mW = 320 mW
```

With the TPS76318 data sheet, we cross reference PD(max) with our ambient temperature in the thermal tables.

| Package | BOARD | $R_{	heta JC}$ | $\textbf{R}_{\theta \textbf{J} \textbf{A}}$ | DERATING FACTOR<br>ABOVE TA = 25°C | $T_A \le 25^\circ C$ POWER RATING | TA = 70°C<br>POWER RATING | TA = 85°C<br>POWER RATING |
|---------|-------|----------------|---------------------------------------------|------------------------------------|-----------------------------------|---------------------------|---------------------------|
| Low K½  | DBV   | 65.8 °C/W      | 259 °C/W                                    | 3.9 mW/°C                          | 386 mW                            | 212 mW                    | 154 mW                    |
| High K± | DBV   | 65.8 °C/W      | 180 °C/W                                    | 5.6 mW/°C                          | 555 mW                            | 305 mW                    | 222 mW                    |

| Parameter                          | MIN | NOM MAX | UNIT |
|------------------------------------|-----|---------|------|
| Input voltage, VI                  | 2.7 | 10      | V    |
| Continuous output current, IO      | 0   | 150     | mA   |
| Operating junction temperature, TJ | -40 | 125     | °C   |

**Figure 9. Power Dissipation Table From the TPS76318 Data Sheet (May 01)**

We see that 320 mW at 70°C is a problem and that the SOT23 package is not suitable for this application. The REG101-A data sheet addresses thermal considerations in terms of θJA. Using equation 7, TA, and PD(max) we can evaluate the REG101-A:

$$\theta_{JA} = (T_J - T_A)/P_D$$

 $\theta_{JA} = (125^{\circ}C - 70^{\circ}C)/0.320 \text{ W} = ~171^{\circ}C/W$

In looking at the θJA ratings shown in Figure 10 for the REG101−A we see that the SOT23 package option is still unacceptable. However the SO-8 package option is suitable having a θJA less than 171°C/W.

| TEMPERATURE RANGE                           | TJ                     | -40                                        | +85  | °C  |  |      |
|---------------------------------------------|------------------------|--------------------------------------------|------|-----|--|------|
| Specified Range                             |                        |                                            |      |     |  | °C   |
| Operating Range                             | TJ                     | -55                                        | +125 | °C  |  |      |
| Storage Range                               | TA                     | -65                                        | +150 | °C  |  |      |
| Thermal Resistance                          | $\theta_{\mathrm{JA}}$ | Junction-to-Ambient                        |      | 200 |  | °C/W |
| SOT23-5 Surface Mount<br>SO-8 Surface Mount | $\theta_{\mathrm{JA}}$ | Junction-to-Ambient<br>Junction-to-Ambient |      | 150 |  | °C/W |

**Figure 10. From the REG101 Data Sheet (July 01)**

In this example, we see quickly how thermal considerations can impact component selection with linear regulators.

To take this example a step further:

- *What would happen if the output current increased to 150 mA?*
  - − PD(max) increases to 580 mW, θJA decreases to 95°C/W, and Eff is the same. Neither part is an option as neither has an acceptable package. 150 mA is beyond the REG101-A specification for output current also. A more appropriate part may be the 250 mA REG102-A in a SOT223 package with a θJA close to 60°C/W among other choices from TI.
- *What would happen if VI were lowered to 3.3 V with 100-mA output current?*
  - − PD(max) becomes 190 mW, θJA becomes to 289°C/W, and Eff is ~54%. Now, both of our original parts would work in the smaller SOT23 package option.

These basic changes produce drastic differences to our thermal considerations.

#### **Example 2:**

The TPS76833 linear regulator is available in an 8-pin SO and a 20-pin TSSOP package. Determine which package option will meet the following criteria:

```html
$$V_I$$
 = 5.0 V + 5\%
 $V_O$  = 3.3 V \pm2\%
 $I_O$ : 0.95 A
 $T_A$  = 50^\circ C, natural convection air flow
```

#### Answer:

First, determine the required worst case power dissipation.

$$P_{D(max)} = (V_I - V_O) \times I_O$$
= [(V<sub>I</sub> x 1.05) - (V<sub>O</sub> x 0.98)] x I<sub>O</sub>
= (5.25 - 3.234) x 0.95
= 1.915 W

Now determine the maximum package thermal impedance requirement given the above criteria.

$$P_{D(max)} = (T_{J(max)} - T_A)/\theta_{JA}$$
 Rearranging and solving for  $\theta_{JA}$   $\theta_{JA} \le (T_{J(max)} - T_A)/P_{D(max)}$

From the TPS76815 data sheet we see that the absolute maximum junction temperature is 125°C. In this application, your company mandates that all components have derated TJ(max). For this example we derate by 10°C.

Let
$$T_{J(max)} = 115^{\circ}C$$

Therefore the required  $\theta_{JA} \le (115 - 50)^{\circ}C/1.915 W = 33.9^{\circ}C/W$

From the data sheet we see that the 8-pin SOIC package (D) does not meet the requirement since it has a θJA of 172°C/W. The 20-pin TSSOP PowerPAD package (PWP) meets the requirement having a θJA of 32.6°C/W if it is mounted on a board having a copper heat sink area of at least four square inches (1 oz. copper).

#### **Example 3:**

The REG104 linear regulator is available in a SOT223 and TO-263 surface mount packaging. Determine which package option meets the following criteria:

$$V_I = 5.0 \text{ V} + 5\%$$

$$V_O = 2.5 \text{ V} \pm 2\%$$

$$I_O: 1.0 \text{ A}$$

$$T_A = 50^{\circ}\text{C}, \text{ natural convection air flow}$$

## Answer:

First, determine the required worst case power dissipation:

$$P_{D(max)} = (V_I - V_O) \times I_O$$

=  $[(V_I \times 1.05) - (V_O \times 0.98)] \times I_O$
=  $(5.25 - 2.45) \times 1 = 2.8 \text{ W}$

Now determine the maximum package thermal impedance requirement given the above criteria.

$$P_{D(max)} = (T_{J(max)} - T_A)/\theta_{JA}$$
 Rearrange and solving for  $\theta_{JA}$   $\theta_{JA} \le (T_{J(max)} - T_A)/P_{D(max)}$

From the REG104 data sheet we see that the absolute maximum junction temperature is 150°C. Thus,

Let
$$T_{J(max)} = 150^{\circ}C$$

Therefore the required  $\theta_{JA} \le (150 - 50)^{\circ}C/2.8 \text{ W} = 35.7^{\circ}C/W$

From Figure 10 of the REG104 data sheet we see that a TO-263 mounted on 1.5 square inches of 1 oz. copper has a θJA of 32°C/W. Since the mounting tab is at ground potential, the entire ground plane can be used to further reduce the thermal impedance.

### **Example 4:**

Given that a TMS320C6201 DSP has the following system requirements:

Core: 1.8 V ±3% at 1.0 W I/O: 3.3 V ±5% at 0.2 W VI = 5.0 V ±5% TA = 50°C

Find a suitable power solution using a dual LDO regulator to power the DSP system.

We must first determine the total power dissipation required for the dual regulator.

$$\begin{split} P_{D(core)} &= (V_I - V_{core})) \; x \; I_{(core)} \\ &= (V_I(1.05) - V_{core}(0.97)) \; P_{core}/V_{core}(0.97) \\ &= (5.25 - 1.75) \; (1.0)/1.75 = 2.0 \; W \\ P_{D(I/O)} &= (V_I - V_{O(I/O)}) \; x \; I_{(I/O)} \\ &= (V_I(1.05) - V_{I/O}(0.95)) \; P_{I/O}/V_{I/O}(0.95) \\ &= (5.25 - 3.14) \; (0.2)/3.14 = 0.134 \; W \end{split}$$
 Total regulator dissipation =  $P_{D(core)} + P_{D(I/O)} = 2.0 \; W + 0.124 \; W = 2.124 \; W$

Next, determine the required maximum package thermal impedance.

Maximum allowable dissipation:

$$P_{D(max)} = (T_{J(max)} - T_A)/\theta_{JA}$$

$$\theta_{JA} \le (T_{J(max)} - T_A)/P_{D(max)}$$

Most of the TI LDO data sheets list an absolute maximum junction temperature rating of 125°C. Thus,

Let
$$T_{J(max)} = 125$$
°C
Therefore  $\theta_{JA} \le (125 - 50)/2.124 = 35.3$ °C

The DSP power selection matrix table (page 35) of the *Power Management Selection Guide*, literature number SLVT145 recommends the TPS767D318 as a possible product to meet the system requirements. From the TPS767D318 data sheet we find that it meets the voltage and tolerance requirements as well as thermal. It features a θJA of 32.6°C/W if at least four square inches of 1 oz. copper heat sink area is used. Since the thermal pad is at ground potential, the entire ground plane could be used to further reduce the thermal impedance.

## References

- 1. S. M. Sze, VLSI Technology, McGraw-Hill, New York, 1988.
- 2. AN1029 Fairchild, April, 1996 Maximum Power Enhancement Techniques for SO-8 Power MOSFETs
- 3. AN-569, Motorola, 1973 Transient Thermal Resistance -- General Data and Its Use

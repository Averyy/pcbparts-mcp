---
source: "TI SLVAE37 -- How to Select a Surge Diode"
url: "https://www.ti.com/lit/pdf/slvae37"
format: "PDF 9pp"
method: "claude-extract"
extracted: 2026-02-16
chars: 20856
---

# How to Select a Surge Diode

## Abstract

For systems in harsh industrial environments, one of the most important parts of system protection is the input TVS diode selection. The input TVS diode is designed to protect fragile system inputs from large transient spikes that are caused by nearby machinery, lightning strikes, or power surges. These surges are modeled and regulated by IEC 61000-4-5, which standardizes the protection requirements systems must meet in order to ensure that they will not see failures when exposed to these transients. However, passing these standards is not trivial, especially to a designer who is unfamiliar with protection diodes and the specifications. This document will provide an introduction to TVS diodes, comparing them to other transient protection solutions, discussing some of the key specifications and then providing a system example.

## 1 Types of Transient Suppression Components

While there are many components, both passive and active, that are capable of protecting a surge at a system input, the most common is to use transient voltage suppression (TVS) to dissipate fault energy, shunting the surge current while clamping the surge voltage to a safe level. In addition to TVS diodes, this current shunting can be implemented through use of metal oxide varistors (MOVs), gas discharge tubes (GDTs), spark gaps, and even RC filters, however each has drawbacks as shown in the table below. While TVS diodes are not a perfect solution, they are generally the most efficient option for surge currents between 2A-250A. GDTs, MOVs, and Thyristors are generally preferred for higher levels of surge dissipation, while filters are good for lower magnitudes of surge dissipation.

| Type | Description | Advantages | Disadvantages |
|------|-------------|------------|---------------|
| Gas Discharge Tube | Gas between two plates that is ionized to carry current during a large voltage spike | Highest power dissipation density and very low capacitance | Long turn on time, light sensitive behavior, large footprint, and poor voltage regulation |
| Metal Oxide Varistor (MOV) | Mass of metal grains that creates a diode-like breakdown | High power dissipation density | Poor voltage regulation, finite life expectancy, catastrophic breakdown mechanism, and poor thermal dissipation |
| Thyristor | Diode-like behavior but with a snapback profile to limit power dissipation | High power dissipation density due to snapback behavior | Chance of latch-up breakdown |
| TVS Diode | Avalanche breakdown diode behavior to shunt current to ground | Decent power dissipation density, long lifetime, and good voltage regulation | Not economical at high (>250A) current dissipation |
| Filter | Passive components to filter out high frequency transients | Cheapest solution | Very low power dissipation density |

Fundamentally, the purpose of a TVS diode at the input of a system is to have no impact during nominal operation, and then during a transient overvoltage to immediately conduct and shunt current to ground, keeping the system voltage exposure to a safe, low level. In reality, TVS diodes will always have non-ideal characteristics that need to be considered to ensure robust protection and minimal system impact. These non-idealities are similar to ESD diodes, however as surge diodes are more critical to system reliability they warrant additional focus during selection.

## 2 TVS Diode Specifications

When reading a TVS diode data sheet, there are a few critical specifications that can be confusing to an inexperienced designer. Table 2 and Figure 2 highlight these key parameters and the remainder of this section discusses in more depth why they matter to a protection design.

| Parameter | Definition |
|-----------|------------|
| V_RWM | The applied voltage where TVS leakage is specified to be very low, generally in the single digit nano-amps. |
| V_BR | The applied voltage where the TVS will see 1 mA leakage and begin shunting current. |
| I_PP | The maximum current for a defined waveform that the TVS diode can sustain before failure. |
| V_CLAMP | The voltage that the TVS diode will regulate to when exposed to a transient current. |
| R_DYN | The resistance in a TVS diode that will cause V_CLAMP to rise when exposed to a transient current. |
| Polarity | Whether the TVS can sustain a +/- V_RWM or only a positive V_RWM without having leakage current. |
| I_LEAK | The leakage current when voltage is applied, typically specced at V_RWM. |
| Capacitance | The parasitic capacitance in the TVS diode that can impact system operation. |

### 2.1 V_RWM

The reverse working maximum voltage (V_RWM) is defined as the voltage that can be applied to a TVS diode with an assurance that the diode will not, over process or temperature, conduct significant current. The definition of 'significant current' depends on the TVS manufacturer, but generally it is < 100 nA. The V_RWM specification enables a designer to select a device that will see minimal leakage across all operating conditions.

In a design, V_RWM should be selected to ensure that it is above the expected maximum operating voltage. If the applied voltage rises above V_RWM, there is a chance to see diode leakage increase significantly. For example, if the protected line operates at 5 V nominal with a maximum variance up to 7 V, ensure that the V_RWM is 7 V or greater.

### 2.2 V_BR

The breakdown voltage (V_BR) is the voltage where a TVS diode begins to conduct current, defined typically at 1 mA leakage. V_BR defines the inflection point on the diode curve where the leakage begins to increase exponentially, which is typically referred as the diode 'turning on'. In contrast to V_RWM, V_BR is a DC value and can shift significantly over process and temperature so it will be defined with a minimum and maximum value.

A common mistake is thinking that since V_BR is where the diode begins to conduct significantly, nominal system voltages below V_BR will assure low leakage. This is not the case, as V_BR can shift and has a relatively high defined leakage at 1 mA. Ensure that nominal voltage stays below V_RWM, rather than V_BR, to assure very low system leakage.

V_BR will always be higher than V_RWM, so when a diode has a properly placed V_RWM, V_BR will not cause significant leakage. During a surge event V_BR is the voltage at which the diode will begin to clamp, so a lower V_BR would imply lower clamping and better protection when comparing two TVS's with the same R_DYN (a specification which will be discussed in an upcoming section).

### 2.3 I_PP

The peak pulse current (I_PP), is defined as the maximum surge current that can be shunted before the diode itself will overheat and fail. Recall that a surge event can be defined in terms of a maximum current -- I_PP is a critical value as it determines whether a given diode can absorb that maximum current without seeing any damage. Ensure that I_PP of a TVS diode is larger than your peak surge current so no TVS failures will occur. Note that TVS diodes fail due to excess current rather than excess voltage, so when selecting a TVS diode I_PP, the surge current magnitude determines the requirement. Make sure when selecting a TVS diode to take into account the derating over temperature of I_PP as many TVS diodes derate significantly (up to 80% of their nominal value) when raised to 105°C or 125°C. All TVS diode data sheets should include a graph showing peak power dissipation against temperature, which can be used to calculate I_PP.

The I_PP that a TVS diode can sustain is dependent on the length of a pulse and so will always be defined relative to a waveform. In TVS data sheets, the specification is almost always defined relative to a 1 ms pulse length (the 10/1000 us waveform as defined in IEC 61643-123), however some data sheets also provide a specification referenced to the IEC 61000-4-5 8/20 us waveform. The shorter the reference waveform pulse is, the higher the I_PP is so it's important to make sure that the I_PP value references to the same waveform as your test condition. If a data sheet does not define I_PP relative to your specific waveform, there is usually a data sheet curve that shows peak pulse power (calculated as I_PP x V_CLAMP) by pulse length, which allows you to roughly determine I_PP for a given pulse length; however, this is not an exact method. The recommended best practice is to use a diode where I_PP is referenced to your exact waveform.

### 2.4 V_CLAMP and R_DYN

Dynamic resistance (R_DYN) and clamping voltage (V_CLAMP) are discussed together because R_DYN is the diode intrinsic property, but V_CLAMP is the important specification in a system. All diodes have some internal resistance, defined as R_DYN. When current flows through a diode, the voltage measured over the leads is defined as V_CLAMP, which can be calculated as V_CLAMP = V_BR + I_SURGE x R_DYN.

V_CLAMP determines the voltage that the system will be exposed to during a surge -- the lower the V_CLAMP, the less chance that the protected system will see failures due to electrical overstress (EOS). In a system, if V_CLAMP violates the absolute maximum voltage of your input circuitry system, failures can occur even if the TVS diode is shunting current. Efficient protection design means selecting a TVS diode with a V_CLAMP that is low enough that it doesn't require high voltage tolerant components, which are often more expensive and have worse performance. Because V_CLAMP is largely determined by R_DYN, this often means selecting a diode with a lower R_DYN.

V_CLAMP will always be specified in a TVS diode data sheet relative to an I_SURGE and a reference waveform, similar to I_PP. Be careful to match the data sheet test conditions to your own, as V_CLAMP will vary significantly based on the conditions. R_DYN is sometimes, but not always, specified in TVS data sheets. If it is not specified, R_DYN can be roughly calculated from a given V_CLAMP by using the formula R_DYN = (V_CLAMP - V_BR) / I_SURGE. Once you have calculated R_DYN, you can calculate V_CLAMP for any test current, provided it is in reference to the same waveform. If R_DYN or V_CLAMP is needed in reference to a different waveform, there is no way to easily calculate these values. In that case, the best practice is to find a diode that specifies those quantities to your given waveform.

Conventional TVS diodes generally have very poor clamping performance. For precise clamping performance, TI's Flat-Clamp surge diodes have very low R_DYN leading to a low clamping voltage.

### 2.5 Polarity

TVS diodes come in both unidirectional and bidirectional configuration. This difference shows when looking at the I/V curves of the devices.

Unidirectional: Used in applications where the voltage is always positive. Provides more robust protection from negative surge pulses.

Bidirectional: Used in applications where the voltage can be positive or negative. Provides more flexibility for input voltages.

As the I/V curves show, unidirectional TVS diodes have a negative breakdown voltage just below 0 V, while bidirectional TVS diodes have a symmetrical breakdown voltage between the positive and the negative directions. This means that if a signal is nominally always positive, a unidirectional TVS diode can be used, but if a signal can nominally go negative, it is required to use a bidirectional TVS diode. The tradeoff is that the negative V_CLAMP of the unidirectional TVS diode will be much better than the V_CLAMP of the bidirectional TVS diode, due to the lower V_BR. Take note of your systems working range to select the proper diode polarity.

### 2.6 I_LEAK and Capacitance

TVS diodes, like all analog components, have a leakage current (I_LEAK) and parasitic capacitance. The ideal diode would have no impact to the system below V_RWM, however leakage and capacitances for actual TVS diodes can be surprisingly high and impact systems if they are not considered. Particularly for lower voltage TVS diodes, leakages can rise to close to 1 mA and capacitances are often above 1000 pF. For some systems this is not significant, but for others it can be critical. For example, on battery powered systems an always-on 1 mA leakage can be a large power drain, while for protection on precise inputs, the high capacitance can lower system SNR. Ensure that these parasitic elements are considered and acceptable when designing a protection stage.

An understanding of these specifications enables a designer to quickly select the proper TVS diode for a system that can assure both reliable operation and minimal system impact.

## 3 Example: Selecting a TVS for a PLC 4/20 mA Input

Let's look at an example by picking a TVS for a PLC 4/20 mA analog output. Per IEC 60601, PLC inputs require protection against a +/-1 kV IEC 61000-4-5 8/20 us surge coupled indirectly through a 40 ohm external coupling resistance. This means that the surge current that must be protected against is 1000 V / (40 ohm + 2 ohm) = 23.9 A of surge current. The system can be expected to be exposed to 85°C temperatures, and has a 60 V input tolerance on the protected IC.

Let's go through the specifications outlined above and select a TVS diode that will reliably protect this type of input.

### 3.1 V_RWM

Commonly, 4/20 mA input terminals have a nominal voltage of 24 V, with a maximum DC voltage tolerance of 33 V. Any TVS diode selected must have a V_RWM of 33 V or greater to enable this operation. There are many options for TVS diodes that meet this requirement. Let's look at a few common options with a 33 V V_RWM: the SMAJ33A, the SMBJ33A, and the TI TVS3300.

### 3.2 V_BR

Once V_RWM is selected, V_BR will always be a few volts above V_RWM. All of the TVS diodes mentioned above have a similar V_BR at roughly 36 V to 38 V.

### 3.3 V_CLAMP and R_DYN

Determining this step requires knowledge about the input circuitry absolute maximum voltage tolerance. If we are using input circuitry that is rated for 60 V, we must make sure that the V_CLAMP is < 60 V to reliably protect this input. However, many TVS diodes will not specify R_DYN and V_CLAMP numbers for the 8/20 us waveform. In this case, assumptions or testing will have to be done. This is not an ideal way to design systems; to simplify designs TI will always specify the values for the 8/20 us waveform. Whether the SMAJ33A or SMBJ33A data sheets include these numbers depends on the vendor, however they can always be estimated by testing or extrapolation.

The SMAJ33A has a R_DYN of 884 mohm, so a nominal V_CLAMP = 38.6 V + (24 A x 0.884 ohm) = 59.8 V. This is the nominal clamping and is very close to the clamping voltage requirement, however we want to ensure that there will be no issues when surges are applied over temperature. The data sheet does not specify clamping or breakdown voltage over temperature; however it does provide a temperature coefficient that we can use to calculate. The temperature coefficient is 10 x 10^-4 /°C, so we can calculate V_CLAMP at 85°C = V_CLAMP at 25°C x (1 + 10 x 10^-4/°C x (T_J - T_A)) = 59.8 V x (1 + 10 x 10^-4/°C x (85°C - 25°C)) = 63.4 V. This clamping voltage violates the 60 V absolute maximum of the input circuitry.

In this case, it's best to find a TVS device that has a lower R_DYN which leads to a lower V_CLAMP. The SMBJ33A, which has an R_DYN of 0.504 ohm, gives a nominal V_CLAMP of 51.1 V and a maximum V_CLAMP of 54.2 V, which can meet the requirements.

If input circuitry is needed with even lower voltage tolerances (40 V or lower), TI's Flat-Clamp devices have an ultra-low R_DYN that enables much tighter voltage regulation. The TVS3300, for example, has a maximum R_DYN of 60 mohm, which leads to a maximum clamping voltage of 39 V. This is 15 V lower than the SMBJ33A diode, which can enable much improved system flexibility. The Flat-Clamp devices also have much better temperature regulation over temperature, such that in situations where temperature variations cause SMA or SMB type TVS diodes to fail, the Flat-Clamp devices will still retain performance.

### 3.4 I_PP

The next step is to ensure that the TVS diode can withstand the expected test surge. In this case the surge current, I_PP, is 24 A, so the diode must be able to withstand the 24 A current pulse at high temperature.

The SMAJ33A data sheet lists nominally that it can withstand 400 W of 10/1000 us transients, which we can translate to 2300 W of 8/20 us power by using the data sheet curves. The power derating over temperature will vary by manufacturer, but at 85°C it is common for devices to derate to around 50% of rated power according to the data sheet curves. This means that the device can safely absorb 2300 W x 50% = 1150 W. The required power dissipation is I_PP x V_CLAMP = 24 A x 63.4 V = 1543 W. This violates the requirement, so the SMAJ33A is not a good choice for this system.

Doing the same analysis for an SMBJ33A gives 4000 W of 8/20 us power, derating to 2000 W at temperature, with a requirement of I_PP x V_CLAMP = 24 A x 54.2 V = 1299 W. This is a safer option that will protect with some margin.

The third option would be to use TI's TVS3300. The TVS3300 data sheet assures survival for this test case, and even specifies 4000 strikes of 30 A surge at 125°C so there is no risk of failure and no calculations are needed, but they are included for completeness sake. The data sheet specifies surge current over temperature in the curves, so you can see that the device can absorb 32 A of surge current at 85°C, surviving the 24 A test with 50% margin. Calculating energy, you can see that due to the low R_DYN of the device, it requires less power dissipation for the same pulse, as I_PP x V_CLAMP = 24 A x 39 V = 936 W. This is 60% of the required power as in the SMAJ33A diode and helps to improve reliability by forcing less current through the system.

### 3.5 Polarity

Next is to decide whether a unidirectional or bidirectional diode is required. This is dependent on the system -- nominally, the signal is expected to be above zero always, so if there are no other requirements a unidirectional TVS diode can be used. However, if the system needs to be protected against miswiring, a bidirectional TVS must be used. Most TVS families include both unidirectional and bidirectional options.

### 3.6 I_LEAK and Capacitance

The leakage and capacitance budget will depend on the system as well. In this case, the SMAJ33A, SMBJ33A, and TVS3300 have similar capacitances at 100 pF to 200 pF. However, the SMAJ33A and SMBJ33A have 25°C leakage at 1 uA, while the TVS3300 has a much lower leakage with <30 nA at 25°C. If a low leakage solution is needed, the TVS3300 offers a much better solution. Any of the device's capacitance would be acceptable for this system as there is no high speed signal, but be aware that some TVS diodes have extremely high capacitance so this step must be checked. The same applies for leakage, where low voltage TVS diodes often have higher than 1 mA leakage which can be damaging to a system power budget.

### 3.7 Final TVS Selection

Through the analysis above, we have learned that for this test case the SMAJ33A is not a good fit to reliably protect the input. If there is a 60 V tolerant input, the SMBJ33A or the TVS3300 would both be able to protect, however if the input is tolerant to a lower voltage the TVS3300 is a better option. However, for the most reliable protection, the TVS3300 offers the lowest clamping voltage and the lowest power dissipation, while still having the lowest leakage current and the smallest package. For precise and reliable protection, the TVS3300 is the best choice.

## 4 Conclusion

Ensuring a robust product is one of the most critical, and difficult, tasks that a designer will go through. The most important part of that protection is assuring protection against transient surges that can destroy equipment and cause failures, leading to higher return rates and upset customers. While surge protection can seem mystifying, surges can be effectively protected against if care is given to understanding TVS specifications.

An up-front assessment of the risks of exposure to high powered transients, taking into account the magnitude of the energy, the distance and coupling method, allows a designer to predict what surges a system might see. It is critical to understand how a TVS diode functions, what the specifications mean and how it will impact your system. By taking the time to walk through those steps, designers can ensure a robust product that will survive a lifetime of operation, regardless of the harsh environment.

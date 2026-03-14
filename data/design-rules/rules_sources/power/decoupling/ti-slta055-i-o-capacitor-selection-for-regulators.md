---
source: "TI SLTA055 -- I/O Capacitor Selection for Regulators"
url: "https://www.ti.com/lit/an/slta055/slta055.pdf"
format: "PDF 11pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 23516
---
# Input and Output Capacitor Selection

Jason Arrigo, PMP Plug-In Power

## Abstract

When designing with switching regulators, application requirements determine how much input and output capacitance is needed. There are a number of key concerns which affect your selection. The electrical performance requirements of your design play a big part in determining the amount of capacitance required. The transient requirements of your system are very important. The load transient amplitude, voltage deviation requirements, and capacitor impedance each affects capacitor selection. Other important issues to consider are minimizing PCB area and capacitor cost.

When selecting input and output capacitance each design has specific requirements which must be addressed. System requirements set hard limits for a design. Depending on what you are trying to accomplish, the amount and type of capacitance can vary.

## 1. Input Capacitor Selection

### 1.1 Reduce Input Ripple Voltage

The first objective in selecting input capacitors is to reduce the ripple voltage amplitude seen at the input of the module. This reduces the rms ripple current to a level which can be handled by bulk capacitors.

Ceramic capacitors placed right at the input of the regulator reduce ripple voltage amplitude. Only ceramics have the extremely low ESR that is needed to reduce the ripple voltage amplitude. These capacitors must be placed close to the regulator input pins to be effective. Even a few nanohenries of stray inductance in the capacitor current path raises the impedance at the switching frequency to levels that negate their effectiveness.

Large bulk capacitors do not reduce ripple voltage. The ESR of aluminum electrolytics and most tantalums are too high to allow for effective ripple reduction. Large input ripple voltage can cause large amounts of ripple current to flow in the bulk capacitors, causing excessive power dissipation in the ESR parasitic.

To reduce the rms current in the bulk capacitors the ripple voltage amplitude must be reduced using ceramic capacitors. As a general rule of thumb, keeping the peak to peak ripple amplitude below 75 mV keeps the rms currents in the bulk capacitors within acceptable limits.

### 1.2 Selecting Input Ceramic Capacitors

Load current, duty cycle, and switching frequency are several factors which determine the magnitude of the input ripple voltage.

The input ripple voltage amplitude is directly proportional to the output load current. The maximum input ripple amplitude occurs at maximum output load. Also, the amplitude of the voltage ripple varies with the duty cycle of the converter. For a single phase buck regulator, the duty cycle is approximately the ratio of output to input dc voltage. A single phase buck regulator reaches its maximum ripple at 50% duty cycle. Figure 1 shows the ac rms, dc, and total rms input current vs duty cycle for a single phase buck regulator. The solid curve shows the ac rms ripple amplitude. It reaches a maximum at 50% duty cycle. The chart shows how this magnitude falls off on either side of 50%. The straight solid line shows the average value or dc component as a function of duty cycle. The curved dashed line shows the total rms current, both dc and ac, of the rectangular pulse as duty cycle varies.

NOTE: Multiphase regulators have multiple humps in the ac rms curve depending on the number of phases.

Figure 1. Input Pulse Current vs Duty Cycle

### 1.3 Calculating Ceramic Capacitance

Use Equation 1 to determine the amount of ceramic capacitance required to reduce the ripple voltage amplitude to acceptable levels:

$$C_{MIN} = \frac{I_{OUT} \times dc \times (1 - dc) \times 1000}{f_{SW} \times V_{P(max)}} \qquad dc = \frac{V_{OUT}}{V_{IN} \times \eta}$$

where:

- f_SW is the switching frequency in kHz
- I_OUT is the steady state output load current
- C_MIN is the minimum required ceramic input capacitance in uF (some of C_MIN is supplied by the module)
- V_P(max) is the maximum allowed peak-peak ripple voltage
- dc is the duty cycle (as defined above)

Notes: (1) The actual capacitance of a ceramic is less than the stated nominal value at a given dc voltage. Make sure the actual value is equal to or greater than the calculated value. (2) 75 mVpp is recommended V_P(max). This will yield approximately 22 mVrms of ripple voltage.

#### Example Ceramic Calculation

Given:
- V_IN = 12 V
- V_OUT = 3.3 V
- I_OUT = 10 A
- eta = 90%
- f_SW = 333 kHz
- dc = 0.3

The minimum ceramic capacitance required to reduce the ripple voltage to 75 mVpp is calculated to be:

$$C_{MIN} = \frac{10 \times 0.3 \times (1 - 0.3) \times 1000}{333 \times 75 \text{ mV}} = 84 \,\mu\text{F}$$

The plots of ripple voltage in Figure 2 show that the ripple amplitude has been reduced by approximately a factor of four once the calculated ceramic capacitors were added. The 75 mVpp ripple voltage amplitude goal has been achieved.

Figure 2. Input Ripple Voltage Plots

Re-arranging the equation to verify the scope plots:

$$V_{P(max)} = \frac{I_{OUT} \times dc \times (1 - dc) \times 1000}{f_{SW} \times C_{MIN}}$$

Note: when calculating using C_MIN, use effective capacitance value at operating voltage. 18 uF is used as an effective internal capacitance.

$$V_{P(max1)} = \frac{10 \times 0.3 \times 0.7 \times 1000}{333 \times 18} = 350 \text{ mVpp}$$

$$V_{P(max2)} = \frac{10 \times 0.3 \times 0.7 \times 1000}{333 \times 84} = 75 \text{ mVpp}$$

Converting Vpp to Vrms: (Vrms = 1/(2 x sqrt(3)) x Vpp)

350 mVpp ~ 101 mVrms; 75 mVpp ~ 22 mVrms

Ohm's law can be used to determine rms ripple current through a 35 mOhm ESR input bulk capacitor:

101 mV / 35 mOhm = 2.9 A; 22 mV / 35 mOhm = 628 mA

The above calculations show that by reducing the ripple voltage amplitude the rms ripple current in the bulk input capacitor will be reduced substantially. The rms ripple current has been reduced from 2.9 A to 628 mA, and is now within the ripple current rating of most electrolytic bulk capacitors. This reduction of rms ripple current greatly reduces the power dissipation and increases the life of the bulk input capacitors. The power dissipation equation below shows how a reduction in the ripple voltage amplitude by a factor of 4.67 to 1 leads to a 21 to 1 reduction in power dissipation.

Bulk capacitor power dissipation: P = I^2 x R

(2.9 A)^2 x 35 mOhm = 294 mW; (0.628 A)^2 x 35 mOhm = 13.8 mW

### 1.4 Input Inductor

If reflected ripple is a concern, use a small (560 nH or less) input inductor. This is the single most effective way to confine ripple currents to the local input bypass caps. An input inductor can reduce the reflected ripple current by an order of magnitude. A single input inductor can be shared by multiple modules.

At lower currents, this input inductor can take the form of a power ferrite bead. In a multiple module system, the use of a filter inductor at each module will help contain the noise generated by each module and keep it localized. It is one of the best ways to deal with beat frequencies caused by multiple modules operating at slightly different frequencies. Ensure the inductor current is below its saturation current rating.

During transient conditions, the use of an input inductor puts larger demands on input bulk capacitors. Take care when using input inductors as they will affect input capacitor selection.

### 1.5 Transients and Bulk Capacitors

When output current transients are involved the key point to keep in mind is that the electrons have to come from the input of the regulator. Bulk capacitors control the voltage deviation at the input when the converter is responding to an output load transient. The higher the capacitance, the lower the deviation. Therefore, the size of the input bulk capacitor is determined by the size of the output current transient and the allowable input voltage deviation.

The amplitude of the input voltage deviation during a transient is directly proportional to the load current change. If the magnitude of the transient load current is doubled, the input voltage disturbance is doubled also.

Lower input voltage means higher input currents. The input current scales directly by duty cycle. At lower input voltages the input transient currents will also be higher. To comply with output voltage deviation limits, more input capacitance is required.

Consider a 2.5 V output regulator with a 10 A transient load. With a 12 V input, the ideal duty cycle is 2.5 / 12 = 0.208. The 10 A load transient on the output transforms to a 2.08 A transient on the input. With a 3.3 V input regulator, the duty cycle is now 2.5 / 3.3 = 0.758. The 10 A load transient is now a 7.58 A input transient. This will cause a larger voltage deviation on the lower voltage supply where the voltage limits are probably tighter.

During a transient, input inductance slows the current slew rate seen by the host supply. The use of a filter inductor places more demands on the input bulk capacitors since more of the initial current demand must come from the input capacitors rather than the host supply. The input voltage at the regulator input now sees a much higher voltage deviation. In the end, both the input and output capacitors have to be recharged, causing higher peak currents to be demanded from the host supply.

### 1.6 Example Bulk Capacitor Calculation

When designing a system consisting of a single POL module, or multiple POL modules that make use of a shared bulk input capacitor bank, the first step is to calculate the magnitude of the input transient current. This is done by calculating the reflected input transient for each POL module's output transient.

After calculating the individual input transients for each module, add them up to get the total transient current. When calculating, you must determine the worst case transient combination of all modules and proceed accordingly.

The magnitude of the input current transient is calculated from:

$$\Delta I_{IN} = \frac{V_{OUT}}{V_{IN} \times \eta} \times \Delta I_{OUT}$$

where:
- eta is efficiency
- delta_I_OUT is the output transient current
- delta_I_IN is the input transient current
- V_OUT is the nominal output voltage
- V_IN is the nominal input voltage

The efficiency value eta is obtained from the regulator data sheet. Use a value from the efficiency curve for the particular output voltage and the highest expected output current.

Figure 3 shows an example diagram of multiple POL modules sharing a single bank of bulk input capacitors. The output voltage, output current and output load transient specifications are given. The input transient current is calculated for each POL. Adding the individual input transients, the total calculated input transient current is 2.774 A.

Figure 3. Multiple POL Modules Example

The next step is to decide if a series filter inductor is going to be used. If using an inductor, pick a value no greater than 560 nH. If not using one, use a value of 50 nH in the calculation to account for stray inductance in the host supply path and its finite bandwidth.

Next, determine the maximum allowable voltage deviation on the bulk capacitors. This is the maximum allowable dip during the peak transient step that was calculated in step one. The smaller the voltage deviation, the higher the required amount of bulk capacitance.

The following equation calculates the minimum required bulk capacitance:

$$C = \frac{1.21 \times I_{tr}^2 \times L}{\Delta V^2}$$

Note that this equation is an approximation. The value it produces should be considered to be an absolute minimum amount. The exact value will have to be determined through experimentation depending on how well regulated your host supply is.

#### 1.6.1 Calculation

- Assume filter L = 560 nH
- Assume allowable delta_V is 100 mV
- Transient current (Itr) was calculated to be 2.774 A

$$C = \frac{1.21 \times (2.774)^2 \times 560 \times 10^{-9}}{(0.100)^2} = 521 \,\mu\text{F}$$

According to the calculation we need 521 uF of bulk capacitance at a minimum. We would use the nearest standard value of 560 uF.

Use low ESR capacitors to implement the bulk network. Capacitors with high ESR induce voltage drops of their own due to the current flowing in them.

Care must be taken when using very low ESR capacitors together with an input inductor as it may cause instability. Always use an oscilloscope to monitor the input voltage to the POLs during transient testing to insure that you have a stable system.

## 2. Output Capacitor Selection

### 2.1 Output Capacitors Affect Feedback

The output capacitance of a switching regulator is a vital part of the overall feedback system. The energy storage inductor and the output capacitor form a second-order low-pass filter.

As the output voltage is sensed across both the filter and load impedance, they both affect the feedback control loop. Adding external capacitance shifts the corner frequency of this filter. The external component parameters, including capacitor impedance, are part of the feedback control loop.

The impedance of the output capacitance affects the damping of the output filter and has a major affect on the transient response of the supply.

In general, low-ESR capacitors are good choices. They provide excellent energy storage and improve the transient performance. However, if the overall impedance of the output capacitor network is too low, the dynamic response of the regulator can be adversely affected.

To understand how output capacitor impedance affects the stability of the feedback loop, it helps to understand the impedance characteristics of various capacitor types.

Figure 4. Capacitor Impedance Characteristics

Figure 4 shows the impedance characteristics for three common capacitor types: electrolytic, polymer tantalum, and multi-layer ceramic. Each capacitor type is characterized by its impedance and the frequency range over which it is most effective. The frequency at which the impedance reaches its minimum is determined by its ESR and ESL. It is known as the self resonant frequency of the capacitor.

The self resonant frequency is considered to be the maximum usable frequency for a capacitor. Above this frequency the impedance of the capacitor begins to rise as the ESL of the capacitor begins to dominate. Note that each capacitor type has a specific frequency band over which it is most effective. Therefore, a capacitor network of multiple capacitor types is more effective in reducing impedance than just one type.

For the PTH family of switching regulators the output capacitor impedance limits can be easily defined. For optimum performance, the overall impedance of the external output capacitor network must meet the following criteria:

- Must be greater than 4 mOhm for frequencies below 20 kHz.
- Must be greater than 2 mOhm for frequencies between 20 kHz and 200 kHz.
- Above 200 kHz the impedance can fall below 2 mOhm.

Figure 5. Impedance Limits

If the output capacitor network's impedance falls below the limit, the transient response will exhibit insufficient damping and may become unstable.

External output capacitors are required to achieve fast response to load transients. This is necessary to compensate for the both the parasitic resistance and inductance of the PCB traces. The capacitors internal to the module will have no effect at the remote load terminals at frequencies above 1 MHz. The parasitic resistance and inductance of the PCB traces decouple the regulator from its load. To insure good high frequency regulation at the point of load, local decoupling capacitors must be used.

There is no limit on the number of low-value (< 1 uF) ceramic capacitors that can be used. Low-value ceramic capacitors are only effective at frequencies above 1 MHz, well beyond the bandwidth of the feedback loop. As a result, they have only a minor impact on the regulator's feedback control loop. They do, however, provide tremendous benefit when dealing with very fast load transients. For this reason these capacitors should be placed right at the ICs that are generating the transients.

The resonant frequency of ceramic capacitors increases by a factor of 3.16 for every decade decrease in capacitance value. A 1 uF ceramic capacitor might have a usable frequency of 5 MHz, and a value of 0.1 uF might work up to 15 MHz. To handle frequencies above 100 MHz, bypass capacitors with values defined in pico-Farads must be used.

### 2.2 Importance of Output Capacitors

The current slew rate of a regulator is limited by its output filter inductor. When the amount of current required by the load changes, the initial current deficit must be supplied by the output capacitors until the regulator can meet the load demand.

Figure 6 shows a simplified buck regulator circuit as an example. When a load transient occurs, the regulator feedback control loop senses the change in output voltage and begins to change the power transistor duty to compensate. Even if the duty cycle is able to instantly rise to 100%, the rate in which the output current can change is limited by the value of the regulator's output filter inductor.

The equation that governs this is: di/dt = delta_V / L.

Figure 6. Regulator Slew Rate Example Circuit

In the example circuit, Vin is 5 V and Vout is 2 V. At 100% duty there is 3 V across the 1 uH inductor. The equation shows that the maximum rate of current change is 3 A/us. This is the fastest rate at which the regulator output current can be increased. Until the regulator can increase the load current to the new value, the deficit must come from the output capacitors.

Capacitors all have some parasitic series resistance (ESR). Any current flowing in the capacitor must also flow through the ESR. This causes a voltage drop due to the I x ESR product. Each mOhm of resistance will cause 1 mV of voltage drop for every 1 A of output transient current.

For a very fast load transient of magnitude delta_I, the best case peak voltage deviation (delta_V) will be delta_I times the combined ESR of the output capacitors. The regulator has no influence over it. For slower transients, the regulator feedback loop will help reduce the peak voltage deviation.

### 2.3 Designing for Transient Performance

When designing for a load transient, the output bulk capacitors and high frequency bypass capacitors determine the response performance and voltage deviation of the regulator. The most important parameters are the magnitude of the load transient (delta_I) and the distributed bus impedance to the load. The selection of the output capacitors is determined by the allowable peak voltage deviation (delta_V). This limit should reflect the actual requirements, and should not be specified lower than needed.

The distribution bus impedance seen by the load is the parameter that determines the peak voltage deviation during a fast transient. The system requires a low impedance bus over all frequencies with adequate bypass capacitors to achieve fast slew rates. If the impedance of the network that supplies the load remains below a maximum impedance, the voltage deviation due to the transient will remain within allowable voltage deviation requirements. It is simply Ohm's Law: delta_V = delta_I x Z. Keep the magnitude of Z below the maximum limit, and the transient voltage deviation will stay within its limits.

Divide delta_V by the delta_I to determine the maximum allowable impedance, Zmax. This is the impedance limit which must be maintained by the output capacitor network for frequencies above which the regulator is effective.

To maintain low impedance from the regulator to the load, high frequency, low value ceramic capacitors must be placed very close to the load to minimize the effects of trace inductance while larger value ceramic capacitors can be placed closer to the regulator.

Figure 7. High Frequency Impedance Plot

### 2.4 Transient Design Example

Calculate the maximum allowable output impedance, given the following requirements:

- VO = 2.5 V
- Output current step from 0.8 A to 12.5 A (delta_I = 11.7 A)
- Maximum allowable voltage deviation (delta_V) is 100 mV
- 20 A/us slew rate.

delta_V / delta_I = Maximum impedance = 100 mV / 11.7 A = 8.55 mOhm

Selecting four 330 uF capacitors with an ESR of 25 mOhm would provide an effective ESR of 6.25 mOhm and 1320 uF of total capacitance. Using these capacitors, the actual amplitude of the transient deviation would be about +/-73 mV (11.7 A x 6.25 mOhm).

By maintaining the low impedance over the complete frequency range, any high slew rate transient will be achieved.

### 2.5 Absolute Maximum Capacitor Limits

All regulators have an absolute maximum capacitance limit.

Many modules incorporate output short-circuit protection. During startup, the regulator must charge the output capacitance in order to raise the output voltage to its set-point. This limits how much capacitance can be added.

Startup behavior is triggered by:
- the application of power
- the removal of a ground signal from the Inhibit pin
- the regulator's recovery from an over-current condition.

Any of these instances result in the regulator's output voltage rising rapidly from zero up to its set-point. When the output voltage rises, current flows to the capacitance according to the equation: I = C dV/dt, where dV/dt is the slew rate of the output voltage.

The output voltage slew rate during the regulator's startup is approximately 1 V/msec for most PTH products. This causes 1 A of current to flow to the output capacitance per 1000 uF of capacitance value. This current is in addition to any load current that may be drawn by the application circuit.

If there is too much output capacitance, the current demanded from the regulator trips its over-current protection circuit. Furthermore, each over-current trip will be followed by further attempts by the regulator to restart. This can result in the regulator entering a perpetual cycle of over-current shut down.

### 2.6 In the Data Sheet

Data sheet tables give the maximum allowable output capacitance for each module. If external capacitance is required for stable operation, the minimum value will be listed in the datasheet. Recommended capacitance is also listed in the datasheet for improved transient performance. The recommended capacitance value will meet a typical delta_V spec at a 50% transient load step.

If the required delta_V is less than the recommended typical delta_V spec, or the transient load step is greater than 50%, more output capacitance must be added. In each case the maximum ESR required to meet your transient goal must be calculated.

### 2.7 Conclusion

In any power system, input and output capacitance is key to optimum performance. Good engineering practice requires that additional external capacitance be placed at the input and output of all regulators. A well designed power supply decoupling network will employ different types of capacitors. System design requirements will determine the amount and type of capacitors for any design.

Detailed analysis has been performed to allow capacitor limits to be accurately defined. By following the capacitor recommendations in the data sheet and selecting capacitors based on your actual operating conditions, a reliable, low-cost power system can be designed.

---
source: "ADI -- How Voltage Supervisors Address Power Supply Noise and Glitches"
url: "https://www.analog.com/en/resources/analog-dialogue/articles/voltage-supervisors-address-power-supply-noise-and-glitches.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 12166
---
### Abstract

Using voltage supervisors adds reliability to microcontroller-based systems by monitoring the power supply failures and putting the microcontroller in reset mode to prevent system error and malfunction. However, power supply imperfections such as noise, voltage glitches, and transients can lead to false and
nuisance resets that can affect the system behavior. This article shows how voltage supervisors address factors that can trigger false and nuisance resets to improve the system’s performance and reliability

### Introduction

Applications that compute and process data requiring field programmable gate arrays (FPGAs), microprocessors, digital signal processors, and microcontrollers depend on safe and reliable operations. These devices tax power supply requirements as they are only allowed to operate at a certain range of power supply tolerance.1 Voltage supervisors are known solutions to achieve system reliability. They can act immediately to put the system in reset mode when an unexpected failure from the power supply arises, such as undervoltage or overvoltage. However, monitoring voltages in power supply rails always comes with some nuisances that can trigger unwanted false reset outputs. These are power supply noises, voltage transients, and glitches that can come from the power supply circuit itself.

This article discusses the different parameters in a voltage supervisor that address unwanted power supply noises, voltage transients, and glitches. It also discusses how these parameters improve the dependability of voltage supervisors when monitoring power supplies to increase the reliability of the system in the application.

### Power Supply Noise, Voltage Transients, and Glitches in a System

Power supplies have inherent imperfections. There are always noise artifacts coupled on the DC that can come from the power supply circuit component itself, noise from other power supplies, and other noise generated from the system. These problems can be worse if the DC power supply is a switch-mode power supply (SMPS). SMPS produces switching ripple that is coherently related to the switching frequency. They also produce high frequency switching transients that occur during switching transitions. These transitions are caused by the fast on and off switching of the power MOSFETs. Figure 1 shows an application circuit in which the [MAX705](/en/products/max705.html) supervisor is used to monitor any failure in the output of the switching regulator, which is the voltage supply of the microcontroller.

Figure 1. The MAX705 supervisor is used to monitor a switching regulator output, which is the input voltage supply of a microcontroller.

Aside from the steady-state operation noise artifacts, there are also scenarios in the power supply where voltage transients are more pronounced. During startup, a voltage output overshoot is usually observed related to the feedback-loop response of the power supply and is followed by voltage ringing for some time until it reaches stability. This ringing can be worse if the feedback loop compensation values are not optimized. Voltage overshoot and undershoot can also be observed during transient or dynamic loading. In the applications, there are times when the load needs more current to execute complex processes, which leads to a voltage undershoot. On the other hand, reducing the load instantly or at a fast ramp rate will give a voltage overshoot. There are also short-duration voltage glitches that can occur to the power supply due to external factors. Figure 2 shows an illustration of the different voltage transients and glitches that can be present on a power supply voltage in different scenarios.

Figure 2. Voltage transients and glitches that can be observed on a supply voltage in different scenarios.

There are voltage transients that can occur in a system that are not associated with the power supply voltage but rather on a user interface such as a mechanical switch or a conductive card for some applications. Turning a switch on and off produces voltage transients and noise on the input pin, typically a manual reset pin. All of these factors—power supply noise, voltage transients, and glitches, if excessive—can unintentionally hit the undervoltage or overvoltage threshold of a supervisor and trigger false resets if not accounted for in the design. This can lead to oscillatory behavior and instability, which is undesirable with regards to system reliability.

How do voltage supervisors address noise and transients prevent the system from nuisance resets? There are parameters that help mask these transients that are associated with the power supply or monitored voltage. These are the reset timeout period, reset threshold hysteresis, and the reset threshold overdrive vs. duration. Meanwhile, for the transients that are associated with the mechanical contact in the circuit such as a push button switch in the manual reset pin, the manual reset setup period, and the debounce time mask the transients. These parameters make the voltage supervisors robust and unaffected by transients and glitches, thus keeping the system from undesirable responses.

### Reset Timeout Period (tRP)

During startup or when the supply voltage is rising up from an undervoltage event and exceeds the threshold, there is an additional time on the reset signal before it deasserts, which is called the reset timeout period (tRP).2 As an example, Figure 3 shows that after the monitored voltage, which in this case is the supply voltage labeled as VCC, reaches the threshold from an undervoltage or startup, an added delay is present for an active LOW reset before it deasserts HIGH. This additional time gives room for the monitored voltage to stabilize first, masking the overshoot and ringing before enabling the system or taking it out of reset mode. The reset timeout period suppresses false system resets to prevent oscillation and potential malfunction, thus helping improve the reliability of the system.

Figure 3. The reset timeout period (tRP) helps keep the system in reset mode while the supply voltage stabilizes.

### Threshold Hysteresis (VTH+)

There are two main benefits of having threshold hysteresis. First, it provides certainty that your monitored voltage has overcome the threshold level with enough margin before deasserting a reset. Second, it gives room for the power supply to stabilize first before deasserting a reset. There is a tendency for the reset output to produce multiple transitions when processing signals with superimposed noise, as the power supply bounces and recrosses the threshold region. This is shown in Figure 4.3 In applications such as industrial environments, noisy signals and voltage fluctuations can occur anytime. Without hysteresis, the reset output will continuously toggle assert and deassert until the power supply stabilizes. It will also put the system into oscillation. Threshold hysteresis cures the oscillation by putting the system hold on reset to prevent the system from unwanted behavior shown in the blue-shaded area in Figure 4. This helps the supervisor in protecting the system from false resets.

Figure 4. RESET output response without and with threshold hysteresis (reset timeout period not shown to focus on the effect of hysteresis).

### Reset Threshold Overdrive vs. Duration

Voltage glitches from external factors can occur in any system for either short or long periods. They can also have different magnitudes of voltage dip. Reset threshold overdrive vs. transient duration has something to do with the magnitude and duration of the voltage glitch or overdrive. A short-duration glitch with a greater magnitude will not trigger a reset signal to assert, while a less-magnitude overdrive with a longer duration will trigger a reset as shown in Figure 5.

Figure 5. A glitch with a less magnitude but occurs in a longer duration will trigger a reset signal as opposed to a short-duration glitch with greater magnitude.

Voltage transients in the monitored supply are ignored depending on their duration. Disregarding these transients will protect your system from nuisance resets such as those caused by short-duration glitches. These glitches can falsely trigger system resets, to undesirable behavior of the system. In the product data sheet, the reset threshold overdrive vs. duration is often illustrated in one of the typical performance characteristics plots such as in Figure 6. Any values above the curve will trigger a reset output while values within the curve will be ignored to prevent the system from false resets.

Figure 6. Asserting of the reset signal will depend on the magnitude of the overdrive and its duration.

### Manual Reset Setup Period (tMR) and Debounce Time (tDB)

The reset timeout period, threshold overdrive vs. duration, and the threshold hysteresis address voltage glitches and transients associated with the monitored voltage, which is usually the power supply of the system microcontroller. For the glitches brought by the mechanical contacts such as switches, the manual reset setup period and the debounce time alleviate the possible effects of the voltage transients and glitches.

The manual reset setup period (tMR) is the time required for the manual reset to hold and complete before it triggers a reset output. Some supervisors are made to have a long manual reset setup period to add protection to the system. These are common on consumer products that you need to hold on to the button for several seconds to reset your system. This method avoids accidental and unintended reset, thus adding protection and reliability. With the manual reset setup period, all the short-duration transients and glitches when pushing on the switch are ignored, as shown in Figure 7a, thus helping the system to be glitch immune.

The same concept applies to the debounce time. Like the setup period, debounce time (tDB) ignores the high frequency periodic voltage transients when pushing on or off a switch. These high frequency transients are considered invalid and do not trigger a reset as shown in Figure 7b. When the signal exceeds the debounce time, that is the time it will be considered a valid input signal from a switch or a push button.

Figure 7. The manual reset setup period and debounce time diagram of a supervisor with a long manual reset setup period ([MAX6444](/en/products/max6444.html)): (a) the manual reset setup period (tMR) needs to be completed first before a reset signal asserts; (b) to be considered as a valid input signal, debounce time (tDB) is required to be completed.

### Conclusion

Without voltage supervisors, systems are at risk of brownout conditions and malfunction during voltage transients and glitches. Voltage supervisors solve this by putting processors into reset mode during such scenarios. All the parameters discussed above including reset timeout period, threshold hysteresis, threshold overdrive, manual reset setup period, and debounce time improve the reliability of voltage supervisors in monitoring power supply voltages by making them immune to glitches and transients. This gives stability and reliability to overall system performance.

## References

1 “[The Why, What, How, and When of Using Microprocessor Supervisors.](/media/en/training-seminars/tutorials/why-what-how-when-of-using-microprocessor-supervisors.pdf)” Maxim Integrated, April 2018.

2 Greg Sutterlin. “[Supervisors in Multivoltage Systems.](/en/resources/technical-articles/supervisors-in-multivoltage-systems.html)” Analog Devices, Inc., November 2003.

3 Pinkesh Sachdev. “[Adding Hysteresis for Smooth Undervoltage and Overvoltage Lockout.](/en/resources/analog-dialogue/articles/adding-hysteresis-for-smooth-undervoltage-and-overvoltage-lockout.html)” Analog Dialogue, Vol. 55, No. 1, March 2021.

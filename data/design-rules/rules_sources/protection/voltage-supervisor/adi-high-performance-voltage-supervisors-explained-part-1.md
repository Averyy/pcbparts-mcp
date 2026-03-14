---
source: "ADI -- High Performance Voltage Supervisors Explained, Part 1"
url: "https://www.analog.com/en/resources/analog-dialogue/articles/high-perf-volt-supervisors-explained-part-1.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 17361
---
### Abstract

This article explains the value of high performance voltage supervisors. It discusses their basic definition, theory of operation, specifications, topology, and polarity. Certain high performance voltage supervisors are designed to help microprocessor-based systems improve reliability by preventing system errors during brownout conditions. Examples are provided.

### Introduction

Applications that require heavy computing and data processing such as embedded systems require devices like microcontrollers, microprocessors, and field programmable gate arrays (FPGAs) to perform complex calculation routines due to their versatility, speed, and flexibility. However, these recommended devices also come with limitations and different power supply requirements that, if not considered during the early stage of system development, may affect the performance and reliability of the system. One of these limitations is a potential system
malfunction during brownout conditions. When the power supply falls below the minimum operating voltage, its microcontroller may malfunction and cause system errors. Thankfully, voltage supervisors are designed to mitigate this problem.

This article discusses high performance voltage supervisors, including some in the Analog Devices product family. Their functions are explained along with input and output fundamentals, and other basics of high performance supervisor products.

### What Is a Voltage Supervisor and How Does it Work?

A voltage supervisor is a device that is used to monitor a voltage supply rail and provides an output that can be utilized to execute an action whenever the monitoring condition is satisfied. It detects whenever the monitored voltage supply rail drops below or exceeds a predefined level of voltage called threshold.1 The output signal it provides, usually called a reset, is used to put another device in another mode of operation such as in reset mode or active mode. It is also desirable for applications wherein operating outside a specific voltage range will lead to errors and malfunction. Occasionally, the reset output is also used to enable and disable another device, like in any application that requires a certain input
voltage range for proper operation. One good example of this application is using them to enable regulators for proper operation, which is shown in Figure 1a. LDO regulators need enough energy in the input or a high enough level of input voltage to ensure proper operation during startup.2

Voltage supervisors are well-known partners of microcontrollers or MCUs. MCUs risk entering an area of malfunction and experiencing system errors whenever the supply voltage drops below its minimum operating range while a command execution is ongoing. In this case, the supply voltage of the MCU is the monitored voltage, and the minimum operating voltage of the MCU should be the threshold voltage. We will discuss how the threshold level is defined further in the article. A simple illustration of a voltage supervisor used in monitoring the power supply of
a microcontroller is the [ADM809](/en/products/adm809.html) shown in Figure 1b. The monitored voltage level is sensed and fed into the VCC pin of the supervisor. Once the monitored voltage goes below the threshold, an active low reset output will put the microprocessor into reset mode until the voltage supply goes back to the proper level.3

Figure 1. The ADM809, an example of a simple voltage supervisor monitoring the input voltage (a) to enable an LDO regulator when the proper input voltage level is met and (b) to put the
microprocessor system into reset mode during brownout conditions.

### What Are the Important Input Specifications of a Voltage Supervisor?

There are four important input specifications that need to be understood regarding voltage supervisors. This will help system designers in implementing voltage supervisors to improve the reliability of the system in applications. These specifications are the reset threshold, threshold accuracy, reset threshold hysteresis, and the power-on reset.

#### Reset Threshold

The reset threshold is the voltage level; when the monitored voltage falls below this value, then it will assert a reset. In voltage supervisor products, the reset threshold is often labeled VTH. When the monitored voltage VCC falls below the reset threshold voltage VTH, a low reset output is asserted, as shown in the timing diagram
in Figure 2. In applications, the threshold voltage is set to the minimum voltage that will allow the system to operate properly.

Figure 2. A timing diagram of a monitored voltage VCC and reset output signal of a voltage supervisor.

One way to set the reset threshold is through an external resistor divider. A fraction of the monitored voltage is compared to a reference to know if the monitored
voltage is above or below the reset threshold, as shown in Figure 3a. The [ADM8612](/en/products/adm8612.html) is an example of this configuration. Some voltage supervisors’ reset thresholds are set through an internal resistor divider by laser trimming at the factory, such as the [MAX16140](/en/products/max16140.html). This gives advantages such as fewer external components, which provides extra space for the solution and is desirable for more compact applications, as in Figure 3b. It also enables higher accuracy as it is not dependent on external factors such as using a standard value resistor with tolerance. However, the
external resistor option gives flexibility when adjusting the reset threshold level.

Figure 3. Ways to set the reset threshold: (a) the ADM8612 reset threshold is set through an external resistor divider, and (b) the MAX16140 reset threshold is set through a factory-trimmed internal resistor divider.

#### Threshold Accuracy

Threshold accuracy is how close the actual threshold is compared to the computed or target reset threshold. Some factors affect the accuracy of the threshold—the resistor divider and the reference voltage. The resistor divider and the reference voltage are both analog circuits and are affected by environmental factors such as temperature. This leads to the tolerance of the reset threshold. The more robust the reference voltage and the resistors become, the tighter the tolerance gets, and the higher the threshold accuracy. The threshold accuracy is normally expressed in percentage. If you have a voltage supervisor with ±1% threshold accuracy, and the threshold is set at 3.3 V, then the actual threshold could be around 3.267 V to 3.333 V.

It is important to understand the threshold accuracy as this is critical when setting the value of the reset threshold. Setting the value of the reset threshold and not considering the accuracy could put your system into an undesirable region of system malfunction.

#### Reset Threshold Hysteresis

The reset threshold hysteresis is the additional voltage required to overcome the monitored voltage to deassert a reset signal. In a voltage supervisor that is monitoring undervoltage, the reset threshold hysteresis is commonly expressed as VHYST or VTH+HYS. Hysteresis has several benefits. First, it makes sure that the monitored voltage comes back to the correct level and overcomes the threshold with some margin. Second, it helps address power supply noise and instability as it gives room for the power supply to stabilize first before deasserting a reset. Without hysteresis, a voltage supervisor repeatedly asserts or deasserts the reset signal as the monitored voltage crosses the threshold.4,5 This could happen in applications where there is power supply noise or in battery-operated systems where the voltage drops with load current due to internal resistance. An example of this is
shown in the purple-shaded area in Figure 4. Meanwhile, with hysteresis, the reset output will keep the system in reset mode until the power supply comes to stability, therefore getting rid of the unstable and oscillatory behavior of the system, as seen in the blue-shaded area of Figure 4.4

Figure 4. A reset output behavior comparison with and without hysteresis.

#### Power-On Reset

During startup when the supply voltage starts to ramp up, the internal circuitry of the voltage supervisor has no sufficient bias. Therefore, the reset output is in an undefined state. As the supply voltage continues to ramp up, there will come a voltage supply level that will take the voltage supervisor out of the undefined state and give a valid reset signal. The minimum supply voltage that will put the supervisor in a defined state and give a valid reset output is called the power-on reset voltage or VPOR. Consider the voltage supervisor simplified schematic in Figure 3b. Given an open-drain reset output pulled up to VCC, at an undefined state, the reset output will reflect the supply voltage VCC. This creates a glitch in the reset output called the power-on glitch.6 When the supply voltage hits VPOR, that is the time that the supervisor will give a valid reset output as shown in Figure 5.

Figure 5. The power-on glitch during startup and the power-on reset voltage VPOR.

In some applications, the power-on glitch is neglected and does not matter such as in high voltage systems. But for some applications, such as in devices with low threshold of logic high voltage, this is undesirable.7

### What Are the Output Specifications of a Voltage Supervisor that I Need to Consider?

One thing to consider in designing a voltage supervisor is the reset output polarity and timing. You can choose the polarity depending on the application, whether an active low or active high output.

#### Active Low

An active low output means that the reset output asserts low whenever the monitored supply goes below the threshold voltage. The timing diagram in Figure 2 shows the response of a voltage supervisor with an active low output. For easy identification, active low reset output is labeled as RESET (read as RESET bar). The RESET output remains asserted for a specified time before it deasserts high when the monitored supply rises above the threshold voltage. This time delay is called the reset timeout period (tRP), which can be either a fixed timing or adjustable through an external capacitor.

#### Active High

Depending on the output requirements of a system, an active high output may be needed. In contrast to the active low output, in the active high output, the reset output
asserts high when the monitored supply goes below the threshold and deasserts low when the monitored supply rises above the threshold voltage after a reset timeout period, tRP. See the illustration in Figure 6.

Figure 6. A timing diagram of VCC and reset of an active high reset output.

Another thing to consider depending on the application is the output topology. Two output topologies are predominantly used—the open-drain and the push-pull topology.

#### Push-Pull Output Topology

The push-pull output topology consists of a pair of complementary MOSFETs shown in Figure 7. The reset output goes high when the bottom FET turns off and the top FET turns on, and goes low when the bottom FET turns on and the top FET turns off. The push-pull output offers high speed, almost rail-to-rail response from low to high, high to low.

Figure 7. A push-pull output topology.

An active low push-pull reset output is appropriate for most applications, but other output types are available. Push-pull outputs in single-voltage systems are straightforward, as shown in Figure 8, but those in multivoltage systems require more care, especially when the microcontroller has only one reset input.8

Figure 8. A single-voltage system.

#### Open-Drain Output Topology

For an open-drain topology, the reset output of the supervisory circuit is the drain of an internal MOSFET. An external pull-up resistor connected from reset to a supply voltage is needed to create a logic signal output like what is shown in Figure 3b. The reset goes low when the MOSFET turns on and goes high when the MOSFET turns off. The pull-up resistor can be connected to a voltage rail other than the supply of the supervisory circuit. This makes it advantageous for a system that requires a different level of reset rather than the supply of the supervisor.8

Another advantage of an open-drain output is the wired-OR capability. Connect the open-drain outputs of two or more supervisory circuits on the same bus to implement a negative logic OR circuit.9 Meaning, the bus is low when the reset output of any one supervisory circuit goes low. The bus is high only when all the reset outputs are high. This is convenient when one wants to monitor multiple voltage supplies and trigger a reset when any one supply drops.

#### Application Use Case Examples

Figures 9, 10, and 11 show some typical application use cases for different output topologies and polarities of a voltage supervisor. Figure 9 shows an example of multiple-voltage systems where an open-drain topology is useful. Active low outputs can be utilized in a daisy-chain connection to perform sequencing in a multivoltage rail system, as shown in figures 10a and 10b. There are some applications where proper power supply sequencing can be one of the most important considerations. Multirail systems like FPGA-based solutions usually require and
specify proper power sequencing to prevent system malfunctions and erratic conditions. Figures 11a and 11b show examples where active high outputs are utilized in applications. For these cases, active high outputs are used to enable or disable a high-side MOSFET for an on/off control scheme. This type of configuration can be used for circuits like overvoltage protection, low voltage sequencing, etc. High-side MOSFETs can also be driven using active low output of a voltage supervisor. Detailed information is discussed in the article “[Driving a High-Side MOSFET Input Switch Using Active Low Output for System Power Cycling.](/en/resources/analog-dialogue/articles/driving-a-high-side-mosfet.html)”

Figure 9. Multivoltage systems for a single microprocessor reset input.

Figure 10. Multirail sequencing using active-low output (a) push-pull topology and (b) open-drain topology.

Figure 11. Applications of active-high output polarity. (a) Low voltage sequencing with an N-channel MOSFET using push-pull topology. (b) Overvoltage protection circuit with P-channel
MOSFET using open-drain topology.

### Conclusion

Voltage supervisors are devices used to enable, disable, or reset another device. The most common application of supervisors is resetting microcontrollers. Supervisors protect the system from errors and malfunction, giving value to the overall reliability of the application. There are input, output, and timing specifications in a voltage supervisor that need consideration when designing. Depending on the applications, the different output topologies and polarities of supervisors give some benefits that can be utilized in achieving the intended function while
increasing the reliability of the system.

## References

1 “[The Why, What, How, and When of Using Microprocessor Supervisors.](/media/en/training-seminars/tutorials/why-what-how-when-of-using-microprocessor-supervisors.pdf)” Analog Devices, Inc., April 2018.

2 “[The ABCs of Glitch-Free Voltage Supervisors.](/en/resources/technical-articles/the-abcs-of-glitchfree-voltage-supervisors.html)” Analog Devices, Inc., November 2021.

3 "[Microprocessor Supervisory Circuits in 3-Lead SC70 and SOT-23.](/media/en/technical-documentation/data-sheets/ADM803_809_810.pdf)” Analog Devices, Inc., October 2014.

4 Noel Tenorio. “[How Voltage Supervisors Address Power Supply Noise and Glitches.](/en/resources/analog-dialogue/articles/voltage-supervisors-address-power-supply-noise-and-glitches.html)” Analog Dialogue, Vol. 57, No. 4, November 2023.

5 Pinkesh Sachdev. “[Adding Hysteresis for Smooth Undervoltage and Overvoltage Lockout.](/en/resources/analog-dialogue/articles/adding-hysteresis-for-smooth-undervoltage-and-overvoltage-lockout.html)” Analog Dialogue, Vol. 55, No. 1, Mar 2021.

6 “[How Glitch-Free Supervisors Aid in High-Reliability Applications.](/en/resources/technical-articles/how-glitchfree-supervisors-aid-in-highreliability-applications.html)” Analog Devices, Inc., September 2021.

7 Niño Angelo Pesigan, Ron Rogelio Peralta, and Noel Tenorio. “[Driving a High-Side MOSFET Input Switch Using Active Low Output for System Power Cycling.](/en/resources/analog-dialogue/articles/driving-a-high-side-mosfet.html)” Analog Dialogue, Vol. 58, No. 1, February 2024.

8 “[Choosing Supervisor Outputs.](/en/resources/technical-articles/choosing-supervisor-outputs.html)” Analog Devices, Inc., May 2002.

9 “[Supervisors in Multivoltage Systems.](/en/resources/technical-articles/supervisors-in-multivoltage-systems.html)” Analog Devices, Inc., November 2003.

10 “[High-Voltage, Adjustable Sequencing/Supervisory Circuits.](/media/en/technical-documentation/data-sheets/MAX16052-MAX16053.pdf)” Analog Devices, Inc., 2018.

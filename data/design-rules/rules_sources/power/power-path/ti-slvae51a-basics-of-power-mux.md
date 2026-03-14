---
source: "TI SLVAE51A -- Basics of Power MUX"
url: "https://www.ti.com/lit/an/slvae51a/slvae51a.pdf"
format: "PDF 13pp"
method: "ti-html"
extracted: 2026-02-16
chars: 13420
---

# Trademarks

All other trademarks are the property of their respective owners.

# 1 What is a Priority Power MUX?

A basic Power Multiplexer (Power MUX)
selects between two or more input supplies to power a single output.

Figure 1-1 Power MUX Block
Diagram

If there is no preference for which
input supply to use, or if the preference is to always use the highest input voltage
supply available, then the minimum requirement for a power MUX solution would be
reverse current blocking for each input path. This can be accomplished using any
combination of diodes or ICs which behave like a diode (such as [*Ideal Diode
Controllers*](http://www.ti.com/idealdiode)).

Figure 1-2 Minimum Functionality for
Power MUX Without Priority

A schottky or silicon diode will
result in a voltage drop around 0.4 V or 0.7 V, respectively. Using an ideal diode
controller will result in a much lower voltage drop (on the order of 10 mV to 100 mV
and there will be a parasitic body diode which must be positioned to block reverse
current when the switch detects reverse current or is disabled.

If there is a priority, then
additional switches must be added to have full control over which path to enable.
Reverse current blocking (through a diode or a FET) must remain present and now a
MOSFET must be added to turn on/off each power path to the load.

Figure 1-3 Example Priority Power
MUX

The focus of this application note
will be on *priority* power MUX solutions and how they can be implemented.

# 2 Control Method

Power MUX solutions need a way to
determine which input supply should provide power to the output. There are generally
three options available on the market: Manual, Automatic, or Both.

## 2.1 Manual

A manual power MUX is one in which each path is individually controlled by an external signal (logic or microcontroller). The example of two load switches used in [Figure 2-1](GUID-653068B8-DA7C-47D8-AC65-C604A4F8C5EA.html#ID-8900E0F8-2A7B-4653-BE63-6C4C3AF15054) is a manual power MUX. There could be one or two EN pins which need to be controlled. This method is generally used when there is already a microcontroller present in the system which can decide under what conditions to enable each input.

Figure 2-1 Manual Power MUX using TPS22910 and TPS22912 Load Switches

## 2.2 Automatic

An automatic power MUX does not require an external signal to switch between loads. There is often a default priority (such as IN1) and the device will determine under what conditions to switch to IN2. The first condition will be when IN1 drops below a certain threshold (such as if IN1 is removed and the voltage decays). There could be other conditions such as during an overvoltage event on IN1, where the supply may switch to IN2 to power the load. This control method is commonly used when there is no microcontroller available or to simplify the design architecture and eliminate the need to rely on the microcontroller's resources. Note that most automatic power MUX solutions can be used in automatic mode or manual mode but not both.

Figure 2-2 Automatic Power MUX using 2x TPS259470x eFuses

## 2.3 Both - Automatic + Manual Override

There are some Power MUX solutions which offer the flexibility to be used in a automatic configuration and be controlled by a manual control signal. The [*TPS212x*](http://www.ti.com/lit/gpn/tps2120) family of Power MUX solutions can have a default (automatic) priority, but then be overriden by an external microcontroller if needed. This method is useful in applications which will have a default priority for most of its operation, but there will be some modes (such as diagnostics) requiring manual control to force which path is enabled.

Figure 2-3 Automatic Power MUX with Manual Override using TPS2120

# 3 Power MUX Topologies

## 3.1 Discrete

A 2-input priority Power MUX solution can be implemented using 4x discrete MOSFETs (2x paths of back-back FETs) along with manual or automatic logic to determine which path to enable. PMOS based solutions are commonly used when there is no higher voltage source or charge pump available (otherwise an NMOS-based architecture would be advantageous).

Figure 3-1 Manual and Automatic Discrete Power MUX with Priority

In this example, the manual power MUX can be controlled with two EN pins tied to a microcontroller. The microcontroller would need logic to ensure only one set of switches is on at a time, to prevent reverse current flow. The automatic MUX features a comparator followed by inverter logic to ensure only one set of switches is turned on at a time. The comparator is configured to turn on the top set of switches when input 1 is present, otherwise default to input 2 when present.

## 3.2 Semi-Integrated

For low-voltage inputs (less than 5 V), there are load switches available with a single integrated MOSFET but have the ability to block reverse current when disabled. These switches can accomplish this by effectively removing the body diode of the integrated FET while the switch is disabled.

Figure 3-2 Load Switch with Parasitic Body Diode Removed

If using one of these load switches with an active high enable and another load switch with active low enable, you can select between each power path while using only 1x GPIO.

Figure 3-3 Semi-Integrated Power MUX using TPS22910 and TPS22912 Load Switches

For higher input voltages (> 5 V), there are
eFuse switches available with back-back MOSFETs. They can be used in a priority mux
configuration (see [Figure 3-4](GUID-FB72D567-559E-467E-B3F7-6B0CEAF32D68.html#ID-735510CA-08BF-4669-D86B-D316F173969D)).

Figure 3-4 Semi-Integrated Power MUX using 2x TPS2660 eFuses

To learn more about how to use load switches or eFuses in a MUX configuration, see [*Power Multiplexing Using Load Switches and eFuses*](http://www.ti.com/lit/an/slva811a/slva811a.pdf).

## 3.3 Fully Integrated

TI’s portfolio of fully-integrated Power MUXes contains all 4x MOSFETs and switching logic in a single IC. These solutions provide all the functionality needed for a priority power mux in the smallest solution size possible. Additional features such as output status, slew rate control, overvoltage and overcurrent protection are included in devices such as the [*TPS212x*](http://www.ti.com/lit/gpn/tps2120) family.

Figure 3-5 Fully-Integrated Priority Power MUX with TPS2120

# 4 Switchover Method

When a power MUX solution transitions
powering the output from one supply to the other supply, this is referred to as the
*switchover* event. The method a power MUX uses to perform the switchover
will affect how much reverse current is conducted and how much the output voltage
will dip.

## 4.1 Break-Before-Make vs. Diode Mode

There are two sets of switchover methods that power MUX solutions fall under:

1. **Break-before-make** method occurs when the switch for the first supply completely turns off before the second supply switch is turned on.
   1. This prevents reverse current flow from one supply to another.
   2. There is a period of time where no power is being delivered from the supply to the output. This is known as the *switchover time*, or tSW.
2. **Diode mode** is a make-before-break method where the diode or switch for the first supply remains on while the second supply switch is turned on. Reverse current is then prevented by the presence of a diode or a device which detects the reverse current flow and shuts off a corresponding FET (such as our eFuse, Ideal Diode or ORing controllers).
   1. The benefit of this approach is minimal output voltage drop, as power is continuously supplied to the load.
   2. The tradeoff depends on what diode device is used:
      1. Schottky or Silicon diode will result in power dissipation and voltage drop during normal operation.
      2. eFuse, ORing or Ideal diode controller methods will result in some level of reverse current flow, potentially significant or insignificant depending on the application.

## 4.2 What is Seamless Switchover?

When switching between one supply to another, there are two possible outcomes:

1. The output voltage drops below operating range, causing the loads to experience a systematic reset.
2. The output voltage remains within operating range, causing uninterrupted operation. We will classify this type of outcome as *seamless switchover*.

If using a break-before-make power MUX, then switchover time is one key factor which will determine whether a seamless switchover will or will not occur. Faster switchover time will help achieve seamless switchover, at the expense of higher inrush current. This balance should be considered and power MUX solutions are available with a range of switchover times.

If using a diode-mode or
make-before-break power MUX, then seamless switchover is often possible since
worst-case output voltage drop will be approximately 0.4 V to 0.7 V (depending on
the diode used).

## 4.3 Output Voltage Drop

With a break-before-make power mux, there will be a period of time (tSW*, switchover time*) where the input supply is not providing power to the output. This will cause the output voltage to decay based on the following equations:

Figure 4-1 Voltage Dip on Output During Switchover Time

Equation 1. VOUT,MIN = VSW - VDIP

Equation 2. VDIP = tSW × (IOUT / COUT)

Therefore a faster switchover time,
tSW will result in a smaller voltage dip on the output,
VDIP.

## 4.4 Inrush Current

A faster slew rate switch will reduce the switchover time, but will cause a faster dVOUT/dt and therefore a larger spike of inrush current based on the equation:

Equation 3. IINRUSH = COUT × dVOUTdt

Figure 4-2 Inrush Current Spike Caused by Supply Switchover

Figure 4-3 Inrush Current Spike on IN2 During Switchover Using 2x TPS25942

In this example, 2x [*TPS25942*](http://www.ti.com/lit/gpn/tps25942a) eFuses were used to form a semi-integrated power MUX solution. The device was initially powered by CH-1, I\_IN and then transitioned to CH-2, I\_IN2. During the switchover time, output voltage began to drop by a diode drop. Once the switchover passed, there was a peak inrush current spike of approximately 3.42 A in order for the output to recharge. More examples of peak inrush current test results can be found at [*Power Multiplexing Using Load Switches and eFuses*](http://www.ti.com/lit/an/slva811a/slva811a.pdf).

There are two variables that can help a designer meet their target output voltage dip versus inrush current performance in a power MUX solution.

1. Output Capacitance - Following equations 1 through 4, increasing COUT will cause lower output voltage dip at the expense of higher inrush current during the transition, and vice-versa.
2. Switchover Times - Discrete power MUX solutions rely on RC delays in order to limit inrush current. This will result in relatively slow switchover times and relatively high dv/dt as the switch rise time will get exponentially larger as it turns on. In comparison, semi-integrated and fully integrated power MUX solutions often use a controlled linear rise time. This will result in relatively lower amounts of inrush current and a faster switchover time. There will be integrated power MUX solutions available at slew rate and switchover time combinations which are simply not possible with a discrete solution.

# 5 Additional Protection

Since power MUX solutions are often used at the input to a system, it is a good location to integrate protection features such as overvoltage or overcurrent protection.

## 5.1 Overvoltage Protection

Some applications need to protect against undesired high-voltage DC supplies or against transient induced voltages (such as from surge events or inductive switching). These potentially harmful voltages can be blocked from downstream components by using a power MUX with protection.

## 5.2 Overcurrent Protection

If a downstream circuit or fault event begins to draw excessive amounts of current, it is essential to limit that current quickly to avoid potential circuit damage or fire. This is another level of protection that can be integrated within a power mux.

TI provides power mux solutions with
both overvoltage and overcurrent protection. For example, 2x [*TPS2660*](http://www.ti.com/lit/gpn/tps2660)
or 2x [TPS25947](http://www.ti.com/product/tps25947) are semi-integrated power MUX solutions and [*TPS212x*](http://www.ti.com/lit/gpn/tps2120)
is a fully-integrated power MUX which each offer this level of protection.

# 6 Summary

There are different power MUX control
methods, topologies, and switchover methods which offer a certain level of
flexibility, protection and performance. System concerns such as output voltage drop
or inrush current can be addressed by utilizing Texas Instruments' portfolio of
semi-integrated Load Switch and eFuse solutions, or a fully-integrated Power MUX
such as the [*TPS212x*](http://www.ti.com/lit/gpn/tps2120) family which can offer the highest level
of functionality in the smallest size available.

# 7 References

* [*Seamless
  Switchover for Backup Power Reference Design*](http://www.ti.com/lit/pdf/tidue50)
* [*Power Multiplexing Using Load
  Switches and eFuses*](https://www.ti.com/lit/pdf/SLVA811)
* [*Basics of eFuses*](https://www.ti.com/lit/pdf/SLVA862)
---
source: "Altium -- Is There an SPI Trace Impedance Requirement?"
url: "https://resources.altium.com/p/there-spi-trace-impedance-requirement"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 13121
---
This article is all about [serial peripheral interface (SPI)](https://resources.altium.com/p/i2c-vs-spi-vs-uart-how-layout-these-common-buses) and its signal integrity challenges, all of which stem from impedance of the interface and the traces carrying digital signals. Before jumping into the primary point of this article, I’ll answer my own question:

* *There is no SPI trace impedance requirement. You can certainly size the traces in the SPI bus such that their impedance is 50 Ohms, but this is not required.*

When I write “there is no SPI trace impedance requirement” and “50 Ohms…is not required,” I mean that SPI does not specify any particular impedance requirement. If you look at other design guidelines that claim something to the effect of “SPI needs controlled impedance,” you will actually see that they often don’t state a specific impedance value. At best, they will state a range from 30 Ohms to 150 Ohms. That’s a big (and not very useful) range of values.

There is another instance I saw just recently of an application note from a major semiconductor manufacturer stating that SPI lines need controlled impedance and length matching, apparently ignoring setup times and full-duplex nature of this interface. They also did not list an impedance value or a length mismatch tolerance value. This is not a useful guideline if you ask me.

The reality is that SPI lines only start to need impedance control when the length of the interconnect becomes very long. And because there is no specific impedance requirement in the bus, you have some freedom in channel design and termination. So what exactly qualifies as “very long” and when is some termination method needed? We’ll break it down in this article.

## SPI Topology and Trace Design

The topology of an SPI is very simple. It uses three lines with a single controller-peripheral link, or four lines where there are multiple slaves on the bus. The upstream controller can send and receive data over a pair of lines at up to 60 Mbps, with data possibly being sent over a cable to another board or device. The topology of a typical SPI bus is shown below.

So what happens on the PCB? If you look at datasheets for a component with an SPI interface, you’ll find [minimum rise time values](https://resources.altium.com/p/what-high-speed-design) as short as 1 ns for advanced components. For some components, the rise time could be much longer, maybe 20 ns or more. Clearly, a slow bus like SPI can still have high-speed signal behavior even though the data rate and clock rate are low, but there is no impedance specification! How is it best to approach SPI designs?

### What’s the Rise Time in SPI Routing?

This problem in SPI is somewhat poorly communicated and it is one of those classic high-speed PCB design problems. Since we have a situation where we need to determine if an SPI link is “fast” or “slow” in terms of rise time, the first step is to understand what exactly contributes to the rise time.

The first step is to look in your datasheets for the master component that will control your SPI bus. If your component is well-documented, the rise time on the SPI interface will be specified for a particular [load capacitance](https://resources.altium.com/p/how-load-capacitance-transmission-line-affects-your-signals) seen on the bus. Note that “load capacitance” assumes zero inductance in the connection between the SPI output and the test load, so you can treat this rise time value as an RC time constant to a first approximation.

*Example datasheet entry relating signal rise time and fall time specified for a particular load capacitance.*

The values in the above example with high load capacitance are not typical of most components, but it illustrates the main point: the rise time is determined by the capacitance of the bus. In this example, if we take the 10%-90% rise time specified above and equate that to a 2.2RC (the standard used for determining time constant values), we would get R = 113.6 as the resistance seen on the bus. This means that, if we were to add some resistance at the driver (see below), then we could slow down the rise time while matching impedance.

Keep these points in mind because, later, we’ll use this to understand why series resistor termination can be used to slow down the SPI bus. Now that we know the rise time on the bus as seen at the receiver, we can determine when the bus is “long”.

### Is the SPI Bus Long or Short?

To a rough approximation, we can compare the distance the signal travels during its rise time to the total length. The other approach is to use a bandwidth estimate from the rise time (this would be 35 MHz in the above example) to determine when the bus input impedance deviates too far from a load impedance [as I’ve described in this article](https://resources.altium.com/p/why-there-transmission-line-critical-length). The simple way to get a rough estimate is to compare the distance traveled by the signal during its rise time to the propagation delay of the interconnect.

I prefer to use a conservative 10% limit to estimate when the bus starts to look long; if the propagation delay is less than approximately 10% of the distance traveled during the signal’s rise time, then the bus is considered short and we don’t need to care about terminating the bus impedance:

Note that other guidelines will state anywhere from 10% to 50% as the cutoff; there is no single value at which the bus is suddenly long, it’s a matter of judgment. As an example, for a 10 ns SPI signal on a PCB layer with Dk = 4, the 10% cutoff is 0.15 meters, or 15 cm. This means, any SPI route carrying a 10 ns signal less than 15 cm will be considered a short bus, which applies to many situations.

If you have a slow SPI bus, there are some very simple guidelines you can use to prevent some basic signal integrity problems. Some of the simplest guidelines you can implement to simultaneously reduce inductance (leading to ringing), crosstalk, and radiated emissions include:

* Route your SPI lines over a ground plane, even if they are not high speed
* Use wider traces on thin dielectrics: on outer layers size these 2-2.5x the distance to GND on the next layer; 10-15 mil traces on inner layers is often fine
* If you’re using a 2-layer board and you don’t have room for a ground plane, then place ground pour around your SPI lines to provide a clear return path

For best performance, I recommend not using 2 layers and instead starting with a PCB stackup that is compatible with high-speed digital designs.

### Why Do People State or Use 50 Ohms for SPI?

In the cases where SPI lines need to have a specific impedance, there is a good reason people use [50 Ohms as a target impedance](https://resources.altium.com/p/mysterious-50-ohm-impedance-where-it-came-and-why-we-use-it). Ironically, I don’t think people actually know the benefit of doing this, but they end up making the right decision for the wrong reasons.

If 50 Ohms is the characteristic impedance target for an electrically long SPI bus, it is likely there are other impedance controlled traces on the board that also target 50 Ohms characteristic impedance. Having a single impedance target makes impedance control much easier for a manufacturer. If they have to swap materials in the stackup to hit your impedance target, it’s much easier to do if there is only one target to hit in your stackup.

### Why Is Series Termination Used on Short SPI Buses?

From what we saw above, in the vast majority of practical situations with an SPI trace, there is no need for termination at the driver or receiver. If there was, you would see an impedance specification somewhere in component datasheets, in the SPI spec, or both. Also, components would likely have on-die termination applied to the target impedance, so you would not have to mess with placing a resistor.

*Terminating resistors placed on an SPI bus.*

The answer is pretty simple: it’s to slow down the signal emitted from the driver. The resistor provides a side benefit of damping any ringing on the output as well. ***Note that this resistor selection in this case has nothing to do with impedance matching in cases of an electrically short line.***

If your controller is an advanced component like an FPGA, and you instantiate an SPI interface in this controller, the rise time can be very short because the physical structure of the device simply ensures very fast rise times. As a result, it may be advantageous to slow down the signal so that you don’t have a fast signal creating crosstalk. In such a case, you must place the resistor close to the driver as this will ensure crosstalk is reduced along the entire length of the line.

Make sure you do not slow down the rise time too much, otherwise the signal will be too slow to toggle the I/O at the load and the signal might not be read correctly. You might also violate setup times if the rise time is made too long. There is a simple RLC model that can be simulated to determine the appropriate series resistor value.

### A Lumped Element Model for a Short SPI Bus

The actual model for an SPI bus is more complex. It includes the following factors:

* Trace capacitance across the entire bus (C)
* Trace inductance (L)
* Source impedance
* Load capacitance

The short bus basically looks like this LC model:

*SPI bus model with a short transmission line.*

The source impedance is ideally 0 Ohms, although in reality it could be a low value of around 10-30 Ohms. The load capacitance should be specified in the receiver’s datasheet.

Howard Johnson talks about this on the SigCon website; it is a bus that can exhibit an underdamped oscillation if excited with a fast signal and if there is too much inductance; it can also be [simulated in SPICE](https://resources.altium.com/p/what-spice-simulation-electronics-design). Adding a series resistor in this case adds damping, which will reduce the rise time.

Note that I’ve left trace resistance off of this list; the trace resistance will be very small and will provide negligible losses and damping. This is because the trace resistance is on the order of milliOhm, and the roughly approximated resistance that governs the rise time can be anywhere from 10-100 Ohms, so clearly the trace resistance is negligible.

### Series Resistor in a Long SPI Bus

In the case of a long bus, which is uncommon, you have to match the SPI line to a target impedance (50 Ohms is convenient). In this case, just by comparing the signal swing on the SPI I/O to the current, you’ll get a resistance value for the signal in the ON state. The series resistor in this case will usually be either 22 Ohms or 33 Ohms required to hit a 50 Ohm target. Place this close to the driver to both impedance match and slow down the signal [as described here](https://resources.altium.com/p/the-right-termination-of-the-right-size-at-the-right-place).

*SPI bus model with series termination resistor.*

To better understand the function of the resistors on the long bus in addition to the effect of slowing down the signal, we can look at the voltage levels at the driver and receiver. Without the termination resistor, the Source attempts to drive a voltage V(out) onto the transmission line, and if the line were very short then that same V(out) would be observed at the load. After placing the termination resistor, we will see the following voltage levels at the source and load:

Why does the voltage at the load appear to double? This is due to reflection from the high input impedance at the load (i.e., from the load capacitance). I've explained this and shown the result using a transfer function formulation [in this article](https://resources.altium.com/p/can-you-use-series-and-parallel-termination-same-net).

The other reason to do this is if you have multiple slave components on the bus; you’ll be matching to the input impedance in each leg of the bus, and you might slow down the rise time enough to where you have to worry less about the input impedance at the splits in the bus. In general, splitting the line closer to the driver is better because the [input impedance](https://resources.altium.com/p/how-use-input-impedance-circuits-and-transmission-lines) into each section will be closer to the line’s characteristic impedance.

Something we haven't covered in this article is the signaling format in SPI. To learn more about this aspect of the SPI protocol, read this excellent overview by Mark Harris:

Whether or not you need to apply an SPI trace impedance requirement, you can design the best boards with the PCB design and routing features in [Altium](https://www.altium.com/). When you’ve finished your design, and you want to release files to your manufacturer, Altium makes it easy to collaborate and share your projects.

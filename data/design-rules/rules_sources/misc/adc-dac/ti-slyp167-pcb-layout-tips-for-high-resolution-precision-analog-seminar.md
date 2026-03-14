---
source: "TI SLYP167 -- PCB Layout Tips for High Resolution (Precision Analog Seminar)"
url: "https://www.ti.com/lit/ml/slyp167/slyp167.pdf"
format: "PDF 22pp"
method: "pdfplumber"
extracted: 2026-03-02
chars: 7469
---

Precision Analog Applications Seminar
PCB Layout Tips for High Resolution
Section 9
Layout of printed circuit boards (PCBs) could be an all-day discussion. Rather than
give you a set of rules to follow, which almost always have exceptions, we’ll look
here at some general principles and then review a number of actual board layouts
that illustrate common mistakes.
Texas Instruments

PCB Layout Tips
Outline
LSB size
(cid:139)
(cid:131) Impact on layout decisions
Basic PCB Design Principles
(cid:131) For High Resolution
PCB Layout Reviews
(cid:131) Learn from the misfortune of others!

LSB Size and Its Impact
Signal Range Is Critical
(cid:131) ±10V is a 20V Range
• 16 Bits: 20V/65,536 = 305µV Per LSB
• 24 Bits: 20V/16,777,216 = 1,192nV Per LSB
(cid:131) ±2.5V is a 5V Range
• 16 Bits: 5V/65,536 = 76.3µV Per LSB
• 24 Bits: 5V/16,777,216 = 298nV Per LSB
(cid:131) ±0.020V is a 0.040V Range
• 16 Bits: 0.040v/65,536 = 0.610µV Per LSB
• 24 Bits: 0.040V/16,777,216 = 2nV Per LSB
Where ±10V gives you an LSB of 305µV, a 5V signal only gives you 76.2µV for a
16-bit LSB. When gain is added into the system, the resolution can sink into the
noise.

High Resolution Measurements
1 inch
1.3µV
10µA
1 inch (7 mil) trace of 1/2 oz copper with
10 A of current => voltage drop of 1.3 V
µ µ
4 LSBs at 24 bits!
You must be careful with the PCB layout for a 12-bit design. For a 16-bit design you
have to do everything correctly to achieve that performance; it should be obvious
that a 24-bit design will be affected by any errors in the layout.

Separate Analog and Digital Signals
AGND and DGND connected at
ADC/DAC
Provide Good Ground Return Paths
High Frequency Bypassing
Minimize Inductance
Control Thermocouples
Differential Signal Measurements
The separation of the Analog and Digital section of the PCB keeps noisy digital from
the low level analog. However, they must come together at the ADC or DAC. It is
important that the Analog Ground and the Digital Ground be connected together at
the ADC or DAC. This allows a quick return for the ground currents as the analog
and digital portions of the device communicate.
Inductance is determined by the size of the loop of current. Providing a path for
return currents next to the signal trace will reduce the inductance. That is the
advantage of a solid ground plane. If a reasonably solid plane can’t be achieved
with two layers, then more layers should be used.

PCB Layout Process
Start with a Split Ground Plane
Digital Signals over the Digital Plane
Analog Signals over the Analog Plane
Then as a Final Step – Remove the Split
The Signal Return Currents will flow only
Next to the Signal Trace. (A larger path
will have increased inductance)
Since AGND and DGND are connected at the ADC/DAC and also at the power
supply, there is a ground loop created. By having a solid ground plane this can be
eliminated. The analog signals will still just flow in the analog portions of the ground
plane and the digital signals will only flow in the digital portion of the ground plane.
The reason why they will not travel throughout the board, is because a larger path
has a larger inductance. The signals will travel through the path of lowest
impedance.

Offset Voltages
A temperature differential with any two
metals will create a thermocouple
This includes PCB feedthroughs
(cid:131) A different number of feedthroughs for
both sides of a differential signal will
create an offset that varies with
temperature.
Your board design can create additional offset voltages because of the traces and
feedthroughs. To minimize offset it is good to route the signal traces differentially
next to each other so that they will see the same thermal gradients and the same
number of feedthroughs.

PCB Layout
A Rogue’s Gallery
We’ll now look at a few examples of circuit layouts that make some common
mistakes.

Layout Review #1
The ground current from U3 was routed to the ground point for the crystal (Y1)
capacitors and then to the rest of the ground in the system. This caused a
significant effect on the oscillator and made the clock very unstable.

Layout Review #2
If we position capacitors and components with an order and goal of symmetry, the
results could be unnecessary inductance and resistance that are introduced which
will reduce the performance of the system.

Layout Review #3
Here this board is designed with a reasonably solid ground plane and rather than
connecting directly with feedthroughs to ground plane, there are large traces to a
centralized ground connection point. The extra inductance and resistance, even with
wide traces, will reduce the performance of the board compared to feedthroughs (or
multiple feedthroughs) placed close to the component’s ground connection.

Layout Review #4
These top planes seem to be just an area fill for the gaps in the traces. When the
plane areas on the top layer are not connected to the ground plane on the bottom,
that means that the ground plane on the bottom doesn’t have a continuous path
available for current. If these top ground planes were connected to the bottom
ground plane, the ground return currents would have a lower inductance path.

Layout Review #5
Ground Pin
Here we see serious splits in the bottom ground plane. A close examination will also
show that the traces that are splitting the ground plane are actually also ground
signals.

Layout Review #6-Top
As this layer is compared with the next slide, it is evident that some of the traces
could have been put on this layer so that the ground layer could have been more
solid.

Layout Review #6 —Bottom
This shows the problem of using a digital PCB layout for an analog board. It
simplifies the routing for most of the traces on each layer to go one direction, but
that might lead to inefficiencies in the ground return currents and an unnecessary
increase in inductance. Remember, inductance is defined by the size of the loop for
the current.

Layout Review #7
There is a good separation between the analog and digital sections, but the AGND
and DGND should be connected together at the ADC.

Forgotten Feedthrough
The goal was to place the resistor to protect the reset pin. The close placement of
the resistor didn’t solve the problem. However the feedthrough was to an external
connector that defeated the purpose of the resistor.

Layout Review #8
The Analog and Digital sections are nicely separated. The AGND and DGND are
connected with a wide connection right at the MSC1210. But the ground plane
sometimes has narrow channels for current which will increase inductance and
noise. The return currents for the digital signals will want to travel under the
horizontal traces, but the channels in the ground plane are generally vertical.

Layout Review #9 —Before
Analog and Digital sections separated with ground planes on both the bottom and
the top. But the bottom ground plane is seriously split so that the ground return
currents can’t flow close to the source signal wires.

Cleaned Up Layout #9 —After
A few simple changes in the routing were able to provide a much better ground
return path. Larger continuous areas of ground plane translate into short return
current paths and lower inductance.

Summary
LSB size
(cid:131) Higher resolution systems reveal PCB layout
errors more clearly!
(cid:131) Separate analog and digital signals
(cid:131) Establish good grounding
(cid:131) Minimize inductance
(cid:131) Control thermocouples
PCB Layout Reviews
(cid:131) Learn from your mistakes!
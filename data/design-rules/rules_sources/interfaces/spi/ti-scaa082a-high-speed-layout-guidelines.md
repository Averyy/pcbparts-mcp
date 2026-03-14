---
source: "TI SCAA082A -- High-Speed Layout Guidelines"
url: "https://www.ti.com/lit/an/scaa082a/scaa082a.pdf"
format: "PDF 21pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 18669
---
# High-Speed Layout Guidelines

Alexander Weiler, Alexander Pakosta, and Ankur Verma -- Clock Drivers

## Abstract

This application report addresses high-speed signals, such as clock signals and their routing, and gives designers a review of the important coherences. With some simple rules, electromagnetic interference problems can be minimized without using complicated formulas and expensive simulation tools. Section 1 gives a short introduction to theory, while Section 2 focuses on practical PCB design rules. Either section can be read independently.

## 1 Theoretical Overview

Some basic understanding is desirable to effectively use the PCB design rules given in this document. It is then easy to identify the undesirable effects that can arise and how to avoid them. The reason PCB layout becomes more and more important is because of the trend to faster, higher integrated, smaller form factors, and lower power electronic circuits. The higher the switching frequencies are, the more radiation occurs on a PCB. With good layout, many EMI problems can be minimized to meet the required specifications.

### 1.1 Electromagnetic Interference and Electromagnetic Compatibility

Electromagnetic interference (EMI) is radio frequency energy that interferes with the operation of an electronic device. This radio frequency energy can be produced by the device itself or by other devices nearby.

Electromagnetic compatibility (EMC) is the ability of an electronic product to operate without causing EMI that would interfere with other equipment and without being affected by EMI from other equipment or the environment.

The goal is to reduce EMI to meet the requirements given by the Federal Communication Commission (FCC) or the International Special Committee on Radio Interference (CISPR).

A basic EMI model: Every device acts as a source and simultaneously as a sink. It can cause interference through a coupling path and can be affected by interference through the coupling path. The coupling can be:

- Capacitive
- Inductive
- Galvanic
- Radiated power

There is not just one coupling mechanism present, but rather a combination of them. With proper PCB layout, however, these effects can be reduced.

### 1.2 Clock Signals

Ideally, a clock signal is a square wave, but in reality, it is not possible to change from low level to high level (and vice versa) in an infinitely short time. Due to the rise and fall time, it has the shape of a trapezoid in the time domain. By means of the Fourier series, the trapezoid consists of a series of sine and cosine signals with different frequency and magnitude. An important aspect is that in the frequency domain the amplitude of the higher frequency harmonics depends on the rise and fall time of the signal. The longer the rise time, the smaller the magnitude of the harmonics. For example, the harmonics of a 100-MHz clock signal are not negligible, especially the third and fifth. In this case, consideration also should be made with frequencies up to 500 MHz. With the CDCE906 from Texas Instruments, the user can set different rise and fall times to reduce the amplitude of the harmonics. However, take care to ensure these times do not violate the slew rate specifications of the driven devices.

### 1.3 Transmission Lines

If the lengths of traces are in the range of the signal's wavelength, then the user has to consider the effects of transmission lines. The problems that a user must deal with are time delay, reflections, and crosstalk. They are simply the traces on a PCB and depend on the length and the frequency of the signals passing through them.

Two common structures: A microstrip has one reference, often a ground plane, and these are separated by a dielectric. A stripline has two references, often multiple ground planes, and are surrounded with the dielectric.

| Symbol | Description |
|---|---|
| H | Height of the dielectric |
| W | Width of the trace |
| L | Length of the trace |
| Z0 | Characteristic impedance of the trace |
| VP | Velocity of the signal relative to the speed of light |
| epsilon_eff | Effective dielectric constant |

#### 1.3.1 Signal Speed and Propagation Delay Time

A signal cannot pass through a trace with infinite speed. The maximum speed is the speed of light (3 x 10^8 m/s). For a stripline:

V = (3 x 10^8 m/s) / sqrt(epsilon_r)

So, the speed is a function of the dielectric which surrounds the trace. For a microstrip, it is more complicated because the trace is not surrounded by one dielectric -- there are at least two: the substrate under the trace and the air above the trace.

The signal speed and the propagation delay time are important when:

- Timing and skew requirements must be met (clock distribution, buses, etc.)
- Differential traces are used (for example, LVDS)

**Example:** length = 100 mm; thickness = 35 um; height = 1.5 mm; epsilon_r = 4.6 (FR4); frequency = 300 MHz

| Structure | Width (mm) | epsilon_r,eff | VP,relative | VP,absolute (mm/ns) | Pd (ps/100mm) |
|---|---|---|---|---|---|
| Microstrip 1 | 0.5 | 3.046 | 0.573 | 171.9 | 581.7 |
| Microstrip 2 | 1 | 3.165 | 0.562 | 168.6 | 593.1 |
| Stripline 1 | 0.5 | 4.6 | 0.466 | 139.8 | 715.3 |
| Stripline 2 | 1 | 4.6 | 0.466 | 139.8 | 715.3 |

#### 1.3.2 Characteristic Impedance, Reflections, and Termination

Another property of a transmission line is the characteristic impedance, Z0. If there are any impedance changes in the signal chain (source - trace - vias - connectors - sink, etc.), reflections occur. These reflections cause over- and undershoots. The reflection coefficient rho expresses the relationship:

rho = (R - Z0) / (R + Z0)

For an open end, rho = +1; for a shorted end, rho = -1. To avoid reflections, the reflection coefficient must be rho = 0, which occurs when the load impedance matches the characteristic impedance.

The most common termination techniques:

- Series termination
- Parallel termination
- Thevenin termination
- AC termination

Each has advantages and disadvantages, and the designer has to trade off which one is the best solution.

### 1.4 Crosstalk

The mutual influence of two parallel, nearby routed traces is called crosstalk. One is called the aggressor (this trace carries the signal) and the other is called the victim (this trace is influenced by the aggressor). Due to the electromagnetic field, the victim is influenced by an inductive and a capacitive coupling. They generate a forward and a backward current in the victim trace, whereas in a homogenous environment (e.g., stripline) the two induced currents cancel each other. In a microstrip environment, the forward current of the inductive coupling tends to be larger than the influence of the capacitive coupling. To minimize the effects of crosstalk on adjacent traces, keep them at least 2 times the trace width apart.

There are two types of crosstalk: forward crosstalk and backward crosstalk. Forward crosstalk travels in the same direction as the aggressor and grows with length and increasing aggressor dV/dt. Backward crosstalk travels in the opposite direction and depends only on the aggressor amplitude.

### 1.5 Differential Signals

In the case of differential signals, the negative effect of crosstalk is a positive one. The signals on each trace are in theory exactly equal in magnitude and opposite in their sign. So, their electromagnetic fields cancel each other and the return current on the ground plane, as well. To achieve this, the traces for both signals must have the same length so that the propagation delay times are equal. The receiver is sensitive to the differences of the signals and not to an absolute level reference. The designer has to make sure that radiation affects both traces equally, which can be realized by routing the differential traces as close as possible.

### 1.6 Return Current and Loop Areas

An electrical circuit must always be a closed loop. With DC, the return current takes the way back with the lowest resistance. With a higher frequency, the return current flows along the lowest impedance -- directly beside the signal.

If this return path (mostly the ground plane) has a slot, the return current has to take another way, resulting in a loop area. The larger the area, the more radiation and EMI problems occur. The designer has to make sure that the return current can flow directly underneath the signal trace. Solutions: place a 0-Ohm resistor over the slot, route the signal the same way as the return current flows, or (best) avoid any slots in the ground reference plane.

## 2 Practical PCB Design Rules

Because many things can affect transmission lines, EMI problems can occur. To reduce these problems, good PCB design is important. It is important to make prudent decisions during new circuit design, like the minimum number of layers. The easiest way to get a good, new design is to copy the recommended design from the TI evaluation modules (EVM).

A good PCB layout starts with the circuit design. Do not postpone considerations about the layout. One of the most important aspects affecting the layout is the location of each functional block. Keep their devices and their traces together.

### 2.1 PCB Considerations During the Circuit Design

- What is the highest frequency and fastest rise time in the system?
- What are the electrical specifications at the inputs and outputs of the sinks and sources?
- Are there sensitive signals to route (controlled impedance, termination, propagation delay)?
- Is a microstrip adequate for the sensitive signals, or is it essential to use stripline technique?
- How many different supply voltages exist? Does each supply voltage need its own power plane?
- Create a diagram with the functional groups of the system
- Are there any interconnections between independent functional groups? Take special care of them.
- Clarify the minimum width, separation and height of a trace with the PCB manufacturer.

### 2.2 Board Stackup

Generally, the use of microstrip traces needs at least two layers, whereas one of them must be a GND plane. Better is the use of a four-layer PCB, with a GND and a VCC plane and two signal layers. If the circuit is complex and signals must be routed as stripline, a six-layer stackup should be used.

**Four-Layer PCB Stackup Options:**

| | Model 1 | Model 2 | Model 3 | Model 4 |
|---|---|---|---|---|
| Layer 1 | SIG | SIG | SIG | GND |
| Layer 2 | SIG | GND | GND | SIG |
| Layer 3 | VCC | VCC | SIG | VCC |
| Layer 4 | GND | SIG | VCC | SIG |
| Decoupling | Good | Good | Bad | Bad |
| EMC | Bad | Bad | Bad | Bad |
| Signal integrity | Bad | Bad | Good | Bad |

**Six-Layer PCB Stackup Options:**

| | Model 1 | Model 2 | Model 3 | Model 4 | Model 5 | Model 6 |
|---|---|---|---|---|---|---|
| Layer 1 | SIG | SIG | GND | SIG | SIG | SIG |
| Layer 2 | SIG | GND | VCC | GND | GND | GND |
| Layer 3 | VCC | VCC | SIG | VCC | VCC | VCC |
| Layer 4 | GND | VCC | SIG | SIG | GND | GND |
| Layer 5 | SIG | GND | VCC | GND | Not used | SIG |
| Layer 6 | SIG | SIG | GND | SIG | SIG | SIG |
| Decoupling | Good | Good | Good | Good | Good | Good |
| EMC | Bad | Good | Satisfactory | Satisfactory | Good | Good |
| Signal integrity | Bad | Good | Bad | Good | Good | Bad |

To determine the right board stackup, consider:

- Define the location of each section by functional diagram. Keep devices together to avoid interaction between separate blocks.
- It is necessary in high-speed designs to have at least one complete ground plane as a reference for microstrip traces.
- With a complete power plane as close as possible to the ground plane, capacitive coupling between them provides low impedance at high frequencies, reducing decoupling capacitor count.

### 2.3 Power and Ground Planes

A complete ground plane in high-speed design is essential. Additionally, a complete power plane is recommended.

Take care when using split ground planes because:

- Split ground planes act as slot antennas and radiate.
- A routed trace over a gap creates large loop areas, because the return current cannot flow beside the signal.
- Crosstalk can arise in the return current path due to discontinuities in the ground plane.

Guidelines:

- If possible, use a continuous ground plane; do not split them.
- If split ground planes are essential:
  - Do not route signals over a gap.
  - Connect split ground planes only at one point.
  - The return current of a subsystem must not be in the path of the other subsystem.
  - Power planes should only reference their own ground plane.
  - Do not connect bypass capacitors between a power plane and an unrelated ground plane.

### 2.4 Decoupling Capacitors

Decoupling capacitors between the power pin and ground pin of the device ensure low AC impedance to reduce noise and to store energy. To reach low impedance over a wide frequency range, several capacitors must be used. A real capacitor consists of its capacitance and a parasitic inductance and resistance, so every real capacitor behaves as a resonant circuit. The capacitive characteristics are only valid up to its self-resonant frequency (SRF). Above the SRF, the parasitic effects dominate and the capacitor acts as an inductor.

A power and GND plane can represent a capacitance that ensures low impedance at high frequencies, minimizing the number of small-value decoupling capacitors needed.

General rules for placing capacitors:

- Place the lowest valued capacitor as close as possible to the device to minimize inductive influence.
- Place the lowest valued capacitor as close as possible to the power pin/power trace.
- Connect the pad of the capacitor directly with a via to the ground plane. Use two or three vias for low-impedance connection.
- Make sure that the signal must flow along the capacitor.

### 2.5 Traces, Vias, and Other PCB Components

A right angle in a trace can cause more radiation. The capacitance increases in the region of the corner, and the characteristic impedance changes, causing reflections.

- Avoid right-angle bends in a trace and try to route them at least with two 45-degree corners. The best routing would be a round bend.
- Separate high-speed signals from low-speed signals and digital from analog signals.
- To minimize crosstalk between adjacent layers, route them at 90 degrees to each other.

The use of vias adds additional inductance and capacitance, and reflections occur due to the change in characteristic impedance. Vias also increase the trace length.

- Avoid vias in differential traces. If impossible to avoid, use vias in both traces or compensate the delay in the other trace.
- The designer must make sure the return current can flow underneath the signal trace. Add ground vias around the signal via (similar to a coaxial line structure).

Tips for routing traces and the use of vias:

- Do not use right-angle bends on traces with controlled impedance and fast rise time.
- Route traces orthogonally to each other on adjacent layers to avoid coupling.
- To minimize crosstalk, the distance between two traces should be approximately 2 to 3 times the width of the trace.
- Differential traces should be routed as close as possible to get a high coupling factor.
- Do not use vias on traces with sensitive signals, if unnecessary.
- Be careful with the return current when changing layers. Use ground vias around the signal via.
- Do not create slots in the ground plane by using closely placed vias.
- Consider stubs created by vias. If necessary, use blind vias or buried vias.

Microstrip implementation for traces can have high crosstalk and are not recommended for high-speed digital systems. Stripline traces inherently have zero crosstalk and minimize EMI/EMC. Striplines require vias because traces must be buried inside the PCB. A PCB via passing completely through the board leaves a stub on the other side, which looks like a capacitor on TDR and can create resonance phenomena. At the quarter wave frequency, the open-ended stub looks like a short and produces nulls of transmission. The designer must back-drill such vias after the PCB is fabricated.

### 2.6 Clock Distribution

Four possible clock distribution circuits:

- **Branching (bad):** Enormous reflections at the branches and different trace lengths to the devices.
- **Daisy-chain (better):** Route the signal in a chain from one device to the other with proper termination. Be careful with delay.
- **Star connection (good):** A clock driver distributes clock signals to different devices. To minimize skew, use the same trace length for every clock signal.
- **Complex star (best for complex systems):** A main clock feeds several clock drivers. Implement delay-time compensation and use proper termination to avoid reflections.

Guidelines:

- Be careful with trace length in clock distribution. Route signals with the same length.
- Avoid branches to reduce reflections. Use a clock driver to distribute the signal.

## 3 Summary

This document presents an introduction to designing a PCB. The rules presented can assist the designer in creating proper PCB designs. The higher the signal frequency, the more complicated the PCB design. Basically, the designer must know which are the sensitive parts in the circuit or where problems due to reflections can occur. With this knowledge, a good placement of the devices can be made. Placement is such an important step in high-speed design -- the designer will do well to always keep it and the return current in mind.

## 4 References

1. *High-Speed DSP Systems Design Reference Guide* (SPRU889)
2. *Crosstalk, Part 1: The conversion we wish would stop*, Douglas Brooks
3. *Crosstalk, Part 2: How loud is your crosstalk?*, Douglas Brooks
4. *Crosstalk, EMI and differential Z*, Douglas Brooks
5. *Crosstalk, Part 1: Understanding Forward vs Backward*, Douglas Brooks
6. *Differential Impedance: What's the difference*, Douglas Brooks
7. *Differential Signals*, Douglas Brooks
8. *Adjusting signal timing (part 1)*, Douglas Brooks
9. *Transmission line termination*, Douglas Brooks
10. *EMV-Design Richtlinien*, B. Foeste/s. Oeing, ISBN: 3-7723-5499-8, Franzis
11. *Elektronik-Praxis: Die Leiterplatte 2010*, Ausgabe 11/06, P72-77
12. *Microstrip propagation times -- slower than we think*, Douglas Brooks
13. *Design for minimizing electromagnetic interference in high frequency RF and digital boards and systems*, Dr. Eric Bogatin
14. *An EMC/EMI system-design and testing methodology for FPD-Link III SerDes* (SLYT719)

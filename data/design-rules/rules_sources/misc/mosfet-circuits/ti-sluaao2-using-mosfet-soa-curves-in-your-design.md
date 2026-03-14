---
source: "TI SLUAAO2 -- Using MOSFET SOA Curves in Your Design"
url: "https://www.ti.com/lit/an/sluaao2/sluaao2.pdf"
format: "PDF 9pp"
method: "fetchaller"
extracted: 2026-02-14
chars: 9315
---

# Using MOSFET Safe Operating Area Curves in Your Design

John Wallace

## Abstract

Power MOSFET data sheets include a safe operating area (SOA) graph with a family of curves to make sure the device can be operated at current and voltage conditions in an application without being damaged. Proper use of SOA data is a critical design element for reliable system operation.

## 1 Using MOSFET Safe Operating Area Curves in Your Design

Power MOSFETs are used in applications where voltage and current stresses may exceed their capabilities leading to long term reliability concerns and/or catastrophic failures. This article will review the SOA graph in the MOSFET data sheet and show how it is used to ensure safe operation of the FET in an application without damaging it.

## 2 Review the SOA Graph

The SOA graph for the CSD19536KTT, 100 V N-channel MOSFET, is shown in Figure 2-1. As explained in the earlier article, "Understanding MOSFET data sheets, Part 2 - Safe operating area (SOA) graph", the SOA curve has five limitations: R_DS(on), current, maximum power, thermal instability and BV_DSS. Please refer to this article for a detailed explanation of each limitation and the test methodology TI uses to generate the SOA graph in the MOSFET data sheet.

*Figure 2-1. CSD19536KTT SOA Graph*

## 3 Applications Where SOA is Important

Power MOSFETs are found in a wide variety of applications but typically fall into two categories: switch-mode and linear-mode. Some examples of switch-mode applications are DC-DC converters, class-D audio amplifiers and motor drives. Inrush control for hot-swap, load switching and as a pass element in a linear regulator are common linear-mode applications.

First, a quick review of MOSFET output characteristics as shown in Figure 3-1. The family of I_DS vs. V_DS curves at different values of V_GS displayed in this chart can be divided into two regions: linear, where V_DS << V_GS - V_GS(th), and saturation, where V_DS > V_GS - V_GS(th). In the linear region the output is ohmic and increasing V_DS results in proportionally higher I_DS. In the saturation region the output is flat or saturated and I_DS only increases slightly with increasing V_DS.

*Figure 3-1. MOSFET Output Characteristics*

Figure 3-2 shows switch-mode (blue circles) and linear-mode (orange triangle) operating points. In a switch-mode application, the FET transitions between the off state (V_GS << V_GS(th), and I_DS = 0 A) and the linear region. During the switching transitions, the FET rapidly passes through the saturation region as depicted by the blue dashed line. Because of the short duration in the saturation region, the FET does not incur excessive power loss and is of little concern for SOA. In a linear-mode application, the FET operates for long periods of time in the saturation region where there is simultaneously voltage across and current through the device leading to high power dissipation and elevated junction temperature. The focus of this article is on linear-mode operation and how to use the data sheet SOA curves to make sure the FET operates within safe limits with no damage.

*Figure 3-2. Switch-Mode and Linear-Mode Operating Points*

## 4 Using the Data Sheet SOA Graph

Consider this simple example using the CSD17570Q5B in a generic design that has to support 12 V for 10 ms during a fault condition. How much current can the FET safely conduct under these conditions? Using the SOA graph from the data sheet in Figure 4-1, draw a vertical line from V_DS = 12 V on the x-axis to the intersection with the 10 ms SOA line. Next, draw a horizontal line from the intersection point to the y-axis. This corresponds to I_DS = 7.3 A. This shows the CSD17570Q5B can safely operate at V_DS = 12 V and I_DS = 7.3 A for 10 ms at 25 C.

*Figure 4-1. CSD17570Q5B Safe Operating Area*

## 5 Temperature Derating of SOA

How much is the SOA current capability reduced at elevated case temperatures? The simplest approach is a linear derating factor as follows:

```
I_DS(TC) = I_DS(25C) x (TJ_max - TC) / (TJ_max - 25C)        (1)
```

Building on the previous example, what is the safe operating current if the case temperature is raised to TC = 100 C? The maximum junction temperature specified in the CSD17570Q5B data sheet is TJ_max = 150 C, and the safe operating current is calculated as follows:

```
I_DS(100C) = 7.3 A x (150C - 100C) / (150C - 25C) = 2.9 A    (2)
```

Therefore, the device is capable of 2.9 A at TC = 100 C with a pulse width of 10 ms and V_DS = 12 V.

## 6 Estimating SOA for Different Pulse Widths

What if the pulse width is different from those shown in the SOA graph? Normally, the pulse widths of the SOA curves in TI MOSFET data sheets are in decile values (for example, 10 us, 100 us, 1 ms, 10 ms, 100 ms) but an application can require a pulse width which is in between these curves. A log-log plot of I_DS vs. t_PW values from the CSD17570Q5B data sheet SOA curves is shown in Figure 6-1.

*Figure 6-1. CSD17570Q5B SOA Current vs. Pulse Width at V_DS = 12 V*

As detailed in section 2.3.2 in the TI application report, "Robust Hot Swap Design", the SOA current capability at different pulse widths can be estimated using the SOA currents at the pulse widths above and below the required pulse width as follows:

```
I_DS(t_PW) = a x t_PW^m                                       (3)

m = ln(I_DS(t_PW1) / I_DS(t_PW2)) / ln(t_PW1 / t_PW2)        (4)

a = I_DS(t_PW1) / t_PW1^m                                     (5)
```

From the original example, if the pulse width is increased to 20 ms, then the current capability is reduced and is estimated as follows:

```
I_DS(10 ms) = 7.3 A                                           (6)
I_DS(100 ms) = 4.1 A                                          (7)

m = ln(7.3 A / 4.1 A) / ln(10 ms / 100 ms) = -0.25           (8)

a = 7.3 A / (10 ms)^(-0.25) = 12.9                            (9)

I_DS(20 ms) = 12.9 x (20 ms)^(-0.25) = 6.1 A                 (10)
```

For a 20 ms pulse at V_DS = 12 V, the capability is I_DS = 6.1 A at TC = 25 C. At TC = 100 C the rating is reduced to I_DS = 2.4 A.

## 7 Estimating SOA for Non-Square Waveforms

What if the waveforms are not square? TI performs SOA testing to destruction using square waveforms as shown in Figure 7-1.

*Figure 7-1. Typical SOA Test Waveform*

In section 2.3.3 of the application report, "Robust Hot Swap Design", a method is presented for approximating the MOSFET stress as a square pulse with equivalent energy and pulse width as follows:

```
E1 = E2 = integral(0 to t1) of v_DS(t) x i_DS(t) dt          (11)

t2 = E2 / P_MAX                                               (12)
```

In many applications, one of the waveforms is a linear ramp while the other is held constant. For example, in a hot swap circuit during inrush, V_DS is ramping down while I_DS is constant as shown in Figure 7-2.

*Figure 7-2. Hot Swap Inrush Example Waveform*

For this example, assume V_DS decays linearly from 12 V down to 0 V in 20 ms while I_DS = 6 A. The energy, E1, in the pink shaded area under the power curve is calculated as follows:

```
E1 = integral(0 to t1) of v_DS(t) x i_DS(t) dt               (13)

v_DS(t) = V_DS x (1 - t/t1)                                   (14)

i_DS(t) = I_DS                                                (15)

E1 = V_DS x I_DS x integral(0 to t1) of (1 - t/t1) dt
   = V_DS x I_DS x t1 / 2                                     (16)
```

For the equivalent square pulse, the energy in the blue shaded area is assumed to be equal and the power P2 is the same as the maximum power in the non-square pulse.

```
E1 = E2 = P_MAX x t2                                          (17)

t2 = E2 / P_MAX = (V_DS x I_DS x t1) / (2 x V_DS x I_DS)
   = t1 / 2                                                   (18)
```

Inserting the values from the example:

```
V_DS = 12 V                                                   (19)
I_DS = 6 A                                                    (20)
t1 = 20 ms                                                    (21)
P_MAX = V_DS x I_DS = 12 V x 6 A = 72 W                      (22)
t2 = t1 / 2 = 20 ms / 2 = 10 ms                               (23)
```

Next, go back and confirm that the equivalent square pulse, V_DS = 12 V and I_DS = 6 A is below the 10 ms curve on the CSD17570Q5B SOA curve as shown in Figure 7-3.

*Figure 7-3. SOA Inrush Example*

This methodology can be extended for use with other types of pulses including non-monotonic, exponential, constant power, and so on.

## 8 Summary

This application note reviewed the MOSFET data sheet SOA graph and demonstrated how to use the graph to make sure the FET can be operated without damage in an application. Practical examples were provided when conditions are not the same as those specified in the data sheet.

## 9 References

- Texas Instruments, E2E Forum: Understanding MOSFET Data Sheets, Part 2 - Safe Operating Area (SOA) graph
- Texas Instruments, Robust Hot Swap Design, application note.
- Texas Instruments, E2E Forum: Discrete FETs vs. Power Blocks - How to Choose the Right SOA for Your Design

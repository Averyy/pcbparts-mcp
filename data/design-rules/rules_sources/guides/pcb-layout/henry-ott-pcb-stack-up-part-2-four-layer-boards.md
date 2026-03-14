---
source: "Henry Ott -- PCB Stack-Up Part 2: Four-Layer Boards"
url: "https://hott.shielddigitaldesign.com/techtips/pcb-stack-up-2.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 6669
---

# PCB Stack-Up

## Part 2. Four-Layer Boards

The most common four-layer board configuration is shown in Fig. 1 (power and ground planes may be reversed). It consists of four uniformly spaced layers with internal power and ground planes. The two external trace layers usually have orthogonal trace routing directions.

                \_\_\_\_\_\_\_\_\_\_\_\_\_ Sig.                 \_\_\_\_\_\_\_\_\_\_\_\_\_ Ground
**Figure 1**                 \_\_\_\_\_\_\_\_\_\_\_\_\_ Power                 \_\_\_\_\_\_\_\_\_\_\_\_\_  Sig.

Although this configuration is significantly better than a two-layer board, it has a few, less that ideal characteristics.  With respect to the list of objectives in Part 1, this stack-up only satisfies objective (1).  If the layers are equally spaced, there is a large separation between the signal layer and the current return plane.  There is also a large separation between the power and ground planes.  With a four-layer board we cannot correct both of these deficiencies at the same time; therefore, we must decide which is most important to us.  As mentioned previously, with normal PCB construction techniques there is not sufficient inter-plane capacitance between the adjacent power and ground planes to provide adequate decoupling.  The decoupling, therefore, will have to be taken care of by other means and we should opt for tight coupling between the signal and the current return plane.  The advantages of tight coupling between the signal (trace) layers and the current return planes will more than outweigh the disadvantage caused by the slight loss in interplane capacitance.

Therefore, the simplest  way to improve the EMC performance of a four-layer board is to space the signal layers as close to the planes as possible (<0.010"), and use a large core (>0.040") between the power and ground planes as shown in Fig. 2.  This has three advantages and few disadvantages.  The signal loop areas are smaller and therefore produce less differential mode radiation.  For the case of 0.005" spacing (trace layer to plane layer),  this can amount to 10 dB or more reduction in the trace loop radiation compared a stack-up with equally spaced layers.  Secondly, the tight coupling between the signal trace and the ground plane reduces the plane impedance (inductance) hence reducing the common-mode radiation from the cables connected to the board.  Thirdly, the close trace to plane coupling will decrease the crosstalk between traces.  For a fixed trace to trace spacing the crosstalk is proportional to the square of the trace height.  This is one of the simplest, least costly, and most overlooked method of reducing radiation on a four-layer PCB.  With this configuration we have satisfied both objectives (1) and (2).

                \_\_\_\_\_\_\_\_\_\_\_\_\_ Sig.                 \_\_\_\_\_\_\_\_\_\_\_\_\_ Ground

**Figure 2**                 \_\_\_\_\_\_\_\_\_\_\_\_\_ Power                 \_\_\_\_\_\_\_\_\_\_\_\_\_ Sig.

What other possibilities are there for a four-layer board stack-up?  Well, we could become a little **non-conventional** and reverse the signal layers and the plane layers in Fig. 2, producing the stack-up shown in Fig 3a.

                \_\_\_\_\_\_\_\_\_\_\_\_\_ Ground.                 \_\_\_\_\_\_\_\_\_\_\_\_\_ Sig.

**Figure 3a**                 \_\_\_\_\_\_\_\_\_\_\_\_\_ Sig.                 \_\_\_\_\_\_\_\_\_\_\_\_\_ Power

The major advantage of this stack-up is that the planes on the outer layers provide shielding to the signal traces on the inner layers.  The disadvantages are that the ground plane may be cut-up considerably with component mounting pads on a high density PCB.  This can be alleviated somewhat, by reversing the planes and placing the power plane on the component side, and the ground plane on the other side of the board.  Secondly, some people don't like to have an exposed power plane and thirdly, the buried signal layers make board rework difficult if not impossible.  This stack-up satisfies objectives (1), (2), and partially satisfies objective (4).

Two of these three problems can be alleviated with the stack-up shown in Fig. 3b, where the two outer planes are ground planes and power is routed as a trace on the signal planes.  The power should be routed as a grid, using wide traces, on the signal layers.  Two added advantages of this configuration are that; (1) the two ground planes produce a much lower ground impedance and hence less common-mode cable radiation, and (2) the two ground planes can be stitched together around the periphery of the board to enclose all the signal traces in a faraday cage.  From an EMC point of view this configuration, if properly done, is the best stack-up possible with a four-layer PCB.  Now we have satisfied objectives, (1), (2), (4), and (5) while using only a four-layer board.

                \_\_\_\_\_\_\_\_\_\_\_\_\_ Ground.                 \_\_\_\_\_\_\_\_\_\_\_\_\_ Sig./Pwr.

**Figure 3b**                 \_\_\_\_\_\_\_\_\_\_\_\_\_ Sig./Pwr.                 \_\_\_\_\_\_\_\_\_\_\_\_\_ Ground

A fourth possibility, not commonly used, but one that can be made to perform very well, is shown in Fig. 4.  This is similar to Fig  2, but with the power plane replaced with a ground plane, and power routed as a trace on the signal layers.

                \_\_\_\_\_\_\_\_\_\_\_\_\_ Sig./Pwr.                 \_\_\_\_\_\_\_\_\_\_\_\_\_ Ground

**Figure 4**                 \_\_\_\_\_\_\_\_\_\_\_\_\_ Ground                 \_\_\_\_\_\_\_\_\_\_\_\_\_ Sig./Pwr.

This stack-up overcomes the rework problem mentioned before, and still provides for the low ground impedance as a result of two ground planes.  The planes however do not provide any shielding.  This configuration satisfies objectives (1), (2), and (5) but not objectives (3) or (4).

So, as you can see there are more options available, than you might have originally thought, for four layer board stack-up.  It is possible to satisfy four of our five objectives with a four layer PCB.  The configurations of Figures 2, 3b, and 4 all can be made to perform well from an EMC point of view.
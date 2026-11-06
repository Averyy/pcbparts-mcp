# Signal Integrity

> Termination, crosstalk, differential pairs, via discontinuities, ground bounce, PCB materials, high-speed ADC layout.

## Quick Reference

- **Series termination is the default for point-to-point CMOS.** R_series = Zo - Z_driver (get Z_driver from the IBIS model, not the datasheet). Place it at the driver; simulate the allowable distance for fast edges [3].
- **Crosstalk: edge-to-edge spacing >= 3h** (3 * dielectric height to reference plane). Trace width has no effect -- only separation and height matter.
- **Unterminated 5V CMOS, 25 ohm driver, 50 ohm line, open load: 6.67V at receiver** (1.67V above VDD). A 25 ohm series resistor matches the source and removes it [3, Figs.13-16].
- **Stripline eliminates FEXT.** In stripline with symmetric dielectric, far-end crosstalk approaches zero because Cm/C ~ Lm/L. Strongly preferred for long parallel runs.
- **Ground bounce:** V_bounce = L_pkg * N * dI/dt [8, p.4]. Example with assumed values: 8 outputs sharing 10 nH, 12 mA each in 1 ns = 960 mV, beyond a 400 mV noise budget. Take L_pkg from the IBIS package model.

## Design Rules

### Termination Techniques

- **Series (default for point-to-point).** R_series = Zo - Z_driver launches V/2. At the open load it reflects and the receiver sees full V on first arrival (one-way delay); the driver end sits at V/2 until the reflection returns and is absorbed at 2x the one-way delay [3, Figs.9-11]. Load taps along the line see the V/2 step: series termination suits a single load at the end.
- **Get Z_driver from the IBIS or SPICE model VI curve,** not the datasheet (rarely published). Most SI tools calculate Z_out and recommend R_series automatically.
- **Parallel (= Zo at receiver to GND or Vtt).** Absorbs incident wave with no reflection. Draws DC current. Use when multiple loads tap the line or driver side cannot be modified. Parallel to Vtt (VDD/2) reduces DC power but requires a dedicated Vtt supply.
- **Thevenin.** Two resistors to VDD and GND, parallel combination = Zo. Creates Vtt without separate supply. DC current: VDD / (R1 + R2).
- **AC termination (series RC at receiver)** degraded a 66 MHz clock in Ritchey's test [3]; whether it works depends on the RC against edge and clock timing. Prefer series or parallel termination for clocks.
- **On-die termination (ODT)** in FPGAs and DDR eliminates external resistors and stub inductance. Programmable 50/75/100/150 ohm. Always enable when available.
- **Resistor arrays for bus termination:** Bourns CAT16 (8-pin, 4 resistors, 0.8 mm pitch, 1206-size), CTS 742C (8-pin convex). Use isolated-element (not bussed) to avoid inter-channel crosstalk.

> WARNING: Stubs act as quarter-wave resonators. A stub at frequency F causes waveform reversals and double-clocking. Keep all termination connections short. Via stubs from BGA ball to die can be long enough to cause problems at rise times < 100 ps -- include package stub length in simulation.

### Component Selection for Clocking

- **Clock buffer/fanout:** TI CDCV304 (1-to-4 LVCMOS, TSSOP-8, 0-200 MHz; at 3.3 V: 50 ps typical output skew, 56-63 fs RMS additive jitter [11, sec.5.7]) for distributing one clock without stub reflections. SiLabs Si5351A (I2C-programmable, 3 outputs, 2.5-200 MHz) for multiple frequencies from one crystal.
- **Equalization ICs when the channel's loss exceeds the PHY's equalization:** linear redrivers add CTLE gain with little delay -- TI DS125BR820 (8 channels to 12.5 Gb/s, PCIe/SAS/40G, 80 ps typical delay [12]), TI SN65LVPE502 (USB 3.0). A retimer (full CDR) resets jitter at the cost of more latency; choose from the channel loss and latency budget.
- Level shifting for mixed-voltage signals -> `misc/level-shifting.md`.

### Crosstalk

- **Near-end crosstalk (NEXT)** saturates at critical coupling length -- longer parallel runs do not increase NEXT beyond saturation. In Ritchey's curves the saturation length is ~150 mm (6 in) at 1.4 ns rise time and < 12.7 mm (0.5 in) at 100 ps; it scales with rise time and dielectric [5, Fig.3].
- **Far-end crosstalk (FEXT)** increases with length (does not saturate). In stripline with symmetric dielectric, FEXT approaches zero because inductive coupling coefficient KL ~ capacitive coupling coefficient KC. Stripline strongly preferred for long parallel runs.
- **Quantified example (stripline, ADI/Ritchey):** 0.13 mm traces at 0.13 mm spacing, 0.13 mm height above plane: ~8% backward crosstalk. Increase spacing to 0.38 mm: < 1%. Improvement comes entirely from separation, not trace width.
- **Worst-case CMOS crosstalk topology:** far ends open, near end at logic low. Backward crosstalk reflects off low-impedance driver, doubles at open receiver -- full-amplitude noise pulse.
- **Guard traces do not shield.** They work by separation only. Without ground vias at lambda/10 spacing, a guard trace is a resonant circuit that can amplify crosstalk. Use spacing instead.
- **Route orthogonally on adjacent layers** (X on one, Y on other). Capacitive coupling dominates between adjacent layers -- only safe control is orthogonal routing. PCB routers sometimes violate this constraint -- verify after autoroute.
- **Power plane edges radiate.** Keep power planes >= 1.27 mm (50 mil) from board edges. Caps grounded at a plane edge have higher impedance than interior caps.
- **Example noise budget (3.3V LVCMOS, ~400 mV margin; allocate your own):** crosstalk <= 150 mV, reflections <= 100 mV, VDD ripple <= 100 mV, ground bounce <= 50 mV.

### Differential Pairs

- **Coupling coefficient K = Zm / Zse.** Higher K (closer spacing) lowers Zdiff, improves CM rejection, but tightens manufacturing tolerance on spacing.
- **When separation exceeds max(trace width, dielectric height),** coupling becomes negligible and Zdiff approaches 2 * Zse. Loosely-coupled pairs lose the noise-rejection benefit but are easier to manufacture.
- **Tightly coupled pairs** route EM fields largely between conductors, reducing sensitivity to reference plane. Advantage for routing across plane splits (though splits should still be avoided).
- **Length match within a pair to the interface's skew budget,** converted with the stackup's delay (at 150 mm/ns, 1 mm = 6.7 ps).
- **In stripline, FEXT cancels** when dielectric above and below is symmetric (KL ~ KC). Strongly preferred for long differential runs.
- **Differential impedance targets:** 90 ohm (USB 2.0), 100 ohm (LVDS, Ethernet, USB 3.x), 120 ohm (CAN).

### Via Discontinuities

- **A 0.25 mm via through a 1.6 mm board: ~1.34 nH, 8.4 ohm at 1 GHz** [10, Vias]. Parallel vias placed close together reduce it by less than half (mutual inductance). Return vias -> `guides/pcb-layout.md`.
- **Via capacitance:** ~0.3 pF for 0.3 mm drill in 2.5 mm board.
- **Ritchey found via L and C acceptable up to ~3 Gb/s without special treatment** (experience, not a limit) [3, Vias]. Above that, simulate the via and its stub: a 2.5 mm open stub resonates near 15 GHz at 150 mm/ns (quarter wave); back-drill or use blind/buried vias when the channel model says so.
- **No impedance discontinuities at 100-200 ps from a high-speed ADC's input or clock** (ADI: 800 mil-1.5 in, 20-38 mm, on FR4) [9, rule 7]. Caps, wide pads and vias are all discontinuities. Closer elements need series resistors: ~10 ohm very close, 49.9 ohm at 100-200 ps for 50 ohm/side.
- **Thermal relief on ground vias near ADC:** avoid spokes -- they increase via inductance. Use thermal collector: copper pour pad grounded with one large via plus distributed smaller vias.
- Return via placement -> `guides/pcb-layout.md`.

### Ground Bounce (SSO)

- **Package lead inductance (typical ranges; use the IBIS package model's L_pkg):** BGA ball ~0.5-1.5 nH. QFN bond wire ~2-5 nH. TSSOP gull-wing ~5-15 nH. DIP ~15-35 nH.
- **Mitigation:** multiple VDD/GND pins near I/O, slew rate control, stagger switching times. Series resistors on simple MCU outputs -> `guides/emc.md`.
- **Decoupling for SSO:** low-inductance caps (0402/0201) at each I/O bank power pin to source transient current locally. Goal: reduce current loop through package GND pins -> `power/decoupling.md`.
- **Programmable drive strength** (e.g., 2/4/8/12/16 mA on FPGAs): use minimum that meets timing. Halving drive current halves SSO contribution.

### PCB Material Selection

- **Standard FR4** (Dk ~4.0, Df ~0.02): adequate below ~3 Gb/s on traces < 250 mm.
- **Mid-loss** (Megtron 4, IS400, Df ~0.008): 3-10 Gb/s.
- **Low-loss** (Megtron 6, IS680, Df ~0.002): > 10 Gb/s or traces > 500 mm at GHz.
- **Dk varies with frequency** -- FR4 drops to ~3.5-3.8 at multi-GHz. Use frequency-dependent Dk in simulation above 1 GHz.
- **Moisture absorption increases Dk and Df.** FR4 absorbs 0.10-0.15% by weight. Bake boards before impedance testing in humid environments.
- **Controlled impedance requires fab-specific Dk.** Generic "FR4 = 4.0" ranges 3.8-4.5 by manufacturer and resin content. Request measured Dk for your laminate and frequency band. DFM stackup -> `guides/dfm.md`.

### Eye Diagram and Channel Analysis

- **S21 (insertion loss):** < 3-6 dB at Nyquist frequency for the data rate. **S11 (return loss):** < -10 dB across signal bandwidth.
- **When to simulate (rule of thumb, no source found):** below 1 Gb/s, point-to-point with controlled impedance and termination, rules of thumb work; 1-3 Gb/s, simulate if connectors, vias or traces > 150 mm are in the path; above 3 Gb/s, extract S-parameters and use IBIS-AMI. Always simulate multi-load buses and termination placement for fast edges [3].

### High-Speed ADC Layout

- **No splits in ground plane under any signal path.** A wire, bead, or inductor in the ground return is a constriction, not a connection.
- **Do not share vias between subsystems.** Supply bypass vias are offensive to analog input and clock return paths. Assume all ADC pins are offensive to all others.
- **Copper flood grounding:** via spacing ~1.27 mm (50 mil) around periphery. Poorly grounded copper acts as antenna. Do not flood close to signal lines unless uninterrupted ground paths exist on both sides.
- **Symmetry is critical for high-speed ADC inputs.** Asymmetric copper flooding converts CM transients to differential error with non-linear charge content, directly degrading SFDR. Even LVDS outputs should see symmetrical loading.
- **ADI's 1.8V-process pipelined ADCs show artifacts to ~10 GHz regardless of sample rate;** their clock inputs have 2-3 GHz bandwidth [9]. Clock has zero noise margin (like a local oscillator).
- **Do not route signals alongside ADC clock.** Maintain 0.76-1.27 mm spacing in same layer for oversampling ADCs. For undersampling ADCs (more jitter-sensitive), use only grounded copper between clock and data.
- **Overlapping power planes create parasitic capacitors** with lowest possible impedance. Coupled noise is nearly impossible to suppress with discrete caps. Avoid overlapping unrelated power planes in ADC region.
- **Termination after the ADC gave ADI its best SFDR** when the driver, filter or transformer sat outside the 100-200 ps zone: extend the line past the ADC, change layers at the input pads [9, rule 7]. Transformer type and common-mode impedance change the compromise.
- **Filter design must account for distance to ADC.** A filter designed in isolation may produce reflections when placed at wrong distance from ADC input. Re-simulate with extracted PCB parasitics after layout.

## Common Mistakes

- **Guard traces without ground vias.** Ungrounded guard resonates, amplifying crosstalk at specific frequencies. Fix: increase spacing instead, or ground guard at lambda/10 intervals.
- **Asymmetric copper flooding near differential pairs.** Unequal capacitive loading converts CM to differential error with nonlinear charge content. Directly degrades ADC SFDR. Fix: symmetric fills on both sides, or remove all flooding within 3h.
- **Using generic Dk = 4.0 for impedance calculations.** A 0.3 Dk error shifts a 50 ohm stripline by ~2 ohm (Z ~ 1/sqrt(Dk)); together with etch and thickness tolerances it can break a +/-10% target. Fix: use the fab's measured Dk at your frequency and its stackup model.
- **Ignoring receiver input capacitance.** CMOS inputs are several pF (IBIS C_comp). At 500 MHz, 5 pF is -j64 ohm: across a 50 ohm termination the load becomes 31-j24 ohm, a ~37% reflection. Fix: include C_in in simulation.
- **Sharing ground vias between ADC subsystems.** Via-to-via coupling makes supply noise appear on analog and clock returns. Fix: dedicate separate ground vias per signal domain.
- **Routing differential pair across plane gap.** Destroys impedance match and CM rejection. Return current forced to detour, creating a large radiating loop. Fix: both traces same layer, continuous reference plane.

## Formulas

**Series termination resistor:**
**Rule of thumb:** take Z_driver from the IBIS VI curve [3]; CMOS drivers are commonly 20-40 ohm (no source found).
**Formula:** R_series = Zo - Z_driver
**Example:** Zo = 50 ohm, Z_driver = 25 ohm -> R_series = 25 ohm -> 24 ohm (E24) or 22 ohm (E12).

**Differential impedance:**
**Rule of thumb:** Zdiff = 2 * Zse * (1 - K). Tightly coupled (K ~ 0.25): Zdiff ~ 1.5 * Zse. Loosely coupled (K < 0.05): Zdiff ~ 2 * Zse.
**Formula:** Zdiff = 2 * (Zse - Zm), where Zm = K * Zse
**Example:** Zse = 55 ohm, K = 0.1 -> Zdiff = 2 * (55 - 5.5) = 99 ohm [6].

**Ground bounce (SSO):**
**Rule of thumb:** compare N * L_pkg * dI/dt (shared return inductance) with the receiver noise budget left [8, p.4]; reduce with more ground pins, slew-rate control or lower drive.
**Formula:** V_bounce = L_pkg * N * (dI/dt)
**Example:** 4 outputs, 10 mA each, 2 ns rise, shared 3 nH (assumed): V_bounce = 3e-9 * 4 * 10e-3 / 2e-9 = 60 mV.

**Knee frequency:**
**Rule of thumb:** 1 ns rise time (10-90%) -> ~500 MHz of significant content [4]. 100 ps -> 5 GHz.
**Formula:** f_knee = 0.5 / t_rise. (0.35 / t_rise is a single-pole -3 dB bandwidth, a lower figure; neither is a channel cutoff [2].)
**Example:** 500 ps rise time -> f_knee = 1 GHz.

## Sources

### Related Rules

- `misc/level-shifting.md` -- Level shifting for mixed-voltage signals
- `guides/pcb-layout.md` -- Return via placement, stackup, microstrip/stripline design
- `guides/emc.md` -- Series resistors on digital I/O, ground bounce mitigation
- `power/decoupling.md` -- Low-inductance decoupling for SSO transient current
- `guides/dfm.md` -- Controlled impedance stackup, fab-specific Dk

### References

1. Altium -- The Ultimate Introduction to High-Speed Signal Integrity: https://resources.altium.com/p/introduction-to-high-speed-signal-integrity-for-pcb-designers
2. Altium -- Why is There a Transmission Line Critical Length?: https://resources.altium.com/p/why-there-transmission-line-critical-length
3. Altium/Lee Ritchey -- Transmission Line Termination Techniques: https://resources.altium.com/p/transmission-lines-and-terminations-in-high-speed-design
4. Altium/Phil's Lab -- High-Speed PCB Design Tips and Guidelines: https://resources.altium.com/p/high-speed-pcb-design-tips
5. Altium/Lee Ritchey -- Crosstalk or Coupling in High-Speed Design: https://resources.altium.com/p/crosstalk-or-coupling
6. Sierra Circuits -- Differential Pairs in PCB Transmission Lines: https://www.protoexpress.com/blog/differential-pairs-in-pcb-transmission-lines/
7. Sierra Circuits -- Handling Crosstalk in High-Speed PCB Designs: https://www.protoexpress.com/blog/crosstalk-high-speed-pcb-design/
8. Intel -- Basic Principles of Signal Integrity: https://cdrdv2-public.intel.com/650327/wp_sgnlntgry.pdf
9. ADI -- A Short Course in PCB Layout for High-Speed ADCs: https://www.analog.com/en/resources/technical-articles/a-short-course-in-pcb-layout-for-high-speed-adcs.html
10. ADI -- Avoid PC-Layout "Gotchas" in ISM-RF Products: https://www.analog.com/en/resources/technical-articles/avoid-pclayout-gotchas-in-ismrf-products.html
11. TI CDCV304 datasheet (SCAS643I): https://www.ti.com/lit/ds/symlink/cdcv304.pdf
12. TI DS125BR820 datasheet (SNLS491B), 8-Channel Linear Repeater: https://www.ti.com/lit/ds/symlink/ds125br820.pdf

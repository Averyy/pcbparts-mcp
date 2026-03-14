# Signal Integrity

> Termination, crosstalk, differential pairs, via discontinuities, ground bounce, PCB materials, high-speed ADC layout.

## Quick Reference

- **Series termination is the default for point-to-point CMOS.** R_series = Zo - Z_driver (get Z_driver from IBIS model, not datasheet). Place within 6 mm of driver.
- **Crosstalk: edge-to-edge spacing >= 3h** (3 * dielectric height to reference plane). Trace width has no effect -- only separation and height matter.
- **Unterminated 5V CMOS on 50 ohm line: 6.67V at receiver** (1.67V above VDD). 25 ohm series resistor eliminates overshoot entirely.
- **Stripline eliminates FEXT.** In stripline with symmetric dielectric, far-end crosstalk approaches zero because Cm/C ~ Lm/L. Strongly preferred for long parallel runs.
- **Ground bounce:** V_bounce = L_pkg * N * dI/dt. 8 LVCMOS outputs in TSSOP (10 nH) switching 12 mA in 1 ns = 960 mV -- exceeds 400 mV noise margin.

## Design Rules

### Termination Techniques

- **Series (default for point-to-point).** R_series = Zo - Z_driver. Signal reaches half amplitude at load, reflects, doubles to full level on return. Receiver sees signal delayed by 2 * one-way propagation. Place resistor within 6 mm of driver. Allowable distance decreases with faster rise time -- simulate if < 500 ps.
- **Get Z_driver from the IBIS or SPICE model VI curve,** not the datasheet (rarely published). Most SI tools calculate Z_out and recommend R_series automatically.
- **Parallel (= Zo at receiver to GND or Vtt).** Absorbs incident wave with no reflection. Draws DC current. Use when multiple loads tap the line or driver side cannot be modified. Parallel to Vtt (VDD/2) reduces DC power but requires a dedicated Vtt supply.
- **Thevenin.** Two resistors to VDD and GND, parallel combination = Zo. Creates Vtt without separate supply. DC current: VDD / (R1 + R2).
- **AC termination (series RC at receiver) degrades at modern clock rates** -- visible at 66 MHz in testing. Not recommended for new designs.
- **On-die termination (ODT)** in FPGAs and DDR eliminates external resistors and stub inductance. Programmable 50/75/100/150 ohm. Always enable when available.
- **Resistor arrays for bus termination:** Bourns CAT16 (8-pin, 4 resistors, 0.8 mm pitch, 1206-size), CTS 742C (8-pin convex). Use isolated-element (not bussed) to avoid inter-channel crosstalk.

> WARNING: Stubs act as quarter-wave resonators. A stub at frequency F causes waveform reversals and double-clocking. Keep all termination connections short. Via stubs from BGA ball to die can be long enough to cause problems at rise times < 100 ps -- include package stub length in simulation.

### Component Selection for Clocking

- **Clock buffer/fanout:** TI CDCV304 (1-to-4 LVCMOS, TSSOP-8, < 50 ps additive jitter) for distributing one clock without stub reflections. SiLabs Si5351A (I2C-programmable, 3 outputs, 2.5-200 MHz) for multiple frequencies from one crystal.
- **Pre-emphasis/equalization ICs for channels > 250 mm at > 3 Gb/s:** Retimers (full CDR -- TI DS125BR820 for 8-channel PCIe) when channel has connectors or exceeds PHY equalization range. Redrivers (TI SN65LVPE502 for USB 3.0) for shorter reach where latency matters -- < 1 ns vs 4-8 ns for retimers.
- Level shifting for mixed-voltage signals -> `misc/level-shifting.md`.

### Crosstalk

- **Near-end crosstalk (NEXT)** saturates at critical coupling length -- longer parallel runs do not increase NEXT beyond saturation. Critical coupling length: ~150 mm at 1.4 ns rise time. At 100 ps: < 12 mm.
- **Far-end crosstalk (FEXT)** increases with length (does not saturate). In stripline with symmetric dielectric, FEXT approaches zero because inductive coupling coefficient KL ~ capacitive coupling coefficient KC. Stripline strongly preferred for long parallel runs.
- **Quantified example (stripline, ADI/Ritchey):** 0.13 mm traces at 0.13 mm spacing, 0.13 mm height above plane: ~8% backward crosstalk. Increase spacing to 0.38 mm: < 1%. Improvement comes entirely from separation, not trace width.
- **Worst-case CMOS crosstalk topology:** far ends open, near end at logic low. Backward crosstalk reflects off low-impedance driver, doubles at open receiver -- full-amplitude noise pulse.
- **Guard traces do not shield.** They work by separation only. Without ground vias at lambda/10 spacing, a guard trace is a resonant circuit that can amplify crosstalk. Use spacing instead.
- **Route orthogonally on adjacent layers** (X on one, Y on other). Capacitive coupling dominates between adjacent layers -- only safe control is orthogonal routing. PCB routers sometimes violate this constraint -- verify after autoroute.
- **Power plane edges radiate.** Keep power planes >= 1.27 mm (50 mil) from board edges. Caps grounded at a plane edge have higher impedance than interior caps.
- **Noise budget (3.3V LVCMOS, ~400 mV margin):** crosstalk <= 150 mV, reflections <= 100 mV, VDD ripple <= 100 mV, ground bounce <= 50 mV.

### Differential Pairs

- **Coupling coefficient K = Zm / Zse.** Higher K (closer spacing) lowers Zdiff, improves CM rejection, but tightens manufacturing tolerance on spacing.
- **When separation exceeds max(trace width, dielectric height),** coupling becomes negligible and Zdiff approaches 2 * Zse. Loosely-coupled pairs lose the noise-rejection benefit but are easier to manufacture.
- **Tightly coupled pairs** route EM fields largely between conductors, reducing sensitivity to reference plane. Advantage for routing across plane splits (though splits should still be avoided).
- **Length match within a pair:** < 5% of rise_time * propagation_speed. Example: 500 ps rise time at 150 mm/ns -> match within 3.75 mm.
- **In stripline, FEXT cancels** when dielectric above and below is symmetric (KL ~ KC). Strongly preferred for long differential runs.
- **Differential impedance targets:** 90 ohm (USB 2.0), 100 ohm (LVDS, Ethernet, USB 3.x), 120 ohm (CAN).

### Via Discontinuities

- **Each 0.25 mm via in a 16 mm board: ~1 nH, presenting ~6.3 ohm at 1 GHz.** In a standard 1.6 mm board, via inductance is ~0.5-1.5 nH depending on pad/antipad geometry. Two vias in parallel halve inductance. Use 2-4 ground vias per signal via on critical nets.
- **Via capacitance:** ~0.3 pF for 0.3 mm drill in 2.5 mm board.
- **Combined L and C acceptable up to ~3 Gb/s** without special treatment. Via stubs: 2.5 mm stub resonates at ~15 GHz. Back-drill or use blind/buried vias above ~3 Gb/s.
- **No impedance discontinuities within 20-38 mm of high-speed ADC inputs/clocks.** Caps, wide pads, and vias are all discontinuities. If closer, add series resistors (10 ohm at ADC, 50 ohm at 20-38 mm for 50 ohm lines).
- **Thermal relief on ground vias near ADC:** avoid spokes -- they increase via inductance. Use thermal collector: copper pour pad grounded with one large via plus distributed smaller vias.
- Return via placement -> `guides/pcb-layout.md`.

### Ground Bounce (SSO)

- **Package lead inductance:** BGA ball ~0.5-1.5 nH. QFN bond wire ~2-5 nH. TSSOP gull-wing ~5-15 nH. DIP ~15-35 nH.
- **Example:** 8 LVCMOS outputs switching 12 mA in 1 ns through TSSOP lead (10 nH): V_bounce = 10e-9 * 8 * 12e-3 / 1e-9 = 960 mV. Exceeds 400 mV noise margin.
- **Mitigation:** multiple VDD/GND pins near I/O, slew rate control, stagger switching times. Series resistors (50-100 ohm) on digital outputs -> `guides/emc.md`.
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

- **When to use IBIS simulation:** (a) trace > 50 mm with rise time < 500 ps, (b) multiple loads (bus topology), (c) board-to-board connectors in path. Short point-to-point with series termination: rules of thumb suffice.
- **S21 (insertion loss):** < 3-6 dB at Nyquist frequency for the data rate. **S11 (return loss):** < -10 dB across signal bandwidth.
- **Decision rule:** below 1 Gb/s with controlled impedance and proper termination, rules of thumb work. Above 3 Gb/s, extract S-parameters and simulate with IBIS-AMI. 1-3 Gb/s: simulate if connectors, vias, or traces > 150 mm.

### High-Speed ADC Layout

- **No splits in ground plane under any signal path.** A wire, bead, or inductor in the ground return is a constriction, not a connection.
- **Do not share vias between subsystems.** Supply bypass vias are offensive to analog input and clock return paths. Assume all ADC pins are offensive to all others.
- **Copper flood grounding:** via spacing ~1.27 mm (50 mil) around periphery. Poorly grounded copper acts as antenna. Do not flood close to signal lines unless uninterrupted ground paths exist on both sides.
- **Symmetry is critical for high-speed ADC inputs.** Asymmetric copper flooding converts CM transients to differential error with non-linear charge content, directly degrading SFDR. Even LVDS outputs should see symmetrical loading.
- **Clock path sensitivity extends to ~10 GHz bandwidth** on modern ADCs regardless of sample rate. Clock has zero noise margin (like a local oscillator).
- **Do not route signals alongside ADC clock.** Maintain 0.76-1.27 mm spacing in same layer for oversampling ADCs. For undersampling ADCs (more jitter-sensitive), use only grounded copper between clock and data.
- **Overlapping power planes create parasitic capacitors** with lowest possible impedance. Coupled noise is nearly impossible to suppress with discrete caps. Avoid overlapping unrelated power planes in ADC region.
- **Termination after ADC gives better SFDR** on undersampling ADCs. Requires layer change near input pads. If the driver/filter/transformer is outside the 20-38 mm critical distance, extend the transmission line and place end termination past the ADC.
- **Filter design must account for distance to ADC.** A filter designed in isolation may produce reflections when placed at wrong distance from ADC input. Re-simulate with extracted PCB parasitics after layout.

## Common Mistakes

- **Guard traces without ground vias.** Ungrounded guard resonates, amplifying crosstalk at specific frequencies. Fix: increase spacing instead, or ground guard at lambda/10 intervals.
- **Ignoring via stubs at multi-Gb/s.** 2.5 mm stub resonates at ~15 GHz -- within passband for 10 Gb/s signaling. Fix: back-drill or blind/buried vias above ~3 Gb/s.
- **Asymmetric copper flooding near differential pairs.** Unequal capacitive loading converts CM to differential error with nonlinear charge content. Directly degrades ADC SFDR. Fix: symmetric fills on both sides, or remove all flooding within 3h.
- **Using generic Dk = 4.0 for impedance calculations.** Actual FR4 ranges 3.8-4.5 by manufacturer. Dk error of 0.3 shifts 50-ohm impedance by ~4 ohm (8%). Fix: request fab's measured Dk at your target frequency.
- **Ignoring receiver input capacitance.** CMOS inputs are 2-8 pF. At 500 MHz, 5 pF adds ~60 ohm in parallel to 50 ohm line, shifting load to ~27 ohm -> 30% undershoot. Fix: include C_in in simulation.
- **Placing termination before ADC instead of after.** Termination after ADC (past the bond wire) gives better SFDR on undersampling ADCs because the high CM impedance of an unterminated transmission line transformer reflects clock transients back. Fix: extend line, terminate after ADC with layer change at input pads.
- **Sharing ground vias between ADC subsystems.** Via-to-via coupling makes supply noise appear on analog and clock returns. Fix: dedicate separate ground vias per signal domain.
- **AC termination at modern clock rates.** Capacitor impedance degrades termination above ~66 MHz. Fix: use series or parallel termination.
- **Routing differential pair across plane gap.** Destroys impedance match and CM rejection. Return current forced to detour, creating a large radiating loop. Fix: both traces same layer, continuous reference plane.

## Formulas

**Series termination resistor:**
**Rule of thumb:** Most CMOS drivers: 20-40 ohm output impedance. Series resistor: 10-33 ohm typical for 50 ohm traces.
**Formula:** R_series = Zo - Z_driver
**Example:** Zo = 50 ohm, Z_driver = 25 ohm -> R_series = 25 ohm -> use 22 ohm (nearest E24).

**Differential impedance:**
**Rule of thumb:** Zdiff = 2 * Zse * (1 - K). Tightly coupled (K ~ 0.25): Zdiff ~ 1.5 * Zse. Loosely coupled (K < 0.05): Zdiff ~ 2 * Zse.
**Formula:** Zdiff = 2 * (Zse - Zm), where Zm = K * Zse
**Example:** Zse = 55 ohm, K = 0.1 -> Zdiff = 2 * (55 - 5.5) = 99 ohm (meets 100 ohm target).

**Ground bounce (SSO):**
**Rule of thumb:** > 8 outputs switching simultaneously in TSSOP at 3.3V LVCMOS will exceed noise margin. Use BGA or add slew rate control.
**Formula:** V_bounce = L_pkg * N * (dI/dt)
**Example:** 4 outputs, 10 mA each, 2 ns rise, QFN (3 nH): V_bounce = 3e-9 * 4 * 10e-3 / 2e-9 = 60 mV (safe for 400 mV margin).

**Knee frequency:**
**Rule of thumb:** 1 ns rise time = 350 MHz bandwidth. 100 ps = 3.5 GHz.
**Formula:** f_knee = 0.35 / t_rise
**Example:** 500 ps rise time -> f_knee = 700 MHz. Trace, termination, and decoupling must handle 700 MHz.

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

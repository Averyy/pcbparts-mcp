# Decoupling

> Capacitor selection, placement, and via design for per-IC power integrity.

## Quick Reference

- **100nF X7R 0402 per 2 VDD pins, within 2mm, via at pad.** Connection inductance matters more than capacitance value -- a 1.5cm trace shifts a 1.9GHz SRF to 314MHz.
- **One cap value for all HF decoupling.** Mixing values creates LC anti-resonance peaks (10-40dB) between individual SRFs. ESL depends on package, not capacitance -- a 1206 measures ~1200pH whether 100pF or 10uF.
- **X7R over C0G for decoupling.** C0G's high Q produces sharp anti-resonance peaks (+/-40dB). X7R's dielectric loss naturally damps them. NP0 groups measured with >40dB negative deflections vs X7R at same values.
- **ESL by package (Kyocera AVX):** 0603 ~870pH, 0805 ~1050pH, 1206 ~1200pH, 1210 ~980pH. Low-inductance 0612: 610pH. 0508: 600pH.
- **15uF+ bulk cap per ~10 power pins.** Recharges HF ceramics but too inductive to replace them.

## Design Rules

### Placement and Via Design

- **Via at pad, never via-then-trace.** Do NOT route BGA balls to the cap before going to the plane -- adds trace length to the entire PDN path. LearnEMC: "Never use traces! If there is no room for the via adjacent to the pad, then move the whole capacitor."
- **Mount caps on PCB face closest to power/ground plane pair.** Connection inductance is nearly proportional to cap-to-plane distance.
- **2+ vias per cap pad, arranged 90 degrees apart.** Four vias cut connection inductance nearly in half vs two. Clustered vias develop mutual inductance -- spreading 90 degrees gives up to 4dB improvement in insertion loss. Best: 3 vias per GND pad at 90 degrees, max 0.3mm from pad edge.
- **Blind/buried vias: 15:1 inductance reduction.** One blind via (d=0.15mm, h=0.15mm) = ~0.07nH vs ~1.1nH for a 0.4mm through-via in 1.5mm board. Height is the dominant factor -- blind vias matter more than microvias.
- **0402 MLCC + 3 vias per pad is optimal above SRF.** 0805 with 1 via is significantly worse -- via inductance dominates. Wurth measured >40dB difference between optimal 0402 layout and poor 0805 layout.
- **Never share a via between a decoupling cap and an active device.** Common impedance couples noise between them.
- **Orient ferrite + caps at 90 degrees.** Parallel arrangement causes parasitic inductive and capacitive coupling that degrades filter insertion loss.
- **Widely-spaced planes (>0.5mm): location matters.** Place caps near the pin connecting to the most distant plane. On 4-layer (L2=GND, L3=PWR), place caps near GND pins since GND plane is closer to surface components.

### BGA Strategy

- **One 0.1uF cap per 2 power pins in 0402 or 0201.** For fine-pitch (<1mm), skip every other via row and share vias between 2 power/ground balls. Sharing >2 balls per via adds too much inductance.
- **Place caps inside BGA footprint, not outside.** Distance to caps when placed outside the footprint introduces far more inductance than via-sharing costs. 0402s fit inside 0.8mm pitch; 0201s fit rotated 90 degrees.
- **Same-side mounting.** Opposite-side mounting adds 2x via height to the PDN loop. Above SRF, bottom-side 0402s are no better than top-side 0805s without blind vias.

### Stackup for Decoupling

- **4-layer (L1 sig, L2 GND, L3 PWR, L4 sig):** Caps on L1 face connect to L2 ground through a short via. L2-L3 spacing provides interplane capacitance above 250MHz.
- **Interplane capacitance:** ~16pF/cm^2 for FR4 (er=4.2) at 0.25mm spacing. Small but effective at 250MHz+ where discrete caps are inductive. Consider paired power/ground planes within 0.25mm for high-speed interfaces (PCIe, SATA, USB).

### Regulator I/O Caps

- **Input ceramics reduce ripple voltage -- bulk electrolytics cannot.** Target <= 75mVpp input ripple. Adding ceramics to a 35 mohm aluminum bulk cap reduced ripple current from 2.9A to 628mA and power dissipation from 294mW to 13.8mW (21:1 reduction).
- **Output caps are part of the feedback loop.** Very low ESR output networks can under-damp the control loop. Some regulators specify minimum output impedance (e.g. >4 mohm below 20kHz, >2 mohm 20-200kHz). More is not always better.
- **Some LDOs require minimum ESR (10-100 mohm) for stability.** Pure MLCC output (ESR < 5 mohm) can cause oscillation on regulators designed for tantalum. Stability details -> `power/ldo.md`.
- **Polymer aluminum: 10x lower ESR than wet aluminum, but limited to <= 25V.** Use for bulk >100uF where ceramic DC bias derating makes MLCC impractical.

> WARNING: Do not place so much bulk capacitance that the startup ramp violates power sequencing or trips regulator OCP. At ~1V/ms startup slew, 1000uF draws 1A of inrush on top of load current. Check regulator max output cap spec.

### Analog Supply Filtering

- **Ferrite bead pi-filter for PLL/ADC/analog supplies:** cap-bead-cap. The IC-side cap is mandatory. If space is tight, delete the input cap, never the IC-side cap -- without local storage, the bead's high-frequency resistance starves the IC of peak current.
- **DON'T use ferrite beads on digital core power.** Digital logic draws high-peak transient current on every clock edge. The bead blocks this, causing voltage droop and logic errors. Even with downstream caps, cap impedance above ~200MHz cannot supply enough peak power. Ferrite also blocks interplane capacitance benefits.

> WARNING: Ferrite bead + downstream cap = LC resonant circuit. If resonance falls in the bead's inductive region (0.1-10MHz), you get 10-15dB gain instead of attenuation -- often right at the switching frequency. Damping guidance -> `guides/passives.md`.

### DC Bias Aging

- **DC bias aging is much worse than normal aging.** Vishay measured 0603 X7R 100nF 50V caps at 40% rated voltage: competitors lost >20% capacitance after 1000 hours, with average loss rates >7% per decade hour -- far beyond the 1-3% per decade specified for normal aging.
- **At 100% rated voltage, drift is faster still.** All tested parts showed accelerated loss. Recovery after bias removal takes 50-1000 hours at room temperature for competing parts; thermal de-aging at 150C for 1 hour restores 100%.
- **Normal aging rate: X7R/X5R -2.5% per decade hour, Y5V -7% per decade hour.** After soldering (de-aging event), capacitance may read high for ~10 hours. Allow 1000 hours for capacitance to stabilize to spec.
- Cap DC bias derating, dielectric selection -> `guides/passives.md`.

## Common Mistakes

- **Sharing decoupling vias between BGA power balls and cap pads.** Routing two power balls through the same via to reach a cap saves space but creates common impedance coupling -- high-frequency switching noise from one power domain injects directly into the other. On a 0.8mm pitch BGA with mixed 1.2V core and 3.3V I/O, this can inject 50-100mV spikes on the 1.2V rail from 3.3V I/O toggling. Fix: dedicate vias per power domain; share only ground vias (which are equipotential by design).
- **Unnecessary trace stubs to cap pads.** 1-2mm of trace adds ~0.5nH of additional ESL per stub. Wurth measured >40dB degradation from traces + shared via + parallel arrangement vs proper layout. If the via won't fit at the pad, move the entire cap.
- **Using C0G/NP0 in parallel cap groups without a ferrite.** C0G's high Q creates sharp anti-resonance peaks between caps of different values. Wurth measured negative deflections >40dB at resonance. Always include at least one X7R in any cap group, or use a ferrite bead to provide broadband damping.
- **Excessive output capacitance tripping OCP at startup.** The inrush is I = C * dV/dt on top of load current. Check regulator max output cap spec -- this is a hard limit, not a recommendation.
- **Ignoring interplane capacitance on multilayer boards.** Closely-spaced planes (<0.5mm) make all surface caps "global" -- location is not critical, connection inductance is. Widely-spaced planes (>0.5mm) make caps "local" -- location near the IC becomes critical.

## Formulas

**Via inductance:**
**Rule of thumb:** Standard 0.4mm through-via in 1.5mm board = ~1.1nH.
**Formula:** L(nH) = (h/5) * (1 + ln(4h/d))
  - h = via height (mm), d = via inner diameter (mm)
**Example:** h = 1.5mm, d = 0.4mm -> L = 0.3 * (1 + ln(15)) = 0.3 * 3.71 = 1.1nH

**Self-resonant frequency:**
**Rule of thumb:** 100nF/0603 resonates at ~17MHz.
**Formula:** f_res = 1 / (2 * pi * sqrt(ESL * C))
**Example:** C = 100nF, ESL = 870pH -> f = 1 / (6.28 * sqrt(870e-12 * 100e-9)) = 17.1MHz

**Input ripple capacitance (buck):**
**Rule of thumb:** Target <= 75mVpp input ripple.
**Formula:** C_min = (I_out * dc * (1 - dc)) / (f_sw * V_ripple)
  - dc = V_out / (V_in * eta)
**Example:** 12V->3.3V, 10A, 90% eff, 333kHz -> dc = 0.306, C_min = (10 * 0.306 * 0.694) / (333e3 * 0.075) = 85uF (effective at operating voltage, not nominal)

**Bulk cap for transient loads:**
**Rule of thumb:** Size bulk caps when regulator inductor cannot slew fast enough.
**Formula:** C_bulk = (1.21 * I_transient^2 * L_filter) / delta_V^2
  - 1.21 constant accounts for inductor current ramp shape
**Example:** 2.8A step, 560nH inductor, 100mV dip limit -> C_bulk = (1.21 * 7.84 * 560e-9) / 0.01 = 531uF minimum

**Connection inductance estimation:**
**Rule of thumb:** Cap pads ~0.5-2nH, each through-via ~0.5-1.1nH, traces ~6-12nH/cm.
**Formula:** L_total = L_pads + L_vias + L_traces (sum all elements in the loop)
**Example:** 0402 cap (0.8nH ESL) + 2 vias (1nH each) + 2mm trace (1.5nH) = 4.3nH total

## Sources

### Related Rules

- `power/ldo.md` -- Output cap ESR stability requirements for LDOs fed by decoupled rails
- `guides/passives.md` -- Ferrite bead damping guidance, cap DC bias derating, dielectric selection

### References

1. TI SPRABV2 -- BGA Decoupling Best Practices: https://www.ti.com/lit/an/sprabv2/sprabv2.pdf
2. TI SLOA069 -- How (Not) to Decouple High-Speed Op Amps: https://www.ti.com/lit/an/sloa069/sloa069.pdf
3. Murata -- Voltage Characteristics of Ceramic Caps: https://article.murata.com/en-us/article/voltage-characteristics-of-electrostatic-capacitance
4. TI SLTA055 -- I/O Capacitor Selection for Regulators: https://www.ti.com/lit/an/slta055/slta055.pdf
5. ADI MT-101 -- Decoupling Techniques: https://www.analog.com/media/en/training-seminars/tutorials/MT-101.pdf
6. Wurth ANP098 -- Layout/Via Effects on Filter Capacitors: https://www.we-online.com/components/media/o695199v410%20ANP098a%20EN.pdf
7. LearnEMC -- PCB Decoupling Guidelines: https://learnemc.com/circuit-board-decoupling-information
8. Kyocera AVX -- Parasitic Inductance of Multilayer Ceramic Capacitors: https://kyocera-avx.com/docs/techinfo/CeramicCapacitors/parasitc.pdf
9. Vishay -- Time-Dependent Capacitance Drift of X7R MLCCs Under DC Bias: https://www.vishay.com/docs/45263/timedepcapdrix7rmlccexptoconstdcbiasvolt.pdf
10. Johanson Dielectrics -- Ceramic Capacitor Aging Made Simple: https://www.johansondielectrics.com/tech-notes/ceramic-capacitor-aging-made-simple/
11. Espressif ESP32-S3 HW Design Guidelines -- PCB Layout (Power Section): https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html

# DFM

> Fabrication tolerances, IPC class differences, tombstoning prevention, panelization, and assembly constraints.

## Quick Reference

- **Fab limits belong to one fab and service: check your fab's capability page.** JLCPCB rigid FR-4: 0.10 mm (4 mil) trace/space on 1-2 layers, 0.15 mm drill, 0.30 / 0.45 mm hole/pad vias without surcharge (table below). PCBWay prototype: 0.10 mm minimum, > 0.15 mm (6 mil) recommended to save cost [2].
- **Get the fab's stackup before routing controlled impedance.** JLCPCB's 1.6 mm 4-layer default is JLC04161H-7628 (0.2104 mm prepreg); JLC04161H-3313 is 0.0994 mm. Calculate widths for the stackup you order [10].
- **JLCPCB assembly:** Economic PCBA is single-sided, 0402 smallest, 0.4 mm IC pitch, reflow 255 +/- 5 C (not adjustable: check each part's rated peak, time and MSL against 260 C), needs no fiducials or rails. Standard PCBA is double-sided, to 01005 and 0.35 mm pitch, reflow 240 +/- 5 C, and needs both [15]: >= 5 mm rails, 3-4 fiducials of 1 mm copper in a 2 mm mask opening, >= 3.35 mm from the board edge [16].
- **Tombstoning on two-terminal passives: heat both pads alike** (Eurocircuits): equal-width feeds for >= 0.25 mm, hole edges >= 0.25 mm from the pad, no legend under 0603 and smaller [6].

## Design Rules

### Fab Capability (other fabs)

Each value is one fab's published limit for the named service; check your own fab's page.

| Parameter | Value | Fab / service |
|-----------|-------|---------------|
| Min trace/space | 0.10 mm (4 mil); > 0.15 mm (6 mil) recommended for cost | PCBWay prototype [2] |
| Min drill | 0.20 mm (8 mil) CNC | PCBWay [2] |
| Min drill | 0.254 mm (2/4-layer), 0.2032 mm (6-layer) | OSH Park [3] |
| Finished-hole tolerance | +/-0.08 mm | PCBWay CNC [2] |
| Annular ring | 0.127 mm (2-layer), 0.1016 mm (4/6-layer) | OSH Park [3] |
| Board thickness tolerance | +/-10% (>= 1 mm), +/-0.1 mm (< 1 mm) | PCBWay [2] |
| Outline tolerance | +/-0.2 mm CNC, +/-0.5 mm V-score | PCBWay [2] |

- **Via aspect ratio:** confirm the ordered process's limit and whether it divides by drilled or finished diameter. Sierra's IPC tables reach 10:1 for particular drilled geometries [5]; no universal ceiling is sourced here.
- **2 oz outer copper raises minimum trace/space:** JLCPCB rigid FR-4 at 2 oz needs >= 0.16 mm on 2-layer, >= 0.15 mm on multilayer [9, 11].
- **Blind/buried vias require sequential lamination;** OSH Park's 4/6-layer services exclude them. Confirm the via technology with the fab before designing [3].
- **Minimum dielectric 0.065 mm (2.56 mil) after lamination for Class 2/3,** per Sierra's IPC-6012 Rev F summary; lowered to allow HDI laser drilling [5].
- **Drill-to-copper clearance:** use the fab's layer-specific hole-to-copper rules and its drilled/finished-hole definitions; annular-ring-to-copper clearance is a different quantity [4, 5, 9].

### JLCPCB

Rigid FR-4 through-hole limits in mm, from JLCPCB's capabilities, copper-weight and impedance pages (read 2026-11-03) [9, 11]. HDI, flex and metal-core services differ.

| Parameter | JLCPCB minimum | Notes |
|-----------|----------------|-------|
| Trace/space, 1 oz outer | 0.10 / 0.10 (1-2 layers), 0.09 / 0.09 (4+) | Inner layers (0.5 or 1 oz): 0.09 / 0.09. 2 oz: 0.16 (2-layer), 0.15 (multilayer) |
| Mechanical drill | 0.15 (2+ layers), 0.30 (1 layer) | 0.10 option: board <= 1.0 mm, ENIG/OSP only |
| Via hole / pad (2+ layers) | 0.15 / 0.25 | Pad = hole + 0.10 minimum, + 0.15 preferred |
| PTH annular ring, 1 oz | 0.18 (2 layers), 0.15 (4+) | Recommended >= 0.25 (2 layers), >= 0.20 (4+) |
| NPTH / castellated hole | 0.50 / 0.50 | Castellated boards >= 10x10 mm and >= 0.6 mm thick. Component PTH: >= 0.50 recommended (mask/tin blocks smaller) |
| Via hole-to-hole / pad hole-to-hole | 0.20 / 0.45 | |
| Via hole / PTH / NPTH to track | 0.20 / 0.28 / 0.20 | PTH-to-track 0.35 recommended |
| Copper to routed edge / V-cut | 0.20 / 0.40 | V-cut: straight lines, zero gap, board >= 0.6 mm |
| Silkscreen stroke / text height | 0.15 / 1.0 | Pad-to-silkscreen 0.15 |
| Pad spacing that keeps a mask dam | 0.10 | Black/white mask 0.13; 2 oz copper 0.20 [13] |

- **No-surcharge default at JLCPCB: 0.30 mm hole / 0.45 mm pad vias.** 0.10 and 0.15 mm holes always cost extra, and 0.20-0.25 mm holes do with a pad under 0.45 mm. 3.0-3.5 mil trace/space adds 20% on 4-8 layers (30% at 10+) [9, 12].
- **Solder mask expansion: 0.05 mm per side on 1-2 layer JLCPCB boards.** The capabilities page allows 1:1 openings since its June 2025 LDI upgrade, but JLCPCB's September 2026 mask article still gives +0.05 mm for standard 1-2 layer boards and 1:1 for multilayer. Keep >= 0.09 mm from a mask opening to a neighbouring trace either way [9, 13].

| 1.6 mm 4-layer, top to bottom [10] | JLC04161H-7628 (default) | JLC04161H-3313 |
|-------------------------------|--------------------------|----------------|
| L1, L4 copper | 0.035 mm (1 oz) | 0.035 mm (1 oz) |
| L1-L2 and L3-L4 prepreg | 7628, 0.2104 mm, Er 4.4 | 3313, 0.0994 mm, Er 4.1 |
| L2, L3 copper | 0.0152 mm (0.5 oz) | 0.0152 mm (0.5 oz) |
| Core | 1.065 mm, Er 4.6 | 1.265 mm, Er 4.6 |

- **Pick the stackup before routing controlled-impedance traces.** An order without an impedance requirement gets JLC04161H-7628; 3313's prepreg is half as thick, so the same 50 ohm microstrip or 90 ohm USB pair is much narrower. Size widths with JLCPCB's impedance calculator for the stackup you order. Other prepregs it lists: 1080 (Er 3.91), 2116 (Er 4.16); 3313 replaced 2313 with the same thickness and Er [10].

### IPC Classes

Sierra Circuits' summary of IPC-6012 and IPC-A-610 [5]:

| Feature | Class 2 | Class 3 |
|---------|---------|---------|
| Annular ring breakout | Up to 90 degrees, subject to spacing and conductor-junction criteria | None. External ring >= 0.05 mm (2 mil), internal >= 0.025 mm (1 mil); isolated 20% external reductions allowed |
| Barrel fill (PTH) | >= 75% (exceptions below) | >= 75% |
| PTH copper voids | One per hole, in <= 5% of holes | None |
| Min PTH plating | 0.020 mm (0.8 mil) | 0.025 mm (1 mil) |

- **Class 2 is the default** for commercial and industrial.
- **Class 2 barrel fill exceptions (IPC-A-610 rev H):** the lesser of 50% depth or 1.2 mm, with the lead visible on the source side and surrounding PTHs compliant; parts with < 14 leads also need plane-connected barrels and 360-degree wetting on the destination side.
- **PTH drill sizing for paste-in-hole (Sierra):** hole 0.38 mm (15 mil) larger than the lead, 0.19 mm (7.5 mil) per side; check the finished-hole tolerance and solder process.
- **Pad sizing:** `Pad = finished_hole + 2 * min_annular_ring + fab_allowance`. Sierra ties an allowance up to 0.2 mm (8 mil) to IPC-2221 producibility level C; agree it with the fab.
- **IST coupons (Sierra's example):** D coupons through 6 reflow simulations + 100 thermal shocks; a 10% resistance change fails. Agree the method and cycles with the fab.
- **Specify the surface finish on the fab drawing.** Sierra says IPC-6012 Rev F defaults to ENIG; not confirmed against the standard itself.

### Panelization

- **V-score:** straight lines only, zero gap between boards; JLCPCB needs a board >= 0.6 mm [9].
- **Tab routing:** PCBWay needs >= 1.6 mm between boards [2]; Sierra's panel example reserves 2.54 mm (0.1 in) of routing space [8].
- **Keep parts away from V-score lines:** depanelization stress cracks nearby solder joints. Agree the keep-out with the assembler [4].
- **Impedance test coupons:** Sierra places them at the panel end; agree their location and that they survive depanelization [8].
- **Castellated half-holes:** PCBWay prototype >= 0.6 mm [2]; JLCPCB 0.5 mm with the conditions above [9].
- **Panel planning (Sierra's example):** > 70% usable area; laminate panels 610 x 457, 305 x 457, 610 x 229 or 305 x 229 mm [8]. JLCPCB recommends assembly panels no larger than 250 x 250 mm [15].

### Tombstoning Prevention

Eurocircuits' guidance for two-terminal passives [6]:

- **Equal-width feeds to both pads for >= 0.25 mm from the pad edge.** Several tracks on one pad and one on the other heat them unevenly -> one pad wets first and pulls the part upright.
- **Hole edges >= 0.25 mm from the pad edge, with a reliable mask dam.** A nearby PTH changes the pad's heating and can wick solder.
- **No legend under small passives such as 0603.** Stacked trace + mask + legend can lift the body off its pads.
- **Matching feed tracks >= 0.25 mm before a pour.** Adapt high-power connections so both pads still heat alike.
- **Via-in-pad on passives:** filling stops most wicking, but the via still draws heat from its pad. Keep hole edges >= 0.25 mm away where possible.

### DFA Component Spacing

Sierra Circuits' recommended ranges [4]; dense small boards differ.

- **Chip-to-chip:** 0.25-0.5 mm (10-20 mil).
- **Chip-to-SOT:** 0.38-0.64 mm (15-25 mil). **Chip-to-SOIC:** 0.51-0.64 mm (20-25 mil).
- **QFP-QFP and BGA-BGA:** 2.54-3.05 mm (100-120 mil). **QFP-BGA:** 1.91-3.05 mm (75-120 mil).
- **BGA courtyard:** 1.0 mm; larger clearances next to PLCC, axial and PTH parts.
- **Courtyard for parts < 0603:** 0.15 mm. **Connectors and crystals:** 0.5 mm plus mating clearance.
- **BGA pads: follow the package's land pattern.** NSMD is generally preferred; NXP allows a constrained NSMD/SMD mix on thin FCCSP outside each corner's 3x3 balls [17, pp.15-16].

### Solder Mask and Silkscreen

- **Mask dams:** fab limits are pad gaps, not dam widths. JLCPCB rigid 1 oz: >= 0.10 mm (black/white 0.13), 2 oz: 0.20 [9, 13]. Fine-pitch pads closer than that get no dam and can bridge.
- **Mask alignment:** JLCPCB multilayer LDI +/-0.02 mm [13].
- **Legend:** PCBWay prototype height >= 0.8 mm, stroke >= 0.15 mm, width:height 1:5 [2]; JLCPCB 1.0 mm height (table above).
- **No silkscreen on solderable pads;** check the fab's pad-to-legend clearance [9].
- Solder mask on test points -> `guides/test-debug.md`.

## Common Mistakes

- **Double-sided reflow with heavy parts on the first side.** First-side parts hang upside down during the second pass. Fix: heavy parts on the side soldered last; check their retention and reflow limits with the assembler [14].
- **Fiducial clearance filled with copper or other features.** The camera can't find a clean target. Fix: use the assembler's fiducial copper, mask-opening and keep-out geometry [8, 16].
- **Designing with 0.1 mm trace/space then specifying 2 oz outer copper.** Thicker copper needs wider etch clearance; the fab rejects the order or widens the spacing, which can break impedance targets. Fix: confirm min trace/space per copper weight before layout [9, 11].
- **Pad size not accounting for drill wander.** Fix: account for drill wander and layer-specific ring measurements; agree the fab allowance and check pad sizes with the fab's DFM tool [5].

## Formulas

**Via aspect ratio:**
**Rule of thumb:** confirm the fab's limit and whether it uses drilled or finished diameter [5, 9].
**Formula:** Aspect_ratio = board_thickness / hole_diameter
**Example:** 1.6 mm board, 0.2 mm hole -> 8:1. 0.15 mm hole -> 10.7:1 (check the fab's limit, or use HDI or a thinner board).

**Pad size:**
**Formula:** Pad = finished_hole + 2 * min_annular_ring + fab_allowance
**Example (Sierra):** 0.25 mm finished hole + 2 * 0.05 mm ring + 0.2 mm allowance = 0.55 mm (22 mil) external pad [5].

## Sources

### Related Rules

- `guides/pcb-layout.md` -- Annular ring breakout probability, via aspect ratio, trace sizing
- `guides/test-debug.md` -- Solder mask on test points, ICT pad sizing

### References

1. JLCPCB -- PCB Design Rules and Guidelines: Complete Best Practices: https://jlcpcb.com/blog/pcb-design-rules-best-practices
2. PCBWay -- PCB Manufacturing Tolerances: https://www.pcbway.com/pcb_prototype/PCB_Manufacturing_Tolerances.html
3. OSH Park -- Fabrication Services and Design Rules: https://docs.oshpark.com/services/
4. Sierra Circuits -- DFA Rules: https://www.protoexpress.com/kb/dfa-rules/
5. Sierra Circuits -- IPC Class 2 vs Class 3: Different Design Rules: https://www.protoexpress.com/blog/ipc-class-2-vs-class-3-different-design-rules/
6. Eurocircuits -- Tombstoning: PCB Assembly Guidelines: https://www.eurocircuits.com/technical-guidelines/pcb-assembly-guidelines/tombstoning/
7. Altium -- Complete Guide to DFM Analysis: https://resources.altium.com/p/complete-guide-dfm-analysis
8. Sierra Circuits -- Panel Requirements for PCB Assembly: https://www.protoexpress.com/kb/panel-requirements-for-pcb-assembly/
9. JLCPCB -- PCB Manufacturing Capabilities (read 2026-11-03): https://jlcpcb.com/capabilities/pcb-capabilities
10. JLCPCB -- Impedance Stackups (read 2026-11-03): https://jlcpcb.com/impedance
11. JLCPCB -- Copper Weight (inner-layer trace/space): https://jlcpcb.com/help/article/jlcpcb-copper-weight
12. JLCPCB -- In What Cases Will There Be Charged Extra: https://jlcpcb.com/help/article/in-what-cases-will-there-be-charged-extra
13. JLCPCB -- Basic Design of Solder Mask: https://jlcpcb.com/blog/basic-design-of-solder-mask
14. PCBCart -- Double-Sided SMT Assembly: How the Second Side Changes Your Design Decisions: https://www.pcbcart.com/article/content/pcba-double-sided-assembly.html
15. JLCPCB -- PCB Assembly Capabilities (read 2026-11-06): https://jlcpcb.com/capabilities/pcb-assembly-capabilities
16. JLCPCB -- How to Add Edge Rails and Fiducials for PCB Assembly Orders (read 2026-11-06): https://jlcpcb.com/help/article/how-to-add-edge-rails-fiducials-for-pcb-assembly-order
17. NXP AN13656 -- Assembly Guidelines for FCPBGA and FCCSP (Rev.1, 2022), secs. 4.1.2, 4.2.1: https://www.nxp.com/docs/en/application-note/AN13656.pdf

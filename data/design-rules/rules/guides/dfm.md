# DFM

> Fabrication tolerances, IPC class differences, tombstoning prevention, panelization, and assembly constraints.

## Quick Reference

- **Standard minimum: 0.15 mm (6 mil) trace/space.** Budget fabs support 0.1 mm (4 mil) but yield drops. 6 mil saves ~15% on fab cost.
- **Minimum drill: 0.2 mm (8 mil).** Finished hole tolerance: +/-0.08 mm. Via aspect ratio <= 10:1 (board thickness : hole diameter).
- **Get verified stackup from fab before routing.** Fab dielectric thicknesses define trace widths for impedance control. A 4-layer designed at 0.2/1.0/0.2 mm may ship as 0.18/1.1/0.18 mm.
- **Three global fiducials per board** for pick-and-place. 1-3 mm bare copper circle, no solder mask, >= 3 mm from board edge. Clearance zone must be bare laminate -- copper pour in the clearance zone causes AOI to misidentify the fiducial.
- **Tombstoning prevention: equal thermal mass on both pads.** Equal trace width for >= 0.25 mm from pad edge, no vias within 0.25 mm of pad edge, no silkscreen under 0603 or smaller.

## Design Rules

### Fab Capability

| Parameter | Budget Fab | Standard | Notes |
|-----------|-----------|----------|-------|
| Min trace/space | 0.1 mm (4 mil) | 0.15 mm (6 mil) | 6 mil saves cost |
| Min drill | 0.2 mm (8 mil) | 0.25 mm (10 mil) | Laser for < 0.15 mm |
| Hole tolerance | +/-0.08 mm | +/-0.05 mm | |
| Min annular ring | 0.1 mm (4 mil) | 0.13 mm (5 mil) | Breakout probability -> `guides/pcb-layout.md` |
| Board thickness tol | +/-10% (>= 1 mm) | +/-0.1 mm (< 1 mm) | |
| Via aspect ratio | 10:1 max | 8:1 preferred | Board thickness / hole diameter |
| Microvia aspect ratio | 1:1 max | 0.75:1 preferred | Depth / hole diameter (laser drill). Deeper traps air -> open circuits |
| Board size tolerance | +/-0.2 mm (CNC routing) | +/-0.5 mm (V-scoring) | |

- **2 oz outer copper increases minimum trace/space** due to thicker etch. Confirm min trace/space per copper weight with fab before routing -- designing at 0.1 mm then specifying 2 oz outer causes fab rejection.
- **Blind/buried vias require sequential lamination** -- not supported by all budget fabs (e.g., OSH Park does not support blind or buried vias on any service). Verify with fab before designing.
- **Minimum dielectric thickness: 0.065 mm (2.56 mil)** per IPC 6012 Rev F (September 2023). Lowered from previous revision to facilitate laser drilling of HDI microvias.
- **Drill-to-copper clearance:** finished hole to nearest copper must account for plating thickness and inner layer registration shift. Insufficient clearance causes tangency or breakout on inner layers where registration shift is largest.

### IPC Classes

| Feature | Class 2 | Class 3 |
|---------|---------|---------|
| Annular ring breakout | 90-degree acceptable | None allowed. Min external ring >= 0.05 mm (2 mil), min internal >= 0.025 mm (1 mil) |
| Barrel fill (PTH) | >= 75% (50% exceptions -- see below) | >= 75% (no exceptions) |
| Plating voids | Max 5% of holes (1 per 20) | None allowed |
| Min copper plating | 0.02 mm (0.8 mil) | 0.025 mm (1 mil) |

- **Class 2 is the default** for commercial and industrial.
- **Class 2 barrel fill exceptions (IPC-A-610 rev H):** >= 14-lead components accept >= 50% fill if visible lead + surrounding PTHs pass. < 14-lead accepts >= 50% fill with 360-degree wetting + thermal plane connection.
- **PTH drill sizing:** drill hole 0.38 mm (15 mil) larger than lead diameter. Gives 0.19 mm (7.5 mil) clearance per side for reliable paste fill.
- **Class 3 pad sizing formula:** `Pad = finished_hole + 2 * min_annular_ring + fab_allowance`. Fab allowance (drill wander) up to 0.2 mm (8 mil) per IPC-2221. Class 3 requires teardrop via pads.
- **Class 3 IST testing:** D coupons subjected to 6 reflow simulations + 100 thermal shocks. Pass = <= 10% resistance change over 300-500 cycles.
- **IPC 6012 Rev F default surface finish is now ENIG** (was tin/lead). If fab drawing doesn't specify, manufacturer assumes ENIG.

### Panelization

- **V-score:** zero spacing between boards, clean break on straight lines only. Not suitable for curves or thin boards (< 0.8 mm).
- **Tab routing:** minimum 1.6 mm clearance between boards. Routing bit consumes 2.5 mm (0.1 in) of material.
- **Component-to-edge clearance:** depanelization shear force cracks solder joints near V-score lines. Maintain >= 1 mm from V-score to nearest pad.
- **Impedance test coupons:** place in panel border outside routing path -- coupons in routing channels get destroyed during depanelization.
- **Half-holes (castellated vias):** minimum plated half-hole diameter 0.6 mm.
- **Panel utilization:** target > 70% usable area. V-score wastes less space than tab routing. Standard panel sizes: 610 x 457 mm (24 x 18 in), 305 x 457 mm (12 x 18 in), 610 x 229 mm (24 x 9 in), 305 x 229 mm (12 x 9 in).

### Tombstoning Prevention

- **Equal trace width to both pads for at least 0.25 mm from pad edge.** Multiple tracks to one pad and a single track to the other creates thermal asymmetry -> one pad wets first, pulls component vertical.
- **No vias within 0.25 mm of pad edge.** Vias wick solder and create thermal imbalance. Even with identical vias on both pads, solder wicking is unpredictable -- one via connects to different copper on different layers.
- **No silkscreen under 0603 or smaller.** Stacked copper + soldermask + silkscreen height exceeds pad height, lifting the component off the pads entirely.
- **Equal copper connection on both pads.** If one pad connects to a large pour, route both through thermal relief traces >= 0.25 mm long before connecting to copper. Large copper areas act as heatsinks and cause one pad to wet later.
- **Via-in-pad for passives:** even filled vias cause unpredictable wicking. Fill vias or move them >= 0.25 mm from pad edge.

### DFA Component Spacing

- **Chip-to-chip (0402-0805):** 0.25-0.5 mm (10-20 mil).
- **Chip-to-IC (SOT, SOIC):** 0.38-0.64 mm (15-25 mil).
- **IC-to-IC (QFP, BGA):** 2.5-3 mm (100-120 mil).
- **BGA courtyard clearance:** 1.0 mm minimum around BGA body. >= 1.9 mm (75 mil) from any component to BGA, 3 mm preferred for rework and inspection.
- **Parts < 0603:** 0.15 mm clearance minimum.
- **Connectors and crystals:** 0.5 mm clearance plus mating connector clearance.
- **NSMD (non-solder-mask-defined) pads preferred for BGA.** Mask opening larger than copper pad gives more consistent pad size. Do not mix NSMD and SMD pads on the same BGA -- inconsistent solder volume causes defects.

### Solder Mask and Silkscreen

- **Solder mask dam width: >= 0.1 mm (4 mil) standard LPI.** Fine-pitch (< 0.5 mm) pads: verify fab can hold 0.075 mm (3 mil) dams -- insufficient dams cause solder bridging between adjacent pads.
- **Solder mask registration tolerance:** 0.05 mm (2 mil) standard, 0.025 mm (1 mil) advanced. Misregistration worsens with board size.
- **Min silkscreen character height: 0.8 mm.** Min stroke width: 0.15 mm. Width-to-height ratio: 1:5.
- **No silkscreen on exposed copper pads** -- prevents solder wetting.
- Solder mask on test points -> `guides/test-debug.md`.

## Common Mistakes

- **Double-sided SMD without considering reflow order.** First-side components see two reflow cycles. Heavy/tall components may fall off during second-side reflow when gravity reverses. Fix: place heavier components on the first-reflow side so they see only one inverted pass.
- **Copper pour under fiducial clearance zone.** AOI and pick-and-place interpret pour copper as part of the fiducial, causing misalignment of all component placements. Fix: clearance zone must be bare laminate, not just mask-free copper.
- **Designing with 0.1 mm trace/space then specifying 2 oz outer copper.** Thicker copper requires wider etch clearance. The fab will reject or silently widen spacing, potentially breaking impedance targets. Fix: confirm min trace/space per copper weight with fab before layout.
- **Pad size not accounting for drill wander on inner layers.** Inner layer registration shift is larger than outer layers. Class 3 boards with minimal annular ring fail at inner layers first. Fix: use IPC pad sizing formula with full fab allowance, verify with fab's DFM tool.

## Formulas

**Via aspect ratio:**
**Rule of thumb:** Stay at 8:1 or below for standard processes. 10:1 is the hard limit.
**Formula:** Aspect_ratio = board_thickness / finished_hole_diameter
**Example:** 1.6 mm board, 0.2 mm drill -> 1.6 / 0.2 = 8:1 (acceptable). 0.15 mm drill -> 10.7:1 (needs HDI process or thinner board).

**Class 3 pad size:**
**Rule of thumb:** Add 0.3 mm (12 mil) to drill diameter for external pads.
**Formula:** Pad = finished_hole + 2 * min_annular_ring + fab_allowance
**Example:** 0.25 mm drill, 0.05 mm ring, 0.2 mm allowance -> Pad = 0.25 + 0.1 + 0.2 = 0.55 mm (22 mil).

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

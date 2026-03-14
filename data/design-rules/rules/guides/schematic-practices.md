# Schematic Practices

> Net naming, signal flow, sheet organization, hierarchy, symbol rules, BOM attributes, and verification.

## Quick Reference

- **Net names: ALL CAPS, 4 chars max preferred.** `BTN1` not `USER_INPUT_BUTTON_1`. Long names truncate on PCB pads -- you may only see `USER_IN...` on a 0402 pad.
- **Voltage rails: `+3V3` not `+3.3V`.** `3.3V` misreads as `33V` on small screens. Use `+` prefix, electrical function first: `+3V3_IO`, `+3V3_AN`, `+1V8_CORE`. If the name truncates, you still see `+3V3`.
- **Pin numbers on every symbol MUST match footprint.** SOT-23 pinouts vary between manufacturers for the same package -- 2N3904 from ON Semi vs Nexperia have different B/C/E mapping. Cross-reference datasheet, symbol, and footprint for every transistor.
- **One logical function per sheet.** Power, MCU, memory, analog front-end each get their own sheet. A sheet that requires scrolling is too large -- split it.
- **Duplicate net names across sheets = unintended shorts.** Two nets with the same name on different sheets merge silently. Copy-paste a block without renaming every net = invisible short that passes ERC.

## Design Rules

### Signal Flow and Sheet Layout

- **Name sheets with letter prefixes for alphabetical ordering.** `A_Block_Diagram`, `B_Power_Supply`, `C_MCU`, `D_Memory`, `E_Connectors`, `Z_Revision_History`.

### Hierarchy vs Flat

- **Block diagram on the top-level sheet always.** Every hierarchical design needs a top sheet showing functional blocks and inter-block signal flow. This is the primary navigation aid when schematics are exported as PDF to non-ECAD reviewers.

### Net Naming

- **Active-low: use `n` prefix consistently.** `nRESET`, `nCS`, `nIRQ`. Pick one convention (prefix `n`, suffix `_B`, or overbar) and enforce project-wide. Mixed conventions cause missed inversions during layout review.
- **Assign net names to ALL nets, including short ones.** Auto-generated names like `Net-C12-Pad2` propagate to PCB pads and tracks -- meaningless during debug, and fab houses may flag or reject boards with auto-generated identifiers.
- **Net names within a sheet, ports between sheets.** Ports are CAD navigation aids -- they do NOT appear in the netlist. Using ports for intra-sheet connections creates invisible connectivity that confuses PDF readers.
- **Cross-probe every off-page connector.** Misspelled net name on an off-page connector creates an open circuit that ERC may not catch -- both sides appear validly connected to their local nets.

### Symbol and Component Rules

- **Heterogeneous ICs (FPGA, MCU): split into sub-symbols (UxA, UxB, UxC).** Show all possible pin functions on the symbol. Annotate the active function externally (label `GPIO6` outside the symbol next to pin `AA5/GPIO.6/CLKOK/PWM/T3`). Prevents accidental dual-assignment of the same pin.
- **Never flip standard-orientation symbols.** Flipping a P-channel MOSFET upside down looks like N-channel. Flipping op-amps can swap +/- terminals silently if wires don't update. Exception: passive 2-pin components (R, C, L, LED) can orient freely.
- **Multi-gate symbols with hidden power pins (LM324, 74HC series).** If the power section isn't explicitly placed, decoupling is missed entirely and BOM has no record of needed caps. Fix: make all power pins visible, or verify power connectivity in netlist before layout.

### Reference Designators

- **Number refdes by sheet, not globally sequential.** Sheet B: R200, C200, U200. Sheet C: R300, etc. When components move between sheets during revision, they keep original refdes -- global renumbering invalidates prior test reports and ECOs.
- **Separate refdes ranges for repeated hierarchical blocks.** Channel 1: R100-R199. Channel 2: R200-R299. Maps directly to physical placement grouping.

### BOM Attributes

- **Minimum BOM fields before layout handoff:** MPN, manufacturer, package/footprint, value, tolerance (where applicable), voltage rating (caps), current rating (inductors/fuses), temperature range, DNP flag.
- **Populate MPN at symbol placement time.** Late MPN assignment leads to footprint mismatches -- 0402 symbol assigned a 0603 part, or SOIC-8 symbol assigned TSSOP-8 MPN. Footprint must be locked to MPN from the start.
- **Mark second-source alternatives in `ALT_MPN` field** (e.g., `ALT_MPN=TPS63001DRCR`). Keeps procurement flexibility without creating schematic variants.
- **DNP components stay in schematic and BOM.** Mark with `DNP=TRUE` attribute. Deleting DNP components loses design intent and makes future population changes require schematic re-editing.

### Documentation Annotations

- **Regulator output formula next to feedback divider** (in documentation color): `Vout = (1 + R2/R1) * Vref`. Saves debug time when probing a rail that reads wrong.
- **LED current, op-amp gain, crystal load caps** annotated next to their respective circuits. `2.1Vf, 20mA` / `Gain = 10 V/V` / `CL = 12pF, C1 = C2 = 18pF`.
- **Use a distinct documentation color** (e.g., purple) for all annotation text. Distinguishes design-intent notes from electrical connections in PDF exports.
- **Include revision history sheet** (first or last page): date, author, reviewer, description of changes, review comments. Only reliable change record when schematics are exported as PDF.

### Verification and DRC

- **ERC waive per-instance only.** Suppressing an ERC category globally (e.g., "unconnected pin") hides real errors introduced later. Re-run full ERC before every layout handoff.
- **Netlist-vs-layout diff before ordering boards.** After any schematic change post-layout, re-synchronize and diff. Unsynchronized changes are the #1 cause of "schematic says X, board does Y" failures.

## Common Mistakes

- **Test points in schematic but missing from layout.** TP symbols exist in netlist but layout engineer treats them as annotation-only. They pass DRC silently because they have one connected pin. Fix: verify every TP has a physical footprint placed, not just a netlist entry.
- **Op-amp feedback tapped after a series sense resistor.** Load-dependent voltage drop enters feedback loop, causing output to shift with load current. Fix: tap feedback directly at the output pin, before any series element.
- **Power port naming inconsistency across sheets.** One sheet uses `VCC3V3`, another `+3V3`, a third `3.3V`. These are three separate nets in the netlist -- power rail is silently split. Fix: define rail names in a project-level net name table before schematic entry.
- **Schematic-to-layout desync after late changes.** Engineer edits schematic after layout is 90% complete, forgets to re-sync. Board arrives with a net connected to the wrong pin. Fix: lock schematic before layout starts; any post-layout change triggers mandatory resync and diff review.
- **Copy-paste schematic block with unchanged net names.** Duplicated subcircuit shares net names with original, shorting unrelated signals across sheets. Silent -- no ERC error because both nets are validly connected. Fix: use hierarchical sheets for repeated blocks, or rename every net in pasted copies.

## Sources

### Related Rules

- `guides/checklist.md` -- Pre-build review checklist covering schematic verification
- `guides/test-debug.md` -- Prototype design-for-debug, swaperoo resistors, board version ID

### References

1. Altium -- Easy Schematics Creation for Elegance and Readability: https://resources.altium.com/p/creating-elegant-and-readable-schematics
2. Altium -- The Anatomy of Your Schematic Netlist, Ports, and Net Names: https://resources.altium.com/p/anatomy-your-schematic-netlist-ports-and-net-names
3. Altium -- Hierarchical Block Diagrams and Schematic Designs: https://resources.altium.com/p/how-hierarchical-schematic-design-can-help-your-next-pcb-schematic-layout
4. Sierra Circuits -- How to Draw and Design a PCB Schematic: https://www.protoexpress.com/blog/how-to-draw-design-pcb-schematic/
5. Cadence -- Best Practices for Capturing Circuit Board Schematics: https://resources.pcb.cadence.com/blog/2021-best-practices-for-capturing-circuit-board-schematics
6. SparkFun -- How to Read a Schematic: https://learn.sparkfun.com/tutorials/how-to-read-a-schematic/all
7. Altium -- Naming Convention and PCB Data Management: https://resources.altium.com/p/naming-convention-and-pcb-data-management

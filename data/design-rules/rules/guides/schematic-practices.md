# Schematic Practices

> Net naming, signal flow, sheet organization, hierarchy, symbol rules, BOM attributes, and verification.

## Quick Reference

- **Use short, unambiguous net names that remain identifiable on PCB pads.** Uppercase and four-character names are readability recommendations, not electrical or industry-standard limits; do not sacrifice uniqueness to meet them [1, Nets and Ports; 4, Net labeling guidelines].
- **Voltage rails: `+3V3_IO`, `+3V3_AN`, `+1V8_CORE` are a naming convention.** Putting voltage first keeps it visible when names truncate; using `3V3` avoids a small decimal point being missed. Apply the convention consistently, without treating it as a standard requirement [1, Nets and Ports; 4, Power and ground symbols].
- **Pin numbers on every symbol must match the selected MPN's footprint.** Cross-reference datasheet, symbol and footprint for every transistor; a package name alone does not validate the B/C/E mapping [4, Transistors and Checklist].
- **Use logical sheets for complex designs.** Power, MCU, memory and analog front-end sheets keep associated circuitry readable in exported PDFs; this is an organization recommendation, not a mandatory sheet-size rule [1, Logical Separation].
- **Check net-identifier scope before copying blocks.** In Altium, same-name net labels connect across sheets in Global scope; local labels in hierarchical designs do not. Inspect compiled connectivity rather than assuming every duplicate name is a short [6, Net Labels and Net Identifier Scope].

## Design Rules

### Signal Flow and Sheet Layout

- **For alphabetical sheet lists, letter prefixes preserve intended order.** `A_Block_Diagram`, `B_Power_Supply`, `C_MCU`, `D_Memory`, `E_Connectors`, `Z_Revision_History` are a project convention, not a standards requirement [4, section 2].

### Hierarchy vs Flat

- **For complex hierarchical designs, use a top sheet showing functional blocks and inter-block signal flow.** This provides navigation when exporting PDF to reviewers without ECAD; small flat designs do not require a block-diagram sheet [1, Easy Schematics Layout; 3; 4, sections 8-9].

### Net Naming

- **Mark active-low signals consistently.** An overbar is Sierra's recommended convention; a textual naming convention must preserve the same polarity meaning throughout the project [4, Net labeling guidelines].
- **Name nets where it improves identification and cross-sheet connectivity.** Auto-generated names remain valid electrical identifiers; directly wired local nets do not require manual names [2, Creating Connectivity With Ports and Net Names; 4, Net labeling guidelines].
- **Use net labels within a sheet and ports between sheets as the default drawing convention.** Port objects are absent as graphical objects from the netlist, but they establish electrical connectivity and can name nets depending on tool options [2, Creating Connectivity With Ports and Net Names; 6, Port].
- **Cross-probe every off-page connector in the compiled design.** Check both its spelling and the applicable sheet-scope rules; text that looks connected on a PDF is not proof of compiled connectivity [4, Checklist; 6].

### Symbol and Component Rules

- **Heterogeneous ICs (FPGA, MCU): split into sub-symbols (UxA, UxB, UxC) when needed for readability.** Annotate the active pin function externally; Sierra's example labels `GPIO6` next to pin `AA5/GPIO.6/CLKOK/PWM/T3`. Verify pin assignments against the selected IC rather than treating that illustration as a universal pinout [4, Heterogeneous schematic symbol].
- **Keep transistor/MOSFET symbols in a recognizable orientation; recheck connections after mirroring op-amps.** Orientation is a readability recommendation, not a change in device type. Two-terminal R/C/L/LED symbols can be oriented for clarity, while polarized parts still require a polarity check [1, Symbol Orientation; 4, Op-amp and Checklist].

### BOM Attributes

- **Populate the actual MPN and package when placing symbols.** Include manufacturer, value and critical tolerance/dielectric/rating parameters; make exceptional requirements visible so procurement does not replace them with generic parts [1, Easy Schematics Documentation; 4, section 17].
- **A DNP attribute alone does not define assembly output.** In Altium, a Not Fitted variant component stays in the schematic and PCB but is omitted from the variant BOM by default. To list it explicitly, enable Show Not Fitted and the Fitted column; check the selected variant in every assembly output [7, Not Fitted; 8, Excluding Not Fitted Components].

### Documentation Annotations

- **Annotate regulator setpoints using the actual feedback-divider designators and device equation.** A generic R1/R2 formula is ambiguous when the top and bottom resistor names are unspecified [1, Easy Schematics Documentation].
- **Annotate expected LED current and amplifier gain using the circuit's calculated values.** The annotations are design-specific, not default current or gain values [1, Easy Schematics Documentation].
- **Use a distinct documentation color** (e.g., purple) for annotation text, and verify readability in the exported PDF; the color is a drawing convention [1, Easy Schematics Documentation].
- **Include revision history in exported schematic documents:** date, description of changes and review information on the first or last page. This preserves useful context for readers without the ECAD project [4, section 6].

### Verification and DRC

- **Run the configured electrical checks before every layout handoff.** Confirm that enabled rules cover the intended pin connections; a clean report checks only the configured rules [5, DRCs; 4, section 15].
- **Re-synchronize and inspect connectivity after any schematic change post-layout.** Review the compiled netlist and transferred connections before ordering boards [2, Better PCB Design Software Keeps You Synchronized; 4, section 16].

## Common Mistakes

- **Assuming matching text on different identifier types guarantees a connection.** Altium ports and net labels do not automatically connect solely because their names match; inspect the configured net-naming options and compiled connectivity [6, Net Identifiers].
- **Relying on letter case to isolate nets.** Altium net identifiers are case-insensitive: `abc` and `ABC` identify the same net wherever the selected scope connects them. Use distinct names or hierarchy, not capitalization, for separate signals [6, Net Identifiers].
- **Naming power ports inconsistently across sheets.** `VCC3V3`, `+3V3` and `3.3V` do not connect by name; explicit wiring or hierarchical connections can still connect them. Verify intended connectivity and naming in the compiled design [6, Power Ports and Net Identifier Scope].

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
6. Altium Designer -- Creating Circuit Connectivity in Your Schematics (updated 2026-10-06; HTML section names cited): https://www.altium.com/documentation/altium-designer/schematic/creating-circuit-connectivity
7. Altium Designer -- Design Variants (updated 2026-11-02): https://www.altium.com/documentation/altium-designer/design-variants
8. Altium Designer -- Preparing a BOM in the Report Manager (updated 2026-10-13): https://www.altium.com/documentation/altium-designer/preparing-for-manufacture/output-jobs/bom-report-manager

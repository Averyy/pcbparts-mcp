# Assembly / Design for Assembly

> Assembly-file orientation, optical registration, tooling and package-specific reflow checks beyond the DFM rules.

## Quick Reference

- **For JLCPCB Economic PCBA, provide 2-3 tooling holes:** 1.152mm NPTH with 0.148mm mask expansion, separated toward opposite corners [1, requirements 1-3].
- **Check the component's physical polarity mark against the PCB legend.** Tantalum and aluminum electrolytic marking conventions differ; one generic capacitor stripe convention reverses a part [2, Capacitors].
- **A standard NXP HVQFN/HVSON's bare-copper terminal side is not guaranteed to wet.** AN10365 describes a wettable-flank option for terminal pitch >=0.65mm when visible side fillets are an inspection requirement [3, Section 2.4.2].
- **Between first and second reflow, track MSL floor life.** NXP requires drying or protected storage if the interval exceeds the applicable floor life [3, Section 4.3].

## Design Rules

### Fiducials, Orientation and Spacing

- **Provide fiducials on each assembled face when the process uses both faces.** JLCPCB's fiducial guide explicitly calls for both sides on double-sided boards; service-specific copper/mask geometry and rail dimensions -> `guides/dfm.md` [4, Optimal Size, Shape, and Placement Rules].
- **Make LED polarity marks specific to the purchased part.** JLCPCB's identification guide distinguishes top- and bottom-view LED marks; reconcile manufacturer polarity, footprint pad numbers, PCB silkscreen and placement rotation before approving assembly [2, II. Light-Emitting Diodes].
- **Verify IC pin 1 from the component's documented mark, not its printed text orientation.** JLCPCB uses dots, notches and chamfers as identification examples; an assembly drawing must agree with the physical part and the PCB's pin-1 indicator [2, Integrated Circuits].
- **For connectors, verify mating direction as well as pin numbering.** JLCPCB notes that electrically non-polar terminal blocks still have an assembly orientation; rotating one can make an external interface inaccessible [2, Terminal Blocks / Connectors].
- **Use the assembler's courtyard/spacing requirements rather than a new universal DFA spacing.** Existing chip-to-chip, BGA/QFP and connector clearance recommendations are in `guides/dfm.md`; NXP notes that even equivalent QFN/SON parts from different suppliers can need different optimized footprints [5, Section 4.1].

### Tooling and Panels

- **Do not replace mechanical tooling holes with fiducials.** JLCPCB distinguishes mechanical fixture references from optical alignment marks; apply its Economic tooling-hole requirement independently of optical registration [1, requirements; 4, What Fiducial Markers Are and Why They Matter].
- **Clear tooling holes on internal copper too.** JLCPCB explicitly requires isolation rings on inner negative layers when a tooling hole is placed in copper; check the final CAM output, not just outer-layer clearance [1, When adding the tooling hole on the copper area].
- Panel routing gaps, V-score keep-outs and assembly rail/fiducial geometry -> `guides/dfm.md`.

### Reflow, Tombstoning and Hidden Joints

- Pad/feed thermal balance, via proximity and legend-under-body failure modes for small two-terminal passives -> `guides/dfm.md`.
- **Reserve NXP HVQFN/HVSON's pin-1 keep-out even when it is absent from the published package outline.** An extra pin-1 pad or die-pad notch can contact an exposed PCB trace and malfunction; use Figure 12's keep-out geometry for the applicable package [3, Section 2.4.1].
- **Treat QFN/SON paste and exposed-pad design as package-specific.** AN1902's HVQFN48 example specifies a 0.1mm stencil but explicitly calls its footprint a starting point to adapt to the assembly process; do not apply that stencil thickness to every QFN or BGA [5, Section 4.1, Figure 12].
- **For BGA reflow, verify solder-ball alloy against the paste and profile.** NXP distinguishes solder-ball packages, whose balls must melt into the joint, from ordinary leaded/leadless finishes; the same paste alone does not prove a valid BGA profile [3, Section 4.4].
- **Qualify first-side retention using the actual package and oven process.** NXP identifies component weight and conveyor vibration as second-pass drop-off causes and allows adhesive retention; it gives no universal safe weight in grams. Heavy-part placement guidance -> `guides/dfm.md` [3, Section 4.3].

## Common Mistakes

- **Accepting a no-side-fillet QFN as a solder failure solely from AOI.** AN1902 identifies terminal-end oxidation during dry bake or storage as a reason a side fillet fails to form; qualify the actual terminal finish and package's inspection method [5, Section 3.4.1].
- **Assuming a nominally interchangeable second-source QFN uses the same assembly process.** NXP warns that a footprint optimized for one supplier can reduce yield or solder-joint life with another; qualify both sources against the actual land pattern and paste process [5, Section 4.1].

## Sources

### Related Rules

- `guides/dfm.md` -- Existing spacing, thermal balance/tombstoning, panelization, fiducial and rail geometry.
- `guides/pcb-layout.md` -- Thermal relief and via design.
- `guides/test-debug.md` -- Fixture and probe access.

### References

1. JLCPCB -- How to Add Tooling Holes for PCB Assembly Order (updated 2026-09-09; read 2026-11-09): https://jlcpcb.com/help/article/how-to-add-tooling-holes-for-pcb-assembly-order
2. JLCPCB -- Component Polarity & Orientation Identification Guide (read 2026-11-09): https://jlcpcb.com/help/article/component-polarity-and-orientation-identification-guide
3. NXP -- AN10365, Surface Mount Reflow Soldering, Rev.8 (2021-10-01): https://www.nxp.com/docs/en/application-note/AN10365.pdf
4. JLCPCB -- PCB Fiducials: Perfect SMT Alignment Guide (read 2026-11-09): https://jlcpcb.com/blog/pcb-fiducials
5. NXP -- AN1902, Assembly Guidelines for QFN and SON Packages, Rev.9 (2021-04-28): https://www.nxp.com/docs/en/application-note/AN1902.pdf

# Design Review Checklist

> Pre-build review -- catches common omissions before fabrication and assembly.

## Quick Reference

- **ERC/DRC must be 100% clean.** Every exception individually reviewed and signed off. Zero unreviewed warnings.
- **Verify ALL symbol pinouts against datasheet.** Even trusted library symbols. Compare pin numbers, not just names.
- **Thermal pad net is NOT always ground.** Some ICs connect exposed pad to VCC, some float. Check datasheet for every IC.
- **Every external connector pin has ESD protection.** TVS or clamp on every line leaving the board -> `protection/esd.md`.

## Design Rules

### Components

- **External pull-up/pull-down on all strapping and config pins.** Internal pulls may not overcome board capacitance during fast power-up. Document expected state in schematic notes.
- **Reset and enable pins: external pull-up/pull-down.** Use supervisor IC when regulator has soft start -> `protection/voltage-supervisor.md`.
- **Check errata sheets for all major ICs.** Silicon bugs affect pin usage, peripheral availability, and required workaround components.
- **Tantalum voltage derating: >= 2x for surge-prone circuits.** Low-impedance source driving tantalum can cause premature failure -- limit switch-on current.
- **Alternate/substitute parts: verify footprint, pinout, AND key specs match.** Two pin-compatible SOT-23-5 LDOs may swap EN and NC pins. Check lifecycle -- no EOL or NRND parts.

### Power

- **Input protection at every power entry: fuse + TVS + reverse polarity** -> `protection/reverse-polarity.md`.
- **Total input capacitance > 100 uF causes inrush** that can trip protection or weld connector pins. Add NTC thermistor or active inrush limiter.
- **Regulator input voltage range vs actual input under all conditions.** Battery droop, USB tolerance (+/-5%), transient overshoot, cable voltage drop.
- **LDO output cap ESR within stable range.** Many LDOs oscillate with near-zero ESR ceramic caps -> `power/ldo.md`.
- **Current-sense resistors placed after regulator output caps.** Not in SMPS switching loop -- added inductance increases noise and EMI.
- **Analog rails filtered or isolated from digital.** Series ferrite + parallel cap minimum. Do not split ground planes -> `guides/pcb-layout.md`.

### Signals

- **TX/RX pairing verified for UART, SPI MOSI/MISO.** Add zero-ohm swap resistors on prototypes -> `guides/test-debug.md`.
- **Verify cable pinout: straight-through vs crossover.** TX/RX swap, D+/D- swap, and connector gender errors are invisible in schematic review.
- **Board version ID readable in firmware.** ADC resistive divider on a spare GPIO pin -- different resistor values per revision. Cheaper and more reliable than GPIO straps for > 4 versions.

### Protection and EMC

- **Identify clock and SMPS switching frequencies.** Ensure harmonics do not fall in sensitive bands (2.4 GHz WiFi/BT, GPS L1 1575.42 MHz).
- **Different connector types for different functions.** Never share the same plug/socket between power and signal -- mis-plugging destroys circuitry. Fermilab Wide Band Lab fire (1987) resulted from a misjoined connector drawing amps through 1 A-rated cables.

### Connectors

- **Hot-plug connectors: ground pin makes first contact.** Power pins second, signal pins last. Verify physical pin length ordering in connector datasheet.
- **Specify exact connector series + position count.** "JST connector" is meaningless -> `guides/connectors.md`.
- **Footprint for common-mode filter on high-speed differential signals off-board.** USB, HDMI, Ethernet -- even if not populated initially. Allows quick fix if EMC testing fails.

### Layout

- **Import fab DRC rules before routing.** Get verified stackup -> `guides/dfm.md`.
- **Decoupling caps within 2 mm of IC power pins** -> `power/decoupling.md`.
- **No vias in pads without fill and cap.** Solder wicking weakens joints -> `guides/dfm.md`.
- **3 mm component-free border** for machine handling and depanelization.
- **Trace-to-trace clearance by voltage per IPC-2221.** Internal layers: 0.1 mm (4 mil) at 31-50 V. External uncoated: 0.6 mm (24 mil) at 31-100 V. Above 500 V: internal 0.025 mm/V, external 0.005 mm/V.
- **Drill-to-copper clearance on all layers.** Finished hole to nearest copper must include plating: clearance = drill-to-copper + (plating thickness * 2). Verify on inner layers where registration shifts are largest.
- **Stress-sensitive MLCCs away from V-score and mouse-bite edges.** Depanelization bending cracks ceramic caps. Orient cap length parallel to board edge (not perpendicular).
- **QFN/BGA exposed pad: segmented solder paste stencil aperture.** Full coverage causes excessive voiding and solder balling during reflow.
- **No traces between adjacent IC pins in copper pour.** Creates inspection ambiguity and potential solder bridges on fine-pitch parts.
- **Smallest component determines stencil thickness.** 0402 and larger: 0.12 mm (5 mil). 0201 or 01005: 0.08-0.10 mm (3-4 mil) -- reduces paste volume for all other pads. Avoid mixing 01005 with large QFN unless segmented stencil is specified.

### Assembly and Mechanical

- **Terminal blocks and cheap plastic connectors: no reflow.** Hand-solder or wave-solder only -> `guides/connectors.md`.

### Pre-Fabrication Output

- **Visual Gerber review in standalone viewer.** Inspect each layer for copper slivers, drill alignment, and solder mask errors. Automated DRC misses cosmetic defects.
- **Fab package:** Gerbers (or ODB++), NC drill file, IPC-356A netlist, stackup drawing, impedance requirements, material and finish specs.
- **Assembly package:** BOM with manufacturer PN + alternates, pick-and-place centroid file (designators, X/Y, rotation, layer), assembly drawing with polarity marks.
- **Impedance test coupons** at panel edge for controlled-impedance verification.

Board bring-up procedure -> `guides/test-debug.md`.

## Common Mistakes

- **Thermal pad connected to wrong net.** Some ICs connect exposed pad to VCC, not ground -- and some have the pad floating (no internal connection). Fix: check datasheet for every IC with exposed pad; verify net, not just "ground."
- **Alternate part with same footprint but different pin assignment.** Two pin-compatible SOT-23-5 LDOs may swap EN and NC pins. Fix: compare pin tables side by side, not just package outline.
- **Right-angle and vertical variants of the same connector series have different pin-1 locations.** Fix: verify pin numbering against the specific orientation variant in the footprint.
- **ERC clean but power flags missing on connector power pins.** KiCad and Altium suppress "undriven net" errors when power flags are absent, hiding real issues. Fix: add power flags on all connector pins that supply or receive power.
- Additional schematic-specific mistakes -> `guides/schematic-practices.md`.

## Sources

### Related Rules

- `protection/esd.md` -- ESD protection on external connector pins
- `protection/voltage-supervisor.md` -- Reset and enable pin supervision
- `protection/reverse-polarity.md` -- Input protection at power entry
- `power/ldo.md` -- LDO output cap ESR stability requirements
- `power/decoupling.md` -- Decoupling cap placement strategy
- `guides/pcb-layout.md` -- Layout rules, ground planes, trace sizing
- `guides/dfm.md` -- Fab DRC rules, via-in-pad, stackup verification
- `guides/test-debug.md` -- Board bring-up procedure, TX/RX swap resistors
- `guides/connectors.md` -- Connector type specification, reflow compatibility
- `guides/schematic-practices.md` -- Schematic-specific review and common mistakes

### References

1. pcbchecklist.com (Henrik Hansen) -- Most exhaustive: https://pcbchecklist.com/
2. azonenberg/pcb-checklist -- Schematic checklist: https://raw.githubusercontent.com/azonenberg/pcb-checklist/master/schematic-checklist.md
3. azonenberg/pcb-checklist -- Layout checklist: https://raw.githubusercontent.com/azonenberg/pcb-checklist/master/layout-checklist.md
4. Altium -- Schematic Design Review Checklist: https://resources.altium.com/p/schematic-review-checklist
5. grosdode/PCB-design -- Prototyping & Bring-up Checklist: https://raw.githubusercontent.com/grosdode/PCB-design/main/PCB_Checklist/pcb_checklist.md
6. Sierra Circuits -- IPC-2221 Standards Reference: https://www.protoexpress.com/blog/ipc-2221-circuit-board-design/
7. Sierra Circuits -- DFM Rules: https://www.protoexpress.com/kb/dfm-rules/
8. Espressif ESP32-S3 HW Design Guidelines -- Schematic Checklist: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html
9. Espressif ESP32-S3 HW Design Guidelines -- PCB Layout Design: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html

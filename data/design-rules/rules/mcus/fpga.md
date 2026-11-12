# FPGA Hardware Design

> Power sequencing, BGA decoupling, configuration flash, IO banking, SERDES power, clock distribution, DDR memory interfaces.

## Quick Reference

- **ECP5 external-flash boot needs VCCIO8 high enough for the flash before POR release, or PROGRAMN/INITN held low.** iCE40 sequencing is different; follow the exact family requirements below [7, p.52; 2, pp.9-10].
- **ECP5/ECP5-5G rail noise targets: < 0.25% peak on PLL supplies, <= 1% peak on SERDES differential supplies.** Include regulator error and filter voltage drop in the supply tolerance budget [1, pp.8-11].
- **ECP5 VCC: 3x 10 uF bulk + 100 nF per pin; iCE40: 4.7 uF per rail + 100 nF per pin.** The iCE40 VCCPLL filter also needs a 100 ohm series resistor [1, p.10; 2, pp.8-9].
- **ECP5 JTAG: 4.7 kohm pull-up on TDI/TMS/TDO to VCCIO8, 4.7 kohm pull-down on TCK.** iCE40 uses SPI configuration; do not apply an ECP5 JTAG pin rule to it [1, p.15; 2, p.11].
- **ECP5 unused VCCIO banks: connect to a power rail, never leave floating.** Other families need their own unused-bank pin rules [1, p.12].

## Design Rules

### Power Supply Architecture

- **ECP5/ECP5-5G and iCE40 regulator recommendation: <= 3% error, leaving 2% for noise/layout within a +/-5% rail budget.** The 1.2V rail loses 1% margin per 12 mV; include reference, line/load, feedback resistor, and filter voltage-drop errors [1, pp.8-11; 2, p.10].
- **ECP5/ECP5-5G analog filtering: 120 ohm ferrite + 10 uF + 100 nF per pin on VCCA, VCCHRX, VCCHTX, and VCCAUXA.** The checklist recommends beads in the 120-240 ohm at 100 MHz range; DC resistance * current must stay below 1% of non-analog rail voltage or 0.25% of sensitive rail voltage. PLL bead DC resistance can be <= 0.3 ohm only when its load current meets that drop budget [1, pp.10-11].

- Ferrite bead resonance and damping -> `guides/passives.md`.
- **ECP5/ECP5-5G unused SERDES DCU: ground VCCA, VCCAUXA, VCCHRX, VCCHTX, REFCLK, and Rx inputs; leave Tx outputs open.** For an unused channel in an active DCU, power VCCA/VCCHTX, ground its unused REFCLK and Rx inputs, and leave the channel's VCCAUXA/VCCHRX and Tx open. Preserve the supply/reference-clock connections needed by the active channel [1, p.12].

### Power Sequencing

- **ECP5/ECP5-5G: the checklist recommends VCCIO before or together with VCC/VCCAUX; external-flash boot has a specific constraint.** VCCIO8 must exceed the flash VIH before at least one of VCC/VCCAUX reaches its POR threshold. If VCCIO8 comes last, hold PROGRAMN or INITN low until it meets flash VIH. On LFE5UM/LFE5UM5G, power VCCA before VCCAUXA [1, p.13; 7, p.52].
- **iCE40 recommended order: VCC + VCCPLL, then SPI_VCC, then VPP_2.5V where present.** Each preceding supply must reach >= 0.5V before the next is applied. Other VCCIO supplies can start any time after VCC/VCCPLL; they need not wait for VPP_2.5V. No power-down order is required, but partial-rail restart must follow the power-up order [2, pp.7, 9-10].
- **Intel/Altera Cyclone V/Arria V: AN-662 does not require a sequence for correct operation, but multi-rail startup timing must avoid excessive transient current.** Use monotonic ramps with sufficient POR current. MSEL selects a typical 4 ms or 100 ms POR delay; extend it through nSTATUS if rails cannot meet ramp timing [5, p.12].
- **PGOOD-to-EN sequencing uses the actual regulator PGOOD threshold.** TI's example uses a typical 90% threshold; it provides monitored startup but no controlled power-down order [4, p.1].
- **Sequencer choices: LM3880 for three timed outputs with up/down sequencing; TPS386000 for monitored reset-based startup.** For programmable dependencies and PMBus monitoring, TI uses UCD90120A; select by timing and monitoring needs rather than a universal rail-count threshold [4, pp.1-3].

### Decoupling

- **ECP5: 3x 10 uF bulk + 100 nF per VCC pin.** VCCAUX: 120 ohm ferrite + 10 uF + 100 nF per pin. VCCIO: 10 uF per bank + 100 nF per pin; unused banks can replace 10 uF with 1 uF, heavy-output banks can add 10 uF or use 22 uF [1, p.10].
- **iCE40: 4.7 uF per rail + 100 nF per power pin.** VCCPLL: 100 ohm series resistor + 4.7 uF + 100 nF, with the capacitors returning to GNDPLL when that pin exists. GNDPLL must not connect externally to board ground when a dedicated pin is present; its DC ground connection is internal. Apply the filter even if the PLL is unused [2, pp.8-9].
- **ECP5 capacitor package recommendations, preferred/next-best:** 100 nF in 0201/0402, 1-2.2 uF in 0402/0603, 4.7 uF in 0603/0402, 10 uF in 0603/0805, 22 uF in 0805/1206. Lattice recommends X5R/X7R and a voltage rating >= 1.8x maximum rail voltage; verify actual biased capacitance separately [1, p.12].

- Per-IC decoupling strategy details -> `power/decoupling.md`.

### Configuration

- **iCE40 LP/HX/Ultra/UltraLite/UltraPlus: SPI_SS_B high at POR release or CRESET_B rising selects NVCM when enabled, otherwise external-flash SPI master boot; low selects SPI slave configuration by an external controller.** LM has no NVCM. FPGA-TN-02006-2.3 p.11 conflicts with the mode-selection description; use FPGA-TN-02001-3.5 pp.10-11 [8].
- **External SPI flash must support 0x0B Fast Read with a 24-bit start address and 8 dummy bits for iCE40 master boot.** Pull SPI_SS_B up to SPI_VCC with 10 kohm for master boot; use 10 kohm down for slave configuration when no processor drives it [2, pp.11-13; 8, pp.19-21].
- **ECP5 configuration flash voltage must match VCCIO8; choose a part in Diamond Programmer's SPI Flash Support list.** For iCE40, match the SPI flash interface to SPI_VCC and its required command format; capacity and maximum clock alone do not prove configuration compatibility [1, p.19; 2, pp.11-13].
- **ECP5 configuration pulls: PROGRAMN/INITN 4.7 kohm up to VCCIO8; CSSPIN 4.7-10 kohm up near the flash; CFG[2:0] 1-10 kohm straps.** MCLK/CCLK uses a 510 ohm-1 kohm pull-up, with a separate 22-80 ohm series resistor selected for the PCB and placed near the transmitter; 510 ohm-1 kohm is not the series-termination value [1, p.15, Table 6.2 and notes].
- **ECP5: route TCK/TMS/TDI/TDO, VCCIO8, and GND to a common test header even when booting from SPI.** For iCE40 SPI access, pull CRESET_B up with 10 kohm to its I/O bank and pull CDONE up to its bank supply; choose CDONE resistance for configuration frequency and trace capacitance (10 kohm is shown in the checklist examples) [1, p.15; 2, pp.11-13].
- **Leave ECP5 configuration ports unused by the selected mode open, while retaining its required dedicated control pins and straps.** Table 6.3 lists the pins required in each mode [1, p.15].

### IO Banking and Pin Assignment

- **ECP5/ECP5-5G: keep switching outputs away from SERDES analog supply and reference-clock pins.** Assign nearby I/Os to static or low-switching signals; the checklist identifies output crosstalk as a leading source of noise on sensitive supplies [1, pp.10, 20].
- **iCE40 LP/HX LVDS inputs require external differential termination.** Emulated LVDS outputs need two series resistors and a parallel resistor network; compute their values from the LP/HX differential-I/O guide. This is not a universal iCE40 Ultra-family pin rule [2, p.16].

### Clock Distribution

- **iCE40 LP/HX: use dedicated GBIN clock inputs.** GBIN7 and its associated PIO are recommended for direct differential clocks; LM/Ultra/UltraLite/UltraPlus have a different global-buffer arrangement [2, p.14, Figure 4.1].
- **ECP5 reference clock oscillator: decouple with 100 nF + 1 uF close to the oscillator.** The checklist shows a dual HCSL/LVDS footprint option [1, p.23].
- **LatticeECP2M/ECP3 LVPECL-to-CML reference clock: use the vendor's driver-load and AC-coupling circuit.** Their reference receivers offer configurable internal 50 ohm termination; LatticeSC requires external termination. PCIe transmitter coupling values are not a reference-clock capacitor rule [3, pp.17-18, Figures 14-15].

### DDR Memory Interfaces

- **For a multi-device DDR4 command/address bus, Micron TN-40-40 recommends fly-by routing with end termination to VTT.** This does not apply to DQ/DQS point-to-point routing; use the selected FPGA memory-controller topology and calibration requirements [6, pp.19, 30].
- **DDR4 additions vs DDR3:** 2.5V VPP supply, internally generated VREFDQ instead of an external VREFDQ input, POD data interface, and ACT_n control. VREFDQ calibration and data-bus write training must complete before DDR4 timing specifications are valid [6, pp.1, 11-12, 16].
- **Include FPGA package and PCB flight times in memory-interface timing.** For Cyclone V/Arria V, Quartus Enable Advanced I/O Timing includes the I/O buffer, package, and board-trace models; PCB length matching alone is incomplete [5, p.19].

## Common Mistakes

- **Missing DDR4 VPP prevents correct operation.** The 2.5V rail powers the internal word line; provide its required current rather than treating it as a reference-only supply [6, p.11].

## Sources

### Related Rules

- `guides/passives.md` -- Ferrite bead LC resonance damping and passive component selection
- `power/decoupling.md` -- Per-IC decoupling strategy, capacitor sizing, and placement rules
- `mcus/rp2040.md` -- RP2040/RP2350 SPI flash configuration (check each device's boot commands)

### References

1. Lattice FPGA-TN-02038-2.0 (July 2024) -- ECP5 and ECP5-5G Hardware Checklist: https://0x04.net/~mwk/doc/lattice/ecp5/FPGA-TN-02038-2-0-ECP5-and-ECP5-5G-Hardware-Checklist.pdf
2. Lattice FPGA-TN-02006-2.3 (April 2024) -- iCE40 Hardware Checklist: https://0x04.net/~mwk/sbdocs/ice40/FPGA-TN-02006-2-3-iCE40-Hardware-Checklist.pdf
3. Lattice TN1114 (Rev 02.9, March 2014) -- Electrical Recommendations for Lattice SERDES: https://www.latticesemi.com/~/media/3E4AA60747DC46FC9EC26A9FD2F35894.ashx
4. TI SLYT598 (4Q 2014) -- Power Supply Sequencing for FPGAs: https://www.ti.com/lit/pdf/slyt598
5. Intel/Altera AN-662-1.3 (November 2016) -- Arria V and Cyclone V Design Guidelines: https://cdrdv2-public.intel.com/654271/an662.pdf
6. Micron TN-40-40 (Rev H, August 2020) -- DDR4 Point-to-Point Design Guide: https://www.mouser.com/pdfDocs/Micron_DDR4_Design_Guide.pdf
7. Lattice FPGA-DS-02012-3.4 (September 2025) -- ECP5 and ECP5-5G Family Data Sheet: https://www.latticesemi.com/view_document?document_id=50461
8. Lattice FPGA-TN-02001-3.5 (August 2026) -- iCE40 Programming and Configuration: https://www.latticesemi.com/view_document?document_id=46502

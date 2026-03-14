# FPGA Hardware Design

> Power sequencing, BGA decoupling, configuration flash, IO banking, SERDES power, clock distribution, DDR memory interfaces.

## Quick Reference

- **Power sequence is family-specific -- no universal rule.** ECP5 hardware checklist recommends VCCIO before or with VCC and VCCAUX (verify against your device's datasheet). iCE40: VCC + VCCPLL first, then SPI_VCC, then VPP_2.5V. Always check your family's datasheet.
- **SERDES analog supplies require isolated LDO or passive LC filter.** Switching regulator ripple at the SERDES PLL bandwidth directly adds jitter. Target < 0.25% peak noise on PLL rails, < 1% on SERDES differential rails.
- **100 nF per power pin + bulk per rail.** ECP5: 3x 10 uF bulk on VCC. iCE40: 4.7 uF + 100 nF per pin.
- **JTAG: always route to header.** 4.7 kohm pull-up on TDI/TMS/TDO, 4.7 kohm pull-down on TCK. Even if primary config is SPI, JTAG enables debug.
- **Unused VCCIO banks: connect to a power rail, never leave floating.**

## Design Rules

### Power Supply Architecture

- **Combined switching + linear strategy for SERDES FPGAs.** Switching regulator for VCC core and VCCIO (high current, efficiency matters). Dedicated LDO for SERDES analog (VCCA, VCCPLL): LP5907 (6.5 uVrms, 250 mA) for low-power SERDES, TPS7A20 (10 uVrms, 300 mA) for general use, LT3045 (0.8 uVrms) for jitter-critical links.
- **Regulator tolerance: <= 3% to leave 2% margin for noise and layout.** The 1.2V core rail is especially sensitive: 12 mV = 1% of rail voltage. Tolerance budget must include reference, line/load regulation, and feedback resistor tolerance.
- **Ferrite bead passive filter for SERDES Rx/Tx termination supplies (VCCIB/VCCOB).** 120-240 ohm at 100 MHz. ESR * current < 1% of rail voltage for non-analog, < 0.25% for PLL. PLL rails draw low current, allowing ferrite ESR up to 0.3 ohm. Murata BLM41PG471SN1L is a known-good choice.

> WARNING: Ferrite bead + downstream cap = LC resonance. If resonance falls in the ferrite's inductive region, you get gain instead of attenuation at the switching frequency. Damping guidance -> `guides/passives.md`.

- **Unused SERDES DCU: connect VCCA, VCCAUXA, VCCHRX, VCCHTX, REFCLK, and Rx inputs to ground.** Leave Tx outputs open. For unused channels within an active DCU: connect VCCA and VCCHTX to power, Rx inputs to ground, leave VCCAUXA/VCCHRX and Tx open.

### Power Sequencing

- **No universal FPGA power sequence -- it is family-specific.** Get it from the hardware checklist document for your exact part.
- **ECP5: Lattice hardware checklist recommends VCCIO before or together with VCC and VCCAUX** (exact requirements may vary by package -- always verify against your device's datasheet). POR de-asserts when VCC >= 0.9V, VCCAUX >= 2.0V, VCCIO8 >= 0.95V. Supplies must ramp monotonically.
- **iCE40: VCC + VCCPLL first, then SPI_VCC, then VPP_2.5V, then VCCIO.** Each supply must reach 0.5V before the next is applied. No power-down sequence required.
- **Intel/Altera Cyclone V/Arria V: no strict sequence required (supports hot socketing).** But design monotonic ramps and ensure minimum POR current is available. MSEL pins select POR delay: 4 ms or 100 ms typical.
- **Simplest sequencing: cascade PGOOD into EN.** Second supply starts when first reaches 90% of final value. Low cost but no timing control and no power-down sequencing.
- **For > 3 rails: use a sequencer IC.** LM3880 (3 outputs, up/down sequencing). For monitored sequencing: TPS386000 (4-channel reset IC with programmable delay). For complex systems: UCD90120A (12 rails, PMBus, GUI-configurable).

### Decoupling

- **ECP5: 3x 10 uF bulk + 100 nF per VCC pin.** VCCAUX: 120 ohm ferrite + 10 uF + 100 nF per pin. VCCIO: 10 uF + 100 nF per pin (unused banks: replace 10 uF with 1 uF; heavy-output banks: add extra 10 uF or use 22 uF).
- **iCE40: 4.7 uF + 100 nF per power pin on every rail.** VCCPLL: 100 ohm series resistor + 4.7 uF + 100 nF. GNDPLL must NOT connect to board ground (except on packages without dedicated GNDPLL ball). This filter is required even if PLL is not used.
- **Capacitor sizing for FPGA decoupling.** Preferred/next-best: 100 nF in 0201/0402, 1-2.2 uF in 0402/0603, 4.7 uF in 0603/0402, 10 uF in 0603/0805, 22 uF in 0805/1206. Use X5R or X7R. Voltage rating >= 1.8x rail voltage to maintain capacitance under DC bias.
- **BGA decoupling: caps on back side directly under power pins.** Via-in-pad recommended for larger caps. Use sub-0402 for fastest high-speed decoupling response.
- Per-IC decoupling strategy details -> `power/decoupling.md`.

### Configuration

- **iCE40 configuration modes are set by SPI_SS_B at POR.** SPI_SS_B = 0: boot from external SPI flash (Controller SPI mode). SPI_SS_B = 1: boot from internal NVCM.
- **External SPI flash must support 0x0B Fast Read command** with 24-bit start address and 8 dummy bits (iCE40). RP2040/RP2350 flash requirements differ -> `mcus/rp2040.md`.
- **Recommended SPI config flash for iCE40: Winbond W25Q32JVSS (32Mbit, 104MHz) or W25Q128JVSIQ (128Mbit).** Must support 0x0B Fast Read with 24-bit addressing. For ECP5: Winbond W25Q128JVSIQ or ISSI IS25LP128 (QSPI, 133MHz). Flash voltage must match FPGA SPI_VCC / VCCIO8 rail. Mismatched flash voltage or unsupported read commands are the #1 cause of ECP5/iCE40 boot failures in open-source designs.
- **ECP5 configuration pins pull-up/pull-down:** PROGRAMN: 4.7 kohm pull-up to VCCIO8. INITN: 4.7 kohm pull-up. MCLK/CCLK: 510 ohm to 1 kohm series resistor near TX side. CSSPIN: 4.7-10 kohm pull-up close to SPI flash. CFG[2:0]: 1-10 kohm as needed.
- **Always route JTAG to a programming header on every PCB** even if primary config is SPI/NVCM. Include VCC and GND on the header. JTAG pin treatment: TDI/TMS/TDO pull-up 4.7 kohm, TCK pull-down 4.7 kohm.
- **Leave unused configuration ports open** (ECP5). Connecting unused config pins can cause contention.

### IO Banking and Pin Assignment

- **Do not place fast-switching single-ended outputs in IO banks adjacent to SERDES channels.** SSO from 8 mA outputs toggling at 100 MHz couples ~30-50 mV into VCCA through PCB via mutual inductance in wire-bond packages. At 3.125 Gbps SERDES, 30 mV on a 1.2V rail adds ~25 ps deterministic jitter -- enough to close an eye diagram. Limit output count and drive strength in adjacent banks, or assign adjacent pins as static/ground.
- **Flip-chip packages are less sensitive to SSO than wire-bond** but still benefit from limiting output count and drive strength in banks adjacent to SERDES.
- **iCE40 LVDS inputs require external 100 ohm differential termination.** LVDS outputs need series resistors (Rs) and parallel resistor (Rp) network -- values computed from output driver specs in the LVDS usage guide.
- **High-speed signals: 5x trace-width clearance from other signals.** Layer transitions need ground vias (ground-ground reference) or stitching caps (power reference change).

### Clock Distribution

- **iCE40: use dedicated GBIN clock input pins.** GBIN7 and its associated PIO are best for direct differential clock inputs. Other GBIN pins can be used for single-ended clocks.
- **ECP5 reference clock oscillator: decouple supply with 100 nF + 10 uF close to oscillator.** Use dual-footprint PCB pad supporting both HCSL and LVDS oscillator packages for flexibility.
- **SERDES reference clock: use two center-tapped 50 ohm resistors to ground** for CML interface (LatticeECP2M/ECP3). LVPECL clock sources require external AC coupling (75-200 nF for PCIe, 20+ nF for 8b/10b/XAUI).

### DDR Memory Interfaces

- **DDR3/DDR4: use fly-by topology** (daisy chain from controller through Chip 0 to Chip N). Fly-by reduces SSN vs double-T topology. DDR protocol handles fly-by skew via write leveling.

> WARNING: Write leveling is mandatory for fly-by DDR3/DDR4 routing. Fly-by topology introduces intentional clock-to-data skew at each DRAM device -- without write leveling calibration, the controller cannot align DQS to CLK per-device. If your FPGA DDR controller does not support write leveling, you cannot use fly-by topology.

- **DDR3 impedance: 50-60 ohm single-ended, 100-120 ohm differential.** DDR4 adds 48 ohm option. On-die termination (ODT) in DRAM handles matching -- verify programmable settings match your trace impedance.
- **100 ohm differential termination at last SDRAM device in chain.** Route ADDR/CMD/CLK on same layer. Minimum 5 mm (200 mil) spacing between memory chips.
- **DDR4 additions vs DDR3:** new VPP supply (2.5V), removed VREFDQ input, POD (pseudo open-drain) instead of SSTL, added ACT_n control. DDR4 training/calibration is mandatory -- VDD calibration and write training must complete before timing specs are valid.
- **Include FPGA pin-package delay in length matching.** Large FPGAs add significant propagation delay through the package. Extract pin-package delay from vendor tools and include in total flight time calculations.
- **Data byte lanes routed on same layer.** DQS lines matched within byte lane. Swap data bits within a byte lane freely to simplify routing.

## Common Mistakes

- **Connecting iCE40 GNDPLL to board ground.** GNDPLL has internal DC connection -- external GNDPLL must NOT connect to board ground (unless the specific device/package lacks a dedicated GNDPLL ball). Violating this couples digital noise directly into PLL, causing excessive jitter.
- **Using switching regulator directly for SERDES analog supply.** Switching ripple at the PLL bandwidth adds deterministic jitter. If ripple frequency is below SERDES/PLL bandwidth, it passes through unfiltered. Always use LDO post-regulation or passive LC filter with cutoff a decade below switching frequency.
- **Single-ended outputs adjacent to SERDES degrading link quality.** SSO from GPIO toggling causes via-to-via coupling into VCCA power pins on PCB. Fix: assign these pins as "soft ground" (output buffer driving low, connected to ground plane), or use only differential/static signals in affected banks.
- **Omitting pin-package delay from DDR length matching.** Large BGA FPGAs add 200-800 ps propagation delay through bond wires and substrate traces, varying per pin. Length-matching PCB traces alone without extracting per-pin package delay from vendor tools causes DQ-to-DQS skew violations at DDR3-1600+ rates. Fix: export pin-package delays from the FPGA vendor's timing model and include them in total flight time calculations.
- **Not accounting for DDR4 VPP supply.** DDR4 requires a separate 2.5V VPP supply that DDR3 did not need. Missing this rail causes immediate DRAM failure.

## Formulas

**FPGA IO bank bulk decoupling estimate:** 100 IO pins switching simultaneously, 8 mA each, 2 ns edge, 50 mV ripple budget -> C_bulk >= 0.8A * 2ns / 50mV = 32 nF. Add 10x margin -> 330 nF bulk minimum per IO bank, plus per-pin 100 nF. Generic capacitor sizing formula and placement rules -> `power/decoupling.md`.

## Sources

### Related Rules

- `guides/passives.md` -- Ferrite bead LC resonance damping and passive component selection
- `power/decoupling.md` -- Per-IC decoupling strategy, capacitor sizing, and placement rules
- `mcus/rp2040.md` -- RP2040/RP2350 SPI flash configuration (shared flash requirements with iCE40)

### References

1. Lattice FPGA-TN-02038 -- ECP5 and ECP5-5G Hardware Checklist: https://0x04.net/~mwk/doc/lattice/ecp5/FPGA-TN-02038-2-0-ECP5-and-ECP5-5G-Hardware-Checklist.pdf
2. Lattice FPGA-TN-02006 -- iCE40 Hardware Checklist: https://0x04.net/~mwk/sbdocs/ice40/FPGA-TN-02006-2-3-iCE40-Hardware-Checklist.pdf
3. Lattice TN1114 -- Electrical Recommendations for Lattice SERDES: https://www.latticesemi.com/~/media/3E4AA60747DC46FC9EC26A9FD2F35894.ashx
4. TI SLYT598 -- Power Supply Sequencing for FPGAs: https://www.ti.com/lit/pdf/slyt598
5. Altium -- How to Start an FPGA PCB Layout For Your Embedded System: https://resources.altium.com/p/how-start-fpga-pcb-layout-your-embedded-system
6. Intel/Altera AN-662 -- Arria V and Cyclone V Design Guidelines: https://cdrdv2-public.intel.com/654271/an662.pdf
7. Altium -- Fly-by Topology for DDR3 and DDR4 Memory: Routing Guidelines: https://resources.altium.com/p/fly-topology-routing-ddr3-and-ddr4-memory
8. Micron TN-40-40 -- DDR4 Point-to-Point Design Guide: https://www.mouser.com/pdfDocs/Micron_DDR4_Design_Guide.pdf

# Nordic nRF52

> nRF52832 and nRF52840 supply, clock, RF and programming decisions tied to named specification revisions.

## Quick Reference

- **nRF52840 high-voltage supply goes to VDDH, not VDD.** Normal mode VDD is 1.7-3.6V, with >=1.75V required during power-on reset; high-voltage mode VDDH is 2.5-5.5V [2, Section 5.3.8.1].
- **nRF52840 REGOUT0 defaults to 1.8V.** GPIO levels follow VDD, so supplying VDDH from 5V does not establish 3.3V I/O [2, Sections 4.5.1.8,5.3.1.2].
- **nRF52832 QFAA/QFAB DC/DC reference circuit uses 10uH plus 15nH and 1uF at DEC4.** Populate the exact reference network before enabling DCDCEN [1, Sections 18.1,53.2].
- **32MHz crystal load capacitance is not each external capacitor.** The nRF52832 reference uses an 8pF-load crystal with two 12pF capacitors [1, Table 148].

## Design Rules

### Supply Modes and Decoupling

- **nRF52832 supports LDO operation without the external DC/DC inductors.** The DC/DC stage is disabled by default; enable it only on a board with the external components shown in the selected package's reference circuit [1, Sections 18.1,18.9.11,53].
- **For nRF52832 QFAA/QFAB, preserve the reference components rather than replacing every DEC capacitor with 100nF.** Table 148 gives C4/C5/C8=100nF, C7=100pF, C9=4.7uF and C10=1uF; its DC/DC inductors are 10uH +/-20% with rated DC current >=50mA, and 15nH +/-10% [1, Section 53.2, Table 148].
- **nRF52840 normal mode connects VDDH to VDD; high-voltage mode supplies VDDH and uses REG0's VDD output.** Do not drive VDD from a second supply while treating it as REG0's output [2, Section 5.3.1].
- **In nRF52840 high-voltage mode, include external load and GPIO current in REG0's budget.** Specification v1.1 allows 1mA in System OFF, 5mA when radio output exceeds +4dBm, and 25mA at <=+4dBm; these are not interchangeable operating conditions. Maintain VDDH - VDD >=0.3V [2, Sections 5.3.1.3,5.3.8.2].
- **Check effective, biased capacitance at the power pins.** nRF52840 v1.1 specifies effective VDD decoupling 2.7-5.5uF and DEC4 decoupling 0.7-1.3uF, with typical effective values 4.7uF and 1uF respectively [2, Section 5.3.8.1].

### Crystal Selection

- **For nRF52832 HFXO, use the ESR limit for the crystal's shunt capacitance.** Specification v1.8 lists 60 ohm at C0=7pF, 80 ohm at 5pF and 100 ohm at 3pF, with load capacitance <=12pF; the BLE tolerance requirement is +/-40ppm [1, Section 19.4.2].
- **nRF52840 v1.1 has a different HFXO table.** ESR is <=60 ohm for 3pF<C0<=7pF or <=100 ohm for C0<=3pF; BLE packet length <=200 bytes requires +/-40ppm, while >200 bytes requires +/-30ppm [2, Section 5.4.4.2].
- **For LFXO selection, both specifications limit load capacitance to 12.5pF, C0 to 2pF and ESR to 100K.** Drive-level limits differ: nRF52832 v1.8 lists 1uW, nRF52840 v1.1 lists 0.5uW. Select the crystal for the actual SoC [1, Section 19.4.4; 2, Section 5.4.4.3].
- **Account for SoC input capacitance when calculating crystal capacitors.** nRF52832 lists 4pF on XC1/XC2 while nRF52840 v1.1 lists 3pF; add PCB stray capacitance rather than copying a capacitor pair across devices [1, Section 19.4.2; 2, Section 5.4.4.2]. Full load-capacitance calculation -> `misc/crystal.md`.

### RF and GPIO

- **nRF52832 QFAA/QFAB's ANT match uses 3.9nH and 0.8pF, with C6 unmounted.** These are the chip-to-RF reference-network values, not a guarantee that a custom antenna is matched. Preserve the reference geometry and tune the antenna separately [1, Section 53.2, Table 148].
- **Keep radio-adjacent GPIO within the package-specific usage restrictions.** nRF52832 defines low-frequency I/O as <=10kHz and identifies pins for low drive; high-frequency, high-current switching near radio supply/antenna pins can degrade radio performance [1, Sections 4.3,20.2].
- **nRF52832 P0.09/P0.10 are NFC antenna pins (NFC1/NFC2) by factory default; write UICR NFCPINS.PROTECT = 0 to use them as GPIO.** NFCPINS resets to NFC mode on both nRF52832 and nRF52840, and the pins stay in NFC mode through power-on reset until the UICR setting applies. In NFC mode a protection circuit shorts the two pins together above about 2 V difference, so circuits driving them as unrelated GPIO misbehave on a blank part. As GPIO they have higher capacitance and leak between each other when at different levels; keep them at the same level before power-saving modes, and don't leave an NFC antenna connected [1, Sections 4.3.2,14.1.63; 2, Section 4.5.1.6].
- **Choose GPIO drive from guaranteed VOH/VOL at the actual VDD.** nRF52832 v1.8 specifies VOH>=VDD-0.4V and VOL<=VSS+0.4V at 0.5mA standard drive (VDD>=1.7V), 5mA high drive (VDD>=2.7V), or 3mA high drive (VDD>=1.7V); retain the package's radio restrictions [1, Sections 20.4.1,4.3].

### USB, Reset and Programming

- **nRF52840 VBUS powers the USB regulator separately from the core supply stages.** Both VBUS and a main supply are required; USB detection and regulator readiness are separate events, so wait for USBPWRRDY before enabling the USB pull-up [2, Section 5.3.2].
- **Keep SWDIO, SWDCLK, ground and target-voltage reference accessible.** SWD is the documented programming/debug path; connector wiring and reset access -> `guides/test-debug.md` [1, Section 16; 2, Section 4.8].
- **Configure both PSELRESET registers identically, with CONNECT=Connected, for pin reset.** Routing a reset switch to a GPIO alone does not enable pin-reset behavior; use the selected package's reset-capable pin and the documented UICR configuration [1, Sections 14.1.60-14.1.61,18.6.2; 2, Sections 4.5.1.4,5.3.6.2].

## Common Mistakes

- **Drawing external current from nRF52840 VDD in System OFF using the active-radio allowance.** The v1.1 specification explicitly reduces external current to 1mA in System OFF; include loads powered through GPIO in that total [2, Section 5.3.8.2, footnote 10].
- **Routing button, LED or bus signals to P0.09/P0.10 without setting UICR NFCPINS.** With NFCPINS at its 0xFFFFFFFF reset value they are NFC antenna pins, so the GPIO looks dead until NFCPINS.PROTECT is written to 0 [1, Sections 4.3.2,14.1.63].
- **Using synthesized LFCLK as a low-power substitute without checking consumption.** nRF52832 v1.8 lists LFSYNT at 100uA versus 0.25uA typical LFXO current; retaining the high-frequency clock changes the sleep budget [1, Sections 19.4.4-19.4.5].

## Sources

### Related Rules

- `misc/crystal.md` -- Crystal load and drive-level calculation.
- `misc/rf-antenna.md` -- Antenna matching and verification.
- `guides/test-debug.md` -- SWD access and programming fixtures.
- `power/decoupling.md` -- Effective capacitance under bias.

### References

1. Nordic Semiconductor -- nRF52832 Product Specification v1.8 (2021-11-01), including reference circuitry Section 53: https://www.mouser.com/datasheet/2/297/nRF52832_PS_v1_8-2942485.pdf
2. Nordic Semiconductor -- nRF52840 Product Specification v1.1, 4413_417 (2019-02-28): https://content.arduino.cc/assets/Nano_BLE_MCU-nRF52840_PS_v1.1.pdf

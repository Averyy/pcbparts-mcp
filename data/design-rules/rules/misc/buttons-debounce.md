# Buttons and Debounce

> Contact qualification, threshold-based RC debounce and reset-button constraints.

## Quick Reference

- **Debounce both press and release for the selected switch.** In an 18-switch measurement set, one pushbutton opened with 157ms bounce but closed within 20us; this is a measured outlier, not a universal debounce delay [1, pp.3-4].
- **Use SN74LVC1G17 for a deliberately slow RC edge.** TI recommends its Schmitt-trigger input for switch debounce; a plain CMOS buffer is not the same input circuit [2, p.1].
- **Internal pulls are not precision debounce resistors:** RP2040 lists 50-80K; ESP32 lists 45K typical at 3.3V/25 degrees C with no min/max; STM32F405/407 ordinary GPIO pulls are 30-50K, versus 7-14K on PA10/PB12, specified at VIN=VSS for pull-up and VIN=VDD for pull-down [7, Table 625; 4, Table 5-3; 5, Table 48].
- **Omron B3F specifies 5ms maximum bounce, not an all-switch guarantee.** Its switch ratings are separate from the MCU's input-current budget [3, Ratings/Characteristics].

## Design Rules

### Switch Qualification

- **Measure both edges and require a stable state before reporting another event.** Of the 18 switches in the cited measurements, 16 averaged 1.557ms and reached 6.2ms maximum, after excluding two longer-bouncing devices. Do not select a debounce interval from that average alone [1, pp.3-4].
- **Specify the actual B3F contact variant for dry switching.** The retrieved B3F sheet rates ordinary models at 1-50mA, 3-24VDC and B3F-G at 100uA-50mA, 3-24VDC; it separately gives 10uA at 1VDC as a minimum applicable load reference. Distinguish this reference from the rated operating range [3, Ratings/Characteristics].
- **Keep B3F within its 50mA at 24VDC resistive rating.** Do not use its signal contacts to switch an LED bank, motor or relay coil merely because the average current looks small [3, Ratings].

### RC and Schmitt Trigger

- **Check the RC topology's DC endpoint as well as its delay.** For the modeled circuit below (Rup from rail to Schmitt input, C from input to ground, Rswitch from input through the switch to ground), the closed switch leaves a divider voltage; input leakage also changes HIGH margin. The cited guidance requires checking leakage drop and limiting capacitor-discharge current, but the example is a separate circuit calculation [1, An RC Debouncer; 2, Design Considerations].
- **Work an actual threshold corner, not two arbitrary time constants.** At exactly 3V, SN74LVC1G17 Rev.Y lists VT+=1.48-1.92V and VT-=0.89-1.20V over -40 to +125 degrees C; its +/-5uA input-leakage limit is tested at VI=5.5V or GND, not throughout the RC ramp [6, Section 5.5].
- **Disable the MCU's internal pull when an external RC is dimensioned without it.** A 30-50K STM32 pull in parallel with a nominal 100K external pull changes charging resistance and the closed-switch divider; PA10/PB12 use a different pull range [5, Table 48].

### Reset and Exposed Controls

- **Separate long-press policy from electrical debounce.** STM32F405/407 NRST has its own pull-up and pulse-filter characteristics; an RC that suits an ordinary GPIO does not prove a valid reset pulse. Check NRST's minimum pulse width and external reset network [5, NRST pin characteristics].
- **For a hardware long-press reset, select a supervisor with specified manual-reset behavior.** Manual-reset debounce and reset-release delay are different specifications -> `protection/voltage-supervisor.md`.
- **For an exposed or off-board button, design the discharge path before the RC input.** Package HBM ratings are not an enclosure-level ESD qualification -> `protection/esd.md`.

## Common Mistakes

- **Treating every contact excursion as a clean digital pulse.** The cited measurements show analog wiping and intermediate levels as well as short pulses; an interrupt counter attached directly to the contact can report events that a slower sampled input never sees [1, pp.5-8].
- **Calling an RC network a guaranteed lockout timer.** Repeated short closures can accumulate capacitor discharge, and a short release can recharge only partly. Verify the measured bounce waveform against both threshold corners; the single-step example below does not prove immunity to every bounce train [1, RC Debouncer; 2, Design Considerations].

## Formulas

**Rule of thumb:** Select the required delay from the actual switch, then check both Schmitt thresholds and leakage; TI's nominal time-constant shortcut is not a guarantee [2, p.1; 6, Section 5.5].
**Formula:** For the modeled topology and constant Iin (positive into the input), Vclosed = (VDD/Rup - Iin) / (1/Rup + 1/Rswitch); Vopen = VDD - Iin*Rup. For a transition from V0 toward Vfinal, t = Rth*C*ln((V0 - Vfinal)/(Vthreshold - Vfinal)). Use Rup || Rswitch when closed and Rup when open; the threshold must lie between the initial and final voltages.
**Example:** Exactly 3V, Rup=100K, Rswitch=10K, C=1uF, ideal contact, nominal components and Iin=0: Vclosed=0.2727V, Rth_closed=9.091K. From fully open, VT-=1.20-0.89V gives 9.81-13.51ms to assert; from fully closed, VT+=1.48-1.92V gives 58.46-92.63ms to release. An assumed constant +/-5uA leakage gives final levels 0.227-0.318V closed and 2.5-3.5V open; these are sensitivity calculations, not guaranteed device bounds. Establish leakage over the actual input-voltage range and include rail limits, resistor tolerance and effective capacitance before claiming a guaranteed interval [6, Section 5.5].

## Sources

### Related Rules

- `protection/esd.md` -- User-accessible interfaces and ESD paths.
- `protection/voltage-supervisor.md` -- Manual reset and reset-release timing.
- `mcus/esp32.md` -- Boot straps that must remain valid during startup.

### References

1. A Guide to Debouncing, Rev.3 (June 2008): https://www.eng.utah.edu/~cs5780/debouncing.pdf
2. Texas Instruments -- Debounce a Switch, SCEA094 (October 2020): https://www.ti.com/lit/pdf/scea094
3. Omron -- B3F Tactile Switch (9-page edition, read 2026-11-09): https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3f.pdf
4. Espressif -- ESP32 Series Datasheet, Version 5.3: https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf
5. STMicroelectronics -- STM32F405xx/STM32F407xx, DS8626 Rev.12: https://www.st.com/resource/en/datasheet/stm32f405rg.pdf
6. Texas Instruments -- SN74LVC1G17, SCES351Y Rev.Y: https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf
7. Raspberry Pi -- RP2040 Datasheet, build 3184e62-clean (2025-02-20), Table 625: https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf

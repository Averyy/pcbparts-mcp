# I2C Bus

> Pull-up sizing, bus capacitance budget, level shifting, bus recovery, off-board protection.

## Quick Reference

- **Pull-ups: 4.7 kohm default (100 kHz, up to 250 pF at the nominal value; about 239 pF with a +5% resistor).** At 400 kHz, 200 pF allows 967 ohm-1.77 kohm at 3.3 V, so use 1.6 kohm; 2.2 kohm meets the rise-time limit only up to 160 pF. Include resistor tolerance, supply tolerance and the weakest device's sink capability [1, pp.3-5].
- **Capacitance is per SDA or SCL line:** 400 pF for Standard/Fast, 550 pF for Fast Plus; these limits do not guarantee that a passive pull-up has a valid resistance window [2, Table 10, pp.43-45].
- **Level shift: PCA9306 or TCA9406 for level-only translation.** A discrete N-MOSFET topology is specified for Standard/Fast mode; both sides need pull-ups [4, pp.2-3; 5, Section 5].
- **Hung SDA with SCL free: send up to 9 SCL pulses, then STOP.** If SDA stays low, use hardware reset or power-cycle; a stuck-low SCL requires reset or power cycling [7, p.2; 2, Section 3.1.16].
- **Off-board protection example: Wurth 742792693 ferrite + 824012823 TVS.** ANP121a measured 46 ns rise time both before and after adding this protection and 20 cm cable with 1 kohm pull-ups; this is a tested setup, not a universal no-effect guarantee [6, pp.3-5].

## Design Rules

### Pull-Up Resistor Selection

- **Size pull-ups for the weakest sink on the connected segment.** At VCC > 2 V, Standard/Fast mode guarantees 3 mA at VOL <= 0.4 V; Fast Plus specifies 20 mA at 0.4 V. At VCC <= 2 V, use the device's low-voltage specification: Fast/Fast Plus lists 0.2*VCC at 2 mA, not 3 mA or 20 mA [2, Table 10, p.43].
- **If Rp_max < Rp_min, no passive pull-up meets both constraints.** Reduce capacitance, add a suitable buffer, or change to a mode with a longer permitted rise time. For operation above the specified capacitance, derive a reduced clock rate from actual rise/fall times and the limiting device's HIGH/LOW times using UM10204 Section 7.2.1; simply assuming a slower clock fixes every timing constraint is insufficient [1, p.3; 2, pp.50-51].

### Bus Buffering and Multiplexing

- **Buffers (PCA9515, TCA9517): isolate capacitance.** Each side gets an independent 400 pF budget for Standard/Fast mode and needs its own valid pull-ups; check the selected buffer's voltage range and offset [3, pp.22-24; 5, Section 4].
- **Multiplexers (PCA9544, 4-ch):** solve address conflicts by enabling one downstream channel at a time. Only one channel active at once [3, pp.18-19].
- **Switches (PCA9548, 8-ch):** can enable multiple channels simultaneously but do NOT buffer capacitance. All active channels sum into total bus load [3, pp.18-20; 5, Section 3].
- **Do not connect two TCA9517 B sides together (A-B B-A topology).** The B-side static voltage offset prevents proper logic-low recognition. PCA9518 uses dedicated expansion signaling for a larger hub [5, Section 4.1.1; 3, pp.23-24].

### Level Shifting

- **The discrete N-MOSFET topology is for Standard and Fast mode (up to 400 kHz).** Gate to lower VDD, source to low side, drain to high side; choose a FET that conducts at the available gate voltage. AN10441 does not specify this topology for High-Speed mode [4, pp.2-3].
- **VDD2 must equal or exceed VDD1 in normal operation.** VDD2 < VDD1 is only acceptable during power sequencing transitions [4, p.3].
- **IC translators:** PCA9306, TCA9406 for level-only. PCA9548 also provides translation between sides [5, Sections 3.4, 5; 3, p.20].
- General level-shifting topology selection -> `misc/level-shifting.md`.

### Hung Bus Recovery

- **A controller reset during a read can leave a target driving SDA low.** Reinitializing only the controller peripheral does not finish the target's interrupted transfer [7, p.1].
- **Clock recovery applies when SDA is stuck and SCL can toggle.** Release SDA, clock SCL and check SDA after each pulse; issue STOP when it releases. AN-686 notes that recovery can need repetition and does not work on every target state machine [7, p.2; 2, Section 3.1.16].
- **Hardware power reset: ADG749 SPDT switch (SC70, 3.5 ohm on resistance at 5 V).** Connect the common terminal to target VDD, one throw to supply and the other to GND, so reset actively discharges the rail. AN-686's test used a 15 us control pulse with two targets and 1 uF, reaching within 0.1 V of GND in <10 us; size the pulse for the actual circuit [7, p.2, Figure 1].

### Off-Board Protection

- **Ferrite + TVS example for off-board I2C:** Wurth 742792693 (WE-CBF, 2.2 kohm at 100 MHz, 0603) and 824012823 (two-channel WE-TVS, 0.18 pF, DFN1210, 3.3 V). Check working voltage against the actual pull-up rail [6, pp.2,6].
- **Use ANP121a's measurements with their stated conditions.** Its 400 kHz setup used 1 kohm pull-ups; adding protection and 20 cm cable kept rise time at 46 ns, while adding 400 pF MLCCs increased it to 344 ns. Error-free operation in that test does not establish compliance with Fast-mode's 300 ns limit [6, pp.3-5; 2, Table 10].
- **A TVS residual voltage is not an allowable IC pin voltage.** ANP121a warns of residual voltage around 10 V and ESD currents >10 A; its ground-path recommendation does not establish that every attached IC survives that clamp waveform [6, p.2].
- **Long-cable figures are extender examples, not bare-bus limits.** AN10216 lists P82B715 with 50 ohm coax/twisted pair at 50 m/85 kHz, and P82B96 with telephone pairs/flat ribbon at 100 m/71 kHz or 1 km/31 kHz; verify the actual cable capacitance and timing [3, p.46].
- ESD protection placement and design -> `protection/esd.md`.

### Hot Insertion

- **For a card inserted into an active bus, use a hot-swap buffer such as PCA9511.** It isolates the card until STOP or bus idle occurs without contention on the card; ENABLE disconnects it and READY reports connection. PCA9512/13/14 are variants with different functions, not unconditional pin-compatible substitutes [3, pp.24-25,45-46].

### Address Conflicts

- **Use PCA9548 or PCA9544 when device address options are exhausted.** PCA9548 can enable multiple channels -- verify no address overlap across enabled channels [3, pp.18-19; 5, Section 3].

### SMBus Interop

- **SMBus timeout limits a prolonged SCL-low condition, not the total transaction length.** The legacy SMBus comparison in UM10204 gives 35 ms as the upper clock-stretch limit; check the actual SMBus device's timeout specification [2, Section 4.2.2, p.31].
- **Check input and output limits in both directions for mixed SMBus/I2C.** UM10204 compares legacy SMBus fixed 0.8 V/2.1 V thresholds with I2C's 0.3*VCC/0.7*VCC; its below-3 V warning is not a guarantee that every device pair above 3 V interworks [2, Section 4.2.1, pp.30-31].

### Series Protection

- **Series resistors are permitted if LOW-level margin and fall time still pass.** UM10204 includes 300 ohm as a protection example, not a default; include the resistor drop, pull-up resistance and bus capacitance in the calculation [2, Section 7.3, p.53].

## Common Mistakes

- **Combining MOSFET-side pull-ups without summing sink currents.** When either side pulls low, that device sinks current from both rails through the conducting FET; separately valid pull-ups can overload it together. Check combined current and the FET voltage drop against VOL [4, p.3, states 2-3].
- **Using an enabled PCA9515 to isolate slow devices from fast traffic.** An enabled buffer propagates the traffic. Disconnect the slow branch with a switch such as PCA9548 before the fast transfer, or keep the connected bus at the slowest device's rate [5, Section 3].

## Formulas

**Passive pull-up window [1, pp.3-5; 2, Table 10]:**
**Rule of thumb:** 4.7 kohm for Standard mode up to 250 pF at nominal (about 239 pF at +5%); 1.6 kohm for Fast mode at 200 pF with 3.3 V, 3 mA sinks. Account for tolerances before choosing a value near either boundary.
**Formula:** Rp_min = (VCC - VOL_max) / IOL; Rp_max = tr / (0.8473 * Cb)
  - tr: 1000 ns (Standard), 300 ns (Fast), 120 ns (Fast Plus), measured from 0.3*VCC to 0.7*VCC.
  - Cb is the capacitance of one bus line, including devices, traces, cable and protection; use actual component/cable data rather than a fixed pF/cm estimate.
**Example:** Fast mode, 3.3 V, 3 mA sink at 0.4 V, Cb = 200 pF: (3.3 - 0.4) / 0.003 = 967 ohm -> use 1 kohm minimum; 300e-9 / (0.8473 * 200e-12) = 1.77 kohm -> use 1.6 kohm (round down: 1.8 kohm is over the limit). At 5 V the same sink specification gives 1.53 kohm minimum, so 1.6 kohm needs a tolerance check there too.

## Sources

### Related Rules

- `misc/level-shifting.md` -- level-shifting topology selection for I2C and other interfaces
- `protection/esd.md` -- ESD protection placement and design for off-board connections

### References

1. TI SLVA689A (October 2026) -- I2C Bus Pullup Resistor Calculation: https://www.ti.com/lit/pdf/slva689
2. NXP UM10204 (Rev.7.0, October 2021) -- I2C-bus Specification and User Manual: https://www.nxp.com/docs/en/user-guide/UM10204.pdf
3. NXP AN10216-01 (March 2003) -- I2C Manual: https://www.nxp.com/docs/en/application-note/AN10216.pdf
4. Nexperia AN10441 (Rev.2, February 2020) -- Level Shifting Techniques in I2C-bus Design: https://assets.nexperia.com/documents/application-note/AN10441.pdf
5. TI SLVA787 (September 2016) -- Choosing the Correct I2C Device for New Designs: https://www.ti.com/lit/pdf/slva787
6. Wurth ANP121a (February 2023) -- Filter and Surge Protection for I2C Bus: https://www.we-online.com/components/media/o734709v410%20ANP121a%20%20Filter%20and%20surge%20protection%20for%20I2C%20Bus%20EN.pdf
7. ADI AN-686 (Rev.0, December 2003) -- Implementing an I2C Reset: https://www.analog.com/media/en/technical-documentation/application-notes/54305147357414AN686_0.pdf

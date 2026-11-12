# Battery Chemistry

> Choosing the right battery chemistry -- cell-specific voltage/current limits, cold operation, aging, and primary-cell pulse capability.

## Quick Reference

- **Charge limits belong to a cell model, not just a chemistry.** Panasonic NCR18650BF specifies CC/CV at 4.20V or 4.10V, standard 0.5CA and 10-45 degrees C; Lithium Werks ANR26650M1B specifies 3.6V with taper to 125mA [1, p.1; 2, p.2].
- **CR2032 pulse capability depends on the complete load profile.** TI measured only 9% average capacity reduction between its 15mA and 30mA peak tests, with 5ms active periods and 200ms sleep; this is not a continuous-current rating [3, pp.2-4].
- **100uF was TI's test capacitor, not a universal BLE default.** It improved effective capacity by >40% for one poor-performing vendor and 5-13% for the good-performing vendor tested [3, pp.6-7].
- **LFP cutoff is cell-specific.** ANR26650M1B lists 2.0V minimum discharge voltage; that does not establish a universal damage threshold or a 2.5V minimum BMS setting [2, p.2].

## Design Rules

### Chemistry Selection

- **Select a graphite-based Li-ion cell by its actual charge limits.** NCR18650BF's 10 degrees C minimum charging temperature is stricter than a generic 0 degrees C gate; its 0.5CA standard rate is not a generic 1C recommendation [1, p.1].
- **For an LFP power-cell example: ANR26650M1B.** Lithium Werks specifies 3A recommended and 10A maximum continuous charge (0-55 degrees C), 50A maximum continuous discharge and a 120A/10s discharge pulse (-30 to +55 degrees C). These ratings belong to that cell, not all LFP cells [2, p.2].
- **For low-temperature LTO operation: Toshiba SCiB.** Toshiba reports repeated charging/discharging at -30 degrees C, with operating range dependent on cell type. Its 20Ah-cell cycle example retains >=70% capacity after 20,000 cycles at 3C charge/discharge and 25 degrees C; neither a generic 5C charge rate nor a 2.85V cutoff follows from that example [4, p.1].
- **For removable AA/AAA rechargeable cells: low-self-discharge NiMH such as Eneloop.** ADI's historical hybrid-NiMH example loses about 15% charge in a year; use the selected cell's storage test rather than applying that estimate to every NiMH product [5, Choosing Battery Chemistry].

> WARNING: Do not put ANR26650M1B on a fixed 4.2V Li-ion charger. Its recommended charge voltage is 3.6V and listed float voltage is 3.45V; a 4S pack's total voltage does not ensure every cell remains within its individual limits. Use cell-voltage supervision and the exact cell's charge specification [2, p.2].

### Primary Cells

- **Panasonic CR2032 is rated 225mAh at 0.2mA continuous drain.** Its February 2026 sheet lists -30 to 85 degrees C and requires consultation for operation at >=70 degrees C. TI's older 220mAh test population is not the specification for every current CR2032 [6, p.1; 3, p.3].
- **LiSOCl2 pulse qualification must include aged cells.** Saft warns that fresh-cell pulse specifications at 20 degrees C do not predict aged IoT pulse response; qualify the actual pulse profile, temperature and storage history. A generic 1-5mA, 1-5s conditioning pulse is not a verified depassivation prescription [7, sections 1-6].
- **Alkaline sleep leakage can dominate replacement interval.** ADI identifies software power switches leaving tens of microamps as a failure case; include off-state current in the battery budget [5, Nonrechargeable: Alkaline].

### Discharge Characteristics

- **Do not infer discharge capability or cold derating from capacity and cylindrical format.** ANR26650M1B's 50A continuous rating belongs to that cell; NCR18650BF provides its own discharge-rate and temperature curves. Unnamed “Energy Cell” and “Power Cell” curves do not establish ratings for another cell [1, pp.2-3; 2, p.2].
- **Use pulse sag and recovery as end-of-life criteria.** TI stopped its CR2032 tests when loaded voltage fell below 2.0V; increasing internal resistance, rather than exhausted nameplate capacity alone, set usable life for its pulse profile [3, pp.2-5].

### Aging and Cycle Life

- **Reduced charge voltage trades capacity against a cell-specific aging curve.** NCR18650BF lists 3200mAh rated capacity at 20 degrees C for its 4.20V option and 2835mAh for 4.10V. This does not support a universal doubling of cycle life per 100mV or a universal optimum at 3.92V [1, pp.1, 4].
- **Keep cycle-life claims attached to their test conditions.** Lithium Werks lists >4000 cycles at 1C/1C, 100% DoD and room temperature for ANR26650M1B. Do not replace that qualification with a chemistry-wide DoD table or a rule that life halves every 10 degrees C [2, p.2].

### CR2032 for IoT

- **TI's vendor comparison used a specific accelerated RF profile.** It drew nominally 8mA for 2ms, 15mA or 30mA for 1ms, 8mA for 2ms, then 100uA for 200ms, using resistor loads dimensioned at 2.5V. Some vendors delivered only about 50% of the assumed 220mAh rating [3, pp.2-4].
- **The reported 30ohm/60ohm limits are test results without the parallel capacitor.** TI found approximately 30ohm at the 30mA peak and 60ohm at 15mA before reaching its 2.0V loaded cutoff; those values are not universal CR2032 end-of-life resistances [3, p.5].
- **TI's 100uF capacitor test targeted about 1kohm cell resistance.** The note says real BLE profiles can need 2-5 times less capacitance than its accelerated test. Check effective capacitance, load charge, minimum rail voltage and recharge time for the actual application [3, pp.6, 10-11].
- **Average current still controls energy consumption.** The 9% peak-current result holds for TI's stated duty cycle; it does not excuse increased pulse duration, repetition rate or sleep leakage [3, pp.2-4, 9].

## Common Mistakes

- **Applying a fixed chemistry-wide thermal-runaway temperature as a safety guarantee.** Lithium Werks reports cell-specific abuse-test outcomes, not an LFP temperature below which every assembled pack is safe. Its ANR26650M1B charging range is 0-55 degrees C; the sheet's separate below-zero 250mA note does not state a lower permitted temperature, so obtain clarification before specifying subzero charging [2, p.2].
- **Selecting a CR2032 capacitor from peak current alone.** Pulse duration and the time available for recharge determine whether voltage recovers before the next transmission; a capacitor that passes a single burst can still fail during repeated traffic [3, appendix A].
- **Treating a fresh LiSOCl2 pulse test as a lifetime qualification.** Saft shows that storage and aging change pulse response; a short high-current acceptance test cannot replace qualification with the application's aged-cell profile [7, section 6].

## Formulas

**CR2032 capacitor recharge time (ideal Thevenin model):**
**Rule of thumb:** Verify recharge time against the actual sleep interval; the formula assumes negligible sleep current, constant cell open-circuit voltage and internal resistance [3, appendix A, pp.10-11].
**Formula:** t = Ri * C * ln((Vp - Vmin) / (Vp - Vmax)), with Vp > Vmax.
**Example:** Ri = 1kohm, C = 100uF, Vp = 2.8V, Vmin = 2.0V, Vmax = 2.6V -> t = 138.6ms (139ms), not 169ms. With nonzero sleep current, use the asymptotic voltage Vp - I_sleep * Ri in place of Vp and require it to exceed Vmax.

## Sources

### Related Rules

- `power/battery.md` -- Charging circuits, BMS design, fuel gauging for the chosen chemistry

### References

1. Panasonic -- Specifications for NCR18650BF (four-page sheet, no revision stated): https://api.pim.na.industrial.panasonic.com/file_stream/main/fileversion/3446
2. Lithium Werks -- 26650 Lithium Ion Power Cell, ANR26650M1B (January 2019), manufacturer sheet hosted by distributor: https://a123batteries.com/product_images/uploaded_images/26650.pdf
3. TI SWRA349 -- Coin Cells and Peak Current Draw (unlettered revision): https://www.ti.com/lit/an/swra349/swra349.pdf
4. Toshiba -- Rechargeable Lithium-ion Battery SCiB brochure (five-page edition, no revision stated): https://www.global.toshiba/content/dam/toshiba/ww/products-solutions/battery/scib/pdf/ToshibaRechargeableBattery-en.pdf
5. ADI -- Match the Battery to the Application to Avoid Disappointment (web article; no revision stated): https://www.analog.com/en/resources/technical-articles/match-the-battery-to-the-application-to-avoid-disappointment.html
6. Panasonic -- CR2032 datasheet (February 2026): https://energy.panasonic.com/dam/master/pdf/en/datasheet/lithium/CR2032_Datasheet_EN.pdf
7. Saft -- How to Ensure a Solid Incoming Inspection of Your Primary Batteries? (18 February 2021, web article): https://saft.com/en/energizing-iot/how-ensure-solid-incoming-inspection-your-primary-batteries

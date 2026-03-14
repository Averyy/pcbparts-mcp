# Battery Chemistry

> Choosing the right battery chemistry -- voltage curves, C-rates, cycle life, aging, form factors, and primary cells.

## Quick Reference

- **Every 0.10V below 4.20V charge cutoff roughly doubles cycle life** (costs ~10% capacity per 70mV). Optimal longevity threshold: 3.92V/cell.
- **CR2032: 220mAh rated, 30mA peak OK with 100uF parallel cap.** Going 15mA to 30mA costs only 9% capacity. Parallel cap improves effective capacity >40% with poor-quality cells.
- **Calendar aging dominates: 25C/100% SoC = 80% capacity after 1 year.** 25C/40% SoC = 96%. Ship and store at 40% SoC.
- **Cold IR roughly doubles at 0C, triples at -20C.** For pulsed loads (BLE, GSM), IR sag is the binding constraint, not capacity loss.
- **LFP below 2.0V/cell = permanent damage.** Copper dissolution from anode current collector creates internal short risk. BMS cutoff at 2.5V minimum.

## Design Rules

### Chemistry Selection

- **If portable, < 2000 cycles, max energy density matters: NMC.** Default choice. NMC532 mainstream. NMC811 for highest density (220+ Wh/kg) but shortest cycle life and most thermal-abuse sensitive -- cobalt below ~10% requires tighter BMS control.
- **If cycle life > 1000, or safety-critical, or lead-acid replacement: LFP.** No thermal runaway at 270C. 4S = 12.8V drop-in for 12V lead-acid. Gotchas: higher self-discharge (3-5%/month) causes cell-to-cell divergence -- active balancing or periodic top-balance required. Flat discharge curve makes voltage-based SoC unreliable -> use coulomb counting.
- **If operating below -20C or need > 5000 cycles: LTO.** Zero-strain anode, no lithium plating. Safe at 5C charge. 80% capacity at -30C. 3000-7000 cycles. Cost ~2-3x NMC per kWh.
- **If max density and you have a robust BMS: NCA.** 200-260 Wh/kg, but same thermal runaway risk as LCO (150C).
- **If user-replaceable AA/AAA form factor: NiMH (Eneloop).** ~15%/year self-discharge. Standard NiMH is 30%/month -- unusable without charger cradle.
- **If EV with high pulse current + range: NMC/LMO blend.** 30% LMO for acceleration power (10C/30C pulse), 70% NMC for range.

> WARNING: LFP charging to 4.2V destroys cells. LFP max is 3.65V/cell. Charger ICs are NOT interchangeable between chemistries. 4S LFP at vehicle float (14.40V) = 3.60V/cell -- within tolerance short-term but prolonged float on long drives causes stress. Disconnect or reduce charge at 3.65V/cell.

### Li-ion Subtype Thermal Safety

| Subtype | Thermal runaway | Max C-rate |
|---------|-----------------|------------|
| LCO | 150C | 1C |
| LMO | 250C | 10C (30C pulse) |
| NMC | 210C | 1-2C |
| LFP | 270C | 25C (40A pulse) |
| NCA | 150C | 1C |
| LTO | Safest | 10C (30C pulse) |

### Primary Cells

- **LiMnO2 (CR2032, 3.0V): BLE/IoT default.** 280 Wh/kg, -30 to 60C, 10-20 year shelf life.
- **LiSOCl2 (3.6V): highest density primary (500+ Wh/kg).** -55 to 85C, industrial. Passivation layer on storage -- first load pulse sees voltage delay (seconds at cold temps). Apply conditioning pulse (1-5mA for 1-5 seconds) before main load. Can vent SO2 under sustained overdischarge. Not for consumer use.
- **Li-FeS2 (1.5V): AA alkaline replacement.** 300 Wh/kg, flat discharge curve, low IR. 15 year shelf life. Higher current capability than alkaline.
- **Alkaline: leak risk and sloping discharge.** Software power switches commonly leave 10s of uA leakage -- drains alkaline faster than expected. Must store charged (discharged storage causes permanent sulfation in lead-acid, corrosion in alkaline).

### Discharge Characteristics

- **Energy Cell (18650, 3200mAh): max 1C continuous.** At 2C, delivers only ~72% of rated capacity (2.3Ah vs 3.2Ah at 3.0V cutoff).
- **Power Cell (18650, 2000mAh): sustains 5C (10A).** Minimal capacity loss at 3.0V cutoff. Temp rises to ~50C at max load.
- **21700: up to 6.0Ah per cell** vs 3.9Ah for 18650. Lower IR, better thermal at high C-rates. Tesla/Panasonic/Samsung standardized on this format.
- **Cold derating (Energy Cell):** 0C = 83%, -10C = 66%, -20C = 53%.
- **Cold derating (Power Cell):** 0C = 92%, -10C = 85%, -20C = 80%.
- **Pulsed loads exploit capacitor-like HF behavior.** GSM draws 2A in 577us pulses. BLE draws 8-30mA peaks for 1-5ms -- within coin cell capability with parallel bypass cap. Battery recharges cap during sleep.
- **Pre-heat circuits (0.3-0.5C resistive): restore performance above -10C** in 5-15 minutes for cold environments.

### Aging and Cycle Life

**Charge voltage vs cycle life (cobalt-based):**

| V/cell | Cycles | Usable capacity |
|--------|--------|-----------------|
| 4.30V | 150-250 | ~110% (overcharge) |
| 4.20V | 300-500 | 100% |
| 4.10V | 600-1000 | ~90% |
| 4.00V | 850-1500 | 73% |
| 3.92V | 1200-2000 | 65% |

**DoD vs cycle life (to 70% remaining capacity):**

| DoD | NMC | LFP |
|-----|-----|-----|
| 100% | ~300 | ~600 |
| 80% | ~400 | ~900 |
| 60% | ~600 | ~1500 |
| 40% | ~1000 | ~3000 |
| 20% | ~2000 | ~9000 |

- **Calendar aging is independent of cycling.** 25C/40% SoC = 96% after 1 year. 25C/100% SoC = 80% after 1 year. 60C/100% SoC = 60% after 3 months. Life halves per ~10C above 25C.
- **Optimal longevity threshold: 3.92V/cell.** Battery experts believe this eliminates all voltage-related stresses. Going lower may not gain further benefits.
- **EV SoC window:** industry practice 85-25% (60% utilization) = ~2000 cycles. Chalmers University: reducing charge to 50% SoC extends EV battery lifetime 44-130%.
- **Ship at 40% SoC.** Cells > 100Wh or batteries > 300Wh require Class 9 dangerous goods shipping (UN3481/UN3480). Air shipment mandated at 30% SoC.
- **Charging to 4.30V/cell: 150-250 cycles.** Some NMC cells rated for 4.30-4.35V with new electrolyte additives -- verify datasheet explicitly supports it.

### Form Factors

- **Cylindrical (18650/21700): lowest $/Wh, 248 Wh/kg.** Built-in PTC, CID, vent. Cells spaced apart to prevent propagation. Does not change size with cycling.
- **Prismatic: swells.** 5mm cell swells to 8mm after 500 cycles. Firm enclosure required for compression. Capacities 20-50Ah for EV.
- **Pouch: 90-95% packaging efficiency (highest).** Swells 8-10% over 500 cycles. Needs mechanical support and stack pressure. Lay flat with expansion space -- do not stack. 3% swelling incidents reported on poor batch runs. Escaping gases (CO2, CO) can ignite if punctured near heat.

### CR2032 for IoT

- **220mAh rated but quality varies wildly.** Some vendors achieve only ~50% of rating. Difference between good and poor vendors dominates over peak current choice.
- **30mA peak OK: going 15mA to 30mA costs only 9% capacity.** The "15mA limit" is a myth. IR at 30mA: ~30 ohm limit. IR at 15mA: ~60 ohm limit. The steep IR incline at end-of-life explains why the capacity difference is small.
- **Parallel cap (100uF) improves capacity >40% with poor-quality cells**, 5-13% with good. Dimensioned for end-of-life IR of ~1kohm. Cap enables circuit to survive high IR by acting as primary power source during pulses.
- **Design for end-of-life IR (~30 ohm at 30mA)**, not fresh-cell IR. Battery recharges cap during sleep.
- **Minimize average current, not peak.** Sleep/quiescent draw dominates coin cell life. 10uA sleep leak matters more than 30mA TX pulse.

## Common Mistakes

- **Specifying by mAh without checking C-rate.** A 3200mAh Energy Cell maxes at 3.2A (1C). A 2000mAh Power Cell sustains 10A (5C). Oversizing with Energy Cells for high-current applications wastes money and volume.
- **LFP voltage-based SoC reporting shows "0%" with 20% capacity remaining.** LFP discharge curve is flat from 3.3V to 3.2V (covers 20-80% SoC). Voltage-based fuel gauges map this entire range to a few percent. Users see sudden death from "15%." Fix: coulomb counting mandatory for LFP; voltage correlation is useless except at extremes.
- **CR2032 without parallel cap in pulsed application.** End-of-life IR (~30 ohm) at 30mA = 0.9V sag. Battery voltage drops below MCU minimum during TX pulse. Cap recharge time must be verified against sleep interval.
- **Pouch cells without expansion allowance.** Allow 8-10% thickness growth over 500 cycles. Cracked displays, broken solder joints, and compromised safety otherwise. Do not stack -- lay flat with expansion space.
- **Charging NMC at 1C in cold warehouse (5-10C) without NTC gate.** Lithium plating begins below ~10C at 1C rate, but cell voltage and capacity look normal for the first 50-100 cycles. By cycle 150, internal shorts appear as sudden capacity cliff (30-50% drop in one cycle). IR measurement after charging shows no warning -- plating is invisible until dendrites bridge. Fix: NTC must reduce charge rate to 0.3C below 10C, hard-disable below 0C.
- **4S LFP pack drifts out of balance after seasonal storage.** LFP self-discharge (3-5%/month) is 3-5x higher than NMC (1%/month). After 3 months of storage, cell-to-cell divergence can reach 0.15V. On first charge, the highest cell hits 3.65V while the lowest is at 3.50V -- charger terminates early, leaving 10-15% capacity on the table permanently until rebalanced. Fix: top-balance before storage or use active balancing with periodic equalization cycles.
- **Alkaline cells venting inside sealed enclosure.** Alkaline electrolyte (KOH) leaks when cells reverse-discharge in series strings -- the weakest cell gets driven negative by stronger cells. In a 4xAA string, the first cell to deplete reverses at -0.2V while others are at 1.0V. KOH corrodes PCB traces, dissolves solder mask, and creates conductive residue that causes shorts weeks later. Fix: per-cell reverse-protection diode (1N5817) or undervoltage cutoff at 0.9V/cell minimum.

## Formulas

**CR2032 parallel cap sizing:**
**Rule of thumb:** 100uF ceramic across CR2032 for BLE pulse loads.
**Formula:** C = dQ / (Vmax - Vmin), where dQ = total pulse charge - (Vmin / Ri) * t_total
**Example:** BLE pulse: 8mA*2ms + 30mA*1ms + 8mA*2ms = 62uC. Depleted Ri = 1kohm, Vmax = 2.6V, Vmin = 2.0V. Battery supplies 10uC. Cap dQ = 52uC. C = 52uC / 0.6V = 87uF -> use 100uF.

**CR2032 cap recharge time:**
**Rule of thumb:** Verify recharge time < sleep interval (typically 100-200ms for BLE).
**Formula:** t = Ri * C * ln((Vp - Vmin) / (Vp - Vmax))
**Example:** Ri = 1kohm, C = 100uF, Vp = 2.8V, Vmin = 2.0V, Vmax = 2.6V -> t = 169ms.

**Temperature life derating:**
**Rule of thumb:** Cycle life halves per 10C above 25C.
**Formula:** cycle_life(T) = cycle_life_25C * 0.5^((T - 25) / 10)
**Example:** 1000 cycles at 25C -> at 45C: 1000 * 0.5^2 = 250 cycles

## Sources

### Related Rules

- `power/battery.md` -- Charging circuits, BMS design, fuel gauging for the chosen chemistry

### References

1. Battery University BU-205 -- Types of Lithium-ion: https://www.batteryuniversity.com/article/bu-205-types-of-lithium-ion/
2. Battery University -- What's the Best Battery?: https://www.batteryuniversity.com/article/whats-the-best-battery/
3. Battery University BU-501a -- Discharge Characteristics of Li-ion: https://www.batteryuniversity.com/article/bu-501a-discharge-characteristics-of-li-ion/
4. Battery University BU-808 -- How to Prolong Lithium-based Batteries: https://www.batteryuniversity.com/article/bu-808-how-to-prolong-lithium-based-batteries
5. Battery University BU-301a -- Types of Battery Cells: https://www.batteryuniversity.com/article/bu-301a-types-of-battery-cells/
6. Battery University BU-106a -- Choices of Primary Batteries: https://www.batteryuniversity.com/article/bu-106a-choices-of-primary-batteries/
7. ADI -- Match the Battery to the Application: https://www.analog.com/en/resources/technical-articles/match-the-battery-to-the-application-to-avoid-disappointment.html
8. TI SWRA349 -- Coin Cells and Peak Current Draw: https://www.ti.com/lit/an/swra349/swra349.pdf

---
source: "Battery University BU-410 -- Charging at High and Low Temperatures"
url: "https://www.batteryuniversity.com/article/bu-410-charging-at-high-and-low-temperatures/"
format: "HTML"
method: "fetchaller"
extracted: 2026-02-14
chars: 11677
---

# BU-410: Charging at High and Low Temperatures

Batteries operate over a wide temperature range, but this does not give permission to also charge them at these conditions. The charging process is more delicate than discharging and special care must be taken. Extreme cold and high heat reduce charge acceptance and the battery should be brought to a moderate temperature before charging.

Older battery technologies, such as lead acid and NiCd, have higher charging tolerances than newer systems, such as Li-ion. This allows them to charge below freezing at a reduced charge C-rate. When it comes to cold-charging NiCd is hardier than NiMH. Lead acid is also tolerant, but Li-ion needs special care.

**Table 1** summarizes the permissible charge and discharge temperatures of common rechargeable batteries.

| Battery Type | Charge Temperature | Discharge Temperature | Charge Advisory |
| --- | --- | --- | --- |
| Lead acid | -20 to 50 deg C (-4 to 122 deg F) | -20 to 50 deg C (-4 to 122 deg F) | Charge at 0.3C or less below freezing. Lower V-threshold by 3mV/deg C when hot. |
| NiCd, NiMH | 0 to 45 deg C (32 to 113 deg F) | -20 to 65 deg C (-4 to 149 deg F) | Charge at 0.1C between -18 deg C and 0 deg C. Charge at 0.3C between 0 deg C and 5 deg C. Charge acceptance at 45 deg C is 70%. Charge acceptance at 60 deg C is 45%. |
| Li-ion | 0 to 45 deg C (32 to 113 deg F) | -20 to 60 deg C (-4 to 140 deg F) | No charge permitted below freezing. Good charge/discharge performance at higher temperature but shorter life. |

**Table 1: Permissible temperature limits for various batteries.** Batteries can be discharged over a large temperature range, but the charge temperature is limited. For best results, charge between 10 deg C and 30 deg C (50 deg F and 86 deg F). Lower the charge current when cold.

### Low-temperature Charge

**Nickel Based:** Fast charging of most batteries is limited to 5 deg C to 45 deg C (41 deg F to 113 deg F). For best results consider narrowing the temperature bandwidth to between 10 deg C and 30 deg C (50 deg F and 86 deg F) as the ability to recombine oxygen and hydrogen diminishes when charging nickel-based batteries below 5 deg C (41 deg F). If charged too quickly, pressure builds up in the cell that can lead to venting. Reduce the charge current of all nickel-based batteries to 0.1C when charging below freezing.

Nickel-based chargers with NDV (negative delta V) full-charge detection offer some protection when fast charging at low temperatures. Poor charge acceptance when cold mimics a fully charged battery. This is in part caused by a high pressure buildup due to the reduced ability to recombine gases at low temperature. Pressure rise and a voltage drop at full charge appear synonymous.

To enable fast charging at all temperatures, some industrial batteries add a thermal blanket that heats the battery to an acceptable temperature; other chargers adjust the charge rate to prevailing temperatures. Consumer chargers do not have these provisions and the end user is advised to only charge at room temperature.

**Lead-acid:** Lead acid is reasonably forgiving when it comes to temperature extremes, as the starter batteries in our cars reveal. Part of this tolerance is credited to their sluggish behavior. The recommended charge rate at low temperature is 0.3C, which is almost identical to normal conditions. At a comfortable temperature of 20 deg C (68 deg F), gassing starts at charge voltage of 2.415V/cell. When going to -20 deg C (0 deg F), the gassing threshold rises to 2.97V/cell.

A lead acid battery charges at a constant current to a set voltage that is typically 2.40V/cell at ambient temperature. This voltage is governed by temperature and is set higher when cold and lower when warm. Figure 2 illustrates the recommended settings for most lead acid batteries. In parallel, the figure also shows the recommended float charge voltage to which the charger reverts when the battery is fully charged. When charging lead acid at fluctuating temperatures, the charger should feature voltage adjustment to minimize stress on the battery.

**Figure 2: Cell voltages on charge and float at various temperatures.** Charging at cold and hot temperatures requires adjustment of voltage limit.

Freezing a lead acid battery leads to permanent damage. Always keep the batteries fully charged because in the discharged state the electrolyte becomes more water-like and freezes earlier than when fully charged. According to BCI (Battery Council International), a specific gravity of 1.15 has a freezing temperature of -15 deg C (5 deg F). This compares to -55 deg C (-67 deg F) for a specific gravity of 1.265 with a fully charged starter battery. Flooded lead acid batteries tend to crack the case and cause leakage if frozen; sealed lead acid packs lose potency and only deliver a few cycles before they fade and need replacement.

**Lithium Ion:** Li-ion can be fast charged from 5 deg C to 45 deg C (41 to 113 deg F). Below 5 deg C, the charge current should be reduced, and no charging is permitted at freezing temperatures because of the reduced diffusion rates on the anode. During charge, the internal cell resistance causes a slight temperature rise that compensates for some of the cold. The internal resistance of all batteries rises when cold, prolonging charge times noticeably. This also affects discharge performance noticeably with Li-ion.

Many battery users are unaware that consumer-grade lithium-ion batteries cannot be charged below 0 deg C (32 deg F). Although the pack appears to be charging normally, plating of metallic lithium occurs on the anode during a sub-freezing charge that leads to a permanent degradation in performance and safety. Batteries with lithium plating are more vulnerable to failure if exposed to vibration or other stressful conditions. Advanced chargers prevent charging Li-ion below freezing.

Advancements are being made to charge Li-ion below freezing temperatures. Charging is indeed possible with most lithium-ion cells but only at very low currents. According to research papers, the allowable charge rate at -30 deg C (-22 deg F) is 0.02C. At this low current, the charge time would stretch to over 50 hours, a time that is deemed impractical. There are, however, specialty Li-ions that can charge down to -10 deg C (14 deg F) at a reduced rate.

Some Li-ion manufacturers offer custom-made cells for cold-charging. Specialty chargers will also be needed that decrease the C-rate according to temperature and charge the battery to a lower voltage peak; 4.00V/cell rather than the customary 4.20V/cell for example. Such limitations decrease the energy a Li-ion battery can hold to roughly 80% instead of the customary 100%. Charge times will also be prolonged and can last 12 hours and longer when cold.

Li-ion batteries charging below 0 deg C (32 deg F) must undergo regulatory issue to certify that no lithium plating will occur. In addition, a specially designed charger will keep the allotted current and voltage within a safe limit throughout the temperature bandwidth. Certification of such batteries and chargers are very costly that will reflect in the price. Similar regulatory requirements also apply to intrinsically safe batteries.

There are cell and charger manufacturers claiming to charge Li-ion at low temperatures; however, most companies do not want to take the risk of potential failure and assume liability. Yes, Li-ion will charge at low temperature but research labs dissecting these batteries see concerning results.

### High-temperature Charge

Heat is the worst enemy of batteries, including lead acid. Adding temperature compensation on a lead acid charger to adjust for temperature variations is said to prolong battery life by up to 15 percent. The recommended compensation is a 3mV drop per cell for every degree Celsius rise in temperature. If the float voltage is set to 2.30V/cell at 25 deg C (77 deg F), the voltage should read 2.27V/cell at 35 deg C (95 deg F). Going colder, the voltage should be 2.33V/cell at 15 deg C (59 deg F). These 10 deg C adjustments represent 30mV change.

**Table 3** indicates the optimal peak voltage at various temperatures when charging lead acid batteries. The table also includes the recommended float voltage while in standby mode.

| Battery Status | -40 deg C (-40 deg F) | -20 deg C (-4 deg F) | 0 deg C (32 deg F) | 25 deg C (77 deg F) | 40 deg C (104 deg F) |
| --- | --- | --- | --- | --- | --- |
| Voltage limit on recharge | 2.85V/cell | 2.70V/cell | 2.55V/cell | 2.45V/cell | 2.35V/cell |
| Float voltage at full charge | 2.55V/cell or lower | 2.45V/cell or lower | 2.35V/cell or lower | 2.30V/cell or lower | 2.25V/cell or lower |

**Table 3: Recommended voltage limits when charging and maintaining stationary lead acid batteries on float charge.** Voltage compensation prolongs battery life when operating at temperature extremes.

Charging nickel-based batteries when warm lowers oxygen generation that reduces charge acceptance. Heat fools the charger into thinking that the battery is fully charged when it's not. Figure 4 shows a strong decrease in charge efficiency from the "100 percent efficiency line" when dwelling above 30 deg C (86 deg F). At 45 deg C (113 deg F), the battery can only accept 70 percent of its full capacity; at 60 deg C (140 deg F) the charge acceptance is reduced to 45 percent. NDV for full-charge detection becomes unreliable at higher temperatures, and temperature sensing is essential for backup.

**Figure 4: NiCd charge acceptance as a function of temperature.** High temperature reduces charge acceptance and departs from the dotted "100% efficiency line." At 55 deg C, commercial NiMH has a charge efficiency of 35--40%; newer industrial NiMH attains 75--80%.

Lithium-ion performs well at elevated temperatures but prolonged exposure to heat reduces longevity. Charging and discharging at elevated temperatures is subject to gas generation that might cause a cylindrical cell to vent and a pouch cell to swell. Many chargers prohibit charging above 50 deg C (122 deg F).

Some lithium-based packs are momentarily heated to high temperatures. This applies to batteries in surgical tools that are sterilized at 137 deg C (280 deg F) for up to 20 minutes as part of autoclaving. Oil and gas drilling as part of fracking also exposes the battery to high temperatures.

Capacity loss at elevated temperature is in direct relationship with state-of-charge (SoC). Figure 5 illustrates the effect of Li-cobalt (LiCoO2) that is first cycled at room temperature (RT) and then heated to 130 deg C (266 deg F) for 90 minutes and cycled at 20, 50 and 100 percent SoC. There is no noticeable capacity loss at room temperature. At 130 deg C with a 20 percent SoC, a slight capacity loss is visible over 10 cycles. This loss is higher with a 50 percent SoC and shows a devastating effect when cycled at full charge.

**Figure 5: Capacity loss at room temperature (RT) and 130 deg C for 90 minutes.** Sterilization of batteries for surgical power tools should be done at low SoC.

CAUTION: In case of rupture, leaking electrolyte or any other cause of exposure to the electrolyte, flush with water immediately. If eye exposure occurs, flush with water for 15 minutes and consult a physician immediately.

### References

[1] Source: Betta Batteries
[2] Courtesy of Cadex
[3] Source: Greatbatch Medical

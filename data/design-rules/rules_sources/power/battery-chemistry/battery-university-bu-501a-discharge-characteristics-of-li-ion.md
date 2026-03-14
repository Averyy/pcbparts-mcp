---
source: "Battery University BU-501a -- Discharge Characteristics of Li-ion"
url: "https://www.batteryuniversity.com/article/bu-501a-discharge-characteristics-of-li-ion/"
format: "HTML"
method: "fetchaller"
extracted: 2026-02-14
chars: 7765
---

# BU-501a: Discharge Characteristics of Li-ion

The early Li-ion battery was considered fragile and unsuitable for high loads. This has changed, and today lithium-based systems stand shoulder to shoulder with the robust nickel and lead chemistries. Two basic types of Li-ion have emerged: The Energy Cell and the Power Cell.

The performance of these two battery types is characterized by energy storage, also known as capacity, and current delivery, also known as loading or power. Energy and power characteristics are defined by particle size on the electrodes. Larger particles increase the surface area for maximum capacity and fine material decreases it for high power.

Decreasing particle size lowers the presence of electrolyte that fills the voids. The volume of electrolyte within the cell determines battery capacity. Decreasing the particle size reduces the voids between the particles, thereby lowering the electrolyte content. Too little electrolyte reduces ionic mobility and affects performance. Think of a drying felt pen that needs recuperating to keep marking papers.

### Li-ion Energy Cell

The Li-ion Energy Cell is made for maximum capacity to provide long runtimes. The Panasonic NCR18650B Energy Cell (Figure 1) has high capacity but is less enduring when discharged at 2C. At the discharge cutoff of 3.0V/cell, the 2C discharge produces only about 2.3Ah rather than the specified 3.2Ah. This cell is ideal for portable computing and similar light duties.

**Figure 1: Discharge characteristics of NCR18650B Energy Cell by Panasonic**
The 3,200mAh Energy Cell is discharged at 0.2C, 0.5C, 1C and 2C. The circle at the 3.0V/cell line marks the end-of-discharge point at 2C.

Cold temperature losses:
- 25 deg C (77 deg F) = 100%
- 0 deg C (32 deg F) = ~83%
- -10 deg C (14 deg F) = ~66%
- -20 deg C (4 deg F) = ~53%

### Li-ion Power Cell

The Panasonic UR18650RX Power Cell (Figure 2) has a moderate capacity but excellent load capabilities. A 10A (5C) discharge has minimal capacity loss at the 3.0V cutoff voltage. This cell works well for applications requiring heavy load current, such as power tools.

**Figure 2: Discharge characteristics of UR18650RX Power Cell by Panasonic**
The 1950mAh Power Cell is discharged at 0.2C, 0.5C, 1C and 2C and 10A. All reach the 3.0V/cell cut-off line at about 2000mAh. The Power Cell has moderate capacity but delivers high current.

Cold temperature losses:
- 25 deg C (77 deg F) = 100%
- 0 deg C (32 deg F) = ~92%
- -10 deg C (14 deg F) = ~85%
- -20 deg C (4 deg F) = ~80%

The Li-ion Power Cell permits a continuous discharge of 10C. This means that an 18650 cell rated at 2,000mAh can provide a continuous load of 20A (30A with Li-phosphate). The superior performance is achieved in part by lowering the internal resistance and by optimizing the surface area of active cell materials. Low resistance enables high current flow with minimal temperature rise. Running at the maximum permissible discharge current, the Li-ion Power Cell heats to about 50 deg C (122 deg F); the temperature is limited to 60 deg C (140 deg F).

To meet the loading requirements, the pack designer can either use a Power Cell to meet the discharge C-rate requirement or go for the Energy Cell and oversize the pack. The Energy Cell holds about 50 percent more capacity than the Power Cell, but the loading must be reduced. This can be done by oversizing the pack, a method the Tesla EVs use. The battery achieves exceptional runtime but it gets expensive and heavy.

### LiFePO4 Power Cell

Lithium iron phosphate (LiFePO4) is also available in the 18650 format offering high cycle life and superior loading performance, but low specific energy (capacity). Table 3 compares specifications of common lithium-based architectures.

| Chemistry | Nominal V | Capacity | Energy | Cycle life | Loading | Note |
| --- | --- | --- | --- | --- | --- | --- |
| Li-ion Energy | 3.6V/cell | 3,200mAh | 11.5Wh | ~1000 | 1C (light load only) | Slow charge (<1C) |
| Li-ion Power | 3.6V/cell | 2,000mAh | 7.2Wh | ~1000 | 5C (continuous large load) | Good temp. range |
| LiFePO4 | 3.3V/cell | 1,200mAh | 3.9Wh | ~2000 | 25C (very large cont. load) | Robust, safe |

**Table 3: Maximizing capacity, cycle life and loading with lithium-based battery architectures**

### Discharge Signature

One of the unique qualities of nickel- and lithium-based batteries is the ability to deliver continuous high power until the battery is exhausted; a fast electrochemical recovery makes it possible. Lead acid is slower and this can be compared to a drying felt pen that works for short markings on paper and then needs rest to replenish the ink. While the recovery is relatively fast on discharge, and this can be seen when cranking the engine, the slow chemical reaction becomes obvious when charging. This only gets worse with age.

A battery may discharge at a steady load of, say, 0.2C as in a flashlight, but many applications demand momentary loads at double and triple the battery's C-rating. GSM (Global System for Mobile Communications) for a mobile phone is such an example (Figure 4). GSM loads the battery with up to 2A at a pulse rate of 577 micro-seconds. This places a large demand on a small battery; however, with a high frequency, the battery begins to behave more like a large capacitor and the battery characteristics change.

**Figure 4: GSM discharge pulses of a cellular phone**
The 577 microsecond pulses drawn from the battery adjust to field strength and can reach 2 amperes.

In terms of longevity, a battery prefers moderate current at a constant discharge rather than a pulsed or momentary high load. Figure 5 demonstrates the decreasing capacity of a NiMH battery at different load conditions from a gentle 0.2C DC discharge, an analog discharge to a pulsed discharge. Most batteries follow a similar pattern in terms of load conditions, including Li-ion.

**Figure 5: Cycle life of NiMH under different load conditions**
NiMH performs best with DC and analog loads; digital loads lower the cycle life. Li-ion behaves similarly.

Figure 6 examines the number of full cycles a Li-ion Energy Cell can endure when discharged at different C-rates. At a 2C discharge, the battery exhibits far higher stress than at 1C, limiting the cycle count to about 450 before the capacity drops to half the level.

**Figure 6: Cycle life of Li-ion Energy Cell at varying discharge levels**
The wear and tear of all batteries increases with higher loads. Power Cells are more robust than Energy Cells.

### Simple Guidelines for Discharging Batteries

- Heat increases battery performance but shortens life by a factor of two for every 10 deg C increase above 25--30 deg C (18 deg F above 77--86 deg F). Always keep the battery cool.
- Prevent over-discharging. Cell reversal can cause an electrical short.
- On high load and repetitive full discharges, reduce stress by using a larger battery.
- A moderate DC discharge is better for a battery than pulse and heavy momentary loads.
- A battery exhibits capacitor-like characteristics when discharging at high frequency. This allows higher peak currents than is possible with a DC load.
- Nickel- and lithium-based batteries have a fast chemical reaction; lead acid is sluggish and requires a few seconds to recover between heavy loads.
- All batteries suffer stress when stretched to maximum permissible tolerances.

### References

[1] Source: Panasonic
[2] Courtesy of Cadex
[3] Source: Zhang (1998)
[4] Source: Choi et al (2002)

---
source: "Battery University BU-409 -- Charging Lithium-ion"
url: "https://www.batteryuniversity.com/article/bu-409-charging-lithium-ion/"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 8117
---

The capacity trails the charge voltage like lifting a heavy weight with a rubber band.

Estimating SoC by reading the voltage of a charging battery is impractical; measuring the open circuit voltage (OCV) after the battery has rested for a few hours is a better indicator. As with all batteries, temperature affects the OCV, so does the active material of Li-ion. SoC of smartphones, laptops and other devices is estimated by coulomb counting. (See [BU-903: How to Measure State-of-charge](https://battery-university.ddev.site/article/how-to-measure-state-of-charge))

Li-ion cannot absorb overcharge. When fully charged, the charge current must be cut off. A continuous trickle charge would cause plating of metallic lithium and compromise safety. To minimize stress, keep the lithium-ion battery at the peak cut-off as short as possible.

Once the charge is terminated, the battery voltage begins to drop. This eases the voltage stress. Over time, the open circuit voltage will settle to between 3.70V and 3.90V/cell. Note that a Li-ion battery that has received a fully saturated charge will keep the voltage elevated for a longer than one that has not received a saturation charge.

When lithium-ion batteries must be left in the charger for operational readiness, some chargers apply a brief topping charge to compensate for the small self-discharge the battery and its protective circuit consume. The charger may kick in when the open circuit voltage drops to 4.05V/cell and turn off again at 4.20V/cell. Chargers made for operational readiness, or standby mode, often let the battery voltage drop to 4.00V/cell and recharge to only 4.05V/cell instead of the full 4.20V/cell. This reduces voltage-related stress and prolongs battery life.

Some portable devices sit in a charge cradle in the ON position. The current drawn through the device is called the *parasitic load* and can distort the charge cycle. Battery manufacturers advise against parasitic loads while charging because they induce mini-cycles. This cannot always be avoided and a laptop connected to the AC main is such a case. The battery might be charged to 4.20V/cell and then discharged by the device. The stress level on the battery is high because the cycles occur at the high-voltage threshold, often also at elevated temperature.

A portable device should be turned off during charge. This allows the battery to reach the set voltage threshold and current saturation point unhindered. A parasitic load confuses the charger by depressing the battery voltage and preventing the current in the saturation stage to drop low enough by drawing a leakage current. A battery may be fully charged, but the prevailing conditions will prompt a continued charge, causing stress.

### **Charging Non-cobalt-blended Li-ion**

While the traditional lithium-ion has a nominal cell voltage of 3.60V, Li-phosphate (LiFePO) makes an exception with a nominal cell voltage of 3.20V and charging to 3.65V. Relatively new is the Li-titanate (LTO) with a nominal cell voltage of 2.40V and charging to 2.85V. (See [BU-205: Types of Lithium-ion](https://battery-university.ddev.site/article/types-of-lithium-ion))

Chargers for these non cobalt-blended Li-ions are not compatible with regular 3.60-volt Li-ion. Provision must be made to identify the systems and provide the correct voltage charging. A 3.60-volt lithium battery in a charger designed for Li-phosphate would not receive sufficient charge; a Li-phosphate in a regular charger would cause overcharge.

### **Overcharging Lithium-ion**

Lithium-ion operates safely within the designated operating voltages; however, the battery becomes unstable if inadvertently charged to a higher than specified voltage. Prolonged charging above 4.30V on a Li-ion designed for 4.20V/cell will plate metallic lithium on the anode. The cathode material becomes an oxidizing agent, loses stability and produces carbon dioxide (CO2). The cell pressure rises and if the charge is allowed to continue, the current interrupt device (CID) responsible for cell safety disconnects at 1,000–1,380kPa (145–200psi). Should the pressure rise further, the safety membrane on some Li-ion bursts open at about 3,450kPa (500psi) and the cell might eventually vent with flame. (See [BU-304b: Making Lithium-ion Safe](http://www.batteryuniversity.com/article/bu-304b-making-lithium-ion-safe/))

Venting with flame is connected with elevated temperature. A fully charged battery has a lower thermal runaway temperature and will vent sooner than one that is partially charged. All lithium-based batteries are safer at a lower charge, and this is why authorities will mandate air shipment of Li-ion at 30 percent state-of-charge rather than at full charge. (See [BU-704a: Shipping Lithium-based Batteries by Air](http://www.batteryuniversity.com/article/bu-704a-shipping-lithium-based-batteries-by-air/))

The threshold for Li-cobalt at full charge is 130–150ºC (266–302ºF); nickel-manganese-cobalt (NMC) is 170–180ºC (338–356ºF) and Li-manganese is about 250ºC (482ºF). Li-phosphate enjoys similar and better temperature stabilities than manganese. (See also [BU-304a: Safety Concerns with Li-ion](https://bu2.ddev.site/article/bu-304a-safety-concerns-with-li-ion) and [BU-304b: Making Lithium-ion Safe](https://bu2.ddev.site/article/bu-304b-making-lithium-ion-safe))

Lithium-ion is not the only battery that poses a safety hazard if overcharged. Lead- and nickel-based batteries are also known to melt down and cause fire if improperly handled. Properly designed charging equipment is paramount for all battery systems and temperature sensing is a reliable watchman.

### **Summary**

Charging lithium-ion batteries is simpler than nickel-based systems. The charge circuit is straight forward; voltage and current limitations are easier to accommodate than analyzing complex voltage signatures, which change as the battery ages. The charge process can be intermittent, and Li-ion does not need saturation as is the case with lead acid. This offers a major advantage for renewable energy storage such as a solar panel and wind turbine, which cannot always fully charge the battery. The absence of trickle charge further simplifies the charger. Equalizing charger, as is required with lead acid, is not necessary with Li-ion.

Consumer and most industrial Li-ion chargers charge the battery fully. They do not offer adjustable end-of-charge voltages that would prolong the service life of Li-ion by lowering the end charge voltage and accepting a shorter runtime. Device manufacturers fear that such an option would complicate the charger. Exceptions are [electric vehicles](https://battery-university.ddev.site/article/electric-vehicle-ev) and [satellites](https://battery-university.ddev.site/article/batteries-for-medical-consumer-hobbyist) that avoid full charge to achieve long service life.

### **Simple Guidelines for Charging Lithium-based Batteries**

* Turn off the device or disconnect the load on charge to allow the current to drop unhindered during saturation. A parasitic load confuses the charger.
* Charge at a moderate temperature. Do not charge at freezing temperature. (See [BU-410: Charging at High and Low Temperatures](https://battery-university.ddev.site/article/charging-at-high-and-low-temperatures))
* Lithium-ion does not need to be fully charged; a partial charge is better.
* Not all chargers apply a full topping charge and the battery may not be fully charged when the “ready” signal appears; a 100 percent charge on a fuel gauge may be a lie.
* Discontinue using charger and/or battery if the battery gets excessively warm.
* Apply some charge to an empty battery before storing (40–50 percent SoC is ideal). (See [BU-702: How to Store Batteries](https://battery-university.ddev.site/article/how-to-store-batteries).)

### **References**

**[1]** Courtesy of Cadex
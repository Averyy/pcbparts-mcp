---
source: "EDN -- Protecting Against Reverse Polarity (Part 2)"
url: "https://www.edn.com/protecting-against-reverse-polarity-methods-examined-part-2/"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 12265
---

**Method 6: Schottky to Ground**

The Schottky to Ground method is nearly identical to the Diode to Ground method described above. It requires that the potential source of reverse polarity be well understood, and that the Schottky be sized accordingly.

Compared to the Diode to Ground method, the Schottky to Ground method offers slightly improved protection of downstream ICs due to the lower reverse bias clamping voltage. It's something to try if a traditional diode is incapable of protecting the downstream electronics.

It's important to note that, even though this method has a lower voltage drop, it doesn't always reduce the power handling requirements of the device. If the reverse-bias power sources are current limited, this method will generate less heat. However, many power sources are power limited, not current limited. If the reverse-bias power source is power limited, this method will pull more current to dissipate similar power.

**Figure 6**  The Schottky to Ground Method

*Strengths*

* Similar to the Diode to Ground method

*Limitations*

* Similar to the Diode to Ground method
* May have higher leakage currents during normal operation

**Method 7: Schottky to Ground and PTC resistor**

From a reverse bias perspective, the Schottky to Ground and PTC resistor method is similar to the TVS and PTC resistor method but, due to the lower forward voltage drop of the Schottky, a smaller Schottky or higher current limit PTC resistor can be used when matching the two devices. Eliminating the TVS means this approach does not offer the same over-voltage transient protection as the TVS and PTC method.

Unfortunately, use of a PTC resistor will still add series resistance to the circuit.

**Figure 7**

The Schottky to Ground and PTC Method

*Strengths*

* Similar to the TVS and PTC resistor method

*Limitations*

* Similar to the TVS and PTC resistor method, however no controlled overvoltage protection

**Method 8: Series MOSFET**

Where power losses and voltage drops are a concern, MOSFETs are a good choice. As with most series solutions, series MOSFETs are blocking devices and therefore dissipate very little power when blocking. However, they are typically not optimized for the protection of reverse polarity and that can make them complicated to implement in this application.

MOSFETs can be configured to effectively block a reverse-polarity power source. A significant advantage they offer it that they do not dissipate significant power during a reverse-bias event and, as a result, can protect against a very wide range of reverse-bias power sources.

During normal positive bias operation, a MOSFET’s primary advantage over other series solutions discussed (diodes, PTCs, fuses) is that it can be implemented with lower resistance levels without sacrificing protection. This is because MOSFETs do not require series resistance or series voltage drop as a fundamental principle of operation. The series resistance becomes a cost/performance tradeoff, made by the system designer, and not a fundamental requirement of the device or protection methodology. This makes MOSFETs a very effective solution where system efficiency is a critical requirement. MOSFETs can also offer additional features like power switching.

One down side to using a MOSFET is that it may not be optimized or specified for protection against reverse polarity. The critical specs to evaluate performance in this application may be missing and this leaves the designer in the uncomfortable situation of having to draw estimates from the performance characteristics on the data sheet and guessing about safe operating windows. Also, depending on how the MOSFETs are implemented, they may require a controller or other costly functions.

**Figure 8**  The Series MOSFET Method

*Strengths*

* Low (user-defined) series resistance and voltage drop
* Small form factor
* Resettable blocking function

*Limitations*

* Complexity of implementation
* Total solution cost

**Method 9: Multi-Function, Monolithic ICs**

Multi-function, monolithic ICs that include protection for reverse polarity have become popular in mobile phones, and front-end ICs are being rated to higher and higher capabilities for reverse polarity.

Multi-function ICs can offer all the benefits of a MOSFET and other series-protection solutions, and at the same time deliver additional IC-based features. Unfortunately, the ability to operate in both a positive bias environment and then operate or survive in reverse polarity mode typically adds significant circuit complexity, and therefore comes with significant performance and/or cost penalties. Due to the cost/performance tradeoff, typical implementations have fairly limited reverse bias capability (-2 V or -6 V).

*Strengths*

* Low (user-defined) series resistance and voltage drop
* Small form factor
* Resettable blocking function
* Simple to install

*Limitations*

* Total solution cost
* Power consumption (good but not best-in-class)

**Method 10: Fairchild Dedicated Reverse-Polarity Protection Devices**

Fairchild's dedicated reverse-polarity protection devices are relatively new but gaining popularity quickly. They represent one of the most cost-effective and highest-performance approaches for reverse polarity and are a very good choice for applications where operating currents exceed 100 mA or where low voltage drop, low power consumption, and small size are critical design requirements.

Dedicated reverse-polarity protection devices are specifically designed for reverse-bias or reverse-polarity protection. They offer the benefits of a series MOSFET without the need for guesswork or a complex implementation. They offer some of the same capabilities as a multi-function IC but, due to their focus on circuit protection and the cost of adding reverse polarity capability to a traditional IC process, dedicated reverse polarity protection devices are typically available at a much lower cost than multi-function ICs that include reverse polarity protection as just one of many add-on features.

Like their MOSFET and multi-function IC counterparts, dedicated reverse-polarity protection devices can keep operating power consumption very low. The series resistance can be selected by the application requirement. Unlike with a PTC, fuse, or series diode, a series voltage drop is not a requirement for proper operation. Leveraging the possibility for very low resistance, the designer can minimize power dissipation and voltage drop as desired. This is good for efficiency and device size, since the requirements for package power dissipation are optimized. Also, quiescent current is kept very low and, due to the limited feature set, can be held much lower than in a typical multi-function IC.

The dedicated design lowers the cost of the extended performance windows that apply to circuit protection (including resistance, ability to withstand voltage, and power consumption), especially compared to traditional multi-function ICs. As an additional advantage over MOSFETs and passives, extra protection functions, like TVS over-voltage protection, can be integrated into the device to help maximize protection and minimize the cost of circuit protection.

As power levels increase, the cost advantage of dedicated reverse polarity protectors does too. A small series Schottky diode is typically less expensive than a dedicated reverse-polarity protection device, but once operating currents begin to increase, the total cost of a Schottky-based method begins to go up as well, including Schottky device costs as well as surrounding support infrastructure like heat sinking and board space. Given the cost/performance tradeoff, the dedicated reverse-polarity protection device is likely to be the most attractive method.

**Figure 9**  The Dedicated Reverse-Polarity Protection Device Method

*Strengths*

* Relative cost
* Low (user-defined) series resistance and voltage drop
* Small form factor
* Resettable blocking function
* Simple to install
* Fast transient response
* Series blocking (no heat dissipation)
* Low power consumption

*Limitations*

* More expensive than a diode or Schottky, if currents are low and if voltage drop and power consumption are not issues.

**Special Note: Reverse Polarity Protection for Battery Contacts**

Historically, mechanical solutions have been the dominant solution for protecting against improper battery installation. Series diodes are typically not an option, due to voltage drop during normal operation, and the diode-to-ground method can be problematic during a reverse battery event, since the batteries can discharge dangerously for extended periods of time and overheat the diode. Discrete MOSFETs require complex structures and, historically, MOSFETs and multi-function ICs have been too costly and inadequate for full protection against reverse polarity.

At the same time, mechanical solutions are not perfect. They require custom tooling with each new design revision, require tight tolerances, are subject to fatigue in the field, and can be subject to user tampering.

As electronic solution costs lower and competitive solutions continue to appear, it's possible that dedicated electronic reverse-polarity protection devices could someday fully replace cumbersome mechanical solutions.

Fairchild’s dedicated reverse-polarity protection devices are a very attractive solution for protection from reverse battery installation. They offer low series resistance, and are very simple to implement. Once designed for specific battery chemistries, the same design can be used again and again, bringing all the benefits of solid state technology to this application.

**Conclusion**

The fact that there are so many ways to protect against damage caused by reverse polarity shows that there is no one approach that fits all situations, but there are some general guidelines we can suggest. First, it's important to take into account whether the design needs to protect just the load or the load and the power supply. If the design needs to protect both, then the number of choices will be limited. Assuming that protecting the power source is not a concern, we have the following recommendations.

For systems with low current (5 V), where efficiency is less of an issue, and voltage drop can be tolerated, we recommend the use of a series PN diode or a Schottky diode. It should be noted that the designer should take care to assure the devices don't overheat during normal operation or during conceivable fault conditions.

For systems with higher current (>100mA), where efficiency and voltage drop are more of a concern and reset ability is not required for extended reverse polarity events, we recommend using the TVS and Fuse method or a dedicated reverse-polarity protection device. If preventing catastrophic failure is the primary concern, and reverse bias reset is not required, the TVS and Fuse method is a suitable approach. If designed with care, the TVS can absorb short reverse polarity transients without triggering the fuse. At the same time, if the fuse safely opens in an extended reverse-bias event care must be taken to verify the life expectancy of the fuse in the field, and the fuse/diode combination must be carefully matched to avoid catastrophic failure modes.

Where the ability to reset against sustained reverse polarity events is needed, power consumption is of concern, and power sources are not easily defined, a Fairchild dedicated reverse-polarity protection device can offer the best cost for performance. Using such a dedicated device optimized for the application can keep costs low, minimize series resistance, and limit the need for case-by-case board-level verification. All these things combine to make the dedicated device one of the easiest and most cost-effective methods to implement. It's also an ideal way to upgrade and simplify battery-operated devices that use mechanical solutions to prevent reverse polarity caused by improper installation of the battery.
---
source: "EDN -- Protecting Against Reverse Polarity (Part 1)"
url: "https://www.edn.com/protecting-against-reverse-polarity-methods-examined-part-1/"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 10869
---

**Preventing Damage to the Power Source**

This article reviews the pros and cons of each method, but we need to begin with a short warning. If the power source has reversed polarity, some of the solutions proposed protect the device by shorting the power supply. If the power supply does not have embedded short circuit protection, the power supply, device connectors, and / or the protection circuit can all be damaged due to sustained high short-circuit currents. **Table 1** shows that, of the ten methods we review in this article, 6 can result in system damage if the power source is reverse polarized and unprotected. If extended reverse polarity of the power supply is a concern, these 6 solutions (highlighted in red or yellow) should be avoided, or at least very carefully evaluated.

**Table 1**  Risk of Damage from Extended Reverse Polarity

|  |  |
| --- | --- |
| **Method** | **Risk of Damage in Extended Reverse Polarity via Short Circuit Current Protection Method** |
| 1. Series Diode | No |
| 2. Series Schottky | No |
| 3. Diode to Ground | Yes |
| 4. TVS to Ground and PTC | Depends |
| 5. TVS to Ground and Fuse | Depends |
| 6. Schottky to Ground | Yes |
| 7. Schottky to Ground and PTC | Depends |
| 8. Series  MOSFET | No |
| 9. Multi-Function, Monolithic ICs | Depends |
| 10. Fairchild Dedicated Reverse-Polarity Protection Devices | No |

**Method 1: Series Diode**

The Series Diode method is a good choice if the design can accept large series voltage drops (±1 V) and the operating currents are low (

**Figure 1**  Series Diode Method

*Strengths*

* Low-cost, simple solution
* Fast blocking, resettable
* Potential for very high breakdown (up to 1000 V+)

*Limitations*

* The cost benefit is quickly minimized as operating currents go up. At higher currents, the increased power consumption ultimately requires a larger, more expensive IC with a more thermally conductive package and heat-sinking structure.
* The voltage drop and power consumption associated with this method typically rule out implementation in all but a few applications.
* In low-voltage systems (≤5V), the diode drop may require additional downstream boost circuits, making what is intended to be a low-cost approach actually quite expensive.

**Method 2: Series Schottky**

The Series Schottky method is similar to the Series Diode method, but with less voltage drop and lower associated power consumption. It is another excellent choice if the design can accept large series voltage drops (0.3-0.6 V) and the operating voltages remain fairly low (

The typical drop of 0.3-0.6 V of a Schottky diode is better than that of a PN diode, and broadens the application space a bit, but it can still be too high for many applications. Although a Schottky diode has a wider operating current range than a series PN diode, the best applications for this method are still those that use low current (5 V), and where power efficiency is not critical.

**Figure 2**

The Series Schottky Method

*Strengths*

* Exceptional blocking, simple design-in, low cost
* Resettable
* High breakdown (up to 200 V+)

*Limitations*

* Reduced voltage drop allows for lower thermal management requirements relative to a traditional PN diode. This may allow for smaller, less expensive packages, but power consumption and the drop in operating voltage still need to be considered.

**Method 3: Diode to Ground**

The Diode to Ground method is a good choice if the potential power sources are well understood and limited in power. The system must be tested to assure other components in the design can sustain the clamping levels associated with reverse polarity.

Power dissipation during the reverse-bias condition is a major consideration. As the diode clamps reverse voltage, the offending power supply may deliver sustained high current according to its power rating. Not only must the diode support these sustained currents and their associated power dissipation, but the supporting interconnects have to, too. For this reason, the Diode to Ground method should only be used where the possible reverse-bias conditions are well understood and can be specifically designed for.

During a reverse-bias condition, a Diode to Ground configuration will clamp the reverse-bias voltage of downstream components (and other components) to ~-1 V. The good news is that many downstream components, even those rated to only -0.3 V, can sustain -1 V for a short period. Most ICs, though, will ultimately fail if this level of negative voltage is sustained. This is another reason the potential list of negative power sources must be well understood. Proper implementation will require system-level validation on a case-by-case basis.

A transient voltage suppressor (TVS) can be used in place of a traditional diode for its ability to protect against over-voltage transients. The considerations for reverse-bias protection are identical to those of a traditional diode.

**Figure 3**  The Diode to Ground Method

*Strengths*

* No operating voltage drop,
* Low operating power consumption – from diode leakage only
* Integrated over-voltage protection if a TVS is used

*Limitations*

* The design must be tested on a system level to ensure downstream devices can withstand the ~-1V clamping response during negative-polarity events.
* The device will dissipate significant power during a reverse-bias event. In order to prevent overheating, the device must be sized and equipped with a proper heat sink, chosen using the worst-case input power condition.
* Depending on the operating voltage and reverse breakdown rating of the diode, this method may leak sufficient current from the power rail to ground, to reduce power efficiency during normal operation.

**Method 4: TVS and PTC resistor (or thermistor)**

Lab testing has shown that the reverse-bias protection capability of a TVS can be augmented by using a series, resettable, variable PTC resistance. However, protection capability must again be validated at the system level, on a case-by-case basis. The TVS, when used in combination with a series PTC resistor in a reverse-bias condition, will clamp reverse voltage by drawing current. If the current is sufficient, the PTC resistor will trip (go to a high-resistance state). When this happens, the PTC resistor will limit reverse-current flow, and in some systems this additional series resistance can be sufficient to protect the circuit. There are cases where this architecture can extend the reverse-bias protection window of the TVS device, and even allow a TVS implementation to protect ICs with ratings as low as -0.3 V from sustained reverse-bias conditions.

**Figure 4. The TVS and PTC resistor Method**

*Strengths*

* Increased window of operation compared to the standalone TVS approach
* PTC resistor adds a level of safety in the event the TVS overheats and fails
* Integrated over-voltage protection

*Limitations*

* Viability must be evaluated on a case-by-case basis, and care must be taken to match the TVS power dissipation capability with the PTC trip response to assure the PTC trips before the TVS overheats and fails.
* Using a thermistor will introduce series resistance. The thermistor requires series resistance in order to sense current and trip. Therefore, if it is to provide protection, it must have sufficient resistance to activate. Unfortunately, that same resistance generates system power loss.

**Method 5: TVS and Fuse**

This method is ideal for helping protect the end-user from short transients (both positive and negative) and for preventing catastrophic failure in the event of extended transients. Protection issues are similar to a standalone TVS, but safety is significantly improved. Unfortunately, it is not a resettable solution in response to sustained faults. The fuse will fail open-circuit permanently once triggered.

On the other hand, permanent open-circuit has advantages in both cost and space requirements. Because the fuse can be designed to open-circuit in a sustained fault, the designer no longer needs to size the diode and its associated heat-sink structures to support sustained over- or under-voltage conditions. The designer can now size the diode based on expected transient events, and what is the required fault condition to open-circuit the fuse. As a result, the diode costs and size can be reduced, saving board space.

Another advantage of this method is that fuse resistance is typically lower than PTC resistance, but it will still introduce some series resistance and power loss.

**Figure 5**  The Fuse and TVS Method

*Strengths*

* A very safe approach
* When used in combination with a series fuse, the TVS will still clamp over-voltage transients, as well as under-voltage and negative transients.
* Integrated over-voltage protection

*Limitations*

* *Not resettable:* If over-voltage or negative voltages are sustained, this method is not resettable by design. Once sufficient current flows through the fuse, the fuse will open permanently. Some care must be taken to assure expected transients do not blow the fuse.
* *Power loss from series resistance* : Based on its operating mode, and that it opens due to I2 R heating, the fuse must have series resistance to function. If it is to provide protection, it must have sufficient resistance to activate. That same resistance generates some system power loss, and can heat and thermally cycle the fuse in normal operation.
* *Fuse fatigue:* Fuses have a well-known mechanism for pulse current fatigue. Pulse currents generate heat inside the fuse (via I2 R heating). Repeated pulses can thermally cycle the fuse, ultimately leading to its degradation. Many of the fuse technologies with the lowest resistance are also the most susceptible to fatigue. For this reason, care should be taken when selecting a fuse to understand fatigue and assure field failures do not result from extended normal operation.
* *Diode matching:* This can be an issue during over-voltage events, when the diode shunts current to ground and pulls enough current to droop the power supply to the clamping voltage of the diode. Although the diode does not need to be designed to sustain this for extended periods, it should be sized such that it will draw sufficient current to open the fuse before the diode fails or overheats. If sized inappropriately, the diode can overheat the board without opening the fuse or the diode can fail open leaving downstream circuits unprotected. Either instance can lead to a downstream thermal event where the fuse does not open and thereby defeats the purpose of using the fuse in the first place.
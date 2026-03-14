---
source: "TI SWRA349 -- Coin Cells and Peak Current Draw"
url: "https://www.ti.com/lit/an/swra349/swra349.pdf"
format: "PDF 14pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 10935
---
# Coin Cells and Peak Current Draw

By Mathias Jensen

**Keywords:** Coin cell, 2032, Battery capacity, CC2540, CC2530/CC2531/CC2533, Bluetooth low energy

## Executive Summary

Designers of portable equipment using coin cell batteries are challenged by system level energy budget considerations, mainly driven by MCU and RF current consumption, as well as by the capacity and specification limits battery manufacturers provide. This report shows that adding a capacitor in parallel with a CR2032 coin cell is the most effective choice a designer can make to maximize battery capacity utilization in low power RF applications (more than 40% improvement with poor quality CR2032s). The test results also show that using 30 mA peak current versus 15 mA peak current only slightly reduces the effective capacity of a CR2032 (9% on average depending on vendor). These observations are valid across all six coin cell vendors tested, and implies that minimizing average current is the key to achieving long battery life with CR2032s.

## 1 Introduction

When designing a small wireless sensor node to be powered by the popular CR2032 coin cell, some sources claim there is a 15 mA "limit" and that drawing more current is not possible or will "damage" the battery. This may give the impression that at 15 mA everything works perfectly and battery capacity is great, while at 16 mA nothing works. There is little public information available to explain why such a limit exists (if it indeed does exist), and little information explaining why 15 mA would be a "magic number".

## 2 Abbreviations

- BLE: Bluetooth low energy
- IR: Internal resistance
- RF: Radio frequency

## 3 Testing Peak Currents

With the specific protocol of Bluetooth low energy (BLE) in mind we set out to test the impact of pulsed loads. Although the examples in this report are derived from BLE, it is equally applicable to other low power RF protocols like ZigBee, RF4CE, and other similar low-power RF protocols.

A common BLE load profile can be simplified to have 4 states: sleep, pre-processing, RX/TX and post-processing. The current drawn during each of these states will vary to some degree, but especially during the RX/TX state as seen below. In our testing we created a load profile that resembles a BLE profile. However, to reduce testing time it exceeds the BLE load profile. Figure 1 shows an example BLE profile and our testing profile (red line).

*[Figure 1. Example BLE profile and our testing profile]*

The load profile used in testing is given in Table 1:

| State | Test case 1 | Test case 2 | Duration |
|---|---|---|---|
| Pre processing | 8 mA | 8 mA | 2 ms |
| TX/RX | 30 mA | 15 mA | 1 ms |
| Post processing | 8 mA | 8 mA | 2 ms |
| Sleep | 0.1 mA | 0.1 mA | 200 ms |

*Table 1. Load profiles for battery tests*

To further simplify the test setup a switching resistor network was created and each resistor was dimensioned to sink the stated current for a voltage of 2.5 V. A battery's end of life was determined when the voltage dropped below 2.0 V.

*[Figure 2. Visual schematics for test and modeling]*

*[Figure 3. Ratio between effective and rated capacity]*

Figure 3 shows the ratio between effective and rated capacity results from a number of vendors. From each vendor, at least 12 batteries were used in testing since the battery-to-battery variation can be quite large. Rated capacity is 220 mAh for all branded vendors; the "No name" vendors did not specify so the same rated capacity was assumed.

From these results, two conclusions can initially be made:

- A. The difference in effective capacity between 15 mA and 30 mA peak current is not very significant. Average capacity loss is 9%.
- B. Effective capacity for both 15 mA and 30 mA peak will be very poor when using batteries from some vendors. Some vendors, including some branded name vendors, only achieve approximately 50% of rated capacity for both 15 mA and 30 mA peak current.

For consistent performance, (B) is more significant than (A). So to ensure consistently good performance, (B) is the main concern and the focus for attention. Clearly limiting peak current to 15 mA is not sufficient for consistently obtaining good effective battery capacity.

*[Figure 4. Battery voltage during load for test case 1 for the "No name 2" battery]*

*[Figure 5. Battery voltage (zoomed) during load for test case 1 for the "No name 2" battery]*

It can be seen that the voltage drop caused by the battery's internal resistance (IR) during peak load is limiting the effective capacity.

*[Figure 6. Calculated internal resistance as capacity is used]*

Figure 6 shows a typical curve for the calculated internal resistance and how it changes as capacity is used. The red line indicates when the voltage dropped below 2.0 V. Since the IR increases rapidly as capacity is used, the circuit must be able to manage a very high IR to achieve good effective battery capacity.

The steep incline in IR also gives a good explanation as to the relatively small difference in effective capacity between 15 mA and 30 mA peak current load. In our testing, the IR limit for 30 mA peak is approximately 30 ohm, and for 15 mA peak is approximately 60 ohm.

## 4 How to Survive a High Internal Resistance

A common technique to handle high peak currents is to use a capacitor to offload the power source. During high current periods the capacitor will act as the primary power source, while during low current periods the battery will be the primary power source and recharge the capacitor.

When dimensioning the capacitor it is important to know the battery's internal resistance and the load profile. With this information it's quite simple to dimension a suitable capacitor.

For our testing we dimensioned for an IR of 1 kohm which resulted in a capacitor of approximately 100 uF. In a low cost application, this capacitor size would probably be too large or too expensive, but in a real BLE application the capacitor can be significantly reduced by a factor of 2-5 depending on application, since the load profile is much easier.

*[Figure 7. Visual schematics for test and modeling with capacitor]*

We tested adding a capacitor using the Sony and "No Name 2" batteries since they represent the best and the worst. Figure 8 shows the result.

*[Figure 8. Ratio between effective and rated capacity]*

So although the "No name 2" batteries still don't achieve 100% of rated capacity, it is still a solid >40% improvement. It can also be seen that the difference between 15 mA and 30 mA peak remains at the same level. The Sony batteries increased their effective capacity by 5% and 13% respectively to an almost identical effective capacity.

In a real BLE application, the increase in effective capacity is most probably even higher for the low performing batteries since real BLE applications will have considerably longer sleep states and much lower average current consumption.

*[Figure 9. Battery voltage during load for test case 1 for the "No name 2" battery]*

*[Figure 10. Battery voltage (zoomed) during load for test case 1 for the "No name 2" battery]*

*[Figure 11. Calculated internal resistance as capacity is used]*

Figure 11 shows that with the added capacitor, the circuit is able to manage high IRs.

## 5 Conclusion

This white paper has demonstrated how adding a capacitor enables a circuit to handle high internal resistance and maximize battery capacity of CR2032 coin cells. In addition, measurements show that different peak currents up to 30 mA have minimal impact on effective battery capacity. Bringing the average current down is therefore the most important factor when maximizing battery life of CR2032 coin cells in low power RF applications.

Note: At low temperatures it probably becomes even more important to use a capacitor since the internal resistance increases with lowering temperatures.

## Appendix A. Dimensioning the Capacitor

To simplify the dimensioning of the capacitor, a few simplifications need to be made:

- A. During the high current states the battery voltage is fixed at Vmin. This will cause an error on the safe side, meaning that the battery will deliver slightly more energy than calculated.
- B. The current consumed by the circuit during the sleep state is normally in the 1 uA range and is therefore omitted.

To calculate the capacitor capacitance, focus on the high load states (processing and RX/TX). The formula is given as:

C = dQ / (Vmax - Vmin), where dQ = Q_dis - (Vmin / Ri) x t_tot

Q_dis is the total energy consumed during the high load states. It is important to note that when dimensioning the capacitor the peak current is of little importance; instead it is the total energy consumed during the high load states that is of importance. In our calculations we used Q_dis = sum(I_n x t_n), but other methods may of course also be used.

Vmin is chosen by design to match the circuit's lowest operating voltage. Ri is the maximum internal resistance the circuit should be able to manage. Vmax is the voltage over the capacitor at the very start of the discharge pulse at the battery's end of life, and must initially be estimated. Further down Vmax can be refined. In our example the following values were chosen:

- Vmax = 2.6 V
- Vmin = 2.0 V
- Ri = 1 kohm

The resulting calculation is as follows:

C = (8 mA x (2+2) ms + 30 mA x 1 ms - (2 V / 1000 ohm) x (2+1+2) ms) / (2.6 V - 2.0 V) = 87 uF

To assess the feasibility of C, verify that the capacitor will be able to recharge during the sleep state. The recharge time is given by:

t = Ri x C x ln((Vp - Vmin) / (Vp - Vmax)), where Vp is the unloaded battery voltage.

Since Vp is unknown it must be estimated. It should be chosen to match the end-of-life unloaded battery voltage, and from our measurements a value of 2.7 V looks like a good starting point. With this, our example yielded:

t = 1000 ohm x 87 uF x ln((2.7 V - 2 V) / (2.7 V - 2.6 V)) = 169 ms

Since t is shorter than the sleep state time, this looks like a good sized capacitor. If t is longer than the sleep state, either Vmax or Ri need to be reduced. If t is considerably shorter than the sleep state, the capacitor is unnecessarily large and can be reduced by increasing Vmax (alternatively if C is left unchanged the circuit will be able to handle a higher Ri).

Note that in the test load profile, the sleep current was a non-negligible 100 uA. This called for a slightly larger capacitor of 100 uF instead of the above calculated 87 uF.

## References

1. Bluetooth (http://www.bluetooth.com)
2. GP CR2032 (http://www.gpbatteries.com)
3. Maxell CR2032 (http://www.maxell.co.jp)
4. Panasonic CR2032 (http://www.panasonic-batteries.be)
5. Sony CR2032 (http://www.sony.co.uk)

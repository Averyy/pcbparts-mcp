---
source: "TI SLVA450B -- Voltage Divider Resistor Selection"
url: "https://www.ti.com/lit/pdf/slva450"
format: "PDF 10pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 12028
---

# IQ vs Accuracy Tradeoff In Designing Resistor Divider Input To A Voltage Supervisor

Anthony Fagnani, Battery Power Products

## Abstract

A resistive voltage divider is commonly used at the input to a comparator to set a threshold voltage for Sense inputs and Power Fail Inputs (PFI) on supply voltage supervisors (SVS) or low battery inputs (LBI) on switching regulator devices. The threshold voltage is set by the ratio of the two resistors in the divider. Keeping the ratio constant, there are tradeoffs to consider for selecting the actual resistor values. With higher resistances, the leakage current at the comparator input can affect the threshold voltage accuracy. On the other hand, with lower resistances, the current through the divider is increased. In battery-powered applications, this current can be a significant drain on battery life and run time. This application report discusses several key factors involved with selecting optimally-sized resistors, considering these constraints.

## 1 Introduction

An SVS monitors a critical system voltage and generates a reset if this voltage is too low. Likewise, an LBI pin monitors a voltage (typically a battery) and drives the low battery output (LBO) pin low when the battery has dropped below the set voltage. A PFI pin monitors a system voltage level and drives a power fail output (PFO) if the PFI voltage gets too low. These three pin types are simply a comparator and a reference voltage that monitor a voltage to ensure proper operation of a processor (SVS), to alert the user that the batteries must be replaced or recharged (LBI), or to send a signal to the host that some system voltage is too low and action needs to be taken (PFI). In each case, all of the voltages monitored are critical to ensure the proper operation of the entire system.

Ideally, a comparator would have infinite input impedance that produces no current at the inputs. In practice, however, a real comparator has a measurable input impedance and some degree of leakage current. These effects impact the accuracy of the trip point set by the resistive divider at the inputs, because this leakage current cannot be exactly determined and varies from device to device. When selecting the resistances, there are two extremes to consider: infinite or very low resistance. With infinite resistance, the trip point is dominated by the leakage current, which usually varies and causes a great loss in accuracy. At a very low resistance, however, amps of current are drawn through the divider, which is also unacceptable. ICs that use a resistive divider at a comparator input must have an accurate trip point and yet not consume a significant amount of current.

As a starting point for making the decision about the tradeoff of accuracy versus current consumption, a good rule of thumb is to have the current through the divider be 100 times larger than the leakage current. However, a given application may require more accuracy or require less current at the cost of reduced accuracy. In this report, an example divider circuit is analyzed using the low quiescent current, programmable-delay TPS3808G01 SVS, although the equations are applicable to any IC or circuit that uses a voltage divider at the comparator input.

## 2 Designing with the TPS3808G01

As Figure 2-1 illustrates, the SENSE pin input of the TPS3808G01 is compared to a 0.405 V internal reference (V_REF). A voltage divider is used to scale down the monitored voltage (V_I) to the level of the SENSE pin. The voltage divider ratio is selected based on the desired trip point of V_I at which the SVS should generate a reset. This trip point is the threshold voltage, V_IT. An accurate trip point is necessary to prevent the system from resetting too early or too late.

When selecting the resistors to use, R2 should be chosen first; then solve for R1 to achieve the desired V_IT. Equation 1 shows the calculation for R1, given a value of R2, while Equation 2 calculates the actual value of V_IT based on the selected values for R1 and R2.

    R1 = R2 * (V_IT / V_REF - 1)                                          (1)

    V_IT = (1 + R1/R2) * V_REF                                             (2)

However, as a result of the leakage current (I_S), the voltage at the SENSE pin (V_S) is not what is expected at the desired V_IT. The actual V_S can be found using Equation 3. The actual input threshold voltage varies because of the leakage current, and can be calculated with Equation 4. The resulting accuracy of the divider can be found using Equation 5.

    V_S = R2 * (V_I - I_S * R1) / (R1 + R2)                               (3)

    V_IT_Actual = V_REF + R1 * (V_REF / R2 + I_S)                          (4)

    %ACC = (1 - V_IT_Actual / V_IT) * 100%
         = (R2 * I_S * (V_IT/V_REF - 1)) / V_IT * 100%                    (5)

Including the effect of the leakage current, the current drawn by the divider, I_R1, is simply the current that passes through the top resistor in the divider. This value can be found using Equation 6. The maximum current into the divider occurs when I_S is positive (flowing into the pin). Equation 6 shows that current drawn from the divider varies almost linearly with the input voltage. When the leakage current is very small and/or the resistors in the divider are small, Equation 6 simplifies to Ohm's law.

    I_R1 = (V_I - I_S * R2) / (R1 + R2)                                   (6)

By rearranging Equation 5 and solving for R2, we can derive Equation 7. This formula can be used to design a voltage divider to meet a desired accuracy requirement. Note that a negative accuracy is equivalent to using a negative leakage current, and produces the same resistance (R2) that exists when both accuracy and leakage are positive. To state it differently, if the leakage current is negative (that is, flowing out of the pin), the threshold voltage is lower than expected, which equates to negative accuracy.

    R2 = (%ACC/100 * V_IT) / (|I_S| * (V_IT/V_REF - 1))                   (7)

By rearranging Equation 4 and solving for R2, we can derive Equation 8. With this formula, we can now design a voltage divider to achieve a desired current, I_R1.

    R2 = V_I / (V_IT/V_REF * (I_R1 - I_S))                                (8)

## 3 Example Calculations

Table 3-1 lists the system requirements that necessitate the use of an SVS with 1% accuracy threshold voltage. When the supply voltage falls below 10% of its nominal value of 3.3 V to 2.97 V, the processor should reset. V_REF and I_S can be found directly from the device data sheet.

| Field | Value |
|-------|-------|
| IC | TPS3808G01 |
| V_REF | 0.405 V |
| I_S | +/-25 nA |
| V_I | 3.3 V |
| V_IT | 2.97 V |
| Desired %ACC | 1% |

First, calculate R2 to its nearest standard value, using Equation 9.

    R2 = (%ACC/100 * V_IT) / (|I_S| * (V_IT/V_REF - 1))
       = (1/100 * 2.97 V) / (25 nA * (2.97V/0.405V - 1))
       = 187 kohm                                                          (9)

With R2 known, calculate R1 to the nearest standard value, using Equation 10.

    R1 = R2 * (V_IT/V_REF - 1) = 187 kohm * (2.97V/0.405V - 1)
       = 1.18 Mohm                                                         (10)

As an effect of using standard-value resistors, the expected threshold voltage can be found by using Equation 11.

    V_IT = (1 + R1/R2) * V_REF = (1 + 1.18 Mohm / 187 kohm) * 0.405 V
         = 2.974 V                                                         (11)

Then, using Equation 6, the input current is found. I_S is evaluated as a positive value to find the maximum amount of current through the divider.

    I_R1 = (V_I - I_S * R1) / (R1 + R2) = (3.3V - 25nA * 187kohm) / (1.18Mohm + 187kohm)
         = 2.41 uA                                                         (12)

One can also observe that this current is roughly 100 times the leakage, which validates the rule of thumb noted earlier.

Figure 3-1 shows the variation in worst-case accuracy and input current to the divider with R2 ranging from 1 kohm to 1 Mohm. Note the accuracy is centered on the new calculated V_IT: 2.974 V.

Figure 3-1 also clearly illustrates the linear relationship of accuracy and exponential relationship of current to R2 (note the logarithmic axes). This correlation demonstrates the diminishing returns for both an increase and a decrease in the resistance R2. At the lower end, the current increases significantly with a small increase in accuracy. On the high end, the accuracy decreases significantly for small decreases in current. The accuracy from the leakage is nearly always better than what is shown in the graph because the amount of leakage is not always at the worst-case conditions. The current, however, does not vary significantly because the leakage current is virtually always a fraction of the current into the divider.

## 4 Other Sources of Inaccuracy

In the equations, calculations, and graph presented here, neither the resistor tolerance nor the tolerance on the SENSE voltage is accounted for. These factors have an effect on the accuracy of V_IT as well, and its tolerance can be estimated by using Equation 13.

    %ACC = %TOL_VREF + 2 * (1 / (1 - V_REF/V_IT)) * %TOL_R               (13)

The accuracy of the TPS3808G01 can be evaluated with 1% tolerance resistors (TOL_R) and the 2% tolerance on V_IT (TOL_VREF) given in the product data sheet. The accuracy of the divider as a result of the leakage current is then added to these other sources of variation, as shown in Equation 14. Therefore, the worst-case accuracy of the 1% divider designed in the example is 4.73%.

    %ACC = 2% + 2 * (1 / (1 - 0.405V/2.97V)) * 1% = 3.73%
    %ACC_Total = 3.73% + 1% = 4.73%                                        (14)

Another concern is that higher-value resistances can have noise coupled into them more easily than lower ones. This additional noise can further decrease the accuracy. An IC with an internal voltage divider, however, addresses both of these concerns by having higher accuracy with a lower current draw than an IC that is set externally. Because the resistors are integrated in the IC, the coupling nodes and capacitances are much smaller, resulting in superior noise immunity. For example, the TPS3808G33 has a fixed V_IT of 3.07 V, and boasts a total accuracy (including SENSE voltage variation, leakage current variation, and internal resistor tolerance) of +/-1.25% along with a current consumption of 0.86 uA at a V_I of 3.3 V. This amount is one-third of the current consumed with 25% lower accuracy than the example calculation discussed, which assumed an ideal SENSE voltage and ideal resistor values. Taking into account the additional variation in these values, then, the total accuracy of the example with the adjustable version is one-third that of the fixed version before the leakage error is even added.

## 5 Conclusion

An adjustable SVS is a flexible and simple component that requires the designer to make a tradeoff between accuracy and current consumption. Effectively designing the resistor divider that generates the trip point ensures that the circuit is as accurate as it can be while not overloading the system. All comparator inputs (SENSE, LBI, PFI, and so forth) have leakage current, and this leakage is a source of inaccuracy. Proper selection of the resistor divider values allows the optimum selection of accuracy and current consumption. The equations presented in this application note can be used to fine-tune the divider to best meet the demands of the application.

## 6 References

- TPS3808 product data sheet, Texas Instruments literature number SBVS050J.
- Falin, J. (2006). Ballast Resistors Allow Load Sharing Between Two Paralleled DC/DC Converters. Texas Instruments application report, literature number SLVA250.

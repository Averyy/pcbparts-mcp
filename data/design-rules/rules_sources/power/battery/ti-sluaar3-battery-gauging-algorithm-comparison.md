---
source: "TI SLUAAR3 -- Battery Gauging Algorithm Comparison"
url: "https://www.ti.com/lit/SLUAAR3"
format: "PDF 11pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 9434
---
# Battery Gauging Algorithm Comparison

Nick Richards

## Abstract

This application note examines and compares the different algorithms used to gauge batteries including voltage correlation, voltage + IR correction, coulomb counting, CEDV, and Impedance Track.

## 1. Introduction

Estimating a battery's State of Charge is a challenging task, and many different types of algorithms have been used to try to achieve this with the lowest accuracy error. Some of the most common algorithms used today include: voltage correlation, voltage + IR correlation, and coulomb counting.

## 2. Voltage Correlation

Voltage correlation is a very basic method for gauging batteries. This algorithm takes the OCV (Open Circuit Voltage) of the battery and references this value to a look-up table of voltages, where each voltage corresponds to a different SOC (State of Charge).

For example, if the OCV of the battery is 3.72 volts, then the gauge can predict that the SOC at that given time is 50%.

While voltage correlation is a very easy method to implement, it comes with many drawbacks:
- Only able to report SOC, not SoH (State of Health), Remaining Capacity, or Remaining Run Time
- SOC is not adjusted for important factors like discharge rate, temperature, and the age of the battery

Voltage correlation is recommended for applications where the battery has long periods of rest where the OCV can be taken to accurately determine SOC and/or the current is low enough where an OCV is still accurate.

## 3. Voltage + IR Correction

Voltage + IR Correction expands on voltage correlation by taking into account the IR drop that occurs when a load is applied to a battery. The amount of IR drop depends on the internal impedance of the battery, the amount of load current, and the temperature of the battery.

Downsides:
- Greater error when gauging aged cells and/or when the battery is exposed to low temperature, since the internal impedance increases

Improvements over voltage correlation:
- SOC is able to be adjusted for discharge rate and temperature towards the end of discharge

## 4. Coulomb Counting

Coulomb counting is a direct measurement of how much electrical charge is leaving or entering the battery:

    q(t) = q0 + integral(I(t) x dt)

The main issue with coulomb counting is knowing what the starting amount of charge is in the battery. Thus, full charge is needed to initialize SOC, otherwise SOC is unknown.

Downsides:
- Full Charge Capacity is needed to report an accurate SOC; to find Full Charge Capacity a full discharge to empty is required, which is not viable for most applications because it would cause data-loss on shut-down
- If the battery experiences extreme changes in temperatures then SOC may be reported incorrectly. For example, if a battery was charged at room temperature, coulomb counting could calculate the full charge capacity at 2250 mAh. If the battery is used in very cold conditions, the total usable capacity could reduce to 1100 mAh -- a difference of about 51%, which would result in coulomb counting reporting more charge than what is actually left

## 5. CEDV

CEDV is an algorithm that uses coulomb counting as the backbone of the gauging. CEDV mathematically models cell voltage as a function of the battery's SOC, temperature, and current. The battery voltage model is used to calibrate full-charge capacity (FCC), and a compensated battery voltage is used for end-of-discharge alarms and when the gauge reports 0% SOC. This algorithm uses specific parameters that are different for each battery, gathered through the GPCCEDV tool.

**CEDV Parameters:**
- EMF and C0: Define the function OCV(SOC, T)
- R0, R1, and T0: Define R(SOC, T). R1 defines the slope of R(SOC) dependence. R0 defines the magnitude of R. T0 defines the slope of R(T) dependence.

**EDV Thresholds:**
- EDV2, EDV1, EDV0: Set voltage thresholds corresponding to given percentages of remaining capacity, usually 7%, 3%, and 0% respectively
- Set towards the end of discharge where there is a greater difference in voltage between SOC points, minimizing error
- Learning of the new FCC after a change of temperature and rate of discharge occurs only at the EDV2 point. An abrupt SOC drop can occur before the end of discharge, sometimes up to 50% if the temperature is low and the rate of discharge is high.

**Improvements over previous methods:**
- Improves on Voltage + IR Correction accuracy
- Estimates initial capacity by reading the voltage and correlating to a 10-point voltage table at device reset
- Able to report remaining run time, SoH, and Remaining Capacity at the end of discharge
- SOC adjusted for discharge rate and temperature towards the end of discharge

**Limitations:**
- Self-discharge can affect accuracy
- Full discharge needed to learn FCC (required for accurate SoH and SOC estimations)
- Cannot report remaining capacity in watt-hours
- Aging of the battery can make the internal impedance underestimated, resulting in 15%-25% error in FCC and SOC for aged batteries

## 6. Impedance Track

Impedance Track vastly expands on the previous algorithms by combining aspects of coulomb counting and Voltage + IR Correction. It uses many factors to calculate SOC including: Depth of Discharge (DOD), total chemical capacity (Q_max), internal battery resistance dependence on DOD, current load, and temperature.

**Mode Detection:** The gauge determines whether the battery is currently in a charge, discharge, or relaxed state using configurable parameters: Chg Current Threshold, Dsg Current Threshold, Quit Current, Chg Relax Time, and Dsg Relax Time.

**DOD Updates:** The gauge updates the Chemical Depth of Discharge (DOD_0) based on OCV reading when the battery is in the relaxed state. DOD is found by correlating the present OCV and temperature with the predefined DOD(OCV,T) table, specific for each chemistry (Chemistry ID). OCV readings occur when the rate of change in voltage is less than 4 microvolts per second. If the current during the OCV reading is non-zero, an IR correction is done.

**Q_max Updates:** The gauge updates Q_max between two DOD readings made before and after a charge or discharge. For Q_max to update, there needs to be more than a 37% change in charge based on the design capacity. For the first Q_max update, there needs to be at least a 90% change in charge. Coulomb counting determines the change in charge.

    Q_max = delta_charge / (SOC1 - SOC2)

**Internal Resistance Updates:** The gauge updates the battery's internal resistance table (Ra table) during discharge:

    Internal Resistance = (OCV(DOD,T) - Present Loaded Voltage) / Measured Current

**Simulation:** The algorithm uses all the information above to run simulations based on the user-programmed Load Select to calculate SOC. The simulation calculates remaining capacity (RemCap) once per second. FCC can update during resistance grid-point update, during relaxation, or during the entry of charge or discharge.

**Key improvements over other algorithms:**
- Does not need to be fully charged to initialize SOC
- Self-discharge is frequently compensated by OCV readings, maintaining high SOC accuracy even when sitting idle for long periods
- Internal resistance constantly updates, keeping gauging error small for aged cells
- No increased error when there is a high rate of discharge
- Temperature-compensated resistance updates improve accuracy at lower temperatures
- FCC is updated at critical points during discharge (reported in mAh and Wh)
- SoH is continuously updated since Q_max and Ra table are always updating
- SOC adjusted for discharge rate and temperature throughout the entire discharge

## 7. Algorithm Comparisons

### 7.1 Calculating SOC Error

SOC error is a direct reflection of the accuracy of the gauging algorithm. The error is found by taking the difference between the true SOC and the calculated SOC.

**Calculating True SOC:**

    dQ_N = ((ElapsedTime_N+1 - ElapsedTime_N) x Current) / 3600 + dQ_N-1

True Full Charge Capacity = sum of all passed charge. Remaining capacity for each sample point:

    Calculated Remaining Capacity = Calculated FCC - dQ

    True SOC = (Calculated Remaining Capacity / True FCC) x 100

**Coulomb Counting SOC:**

    SOC_N = (1 - sum(dQ) / Design Capacity) x 100

### 7.2 Comparing SOC Error

Test environment: robot vacuum cleaner with 4S2P battery at room temperature.

| Algorithm | Test 1 Peak Error | Test 2 Peak Error |
|---|---|---|
| Voltage Correlation | ~20% | ~17% |
| Voltage + IR Correction | ~11% | ~10% |
| Coulomb Counting | ~6% | ~6% |
| CEDV | Similar to Coulomb Counting | Similar to Coulomb Counting |
| Impedance Track | ~1% | ~1% |

## 8. Summary

Impedance Track offers the highest accuracy battery gauging when compared to other commonly used algorithms. While voltage correlation is the simplest method to implement, it has the largest SOC error. Voltage + IR correction reduces the peak SOC error from voltage correlation in half, and coulomb counting can further reduce the SOC error. Impedance Track offers the most accurate gauging because it uses all three of these algorithms. The largest benefit to using an accurate gauging algorithm is that it can increase the run time of the application.

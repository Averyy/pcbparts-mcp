---
source: "Vishay -- Fast Charging Control with NTC Temperature Sensing"
url: "https://www.vishay.com/docs/29089/fastappl.pdf"
format: "PDF 4pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 12041
---

# Fast Charging Control with NTC Temperature Sensing

Vishay BCcomponents -- Resistive Products Application Note

## 1. Introduction

The need for increased autonomy for new models of laptops and cellular phones has resulted in high-energy density power packs - Ni MH and Li-ion batteries.

These batteries can be charged quickly, on the condition that the fast charging complies with several criteria.

The techniques used are the following:

- For the Ni MH cells, the quick and fast charging operation uses the -dV, d2V/dt2, the maximum time, the TCO (Temperature Cut Off), or the dT/dt techniques. The measurement of high temperature is used as a protection, but the temperature variation (dT/dt) can also be used for monitoring.
- For the Li-ion cells, the fast charging uses the CCCV techniques (Constant Current Constant Voltage). The initial temperature is measured in order to allow initiation of fast charging. If the temperature reaches a high threshold (TCO), the fast charging would stop.

The sophistication of the electronic system depends principally upon cost and upon the requirements of the batteries. Often, the fast charging is monitored by an IC, measuring the voltage of the batteries, the charging current via a sense resistor, and measuring the temperature of the batteries via one or several Negative Temperature Coefficient (NTC) thermistor(s). The ICs are almost always in the chargers or integrated in the battery pack (Li-ion). The thermistors are almost always integrated in the battery packs, sometimes placed in the charger, and/or in the final apertures (low cost cellular phones).

This application note explains how to design an NTC thermistor from Vishay BCcomponents for a BQ2005 from Texas Instruments dual Ni MH batteries charging IC.

The computation methods performed here are sufficiently general to be extended to a lot of other configurations.

## 2. The Fast Charge Algorithm for the BQ2005

Referring to the notice of the BQ2005 IC, we will focus on the design part related to the temperature control of the charge operation (see figure 1).

An NTC thermistor, together with fixed resistors R_T1 and R_T2, is used in a voltage divider between V_cc and the current sense resistor input V_SNS of the IC.

At the beginning of a new charge cycle, the IC checks if the voltage V_temp = V_TS - V_SNS is within the limits designed by the IC manufacturer (low temperature: 0.4 V_cc and high temperature: 0.1 V_cc + 0.75 V_TCO).

V_TCO is a cut off threshold defined by external resistors (not represented in figure 1): If after starting the fast charge phase, V_temp becomes lower than V_TCO, then the return to trickle mode is operated.

During the fast charge period, the IC samples the voltage V_temp and the return to trickle mode can also be operated when the variation in time of V_temp is going over a threshold. This is called the dT/dt termination: each 34 s, V_temp is sampled and if V_temp has fallen by 16 mV +/- 4 mV compared to the value measured two samples earlier, then the fast charge is terminated.

The following table summarizes the voltage levels applicable here:

| Symbol | Parameter | Average | Tolerance |
|--------|-----------|---------|-----------|
| V_cc | Supply voltage | 5 V | +/- 10% |
| V_TCO | Cut off voltage | Adjustable between 0.1 V_cc and 0.2 V_cc | -- |
| V_temp_low | Low temperature fault | 0.4 V_cc | +/- 30 mV |
| V_temp_high | High temperature fault | 0.1 V_cc + 0.75 V_TCO | +/- 30 mV |
| V_therm | TS input change for dT/dt termination | 16 mV/period of 2 x 34 s | +/- 4 mV |

## 3. Configuration of External Thermistor/Resistor Network

The voltage around the TS input is:

    V_TS - V_SNS = (R_T2 * R_NTC) / (R_T1*R_T2 + R_T1*R_NTC + R_T2*R_NTC) * (V_CC - V_SNS)   (1)

The voltage around the NTC for the low fault, high fault, and cut off temperatures has to comply to the thresholds designed for the BQ2005. This is expressed by equations (1a), (1b) and (1c).

    V_TS(T low) - V_SNS = 0.4 V_cc                                         (1a)
    V_TS(T high) - V_SNS = 0.1 V_cc + 0.75 V_TCO                          (1b)
    V_TS(T cut off) - V_SNS = V_TCO                                        (1c)

Normally V_SNS is of the order of 0.1 V. For simplicity, we will consider here that V_SNS = 0. Should this approximation not be valid, then the computations hereunder must be modified.

Let us call R_NTC(low temperature fault), R_NTC(high temperature fault) and R_NTC(cut off temperature) respectively R_nL, R_nH, and R_TCO.

Introducing (1) in (1a) and solving with respect to R_T2, we obtain:

    R_T2 = 0.666 * R_T1 * R_nL / (R_nL - 0.66 * R_T1)                    (2a)

Introducing (1) and (2a) in (1c) we obtain:

    R_T1 = R_TCO * R_nL / (R_nL - R_TCO) * (V_CC / V_TCO - 2.5)          (2b)

Once the thermistor characteristics and V_TCO are defined, R_T1 and R_T2 will be defined.

We also have to compute the speed of variation of temperature on the thermistor, which will induce the voltage V_therm operating the dT/dt termination.

Assuming the exponential dependence of the electrical resistance of the thermistor in function of the temperature:

    R_ntc(T) = R25 * exp(B * (1/T - 1/298.15))                            (3)

where R25 is the electrical resistance of the NTC at 25 C, B is the B25/85 characteristic of the component (K), and T is the absolute temperature (K).

We can derive from equations (1) and (3):

    dV_TS/dt = dV_TS/dT * dT/dt
             = -B * R_T1 * R_T2^2 * R_NTC * V_CC / (T^2 * (R_T1*R_T2 + R_T1*R_NTC + R_T2*R_NTC)^2) * dT/dt   (4)

dT/dt, T_low and TCO are given by the battery manufacturer. dV_TS/dt is defined by TI.

The characteristics of the thermistor are defined by Vishay BCcomponents T_low and TCO values. The B value can be found in the catalog or by using the Steinhart & Hart interpolation polynomials calculation.

On this base, all the remaining parameters can be defined with the help of relations (2a), (2b), and (4) which have to be verified simultaneously: R_T1 and R_T2 are chosen to respect T_low and TCO via equation (2a) and (2b). V_TCO will be defined so that the required dT/dt (equation (4)) will be respected. At last, T high fault will be computed with equation (1b).

## 4. Numerical Example

### Example 1

The following data are currently applicable to Ni MH batteries:

- T low fault = 10 C
- T cut off = 50 C
- dT/dt = 1 C/min +/- 0.3 C/min

Then:
- Using V_cc = 5 V, dV/dt = 16 mV / (2 x 34 s)
- Designing for the sensor the Vishay BCcomponents leaded thermistor NTCLE203E3103JB0: R25 = 10 kohm +/- 5%, B25/85 = 3977K +/- 0.75%
- Using V_TCO = 1.6 V arbitrarily

We derive R_T1 = 2753 ohm and R_T2 = 2020 ohm.

Then we compute dT/dt for different temperatures from 10 C to TCO. The results are shown in the following table:

| Temp | R_NTC (ohm) | V_TS (V) | V_threshold (V) | dV_TS/dT (mV/C) | dT/dt (C/Min) |
|------|-------------|----------|------------------|------------------|---------------|
| Low fault 10 C | 19872 | 1.999 | 2.000 | -5 | 2.57 |
| High fault 42.5 C | 4824 | 1.704 | 1.700 | -13 | 1.07 |
| Cut off 50 C | 3605 | 1.599 | 1.600 | -15 | 0.95 |

We see that the dT/dt falls into the range of 1 C/min +/- 0.3 C/min. If it would not be the case, then one should have let the V_TCO slightly change.

The tolerances on the electrical characteristics introduce also a variation on the thresholds. For the limit case: Let us make the calculations for the value of the thermistor being at the limits +/- 5% and the B value at +/- 0.75%. We will also take into account the errors introduced by the tolerances on the fixed resistors (supposed +/- 1%).

The error dT in the thresholds (low fault temperature and TCO) due to these tolerances are simply obtained by performing the calculations of the V_TS at the fixed temperature (10 C and 50 C) and by comparing these values with the requested ones, and dividing these differences by the sensitivity dV_TS/dT.

**R_NTC(25 C) = 10500 ohm, B25/85 = 3977K - 0.75%, R_T1 = -1%, R_T2 = +1%:**

| Temp | R_NTC (ohm) | V_TS (V) | V_threshold (V) | dV_TS/dT (mV/C) | dT/dt (C/Min) | dV (mV) | dT (C) |
|------|-------------|----------|------------------|------------------|---------------|---------|--------|
| Low fault 10 C | 20755 | 2.027 | 2.000 | -5 | 2.66 | 27 | -5.01 |
| Cut off 50 C | 3815 | 1.639 | 1.600 | -15 | 0.97 | 39 | -2.70 |

**R_NTC(25 C) = 9500 ohm, B25/85 = 3977K + 0.75%, R_T1 = +1%, R_T2 = -1%:**

| Temp | R_NTC (ohm) | V_TS (V) | V_threshold (V) | dV_TS/dT (mV/C) | dT/dt (C/Min) | dV (mV) | dT (C) |
|------|-------------|----------|------------------|------------------|---------------|---------|--------|
| Low fault 10 C | 18979 | 1.971 | 2.000 | -6 | 2.48 | -29 | 5.12 |
| Cut off 50 C | 3399 | 1.558 | 1.600 | -15 | 0.93 | -42 | 2.73 |

With these tolerances:
- Low temperature fault will fall in the range 10 C +/- 5 C approx.
- Temperature cut off will fall in the range 50 C +/- 2.7 C approx.

If such variations should not be acceptable, then design a thermistor with R25 tolerance down to +/- 1% (code number: NTCLE203E3103FB0) instead of +/- 5%: The tolerances on the definition of threshold will become negligible compared to inherent tolerances of the IC.

### Example 2

The same calculations for all the SMD NTC thermistors (NiSn terminations, sizes 0805, 0603, or 0402 described in the appendix) give the following results:

Adjusting slightly V_TCO to 1.55 V, in order to keep dT/dt nominal at 1 C/min at the high fault temperature, we then can compute:

| Component | Temp | R_NTC (ohm) | V_TS (V) | V_threshold (V) | dV_TS/dT (mV/C) | dT/dt (C/Min) | R_T1 (ohm) | R_T2 (ohm) |
|-----------|------|-------------|----------|------------------|------------------|---------------|------------|------------|
| NTCS0805E3103xMT | Low fault 10 C | 18515 | 1.999 | 2.000 | -7 | 1.98 | 3708 | 2850 |
|  | High fault 41.8 C | 5331 | 1.668 | 1.663 | -14 | 1.01 |  |  |
|  | Cut off 50 C | 4004 | 1.549 | 1.550 | -15 | 0.93 |  |  |
| NTCS0603E3103xMT | Low fault 10 C | 18664 | 1.999 | 2.000 | -7 | 2.01 | 3649 | 2794 |
|  | High fault 41.9 C | 5271 | 1.668 | 1.663 | -14 | 1.01 |  |  |
|  | Cut off 50 C | 3960 | 1.549 | 1.550 | -15 | 0.92 |  |  |
| NTCS0402E3103xLT | Low fault 10 C | 18290 | 1.999 | 2.000 | -7 | 1.95 | 3811 | 2947 |
|  | High fault 41.75 C | 5408 | 1.668 | 1.663 | -14 | 1.02 |  |  |
|  | Cut off 50 C | 4079 | 1.549 | 1.550 | -15 | 0.94 |  |  |

## 5. Conclusion and General Comments

Due to their low tolerances, low cost, and high sensitivity, NTC thermistors are perfectly suited for fast charging monitoring and protection of the battery packs.

The notes and calculations described in this note can be easily extrapolated to other ICs, for example the BQ2954 for Li-ion packs. In this case, the dT/dt charge termination is not of application, which makes it even more simple.

The greatest care should be used when positioning the thermistor into the pack to ensure close contact between the thermistor and the batteries. Otherwise, all calculations about tolerances will not be applicable.

## 6. Appendix: Thermistor Steinhart & Hart Characteristics

Formula: Ln(R(T)/R25) = A + B/T + C/T^2 + D/T^3 where T is expressed in Kelvins (C + 273.15)

| Code Number | Type | R25 Tol. | B25/85 (K) | B Tol. | A | B | C | D |
|-------------|------|----------|------------|--------|---|---|---|---|
| NTCLE203E3103xB0 | Leaded | 1-5% | 3977 | 0.75% | -14.63372 | 4791.842 | -115334 | -3730535 |
| NTCS0805E3103xMT | SMD 0805 NiSn | 1-5% | 3570 | 3% | -13.40886 | 4547.961 | -176965.9 | 3861154 |
| NTCS0603E3103xMT | SMD 0603 NiSn | 1-5% | 3610 | 1% | -13.40957 | 4481.799 | -150521.7 | 1877103 |
| NTCS0402E3103xLT | SMD 0402 NiSn | 1-5% | 3490 | 3% | -12.0714 | 3503.902 | 109391 | -24154454.74 |

Tolerance code: x = F (1%), G (2%), H (3%), J (5%).

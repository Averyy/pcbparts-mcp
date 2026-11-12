# EV Power Systems

> High-voltage DC buses (48V-800V+), precharge circuits, contactor drivers, fusing, and wire sizing for electric vehicle and battery energy storage systems.

## Quick Reference

- **TI's example sequence closes the main positive contactor at 90-95% of pack voltage.** Close negative, close precharge, verify voltage rise, close positive, then open precharge. The residual voltage must satisfy the actual contactor's make-current limit; 5 * tau reaches 99.3%, not 90-95% [3, p.3; 2, p.5].
- **R = t_precharge / (5 * C_dclink) applies to a 99.3% target from zero initial voltage.** Size pulse energy at maximum charged-pack voltage, not nominal bus voltage [2, p.5].
- **Non-economized coils need pickup/hold/fast-decay control.** Use the contactor's specified currents and timing; AN5940 uses >= 20kHz PWM to limit audible noise [3, pp.3-5; 4, p.9].
- **Eaton's 1.89x fuse example needs all its stated derating factors.** A 30A load gives 56.9A minimum, rounded to 60A, for Kt=0.8, Ke=0.85, Kv=Kf=1, Ka=0.97 and Kx=0.8; this is not a universal 60 degrees C enclosure rule [7, pp.2-4].
- **Victron's current/3 cable-area shortcut is for a total (positive plus negative) cable length up to 5m.** Its table is a 0.259V voltage-drop limit over positive-plus-negative length, not an ampacity rating; check cable temperature/installation and connector limits separately [8, Section 4.1].

## Design Rules

### Precharge Circuit Design

- **Use precharge when inrush exceeds battery, contactor, capacitor or protection-device limits.** Sensata describes 50-100us inrush events reaching thousands of amps in the systems it discusses; those are examples, not every capacitive load's waveform [1, pp.2-4].
- **Precharge contactor + series resistor in parallel with the main contactor.** Positive-leg placement is common; negative-leg placement is also possible. Placing the resistor after the precharge contactor reduces continuously energized connection points [1, pp.4-5].
- **Monitor voltage rise during precharge -- do not use a simple timer.** Voltage rising too slowly can indicate a soft short or downstream load left on. Voltage rising too fast can indicate disconnected loads. Program upper/lower bounds on the voltage curve [1, p.11].
- **Rate the precharge contactor for full pack voltage and peak make current.** Its normal few-second conduction reduces the continuous-current requirement, and it normally opens after the main contactor closes with negligible current; fault interruption still needs a defined path [1, p.5].
- **Open precharge contactor after main contactor closes.** If main contactor fails open with precharge still connected, system current flows through precharge resistor -> thermal failure [1, p.12].
- **TIDA-050080 uses TPSI3100-Q1 + external FET for passive precharge without a secondary bias supply.** Its 5kV RMS reinforced-isolation rating is an isolation-test rating, not a PCB working-voltage or creepage allowance. INA180-Q1 and the driver's fault comparator implement a 25A trip for this design's 20A initial current at 1000V [2, pp.1,6-8].

> WARNING: Select the precharge resistor for the actual exponential pulse and repetition rate. A 400V/6mF initially discharged capacitor dissipates approximately 480J in the series resistance on a full charge. A 5x-power/5s overload specification alone does not establish capability at a shorter, higher-power pulse; obtain capacitive-pulse data or manufacturer confirmation [1, pp.6-10; 2, pp.5-6].

### Contactor Driver ICs

- **Economized vs non-economized coils: know which type you have.** Economized coils integrate internal circuitry (two-coil economizer, or internal PWM with voltage/current feedback) -- just apply power. Non-economized coils are bare windings requiring external driver for pickup/hold/fast-decay profiles [3, pp.3-4].
- **DRV3946-Q1: dual-channel integrated contactor driver for non-economized coils.** Programs pickup and hold current directly, eliminates external current regulation circuitry. Integrated current sense for closed-loop control [3, pp.5-6].
- **VNH7100BAS: H-bridge contactor driver for single-coil non-economized contactors.** Provides all 4 phases: pull-in (full voltage, HSA to LSB), slow recirculation (both high-side on), hold (PWM on LSB at 20kHz), fast decay (reverse polarity). Supports both MCU-controlled and standalone operation [4, pp.5-14].
- **For externally economized coils, TI recommends both high-side and low-side isolation.** A coil-wire short bypassing a single switch can leave the coil energized. TI also shows a converter-enable implementation; the two-switch recommendation is not universal for internally economized coils [3, pp.4-6].
- **Use coil resistance at operating temperature in voltage-based PWM control.** AN5940 uses R(T) = R25 * (1 + 0.00393 * (T - 25)) plus +/-5% winding tolerance over -40 to +125 degrees C. Closed-loop current feedback removes the pre-calibrated voltage/duty map, but still has sensor/control tolerances [4, pp.8-9; 3, pp.5-6].
- **AN5940 measured < 8ms fast decay with L=52mH, R=11ohm and approximately 0.5A hold current.** This is one contactor test. On battery disconnection, the bulk capacitor/clamp must absorb energy at the worst pull-in current while keeping VNH7100BAS supply below its 38V absolute maximum; AN5940 gives the conservative estimate C_bulk > I_coil^2 * L_coil / (V_limit - Vbat)^2; use a V_limit below the absolute maximum with clamp/tolerance margin [4, pp.10-12].
- **A pull-in current dip provides secondary evidence of armature motion.** AN5940 uses this diagnostic in addition to other actuation checks; a waveform feature alone does not prove main-contact closure [4, pp.4-5].
- **Implement contactor-status and insulation diagnostics before closing the main contactors.** Sensata's individual close/open check is conditional on auxiliary feedback and acceptable startup time, rather than a universal startup sequence [3, p.3; 1, p.11].

### Fusing

- **Choose the fuse's DC voltage rating above maximum charged-pack voltage.** TIDA-050080 sizes semiconductor blocking ratings to 1200V for its 800V nominal/1000V maximum bus; that semiconductor example does not establish a universal EV fuse rating [7, p.2; 2, p.6].
- **Many EV fuses provide short-circuit protection only** with a minimum breaking capacity. Overload faults below minimum breaking capacity will not clear -- requires separate protection mechanism [7, p.4].
- **Bourns SF-0603HIA-M and SF-1206HIA-M are separate high-inrush slow-blow families.** The white paper's 0.5-20A and 24-250V ranges cover its broader fuse portfolio, not every HIA-M part. Use the exact part's DC voltage, interrupt rating and time-current curve; the paper describes Bourns' internal AEC-Q200-equivalent tests [6, pp.3-5].
- **Eaton offers bolt-down and PCB through-hole EV fuse mounting.** Its guide lists AEC-Q200, JASO D622 and ISO 8820 as tests used in combinations depending on the fuse rating and mounting; verify qualification of the selected part [7, pp.1-2].
- **Eaton's fuse thermal-connection reference is 1.3A/mm^2.** Higher connection current density needs Ke derating. This reference describes heat conducted out of the fuse, not allowable current density for every busbar or cable [7, p.3].
- **Eaton recommends an additional 0.8 factor for irregular cyclic loading.** Evaluate the actual load profile and time-current coordination separately; the guide calls for further review of loads exceeding 80% of fuse rating for longer than 1s [7, p.4].

### Wire Sizing and Connectors

- **Victron's inverter-system voltage guideline:** 12V up to 3000VA, 24V up to 5000VA, 48V at 5000VA and above. These are its low-voltage installation recommendations, not EV traction-bus limits [8, Section 4.1].
- **Victron voltage-drop table (total positive + negative length, 0.259V drop; contact losses excluded).** These are voltage-drop current limits, not thermal ampacity ratings [8, Section 4.1]:

| Cross-section (mm^2) | Max current at 5m | Max current at 10m |
|----------------------|-------------------|---------------------|
| 16 | 48A | 24A |
| 25 | 75A | 38A |
| 35 | 105A | 53A |
| 50 | 150A | 75A |
| 70 | 210A | 105A |
| 95 | 285A | 143A |

- **Anderson's SB50 derating example allows 58A with 6 AWG at 75 degrees C ambient and a 105 degrees C connector limit.** The 30 degrees C rise is not permission to handle a connector at 105 degrees C; use the manufacturer's touch-temperature guidance as well as its wire-specific curves [5, pp.11-12].
- **Anderson flat-wiping/crimp contacts require multi-stranded copper.** Aluminum promotes galvanic corrosion and crimp relaxation; solid wire does not retain correctly in crimp barrels and can displace the wiping contact. This is Anderson's connector guidance [5, p.12].
- **For parallel Victron inverters/chargers, fuse each unit individually with identical fuses.** The shared large fuse can fail to clear a branch fault quickly enough; coordinate branch cables, fuse curves and available fault current [8, Sections 4.7-4.8].

### BMS Integration

- **CAN bus for BMS communication** -- automotive-standard transceiver with ESD protection (-> `interfaces/can.md`).
- **Cell tap wiring: route sense wires away from high-current conductors.** Filter each sense line with RC to BMS AFE. Cell voltage monitoring and balancing details -> `power/battery.md`.
- **Detect insulation faults before main-contactor closure.** Select the monitoring architecture and trip limits from the applicable vehicle/system requirements; TI's contactor note does not specify a universal ohm/V threshold or qualify a cell-monitor IC as an insulation monitor [3, p.3].
- **TIDA-050080's TPSI2140-Q1/resistor path is non-emergency discharge.** Its example discharges a 2mF link from 1000V to below 60V in about 2 minutes. It does not meet a crash-discharge requirement measured in seconds; determine that time from the actual system requirement [2, pp.3,5,8].

## Common Mistakes

- **Welded contactor diagnosed as "failed to open" when it actually welded on close.** Most contactor welding happens during closure from inrush current, not during opening. Problem not discovered until open is commanded [1, p.2].
- **Precharge resistor burns out from repeated cycling.** Vehicle key cycling triggers precharge every time. Either size resistor for unlimited rapid cycles (heat-sinkable) or implement precharge counter with cooldown timer [1, p.12].
- **Match wet/dry switching ratings to the actual contactor.** Sensata warns that wet-switching a dry-rated gold contact can destroy it in one event; its hermetically sealed GIGAVAC P195/GV210 examples support wet or dry use within their ratings, not immunity to arbitrary arcing [1, pp.12-13].
- **Do not substitute resistor pulse power for FET dissipation.** TIDA-050080 uses a fully switched FET with a series precharge resistor; the resistor's power decays to exp(-2), approximately 13.5%, after one RC time constant. Its 100ms SOA check and 1200V device choice belong to its 50ohm/2mF, 1000V-maximum design, not every precharge circuit [2, pp.5-6].
- **Do not assume a solid-state contactor fails open.** TI's contactor white paper states that mode is most common but supplies no device-level fail-open guarantee or cited regulation. Establish fault isolation and off-state leakage for the actual switch; do not remove mechanical isolation on that statement alone [3, p.6].

## Formulas

**Passive precharge sizing, initially discharged link and no downstream load [2, p.5]:**
**Rule of thumb:** TIDA-050080 uses 5 * R * C for 99.3% voltage, not for the separate 90-95% contactor-sequence example.
**Formula:** R = t_precharge / (5 * C_dclink); full-charge resistor energy E = 0.5 * C_dclink * V_pack_max^2. Use the resistor's pulse curve at the actual time, temperature and repeat rate; equal energy does not imply equal pulse capability.
**Example:** 2mF, 0.5s target -> R=50ohm and RC=0.1s. At 800V the initial current is 16A and full-charge energy is 640J; at the reference design's 1000V maximum they become 20A and 1000J. Initial resistor power is respectively 12.8kW and 20kW; at 5 * RC the dissipated energy is (1 - exp(-10)) of the full-charge value.

**VNH7100BAS hold duty, AN5940's diode-recirculation topology [4, p.8, Equation 6]:**
**Rule of thumb:** V_hold / V_bat omits recirculation-diode and bridge losses.
**Formula:** Duty = (Vf + I_hold * R_coil) / (V_bat + Vf - I_hold * R_HBr). Use hot coil/bridge resistance and the actual recirculation path; this expression does not describe synchronous recirculation through an enabled FET.

**Eaton continuous-load fuse sizing [7, pp.2-4]:**
**Rule of thumb:** Use part-specific corrections, then check cyclic loading, fault interruption and downstream coordination separately.
**Formula:** In >= Ib / (Kt * Ke * Kv * Kf * Ka * Kx). Kf=1 for DC; Kx=0.8 is Eaton's small unventilated enclosure factor. The guide's Ke example has inconsistent wire-size arithmetic, so take Ke from the selected fuse's actual connection data rather than reproducing that derivation.

## Sources

### Related Rules

- `interfaces/can.md` -- CAN bus transceiver selection and ESD protection for BMS communication
- `power/battery.md` -- Cell voltage monitoring, balancing, and BMS design

### References

1. Sensata WP-00012 (Rev. December 11, 2020) -- How to Design Precharge Circuits for EVs White Paper: https://www.sensata.com/sites/default/files/a/sensata-how-to-design-precharge-circuits-evs-whitepaper.pdf
2. TI TIDUF73 (September 2024) -- High-Voltage Passive Precharge Reference Design: https://www.ti.com/lit/pdf/tiduf73
3. TI SLVAF35A (July 2024) -- Driving High-Voltage Contactors in EV and HEVs: https://www.ti.com/lit/pdf/slvaf35
4. ST AN5940 (Rev.1, March 2023) -- Contactor Driver using VNH7100BAS: https://www.st.com/resource/en/application_note/an5940-contactor-driver-using-the-vnh7100bas-stmicroelectronics.pdf
5. Anderson Power -- Technical Reference (Amperage Ratings): https://www.andersonpower.com/content/dam/app/site/resources/techreference/ppmptecref.pdf
6. Bourns -- Automotive Grade Fuses for 48V Systems White Paper: https://www.bourns.com/docs/technical-documents/technical-library/singlfuse/bourns-automotive-grade-fuses-provide-overcurrent-protection-in-harsh-environment-applications-white-paper.pdf
7. Eaton ELX1527 (June 2025) -- EV Fuse Selection Guide ELX1527: https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/technical/eaton-ev-fuse-selection-guide-elx1527-en.pdf
8. Victron Energy -- DC Wiring (Cable Thickness Guide): https://www.victronenergy.com/media/pg/The_Wiring_Unlimited_book/en/dc-wiring.html

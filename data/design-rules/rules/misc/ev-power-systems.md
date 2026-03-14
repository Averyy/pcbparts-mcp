# EV Power Systems

> High-voltage DC buses (48V-800V+), precharge circuits, contactor drivers, fusing, and wire sizing for electric vehicle and battery energy storage systems.

## Quick Reference

- **Precharge to 90-95% of pack voltage before closing main contactors.** 5*tau = 99.3%. Sequence: close negative contactor, close precharge contactor, monitor voltage rise, close positive contactor at threshold, open precharge contactor.
- **Precharge resistor: R = t_precharge / (5 * C_dclink).** Energy dissipated equals E = 0.5 * C * V^2.
- **Contactor coil drive: 3-phase current profile (pickup/hold/fast-decay).** Pickup current up to 5A, hold current in tens of mA. PWM at >= 20kHz to avoid audible noise.
- **EV fuse derating: In >= Ib / (Kt * Ke * Kv * Ka * Kx).** At 60C ambient in sealed enclosure, derate by ~1.89x (60A fuse for 30A continuous load).
- **Wire sizing rule of thumb: cross-section (mm^2) = current (A) / 3** for runs up to 5m at <= 2.5% voltage drop.

## Design Rules

### Precharge Circuit Design

- **Precharge is mandatory for any system with DC-link capacitance and contactors.** Without precharge, inrush current spike (50-100us duration, thousands of amps) welds contactor contacts. Most common contactor failure mode.
- **Precharge contactor + series resistor in parallel with main positive contactor.** Place resistor after contactor to minimize energized connection points when system is off.
- **Monitor voltage rise during precharge -- do not use a simple timer.** Voltage rising too slowly indicates soft short or downstream load left on. Voltage rising too fast indicates disconnected loads. Program upper/lower bounds on the voltage curve.
- **Precharge contactor does not need high continuous current rating** -- precharge events last seconds. Must handle make-under-load thousands of times over vehicle life. Does not need to break current (opens after main contactor closes).
- **Open precharge contactor after main contactor closes.** If main contactor fails open with precharge still connected, system current flows through precharge resistor -> thermal failure.
- **Solid-state precharge replaces mechanical contactor.** TPSI3100-Q1 isolated switch driver + external FET forms solid-state relay needing no secondary bias supply. 5kV RMS reinforced isolation. Pair with INA180-Q1 for overcurrent detection at 25A fault threshold.

> WARNING: Precharge resistor must handle pulse energy, not continuous power rating. A 400V/6mF system dissipates 480J in the resistor. Use wire-wound resistors with short-term overload rating (typically 5x for 5s = 25x for 1s). Confirm capacitive pulse energy with manufacturer if pulse data not published.

### Contactor Driver ICs

- **Economized vs non-economized coils: know which type you have.** Economized coils integrate internal circuitry (two-coil economizer, or internal PWM with voltage/current feedback) -- just apply power. Non-economized coils are bare windings requiring external driver for pickup/hold/fast-decay profiles. Most high-voltage EV contactors (TE, Panasonic, GIGAVAC) offer both types.
- **DRV3946-Q1: dual-channel integrated contactor driver for non-economized coils.** Programs pickup and hold current directly, eliminates external current regulation circuitry. Integrated current sense for closed-loop control.
- **VNH7100BAS: H-bridge contactor driver for single-coil non-economized contactors.** Provides all 4 phases: pull-in (full voltage, HSA to LSB), slow recirculation (both high-side on), hold (PWM on LSB at 20kHz), fast decay (reverse polarity). Supports both MCU-controlled and standalone operation.
- **Always use both high-side and low-side switches for coil drive.** Single-side switching has no protection against short-circuit to battery (high-side) or ground (low-side) -- coil energizes permanently and overheats.
- **Contactor coil resistance varies ~60% over -40C to 125C** (copper tempco 0.393%/C). Voltage feedback (open-loop) requires pre-calibrated voltage-duty cycle map -- poor accuracy with large margin. Current feedback (closed-loop) measures coil current directly and adjusts PWM, eliminating calibration and temperature compensation.
- **Fast decay time < 10ms typical** (L=52mH, R=11ohm contactor). Bulk capacitor absorbs inductive energy if battery path interrupted: C_bulk > I_coil * sqrt(L_coil) / (Vcc_max - Vbat). For VNH7100BAS, keep bulk cap voltage below 38V abs max.
- **Back-EMF dip during pull-in confirms armature movement.** Monitor coil current during pull-in -- dip in rising current waveform indicates armature closing contacts. Absence means contactor did not actuate (mechanical jam or insufficient pull-in current).
- **Contactor weld detection: close and open each contactor individually before precharge** to verify auxiliary feedback. Check downstream voltage sensors before initiating precharge sequence.

### Fusing

- **EV fuse voltage rating must exceed maximum battery voltage at full SoC.** 800V system can reach 1000V at full charge -- use 1200V rated fuses.
- **Many EV fuses provide short-circuit protection only** with a minimum breaking capacity. Overload faults below minimum breaking capacity will not clear -- requires separate protection mechanism.
- **Bourns SinglFuse SF-1206HIA-M: AEC-Q200 equivalent SMD fuse** for BMS cell balance and sense lines. 0603 and 1206 packages, 0.5-20A, up to 250V. High inrush withstand, slow-blow.
- **Eaton EV fuses for main power path:** bolt-down terminals for busbar, PCB thru-hole for board mount. Rated per JASO D622 and ISO 8820 for thermal shock, vibration, cyclic loading.
- **Busbar/wire current density: target 1.3 A/mm^2** (IEC 60269-4 range 1.0-1.6). Higher density requires additional fuse derating (Ke factor).
- **Cyclic loading derating: apply additional 0.8x factor** for variable loads with non-continuous profiles to buffer against thermal fatigue. Sustained overloads > 80% of fuse rating for > 1 second require further derating.

### Wire Sizing and Connectors

- **Voltage-power thresholds:** 12V: up to 3000VA practical. 24V: up to 5000VA. 48V: 5000VA and above.
- **Cable ampacity table (total length positive + negative, 0.259V drop):**

| Cross-section (mm^2) | Max current at 5m | Max current at 10m |
|----------------------|-------------------|---------------------|
| 16 | 48A | 24A |
| 25 | 75A | 38A |
| 35 | 105A | 53A |
| 50 | 150A | 75A |
| 70 | 210A | 105A |
| 95 | 285A | 143A |

- **Anderson Powerpole connectors: derate for ambient temperature.** At 75C ambient, SB50 with 6 AWG (13.3 mm^2) drops from 80A to 58A max. CSA ratings (30C rise) are safe reference for user-accessible connectors; UL ratings (80C rise, 105C housing limit) are for enclosed-only applications.
- **Use multi-stranded copper wire only.** Aluminum causes galvanic corrosion in copper contacts. Solid wire does not compress properly in crimp barrels and acts as lever arm on flat wiping contacts.
- **Fuse each parallel inverter/charger individually** with identical fuses. Single large fuse will not trip on a short in one unit -- fault current through one unit is insufficient to blow oversized fuse.

### BMS Integration

- **CAN bus for BMS communication** -- automotive-standard transceiver with ESD protection (-> `interfaces/can.md`).
- **Cell tap wiring: route sense wires away from high-current conductors.** Filter each sense line with RC to BMS AFE. Cell voltage monitoring and balancing details -> `power/battery.md`.
- **Insulation monitoring mandatory before closing contactors.** Bender A-ISOMETER iso165C (up to 1000V DC, AEC-Q100) or TI BQ79616-Q1 isolation monitor. Trip threshold: >= 100 ohm/V (IEC 61557-8), typical 500 ohm/V for EV packs.
- **Discharge path for DC-link capacitor.** Safety-critical discharge (crash): must reach < 60V within seconds. Non-emergency: minutes acceptable. TPSI2140-Q1 isolated switch + power resistor discharges 1000V/2mF to < 60V in ~2 minutes.

## Common Mistakes

- **Welded contactor diagnosed as "failed to open" when it actually welded on close.** Most contactor welding happens during closure from inrush current, not during opening. Problem not discovered until open is commanded.
- **Precharge resistor burns out from repeated cycling.** Vehicle key cycling triggers precharge every time. Either size resistor for unlimited rapid cycles (heat-sinkable) or implement precharge counter with cooldown timer.
- **Wet-switching a dry-rated contactor destroys it in one event.** Gold-contact dry-rated open-air switches cannot handle arcing. Conversely, wet-rated open-air contactors develop surface contamination in dry service. Use hermetically sealed contactors (GIGAVAC P195, GV210) for both wet and dry switching -- sealed gas environment prevents both arcing damage and contamination.
- **FET SOA not checked for precharge switch.** In RC precharge, power dissipation in FET is ~1/3 of initial magnitude after one time constant. Use 100ms pulse length on SOA chart. Select 1200V breakdown for 800V systems.
- **Single fuse for multiple parallel inverters.** Fault in one unit draws insufficient current to blow shared fuse. Each unit needs individual fusing.
- **Solid-state relay as contactor replacement: failure mode is open, not welded.** Solid-state switches have leakage current in OFF mode and fixed voltage drop in ON mode. Regulations still require at least one electromechanical contactor at one pole when using solid-state at the other.

## Formulas

**Precharge resistor value:**
**Rule of thumb:** 50 ohm for 400V/6mF system with 1.5s precharge time.
**Formula:** R = t_precharge / (5 * C_dclink)
**Example:** 800V system, 2mF DC-link, 0.5s precharge -> R = 0.5 / (5 * 0.002) = 50 ohm. Peak current at t=0: 800V / 50 ohm = 16A.

**Precharge resistor energy:**
**Rule of thumb:** Energy in resistor equals energy stored in capacitor (for precharge >= 3 tau).
**Formula:** E = 0.5 * C * V^2
**Example:** 2mF at 800V -> E = 0.5 * 0.002 * 800^2 = 640J. Average power over 0.5s = 1280W. Select resistor with pulse energy rating >= 640J (e.g., 100W wire-wound with 5x/5s overload = 2500J capacity).

**Contactor hold current duty cycle:**
**Rule of thumb:** Duty = V_hold / V_bat for first approximation. Actual calculation must include body diode drop and coil resistance.
**Formula:** Duty = (Vf + I_hold * R_coil) / (V_bat + Vf - I_hold * R_HBr)
**Example:** Vf=0.7V (body diode), I_hold=0.5A, R_coil=11 ohm, V_bat=12V, R_HBr=0.2 ohm -> Duty = (0.7 + 5.5) / (12 + 0.7 - 0.1) = 6.2 / 12.6 = 0.49 (49%).

**Fuse nominal current with derating:**
**Rule of thumb:** In sealed enclosure at 60C ambient, select fuse rated ~2x continuous load current.
**Formula:** In >= Ib / (Kt * Ke * Kv * Ka * Kx)
**Example:** 30A continuous, 60C ambient (Kt=0.8), sealed enclosure (Kx=0.8), 15mm^2 wire (Ke=0.85), 2500m altitude (Ka=0.97), DC (Kf=1.0), no forced air (Kv=1.0) -> In >= 30 / (0.8 * 0.85 * 1.0 * 0.97 * 0.8) = 56.7A -> use 60A fuse.

## Sources

### Related Rules

- `interfaces/can.md` -- CAN bus transceiver selection and ESD protection for BMS communication
- `power/battery.md` -- Cell voltage monitoring, balancing, and BMS design

### References

1. Sensata -- How to Design Precharge Circuits for EVs White Paper: https://www.sensata.com/sites/default/files/a/sensata-how-to-design-precharge-circuits-evs-whitepaper.pdf
2. TI TIDUF73 -- High-Voltage Passive Precharge Reference Design: https://www.ti.com/lit/pdf/tiduf73
3. Battery Design Net -- Pre-Charge Resistor: https://www.batterydesign.net/pre-charge-resistor/
4. TI SLVAF35 -- Driving High-Voltage Contactors in EV and HEVs: https://www.ti.com/lit/pdf/slvaf35
5. ST AN5940 -- Contactor Driver using VNH7100BAS: https://www.st.com/resource/en/application_note/an5940-contactor-driver-using-the-vnh7100bas-stmicroelectronics.pdf
6. Anderson Power -- Technical Reference (Amperage Ratings): https://www.andersonpower.com/content/dam/app/site/resources/techreference/ppmptecref.pdf
7. Bourns -- Automotive Grade Fuses for 48V Systems White Paper: https://www.bourns.com/docs/technical-documents/technical-library/singlfuse/bourns-automotive-grade-fuses-provide-overcurrent-protection-in-harsh-environment-applications-white-paper.pdf
8. Eaton -- EV Fuse Selection Guide ELX1527: https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/technical/eaton-ev-fuse-selection-guide-elx1527-en.pdf
9. Victron Energy -- DC Wiring (Cable Thickness Guide): https://www.victronenergy.com/media/pg/The_Wiring_Unlimited_book/en/dc-wiring.html
10. ST AN5878 -- How to Design a Robust Automotive CAN System: https://www.st.com/resource/en/application_note/an5878-how-to-design-a-robust-automotive-can-system-stmicroelectronics.pdf

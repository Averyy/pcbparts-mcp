---
source: "TI SLVAE65 -- Dead Battery Application (TPS6598x)"
url: "https://www.ti.com/lit/an/slvae65/slvae65.pdf"
format: "PDF 6pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 6186
---

# TPS6598x Dead Battery Application Note

## Abstract

A system that supports charging with USB Type-C also supports charging when the battery is dead or deeply discharged, and must present Rd on CC1, CC2 and follow all sink rules. This application report describes the implementation of a dead battery in the TPS6598x and the mechanism by which 3.3-V internal circuitry and I/O is powered during dead battery mode.

## 1. Introduction

In many systems, the battery voltage is used to supply voltage to the PD controller's core circuitry and I/O through VIN_3V3. In the event of a deeply discharged battery, the voltage may not be sufficient enough to provide power to the PD controller, resulting in the PD controller not presenting Rd on the CC lines. Type-C USB ports require a sink to present Rd on the CC pin before a USB Type-C source provides a voltage on VBUS, as a result of which the battery will never charge and the system cannot wake up. The TPS6598x supports booting from no-battery or dead-battery conditions by receiving power from VBUS.

Figure 1. Example Power Bank Design

## 2. Device Overview

The TPS6598x power management block receives power and generates voltages to provide power to the TPS6598x internal circuitry. These generated power rails are LDO_3V3 and LDO_1V8. LDO_3V3 may also be used as a low power output for external flash memory. The TPS6598x is powered from either VIN_3V3, VBUS1, or VBUS2. The normal power supply input is VIN_3V3. In this mode, current flows from VIN_3V3 to LDO_3V3 to power the core 3.3-V circuitry and I/Os. A second LDO steps the voltage down from LDO_3V3 to LDO_1V8 to power the 1.8-V core digital circuitry. When VIN_3V3 power is unavailable and power is available on VBUS1 or VBUS2, the PD controller is in dead battery mode, and the TPS6598x is powered from VBUS. In this mode, the voltage on VBUS1 or VBUS2 is stepped down through an internal LDO to LDO_3V3.

Figure 2. Internal Power Management Circuitry

## 3. Device Description

The TPS6598x contains an internal high-voltage LDO which is capable of converting up to 22 V from VBUS to 3.3 V for powering internal device circuitry. The VBUS LDO is only used during dead battery operation while the VIN_3V3 supply is not present. The VBUS LDO may be powered from either VBUS1 or VBUS2. The path connecting each VBUS to the internal LDO blocks reverse current, preventing power on one VBUS from leaking to the other. When power is present on both VBUS inputs, the internal LDO draws current from both VBUS pins.

VIN_3V3 takes precedence over VBUS, meaning that when VIN_3V3 is initially present, the TPS6598x powers from VIN_3V3, and does not boot in dead battery mode. There are two cases in which a power supply switch-over occurs.

### 3.1 Dead Battery Boot Mode

The first is when VBUS is initially present and then VIN_3V3 becomes available. When VIN_3V3 becomes available and then the Dead Battery Flag is cleared, the LDO_3V3 supply will switch from internal VBUS LDO to VIN_3V3 and brown-out prevention is verified by design.

#### 3.1.1 Test Setup and Results

1. Connect source PD controller to unpowered TPS65988 sink to ensure TPS65988 boots in Dead Battery Mode
2. Connect oscilloscope probes
   - CH1: Voltage probe to measure VBUS
   - CH2: Current probe to measure current from external 3.3-V power supply
   - CH4: Current probe to measure current into TPS65988 VBUS
3. Apply external 3.3-V supply to VIN_3V3
4. Clear Dead Battery Flag

In the test below, TPS65988 boots in dead battery mode, and the LDO_3V3 is initially powered by VBUS as can be seen by the positive current flowing into VBUS. When VIN_3V3 is available, and the DeadBattery Flag Clear (DBfg) 4CC command is executed, then LDO_3V3 is supplied by the external VIN_3V3 supply, with no change to VBUS preventing brown-out of any downstream components.

Figure 3. VBUS LDO to VIN_3V3 Supply Switchover

### 3.2 VIN_3V3 Boot Mode

The other way a supply switch-over occurs is when VIN_3V3 is initially present during bootup (device is not in dead battery mode) then VIN_3V3 is removed and falls below 2.85 V. In this case, a hard reset of the TPS6598x is initiated by device firmware, prompting a reboot.

#### 3.2.1 Test Setup and Results

1. Apply 3.3 V from external supply on VIN_3V3 to ensure TPS65988 does not boot in dead battery mode
2. Connect source PD controller to TPS65988 sink
3. Connect oscilloscope probes
   - CH1: Voltage probe to measure VIN_3V3
   - CH2: Current probe to measure current from external 3.3-V power supply
   - CH3: Voltage probe to measure VBUS
   - CH4: Current probe to measure current into TPS65988 VBUS
4. Remove external 3.3-V supply

When VIN_3V3 is removed, the LDO_3V3 is immediately supplied by the internal VBUS LDO, as can be seen by the current transition. To account for fluctuating external 3.3-V supplies, once a specified time interval is passed without a valid external VIN_3V3 supply, the device firmware initiates a hard reset of the TPS65988. After VBUS transitions to VSAFE0V, a new PD contract is negotiated and TPS65988 boots in dead battery mode, as can be seen by internal VBUS LDO supplying LDO_3V3.

Figure 4. VIN_3V3 to VBUS LDO Supply Switchover

## 4. Summary

The TPS6598x supports booting from no-battery or dead-battery conditions by receiving power from Px_VBUS. Type-C USB ports require a sink to present Rd on the CC pin before a USB Type-C source provides a voltage on VBUS. TPS6598x hardware is configured to present this Rd during a dead-battery or no-battery condition. Additional circuitry provides a mechanism to turn off this Rd once the device no longer requires power from VBUS, thus providing the TPS6598x with stable operating conditions during dead battery mode, and eventually when external VIN_3V3 is available.

## 5. References

- USB Type C PD Power Bank Reference Design, TIDA-01627
- TPS65988 Dual Port USB Type-C and USB PD Controller with Integrated Power Switches, Datasheet, Texas Instruments

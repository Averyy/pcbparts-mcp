---
source: "NXP AN11127 -- Bidirectional Voltage Translators NVT20xx/PCA9306"
url: "https://www.nxp.com/docs/en/application-note/AN11127.pdf"
format: "PDF 25pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 14225
---
# Bidirectional Voltage Level Translators NVT20xx and PCA9306

NXP Semiconductors AN11127 (Rev. 2.0, 23 January 2023)

## 1. Introduction

There are many I/O standards that have different voltage level requirements for the input voltage (VIH or VIL) and output voltage (VOH or VOL) typically based on the device operating voltage. In order to interface two devices of differing technologies successfully, voltage level translation is needed and certain requirements must be met:

1. The VOH of the driving device must be greater than the VIH of the receiving device.
2. The VOL of the driving device must be less than the VIL of the receiving device.
3. The output voltage from the driving device must not exceed the I/O voltage tolerance of the receiving device.

Since new low-power devices are designed with advanced sub-micron semiconductor process technologies, there has to be an easy way to prevent damage to the new low-power device and translate voltage switching levels of the higher voltage legacy device.

## 2. Product Offering

The NVT2001, NVT2002, NVT2003, NVT2006, NVT2008, NVT2010, and PCA9306 devices are offered in a wide range of bit widths and packages:

| Device | I/O Pairs | Packages |
|---|---|---|
| NVT2001 | 1 | XSON6 |
| NVT2002 | 2 | TSSOP8, HXSON8 |
| PCA9306 | 2 | SO8, VSSOP8, XSON8, TSSOP8, XQFN8, X2SON8 |
| NVT2003 | 3 | TSSOP10 |
| NVT2006 | 6 | TSSOP16, HVQFN16, DHVQFN16 |
| NVT2008 | 8 | TSSOP20, DHVQFN20 |
| NVT2010 | 10 | TSSOP24, HVQFN24 |

PCA9306 is the same design and function as NVT2002 for SMBus voltage level translation, with more packages available.

## 3. Key Features and Benefits

The NVT20xx family of devices has a lower Ron, Cio, and higher ESD rating than the PCA9306. For PCA9306 and NVT20xx family, VCC(B) - VCC(A) >= 1.0V is needed for operation without a pull-up resistor on the A-side.

| Feature | Description |
|---|---|
| Easy PCB trace routing | Bn and An I/O pairs are matched on either side (flow through pinout) |
| Wide signal supply range | 1.0V to 3.6V (An) and 1.8V to 5.5V (Bn) |
| Minimal channel-to-channel deviation | All transistors on one die with same electrical characteristics |
| Easy migration to lower voltages | Just change VCC(A) voltage without modifying circuit design |
| Lowest 5 uA standby current | Perfect for mobile application |
| Less than 1.5 ns max propagation delay | Accommodates Standard-mode, Fast-mode and Fast-mode Plus I2C-bus |
| Low ON-state resistance | NVT20xx and PCA9306 have lowest Ron at 3.5 Ohm |
| Open-drain I/O ports | Bidirectional voltage translation with no direction pin |
| High ESD protection | NVT20xx provides 4 kV HBM. PCA9306 provides 2 kV. |

## 4. What Is a Voltage Translator and How It Works

The NVT20xx and PCA9306 are functionally the same, but with slightly different electrical characteristics (Ron, Cio, ESD protection). They can be used for bidirectional level translation but do not provide capacitance isolation. They do not need a direction control signal if both sides of driving devices are open-drain outputs.

Each device consists of an array of matching N-channel pass transistors with their gates tied together internally at the EN pin. All transistors are fabricated on one integrated die, leading to very small fabrication-process variation. The source and drain are interchangeable -- either side of the FET can be used as the low-voltage side.

One FET is connected as a reference transistor, and the remainder as pass transistors. The low-voltage side (A1 to An) is the source; the high-voltage side (B1 to Bn) is the drain. The voltage at the low-voltage side of pass transistors is limited to VCC(A).

**Operating requirements:**
- VCC(A) must be <= VCC(B) - 1V to bias the reference transistor into conduction
- The gate of the reference transistor is tied to its drain to ensure FETs operate in saturation

The reference transistor along with a 200 kOhm resistor sets the bias voltage and gate voltage (VG) of all pass transistors. The gate voltage is VG = VCC(A) + VGS, where VGS varies between 0.6V and 1V.

When either An or Bn port is driven LOW, the FET turns ON and a low resistance path exists between them. When Bn is driven/pulled HIGH, the voltage on An is limited to VCC(A). When An is driven/pulled HIGH, Bn is pulled to VCC(B) by pull-up resistors.

When EN is connected through a 200 kOhm pull-up resistor to VCC(B) and I/Os are connected, the translator switch is ON, allowing bidirectional data flow. When EN is pulled LOW, a high-impedance disconnect state exists between ports.

## 5. Applications

### 5.1 Open-Drain I/Os and Bidirectional Translation

For bidirectional translation, drivers on both sides must be open-drain outputs, or they must be controlled to prevent contention between a HIGH on one side and LOW on the other. Pull-up resistors are always required on the B-side and must be sized to not overload the output drivers.

If VCC(B) - VCC(A) < 1V, pull-up resistors are required on the A-side to pull An outputs to VCC(A). The equivalent pull-up resistor value becomes the parallel combination when the pass transistor is ON. If VCC(B) - VCC(A) >= 1V, A-side pull-up resistors are not required.

### 5.2 Multiple Voltages Bidirectional Translation

The NVT2006 can be used in a bidirectional I2C-bus and unidirectional SPI application where a microcontroller at 1.8V interfaces to a 3.3V SPI slave device and a 5.0V I2C-bus slave device simultaneously. Different Bn pull-up voltages can be used for different channels (3.3V for SPI, 5V for I2C). Since VCC(B) - VCC(A) > 1V, A-side pull-up resistors are not required.

### 5.3 Push-Pull I/Os and Unidirectional Translation

The NVT devices can support push-pull or totem pole I/Os, but great care must be taken. They can operate in either down or up unidirectional translation, but the push-pull I/O must be the only driver on the bus. For bidirectional push-pull control, there must be a direction control bit to prevent bus contention.

**Down translation (Bn to An):** Higher voltage driver may be totem pole without pull-up or open-drain with pull-up. If VCC(B) - VCC(A) < 1V, a pull-up is needed on the low voltage side.

**Up translation (An to Bn):** A pull-up resistor is always required on the high voltage side. Totem pole or open-drain driver on low-voltage side.

## 6. How to Size Pull-Up Resistor Value

Sizing depends on:
- Driver sink current
- VOL of driver
- VIL of driver
- Frequency of operation

### 6.1 Driver Sink Current Derating

If VOL of a driver is higher than VIL of the input it drives, the pull-up resistor must be increased. The drive strength is linearly derated as a function of voltage:

    Io = IOL * VIL / VOL

where Io is the estimated derated output current, IOL is the specified output drive strength, VIL is the input LOW threshold, and VOL is the output LOW voltage.

### 6.2 Pull-Up Resistor When VCC(B) - VCC(A) >= 1V

Pull-up resistors needed on B-side only. Two equations must be evaluated (for A-side driven LOW and B-side driven LOW) and the higher value determines minimum Rpu(B).

**When A-side drives LOW:**

    Rpu(B) = (VCC(B) - VOL(A) - Rsw * ID(A)) / ID(A)

**When B-side drives LOW:**

    Rpu(B) = (VCC(B) - VIL(A)) / ID(B)

Example: VCC(A) = 1.5V, VCC(B) = 3.3V, Rsw = 3 Ohm, ID(A) = 10 mA, ID(B) = 15 mA. Minimum Rpu(B) = 312 Ohm.

### 6.3 Pull-Up Resistor When VCC(B) - VCC(A) < 1V

Pull-up resistors needed on BOTH A-side and B-side. Three equations are derived and the minimum Rpu is the higher of:

    Rpu = (VCC(A) + VCC(B) - 2*VOL(A)) / ID(A) [A-side asserted]
    Rpu = (VCC(A) + VCC(B) - 2*VIL(A)) / ID(B) [B-side asserted]

Example: VCC(A) = 2.5V, VCC(B) = 3.3V, ID(A) = 10 mA, ID(B) = 15 mA. Minimum Rpu = 530 Ohm.

**Pull-Up Resistor Minimum Values (3 mA driver):**

| A-side \ B-side | 1.2V | 1.5V | 1.8V | 2.5V | 3.3V | 5.0V |
|---|---|---|---|---|---|---|
| 1.0V | 750 | 845 | 976 | 887 B-only | 1.18k B-only | 1.82k B-only |
| 1.2V | - | 931 | 1.02k | 887 B-only | 1.18k B-only | 1.82k B-only |
| 1.5V | - | - | 1.1k | 866 B-only | 1.18k B-only | 1.78k B-only |
| 1.8V | - | - | - | 1.47k | 1.15k B-only | 1.78k B-only |
| 2.5V | - | - | - | - | 1.96k | 1.78k B-only |
| 3.3V | - | - | - | - | - | 1.74k B-only |

(Resistor values assume VOL = VIL = 0.1*VCC, +/-5% VCC tolerance, +/-1% resistor values. Both-side resistors shown unless marked "B-only".)

## 7. Design for Maximum Frequency Operation

Maximum frequency is limited by minimum pulse width LOW/HIGH and rise/fall times:

    fmax = 1 / (tHIGH(min) + tLOW(min) + tr(actual)/2 + tf(actual)/2)

Rise and fall times depend on translation voltages, drive strength, total node capacitance (CL(tot)), and pull-up resistors.

**Fall time:** Whichever side falls first discharges to VCC(A), then once the channel turns on, both sides discharge together with combined capacitance and parallel pull-up resistance.

**Rise time:** When LOW, both sides rise together (Ron is at minimum, so A and B are essentially one node). As the signal approaches VCC(A), channel resistance increases and waveforms separate, each finishing with its own RC time constant.

**Guidelines to maximize performance:**
- Keep trace length to a minimum by placing the NVT device close to the processor
- Signal round trip time on trace should be shorter than rise/fall time to reduce reflections
- The faster the signal edge, the higher the chance for ringing
- Higher drive strength (via lower pull-up resistor, up to 15 mA) enables higher frequency

## 8. Design for Similar Voltage Levels from Two Different Power Domains

For server applications where two 3.3V power domains cross a boundary (one may be at 3.0V while the other is at 3.6V, or one experiencing power failure):

NVT2003 can be configured with a second reference transistor (made from one channel transistor) connecting A1 to VCC1 and B1 to a supply VCC2 at least 1V above the maximum of either domain. If either pull-up voltage drops to 0V, channels are disabled and in high-impedance state. Pull-up resistors are required on both sides.

## 9. Frequently Asked Questions

**Q: Are the NVT20xx devices arrays of NMOS transistors?**
A: Yes. They were designed as level shifters/clamps where the inherent matching is used by making one transistor a reference and the remaining as level shifters/clamps. Not shown in the schematic are ESD protection devices between each pin and ground.

**Q: Can any transistor be used as the reference?**
A: Yes. However, the VREFB pin is easiest because of its proximity to the EN pin.

**Q: Are An and Bn pins interchangeable?**
A: Yes. The labels are for convenience. An pin could be used as a drain and Bn as a source.

**Q: Are both An and Bn ports 5V tolerant?**
A: Yes. Both ports are 5.5V tolerant, and the EN pin is also 5.5V tolerant.

**Q: Do the NVT20xx devices isolate capacitance?**
A: No. They are basically an array of NMOS transistors.

**Q: What is the typical propagation delay?**
A: With a 50 pF load and low resistance driver, measuring both sides at the same voltage level (e.g., 1.5V), the delay is about 0.25 ns (5 Ohm * 50 pF). The delay from low-voltage side measurement point to high-voltage side is primarily the system RC time constant (pull-up resistor * line capacitance), not the NVT device delay.

**Q: Will NVT prevent ESD from reaching my FPGA?**
A: The NVT20xx devices have ESD protection > 4 kV HBM and should absorb most energy. Very little may reach the FPGA, but this cannot be guaranteed.

**Q: Minimum VCC(B) - VCC(A) differential is 1V. What if I only have 0.8V?**
A: The device will work with 0.8V differential, but the low-voltage side may only reach 2.3V instead of 2.5V. The exact value varies part to part. An external pull-up resistor to the low-voltage supply can ensure the correct level.

**Q: What about unused data paths on an NVT2006?**
A: Treating them as not connected is easiest. Include pads for firm attachment. Alternatively, connect unused Bn and An pins together and tie to GND. Do NOT connect unused paths to EN.

**Q: Can the 200 kOhm resistor be shared by multiple NVT devices?**
A: No, it is best to use separate resistors for each device because different packages may not have identical characteristics and separate resistors allow the circuit to compensate. A 0.1 uF filter capacitor on VREFB is recommended. Note: the capacitor slows power-up to approximately 100 ms with a 200 kOhm resistor.

**Q: Can I use NVT2006 to shift from 1.8V to 3.3V and from 1.8V to 5V simultaneously?**
A: Yes, as long as the low side voltage is the same (1.8V). VREFA connects to 1.8V, and different channels use different drain-side pull-up voltages (3.3V or 5V). Pull-up resistors must not exceed 15 mA per channel.

**Q: Can NVT2010 be used if drivers are not open-drain?**
A: If drivers are not open-drain, you need bus contention prevention (a flag between devices). With that, NVT2010 can be used.

**Q: Can NVT2010 be used to mix 1.5V-to-3.3V and 3.3V-to-5V on one device?**
A: Yes. To protect 1.5V parts, VCC(A) must stay at 1.5V. The 3.3V A-side and 5V B-side pull-ups determine the HIGH levels, with LOW passed through the NVT2010. Pull-up resistor on the 1.5V A-side is optional.

**Q: What is the maximum power dissipation?**
A: The NVT is a passive device with no active control logic. Only standby/reference current flows through the 200 kOhm resistor (approximately 16 uA worst case). Maximum per-channel power dissipation is P = I^2 * R = (15 mA)^2 * 5 Ohm = 1.125 mW maximum per channel.

**Q: How to calculate rise time without a pull-up resistor?**
A: Without a pull-up on the low-voltage side (An), the rise to VCC(A) is essentially the same for both sides. Since propagation measurement is at 50% of swing, the exponential slow-down near the top is not relevant.

## References

1. UM10539 -- NVT2003DP, NVT2004TL and NVT2006PW demo boards user manual
2. UM10540 -- NVT2001GM and NVT2002DP demo boards user manual
3. UM10541 -- NVT2008PW and NVT2010PW demo boards user manual

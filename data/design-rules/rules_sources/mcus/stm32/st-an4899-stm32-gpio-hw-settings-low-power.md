---
source: "ST AN4899 -- STM32 GPIO HW Settings & Low-Power"
url: "https://www.st.com/resource/en/application_note/an4899-stm32-microcontroller-gpio-hardware-settings-and-lowpower-consumption-stmicroelectronics.pdf"
format: "PDF 31pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 16354
---
# STM32 microcontroller GPIO hardware settings and low-power consumption

## Introduction

The STM32 microcontroller general-purpose input/output pin (GPIO) provides many ways to interface with external circuits within an application framework. This application note provides basic information about GPIO configurations as well as guidelines for hardware and software developers to optimize the power performance of their STM32 32-bit Arm Cortex MCUs using the GPIO pin.

This application note must be used in conjunction with the related STM32 reference manual and datasheet.

## 1 General information

STM32 microcontrollers are based on the Arm Cortex processor.

## 2 Documentation conventions

### 2.1 Glossary

- **AMR:** absolute maximum rating
- **GPIO:** general-purpose input output
- **GP:** general-purpose
- **PP:** push-pull
- **PU:** pull-up
- **PD:** pull-down
- **OD:** open-drain
- **AF:** alternate function
- **VIH:** minimum voltage level interpreted as logical 1 by a digital input
- **VIL:** maximum voltage level interpreted as logical 0 by a digital input
- **VOH:** guaranteed minimum voltage level provided by a digital output set to logical 1
- **VOL:** guaranteed maximum voltage level provided by a digital output set to logical 0
- **VDD:** external power supply for the I/Os
- **VDDIO2:** external power supply for the I/Os, independent from VDD
- **VDDA:** external power supply for analog
- **VSS:** ground
- **IIH / IIL:** input current when input is 1 / 0
- **IOH / IOL:** output current when output is 1 / 0
- **Ilkg:** leakage current
- **IINJ:** injected current

### 2.2 Register abbreviations

- **GPIOx_MODER:** GPIO port mode register
- **GPIOx_OTYPER:** GPIO output type register
- **GPIOx_OSPEEDR:** GPIO output speed register
- **GPIOx_PUPDR:** GPIO port pull-up / pull-down register
- **GPIOx_IDR:** GPIO port input data register
- **GPIOx_ODR:** GPIO port output data register
- **GPIOx_BSRR:** GPIO port bit set / reset register
- **GPIOx_LCKR:** GPIO port configuration lock register
- **GPIOx_AFRL:** GPIO alternate function low register
- **GPIOx_AFRH:** GPIO alternate function high register
- **GPIOx_ASCR:** GPIO port analog switch control register

## 3 GPIO main features

STM32 GPIO exhibits the following features:

- Output states: push-pull, or open drain + pull-up/pull-down (GPIOx_MODER, GPIOx_OTYPER, GPIOx_PUPDR)
- Output data from GPIOx_ODR or peripheral (alternate function output)
- Speed selection for each I/O (GPIOx_OSPEEDR)
- Input states: floating, pull-up/pull-down, analog (GPIOx_MODER, GPIOx_PUPDR, GPIOx_ASCR)
- Input data to GPIOx_IDR or peripheral (alternate function input)
- Bit set and reset register (GPIOx_BSRR) for bitwise write access to GPIOx_ODR
- Locking mechanism (GPIOx_LCKR) to freeze I/O port configurations
- Analog function selection (GPIOx_MODER and GPIOx_ASCR)
- Alternate function selection (GPIOx_MODER, GPIOx_AFRL, GPIOx_AFRH)
- Fast toggle capable of changing every two clock cycles
- Highly flexible pin multiplexing

## 4 GPIO functional description

STM32 GPIO can be individually configured in any of the following modes:

- Input floating
- Input pull-up
- Input pull-down
- Analog
- Output open-drain with pull-up or pull-down capability
- Output push-pull with pull-up or pull-down capability
- Alternate function push-pull with pull-up or pull-down capability
- Alternate function open-drain with pull-up or pull-down capability

### 4.1 GPIO abbreviations

| Name | Abbreviation | Definition |
|---|---|---|
| S | Supply pin | |
| I | Input only pin | |
| I/O | Input / output pin | |
| FT | Five-volt tolerant I/O pin | |
| TT | Three-volt tolerant I/O pin | |
| TC | Three-volt capable I/O pin (Standard 3.3 V I/O) | |
| B | Dedicated boot pin | |
| RST | Bidirectional reset pin with embedded weak pull-up resistor | |

Before starting a board design, refer to the datasheet of the STM32 product or to STM32CubeMX to check for GPIO availability.

### 4.2 GPIO equivalent schematics

STM32 products integrate three main GPIO basic structures:

- **Three-volt compliant (TC)** -- see Figure 1
- **Three-volt tolerant (TT)**
- **Five-volt tolerant (FT)** -- see Figure 2

*[Figure 1. Three-volt compliant GPIO structure (TC)]*

*[Figure 2. Three-volt or five-volt tolerant GPIO structure (TT or FT)]*

> The parasitic diode in the analog domain is connected to VDDA and cannot be used as a protection diode. The voltage level VDD_FT is inside the ESD protection block.

> When the analog option is selected (by enabling analog peripheral on the given pin), the FT I/O is not five-volt tolerant anymore since the pin is supplied with VDDA.

> **Caution:** A TT or FT GPIO pin has no internal protection diode connected to VDD. There is no physical limitation against over-voltage. For applications requiring a limited voltage threshold, connect an external diode to VDD.

### 4.3 GPIO modes description

#### 4.3.1 Input mode configuration

Three options:
- **Input with internal pull-up** -- ensures well-defined logical level for floating input
- **Input with internal pull-down** -- ensures well-defined logical level for floating input
- **Floating input** -- signal follows external signal; when no external signal, Schmitt trigger randomly toggles increasing consumption

Programmed as input: output buffer disabled, Schmitt trigger activated, pull-up/pull-down per GPIOx_PUPDR, data sampled into input data register at each AHB clock cycle.

#### 4.3.2 Output mode configuration

Two options:

- **Push-pull output mode:** Uses PMOS (drives HIGH) and NMOS (drives LOW) transistors. Writing 0 to GPIOx_ODR activates NMOS to force pin to ground. Writing 1 activates PMOS to force pin to VDD.

- **Open-drain output mode:** Does not use PMOS; requires pull-up resistor. Internal pull-up (typical 40 kOhm) activated through GPIOx_PUPDR, or external pull-up with value adapted to GPIO output voltage/current characteristics.

> It is not possible to activate pull-up and pull-down at the same time on the same I/O pin.

Open-drain output is often used to control devices at different voltage supply or drive I2C devices with specific pull-up resistors.

#### 4.3.3 Alternate functions

Each pin multiplexed with up to sixteen peripheral functions (SPI, UART, I2C, USB, CAN, LCD, timers, debug, etc.). Configured through GPIOx_AFRL (pin 0-7) and GPIOx_AFRH (pin 8-15).

#### 4.3.4 Analog configuration

Some GPIO pins can be configured in analog mode for ADC, DAC, OPAMP, and COMP internal peripherals. Registers: GPIOx_MODER (mode selection), GPIOx_ASCR (analog function selection).

When in analog configuration: output buffer disabled, Schmitt trigger deactivated (zero consumption for any analog value), pull-up/pull-down disabled by hardware. The analog switch is closed only when analog peripheral is selected/enabled on the given pin.

## 5 GPIO electrical characteristics and definitions

### 5.1 GPIO general information

**AMR (absolute maximum ratings):** Values that must never be exceeded to avoid deterioration or destruction.

**Operating conditions:** Range of guaranteed values for proper operation.

#### 5.1.1 Pad leakage current (Ilkg)

Current sourced from the input signal by the I/O pin when configured in input mode. Depends on I/O structure and voltage range. Product dependent.

#### 5.1.2 Injected current (IINJ)

Current forced into a pin by input voltage (VIN) higher than VDD + delta_V or lower than VSS. Even very small current exceeding the specified limit is not allowed.

- **Negative injection:** VIN < VSS. Maximum -5 mA, minimum VIN = -0.3 V for TT and FT GPIO.
- **Positive injection:** VIN > VDD. For TT and FT GPIO, defined as N/A or 0 mA.
  - N/A: no current injection occurs within AMR range
  - 0 mA: current injection can damage GPIO

> **Warning:** positive current injection is prohibited for a TT or FT GPIO defined as 0 mA.

Maximum VIN = VDD + 0.3 V for TT GPIO. For FT GPIO, VIN max is min(VDD, VDDA, VDDIO2, VDDUSB, VLCD) + 3.6 V, capped at 5.5 V.

Total injected current is limited to typically 25 mA per device.

#### 5.1.3 GPIO current consumption

Two types:
1. **Static current:** mainly due to pull-up resistors when I/O is input held low or output with external pull-down/load.
2. **Dynamic current:** ISW = CL x VDD x FSW
   - CL = total load capacitance (internal + external + PCB + package)
   - FSW = I/O switching frequency

> GPIO speed has no impact on dynamic current consumption.

#### 5.1.4 Voltage output and current drive

All STM32 GPIOs are CMOS and TTL compliant. IOH is sourced current (HIGH state), IOL is sunk current (LOW state). Maximum output current is limited to preserve GPIO and sum cannot exceed AMR values.

*[Figure 3. Output buffer and current flow]*

*[Figure 4. Logical level compatibility]*

CMOS thresholds: VIHmin ~ 2/3 VDD, VILmax ~ 1/3 VDD.
TTL thresholds: VIHmin = 2V, VILmax = 0.8V.

#### 5.1.5 Pull-up calculation

*[Figure 5. STM32 current flow according to output voltage level]*

RPU range: (VDDmax - VOLmax) / (IOL + Ilkg) < RPU < (VDDmin - VOHmin) / (IIH + Ilkg)

**I2C bus pull-up calculation:**

Minimum: RPUmin = (VDD - VOLmax) / IOL

Maximum: RPUmax = trmax / (0.8473 x Cb)

Where Cb is total bus capacitance and trmax is maximum rise time. The 0.8473 factor derives from the RC time constant analysis:
- t1 = 0.3566749 x RPU x Cb (time to reach VIH = 0.3 x VDD)
- t2 = 1.2039729 x RPU x Cb (time to reach VOH = 0.7 x VDD)
- tr = t2 - t1 = 0.8473 x RPU x Cb

### 5.2 Three-volt tolerant and five-volt tolerant

#### 5.2.1 Three-volt tolerant GPIO (TT)

Input voltage cannot exceed VDD + 0.3 V. If analog input function is enabled (ADC, COMP, OPAMP), maximum operating voltage cannot exceed min(VDDA, VREF+) + 0.3 V.

#### 5.2.2 Five-volt tolerant GPIO (FT)

Actually tolerant to VDD + 3.6 V. VIN cannot exceed 5.5 V regardless of supply voltage. When VDD = 0 V, max input = 3.6 V. For multi-supplied GPIO, tolerance is min(VDD, VDDUSB, VLCD, VDDA) + 3.6 V.

> GPIO is five-volt tolerant only in input mode. When output mode is enabled, GPIO is no longer five-volt tolerant.

> GPIO is five-volt tolerant only if no analog function is enabled on pin.

### 5.3 Five-volt tolerant application examples

#### 5.3.1 White LED drive

White LED needs ~20 mA at ~3.5 V (4 V max). STM32 max sink current is 25 mA -- not enough margin for direct drive. Options: external MOSFET/BJT, or driving via two GPIOs in parallel (open-drain, internal pull-up disabled).

*[Figure 6. Example of white LED drive connections]*

#### 5.3.2 Triac drive

*[Figure 7. Example of triac drive connections]*

GPIO must be set in open-drain mode. If drive current insufficient, coupled GPIOs can be used in parallel.

#### 5.3.3 I2C application

STM32 supplied by 1.8 V or 3.3 V can directly communicate with a 5 V I2C bus.

*[Figure 8. Example of I2C connections]*

If VDD = 0 V while VDDX = 5 V (even transient), place a Zener diode (e.g., 3.3 V) between VDD and VDDX.

#### 5.3.4 UART application

If UART transceiver is TTL-compatible 5 V, STM32 can directly communicate. TTL compatible: VOL < 0.8 V, VOH > 2.0 V. A 3.3 V CMOS output can drive without problem. FT pad accepts 0-5 V CMOS level when VDD = 3.3 V.

*[Figure 10. Example of UART connections]*

#### 5.3.5 USB VBUS example

VBUS pad is five-volt tolerant but must comply with VDD maximum rating. Must not connect VBUS when MCU is not powered. Place Zener diode (e.g., 3.3 V) between VBUS and VDD.

*[Figure 11. Example of USB VBUS connections]*

#### 5.3.6 I/O usage for five-volt ADC conversion

FT pads connected to ADC input: when ADC not connected (analog switch open), I/O can accept VDD + 3.6 V. Once I/O input connected to ADC during sampling, parasitic diode to VDDA/VREF+ is forward biased.

Recommended: clamp input voltage with external series resistor and Schottky diode to VREF+. Parasitic diodes are not characterized for reliability.

**Workaround:** If unused FT pad available, connect to ADC input pad in parallel configuration. ADC converts with pull-down enabled first; if result < 2 V (inside ADC range), re-do conversion with pull-down disabled.

## 6 GPIO hardware guidelines

### 6.1 Avoid floating unused pin

Do not leave unused pin floating. Connect to ground or supply on PCB, or use PU/PD. Noise on non-connected input causes extra consumption by making input buffer switch randomly.

If application is sensitive to ESD, prefer connection to ground or define pin as PP output and drive low.

### 6.2 Cross-voltage domains leakage

In multi-voltage applications (3.3 V and 1.8 V, or 5 V and 3.3 V), check that all GPIOs with PU are not exposed to input voltage exceeding VDD. Particularly valid when external circuitry is connected (debugger probe, etc.).

*[Figure 15. Multi voltage leakage example]*

### 6.3 Voltage protection when no VDD is supplied

Five-volt tolerance is guaranteed only if STM32 is supplied. Only possible if VDD > minimum operating voltage. If VDD is not present (grounded), maximum voltage must not exceed 3.6 V.

> **Warning:** If external voltage exceeds maximum, the STM32 device can be damaged.

*[Figure 16. Voltage protection when VDD is not supplied]*

### 6.4 Open-drain output with no load

When GPIO is configured as open drain with no external pull-up or internal pull-up, it must be forced to low drive so input signal is defined. Avoids floating input.

### 6.5 Using the MCO clock output

Clock signals can be a major factor of high current consumption. Choose between routing PCB wire from MCO pin to other clock input components or using an external oscillator based on full clock requirements.

### 6.6 Debug pins have PU or PD by default

Some pins are by default programmed as inputs with PU or PD. If used for other purposes, avoid forcing 0 while PU or 1 while PD (causes extra consumption).

### 6.7 NRST pin cannot be used as enable

Permanently grounding NRST maintains the device in startup phase. Prefer releasing NRST and entering low-power mode (Standby or Shutdown) if possible. NRST already integrates a weak PU (~40 kOhm).

### 6.8 VBAT GPIO has limited current strength

Backup GPIOs are supplied through an integrated switch that has limited drive strength (cannot exceed 3 mA). These I/Os must not be used to drive high current and their speed is limited, even when VDD is valid.

### 6.9 BOOT0 pin

Applying VDD voltage permanently to BOOT0 generates extra consumption.

## 7 GPIO software guidelines for power optimization

### 7.1 Configure unused GPIO input as analog input

If it is not necessary to read the GPIO data, prefer analog input configuration. Saves consumption of input Schmitt trigger.

### 7.2 Adapt GPIO speed

Rise time, fall time and maximum frequency are configurable via GPIOx_OSPEEDR. Adjustment impacts EMI and SSO (simultaneous switching output) due to higher switching current peak. Compromise between GPIO performance vs noise.

IBIS model available for signal integrity control.

### 7.3 Disable GPIO register clock when not in use

If a GPIO bank does not need to be used for a long period, disable its clock via HAL_RCC_GPIOx_CLK_DISABLE().

### 7.4 Configure GPIO when entering low-power modes

All pin signals must be tied to VDD or ground. If GPIO is connected to external receiver, force signal value using PP or PU/PD. When connected to a driver, the driver must provide a valid level.

For practical reasons, use input PU/PD in low-power mode when GPIO is input in Run mode; output PP when GPIO is output in Run mode.

### 7.5 Shutdown exit mode

Applies to STM32L4, STM32L4+, STM32L5, and STM32U5 Series.

When exiting Shutdown mode, GPIOs are reconfigured to default Power On Reset values. This can create extra consumption before reprogramming. If this is an issue, use Standby mode instead.

## 8 GPIO selection guide and configuration

*[Figure 18. GPIO configuration flowchart (1 of 2)]*

*[Figure 19. GPIO configuration flowchart (2 of 2)]*

General recommendations:
- No floating pins
- No pins driving in opposite direction of the internal pull-up / pull-down resistor

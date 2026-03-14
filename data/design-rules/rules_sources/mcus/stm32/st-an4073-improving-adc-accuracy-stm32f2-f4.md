---
source: "ST AN4073 -- Improving ADC Accuracy (STM32F2/F4)"
url: "https://www.st.com/resource/en/application_note/an4073-how-to-improve-adc-accuracy-when-using-stm32f2xx-and-stm32f4xx-microcontrollers-stmicroelectronics.pdf"
format: "PDF 32pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 12552
---
# How to improve ADC accuracy when using STM32F2xx and STM32F4xx microcontrollers

## Introduction

The purpose of this application note is to show how to improve the accuracy of A/D conversions for applications using the STM32F2xx and STM32F4xx microcontrollers. It explains the firmware methodology to reduce ADC error and gives general tips for better ADC accuracy.

Data provided is for reference only, measured in a lab under typical conditions (unless specified otherwise) and not tested in production.

**Applicable products:** STM32F2xx (STM32F20x, STM32F21x), STM32F4xx (STM32F405, STM32F407, STM32F415, STM32F417, STM32F42x, STM32F43x)

## 1 Overview of parameters impacting ADC accuracy

The accuracy of an analog to digital conversion has an impact on overall system quality and efficiency. Many parameters impact ADC accuracy: PCB layout, voltage source, I/O switching, and analog source impedance.

The ADC itself cannot ensure accuracy of results -- it depends on overall system design.

For more details about ADC errors, refer to AN2834 (How to get the best ADC accuracy in STM32F10xxx devices) and AN3137 (A/D converter on STM8L devices).

## 2 Firmware techniques for improving conversion accuracy

### 2.1 Averaging

Averaging is a simple technique where you sample an analog input several times and take the average of the results. Helpful to eliminate the effect of noise on the analog input or a wrong conversion.

#### 2.1.1 Averaging of N ADC samples

Collect samples in multiples of 2 (N should be a multiple of 2). Division can be done by right-shifting the sum (1 CPU cycle in Cortex-Mx).

*[Figure 1. Graphical representation of averaging technique]*

*[Figure 2. Averaging of N sample algorithm]*

Total conversion time = (number of samples x ADC conversion time) + computation time

Computation time = time to read results, add them together, and calculate average.

There is a trade-off between total conversion time and number of samples, depending on analog signal variations and time available.

#### 2.1.2 Averaging of N-X ADC samples

Based on taking N ADC samples, sorting from highest to lowest, and deleting the dispersed X samples. Recommended to choose N and X as multiples of 2.

More efficient than simple averaging as it deletes the most dispersed values that could impact the average. Good trade-off between execution time and conversion accuracy.

*[Figure 3. Averaging of N-X ADC sample algorithm]*

### 2.2 Additional recommendations

ADC conversion results are the ratio of input voltage to reference voltage. If there is noise in the reference voltage, results may not be accurate.

To reduce noise on VDDA (or VREF) and VSSA analog supply pins, connect a capacitor filter to filter high frequency noise.

General firmware design tips for reducing system noise:

1. Avoid starting transmission on communication peripherals just before ADC conversion. I/O toggling creates noise in supply voltage.
2. Avoid toggling high-sink I/Os which cause noise ripples in power supply.
3. Avoid toggling digital outputs on the same I/O port as the A/D input being converted. Introduces switching noise into analog inputs.
4. **Configure ART with data cache + instruction cache enable, and disable the prefetch.** This avoids extra CPU accesses to Flash memory causing additional noise that can significantly decrease ADC accuracy.

## 3 STM32F2 and STM32F4 practical measurements

Applies to all STM32F2xx, STM32F405, STM32F415, STM32F407 and STM32F417 microcontrollers.

### 3.1 Measurement conditions

**Hardware setup:**
- STM32F407ZGT6 on test board (minimum other hardware components)
- Ambient temperature: 25C
- 3 power supplies: VDD/VSS, VDDA/VSSA, VREF+/VREF-
- VDD = VDDA = VREF+ = 3.3 V, fADC = 36 MHz
- External clock 8 MHz, PLL enabled, fCPU = 144 MHz
- Three fixed analog input voltages: 0.3 V, 1.65 V, 3 V

**Firmware setup:**
- ADC channel 2, single conversion mode
- 50000 acquisitions per input voltage
- Five methods: Raw data, Averaging by 4, Averaging by 6, Averaging by 8, Averaging by 8 deleting 4 most dispersed

All tests: fADC = 36 MHz, sampling time = 3 ADC cycles, 12-bit resolution (fastest: 2.4 Msps).

### 3.2 Results

Three ART configurations evaluated:
- ART ON: (data cache + instruction cache + prefetch) ON
- ART OFF: (data cache + instruction cache + prefetch) OFF
- (Data cache + instruction cache) ON + prefetch OFF

Results evaluated versus dispersion range of +/-5 LSB around the most frequent histogram value.

#### 3.2.1 ADC measurements when ART is ON

| VIN | Raw data dispersion (LSB) | Raw over +/-5 LSB | Avg 4 disp | Avg 4 over | Avg 6 disp | Avg 6 over | Avg 8 disp | Avg 8 over | Avg 8-4 disp | Avg 8-4 over |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.3 V | 19 | 6.37% | 10 | 0% | 9 | 0% | 7 | 0% | 8 | 0% |
| 1.65 V | 21 | 7.90% | 13 | 0.05% | 10 | 0% | 10 | 0% | 9 | 0% |
| 3 V | 21 | 21.53% (worst) | 15 | 0.38% | 13 | 0.13% | 12 | 0.006% | 12 | 0.04% |

#### 3.2.2 ADC measurements when ART is OFF

| VIN | Raw data dispersion (LSB) | Raw over +/-5 LSB | Avg 4 disp | Avg 4 over | Avg 6 disp | Avg 6 over | Avg 8 disp | Avg 8 over | Avg 8-4 disp | Avg 8-4 over |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.3 V | 18 | 4.07% | 11 | 0.004% | 9 | 0% | 7 | 0% | 8 | 0% |
| 1.65 V | 20 | 5.99% | 11 | 0.01% | 11 | 0.002% | 10 | 0% | 9 | 0% |
| 3 V | 24 | 16.28% (worst) | 18 | 6.92% | 13 | 0.044% | 11 | 0.008% | 12 | 0.028% |

#### 3.2.3 ADC measurements when (Data+Instruction) cache ON + prefetch OFF

| VIN | Raw data dispersion (LSB) | Raw over +/-5 LSB | Avg 4 disp | Avg 4 over | Avg 6 disp | Avg 6 over | Avg 8 disp | Avg 8 over | Avg 8-4 disp | Avg 8-4 over |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.3 V | 16 | 0.06% | 7 | 0% | 5 | 0% | 4 | 0% | 4 | 0% |
| 1.65 V | 18 | 0.064% | 8 | 0% | 6 | 0% | 5 | 0% | 4 | 0% |
| 3 V | 17 | 0.068% | 8 | 0% | 6 | 0% | 4 | 0% | 4 | 0% |

### 3.3 Timing considerations

Timing based on optimum ART configuration: (Data+Instruction) cache ON, Prefetch OFF.

| Method | CPU cycles |
|---|---|
| Averaging by 4 | 18 |
| Averaging by 6 | 26 |
| Averaging by 8 | 36 |
| Averaging by 8, delete 4 | 517 (sort-based) |

CPU frequency: 144 MHz. Time to get N samples = N x (tSAMPLING + tCONVERSION).

### 3.4 Measurement conclusion

For the most accurate conversion results with STM32F2/F405/F415/F407/F417 ADC: configure ART Flash memory accelerator with **(Data+Instruction) ON and prefetch OFF** to achieve best accuracy by limiting internal noise from Flash.

With 12-bit ADC resolution, +/-5 LSB can be achieved using averaging by 4 algorithm (0.6 Msps) when ART is configured with (Data+Instruction) ON and prefetch OFF.

## 4 STM32F4 ADC accuracy options

Applies to STM32F42x/F43x microcontrollers only.

These products have noise filtering techniques activated internally between ADC analog block and other microcontroller blocks (signal crosstalk, EMI-induced noise, power supply noise).

### 4.1 Configuration options for ADC accuracy

- **Default:** Always active out of reset.
- **Option 1:** Activated by firmware. Continuously masks extra flash access from prefetch mechanism.
- **Option 2:** Activated by firmware. Masks internal flash noise during last ADC sampling cycle.

#### 4.1.1 Option 1

Set ADCDC1 (bit 13) in PWR_CR register.

**Conditions:**
- Prefetch must be OFF
- VDD ranges from 2.4 V to 3.6 V
- Must not be set when ADCxDC2 bit in SYSCFG_PMC is set

#### 4.1.2 Option 2

Set ADCxDC2 (bit 16-18) in SYSCFG_PMC register. One bit per ADC for independent control.

**Conditions:**
- Minimum ADC clock is 30 MHz
- Only one ADCxDC2 bit in case ADC conversions don't start at same time with different sampling times
- ADC resolution should be 12 bits
- Must not be set when ADCDC1 bit in PWR_CR is set

| ADC Mode | One ADCxDC2 | Some/All ADCxDC2 |
|---|---|---|
| Single mode | YES | NO |
| Injected simultaneous | YES | Same sampling time required |
| Regular simultaneous | YES | Same sampling time required |
| Alternate trigger | YES | NO |
| Interleaved | YES | 15+ ADC cycle interval required |
| Regular simultaneous + Alternate trigger | YES | Same sampling time required |
| Injected simultaneous + Regular simultaneous | YES | Same sampling time required |

### 4.2 Practical measurements

Same hardware as Section 3.1.1 but using STM32F43x. ADC1 Channel 1, single conversion, sampling time = 3 cycles, 50000 acquisitions, 12-bit, fADC = 36 MHz (2.4 Msps).

#### Results when ART is ON

| VIN | Default disp (LSB) | Default over | Option 2 disp | Option 2 over |
|---|---|---|---|---|
| 0.3 V | 7 | 0% | 4 | 0% |
| 1.65 V | 9 | 0% | 6 | 0% |
| 3 V | 7 | 0% | 6 | 0% |

(Option 1 not applicable since Prefetch is ON)

Compared to STM32F2xx/F405/F415/F407/F417 max 21 LSB, max here is 9 LSB default, ~75% improvement with Option 2.

#### Results when ART is OFF

| VIN | Default disp | Default over | Option 1 disp | Option 1 over | Option 2 disp | Option 2 over |
|---|---|---|---|---|---|---|
| 0.3 V | 9 | 0% | 5 | 0% | 5 | 0% |
| 1.65 V | 10 | 0% | 7 | 0% | 7 | 0% |
| 3 V | 8 | 0% | 6 | 0% | 6 | 0% |

#### Results when (Data+Instruction) cache ON + Prefetch OFF

| VIN | Default disp | Default over | Option 1 disp | Option 1 over | Option 2 disp | Option 2 over |
|---|---|---|---|---|---|---|
| 0.3 V | 7 | 0% | 4 | 0% | 4 | 0% |
| 1.65 V | 8 | 0% | 6 | 0% | 6 | 0% |
| 3 V | 7 | 0% | 6 | 0% | 7 | 0% |

### 4.3 Measurement conclusions

ADC accuracy options improve code dispersion up to 75% compared to STM32F2xx/F405/F415/F407/F417.

Best ADC accuracy for these products:
- **Default:** Prefetch OFF + Data cache ON + Instruction cache ON = max 8 codes dispersion
- **Option 1:** Same ART config = max 6 codes dispersion
- **Option 2:** Prefetch ON + Data cache ON + Instruction cache ON = max 6 codes dispersion

Options 1 and 2 should only be applied in specific conditions to avoid MCU malfunction.

## Appendix A: Averaging of N ADC samples source code

```c
uint16_t ADC_GetSampleAvgN(uint8_t N)
{
    uint32_t avg_sample = 0x00;
    uint16_t adc_sample[8] = {0,0,0,0,0,0,0,0};
    uint8_t index = 0x00;

    for (index = 0x00; index < N; index++)
    {
        ADC_SoftwareStartConv(ADC1);
        while(ADC_GetFlagStatus(ADC1, ADC_FLAG_EOC) == RESET);
        adc_sample[index] = ADC_GetConversionValue(ADC1);
    }

    for (index = 0; index < N; index++)
    {
        avg_sample += adc_sample[index];
    }

    avg_sample /= N;
    return avg_sample;
}
```

## Appendix B: Averaging of N-X ADC samples source code

```c
uint16_t ADC_GetSampleAvgNDeleteX(uint8_t N, uint8_t X)
{
    uint32_t avg_sample = 0x00;
    uint16_t adc_sample[8] = {0,0,0,0,0,0,0,0};
    uint8_t index = 0x00;

    for (index = 0x00; index < N; index++)
    {
        ADC_SoftwareStartConv(ADC1);
        while(ADC_GetFlagStatus(ADC1, ADC_FLAG_EOC) == RESET);
        adc_sample[index] = ADC_GetConversionValue(ADC1);
    }

    Sort_tab(adc_sample, N);

    for (index = X/2; index < N - X/2; index++)
    {
        avg_sample += adc_sample[index];
    }

    avg_sample /= N - X;
    return avg_sample;
}

void Sort_tab(uint16_t tab[], uint8_t length)
{
    uint8_t l = 0x00, exchange = 0x01;
    uint16_t tmp = 0x00;

    while(exchange == 1)
    {
        exchange = 0;
        for(l = 0; l < length - 1; l++)
        {
            if(tab[l] > tab[l+1])
            {
                tmp = tab[l];
                tab[l] = tab[l+1];
                tab[l+1] = tmp;
                exchange = 1;
            }
        }
    }
}
```

## Appendix C: Firmware sequence to activate Option 1 and Option 2

### C.1 Option 1

```c
void SET_ADCOption1(FunctionalState NewState)
{
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_PWR, ENABLE);
    if (NewState != DISABLE)
        PWR->CR |= ((uint32_t)PWR_CR_ADCDC1);
    else
        PWR->CR &= (uint32_t)(~PWR_CR_ADCDC1);
}
```

### C.2 Option 2

```c
void SET_ADCOption2(uint32_t ADCxDC2, FunctionalState NewState)
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_SYSCFG, ENABLE);
    if (NewState != DISABLE)
        SYSCFG->PMC |= (uint32_t)ADCxDC2;
    else
        SYSCFG->PMC &= (uint32_t)(~ADCxDC2);
}
```

ADCxDC2 parameter can be: SYSCFG_PMC_ADCxDC2 (all), SYSCFG_PMC_ADC1DC2, SYSCFG_PMC_ADC2DC2, or SYSCFG_PMC_ADC3DC2.

---
source: "ADI -- Practical Filter Design Challenges for Precision ADCs"
url: "https://www.analog.com/en/resources/analog-dialogue/articles/practical-filter-design-precision-adcs.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 18781
---
Precision analog-to-digital converters are popularly used in many applications, such as instrumentation and measurement, PLM, process control, and motor control. Current SAR ADCs go up to 18-bit or even higher resolution at x-MSPS, while Σ-Δ ADCs can be 24- or 32-bit resolution at hundreds of kSPS. Users are facing more and more difficulties in limiting the signal chain noise, like in implementing filters, to take advantage of high performance ADCs without limiting the ADCs' capabilities.

This article discusses the design challenges and considerations associated with implementing analog and digital filters into the ADC signal chain to achieve optimum performance. As shown in Figure 1, the data acquisition signal chain can utilize analog or digital filtering techniques, or even a combination of both. Since precision SAR and Σ-Δ ADCs are commonly sampling within the first Nyquist zone, this article will focus on low-pass filters. It is not the intent to address specific low-pass filter design techniques in this article but rather their application in ADC circuits.

Ideal low-pass filters should have a steep transition band and excellent gain flatness in the pass band as shown by the brick wall dashed line in Figure 2. Furthermore, the stop band attenuation should reduce any residual out-of-band signal to zero. The response of some commonly used practical filters are shown in the colored lines in Figure 2. If the pass band gain is not flat or exhibits ripples, this response may scale the fundamental signal. The attenuation of the stop band is not infinite, which limits screening the noise out of band. There can also be a transition band without steep falloff, which degrades noise attenuation around the cutoff frequency. In addition, all non-ideal filters introduce a phase delay or group delay.

The analog low-pass filter can remove high frequency noise and interference from the signal path prior to the ADC conversion to help avoid contaminating the signal with aliased noise. It also eliminates the effects of overdriven signals beyond the bandwidth of the filter to avoid modulator saturation. In case of input overvoltage, the analog filter also limits the input current and attenuates the input voltage. Thus, it can protect the ADC's input circuitry. Noise peaks riding on signals near full scale have the potential to saturate the analog modulator of ADCs. They have to be attenuated with analog filters.

Since the digital filtering occurs after the conversion, it can remove noise injected during the conversion process. In real applications, the sampling rate is much higher than twice the fundamental signal frequency indicated by the Nyquist theorem. So, a postdigital filter could be utilized to reduce noise (such as input noise outside of signal bandwidth, power supply noise, reference noise, noise feed through digital interface, ADC chip thermal noise, or quantization noise) injected during the conversion process by using filtering techniques for a higher signal-to-noise ratio with even higher resolution.

Table 1 briefly lists the advantages and disadvantages of an analog filter vs. a digital filter.

Table 1. Analog Filter vs. Digital Filter

|  |  |  |
| --- | --- | --- |
| Design Complexity | High for high performance filters | Low |
| Cost | High (depending on selected analog components) | Low |
| Latency | Low | High |
| Additive Noise | Adds component thermal noise in band | May introduce digital noise due to quantization |
| ADC Input Protection | Yes | No |
| Programmable | No | Yes |
| Drift Error | Yes | No |
| Aging | Yes | No |
| Multichannel Matching Error | Yes | No |

### Analog Filter Considerations

Antialiasing filters are placed in front of ADCs, so these filters consequently are required to be analog filters. An ideal antialiasing filter features unity gain in the pass band with no gain variation and a level of alias attenuation that matches the theoretical dynamic range of the data conversion system in use.

ADCs exhibit different input resistance depending on their architecture, which impacts the input filter design. The following considerations pertain to designing an ADC's analog input filter.

### Limitations of an RC Antialias Filter Interfacing to an ADC Front End

In the Analog Dialogue article "[Front-End Amplifier and RC Filter Design for a Precision SAR Analog-to-Digital Converter](/en/resources/analog-dialogue/articles/front-end-amp-and-rc-filter-design.html)," by Alan Walsh, there is an application example of an RC filter for the [AD7980](/en/products/ad7980.html) ADC shown in Figure 3.

The calculated RC filter makes a low-pass filter with a cut-off bandwidth of 3.11 MHz. However, some designers may realize that 3.11 MHz is much larger than the input signal of 100 kHz, so the filter cannot efficiently reduce the noise out of band. To achieve higher dynamic range, they may replace the resistor with 590 Ω to get a 100 kHz, –3 dB bandwidth. There are two main problems with this approach. Since there will be more attenuation in the pass band, and up to 30% amplitude attenuation around 100 kHz for the example AD7980 ADC, the signal chain accuracy will be greatly reduced. Smaller bandwidth means larger settling time, which makes the AD7980's internal sample and hold cap unable to fully charge in the specified acquisition time for the next valid conversion. This results in degraded accuracy for the ADC conversion.

The designer should ascertain that the RC filter in front of the ADC can fully settle within the target acquisition time. This is especially important for precision ADCs requiring a larger input current or having the equivalent smaller input impedance. Some Σ-Δ ADCs have maximum input RC value requirements in an unbuffered input mode. Extra narrow low-pass filters with larger resistors or caps that can be added in front of the input amplifier that generally has a large input impedance. Alternatively, ADCs with very high input impedances can be selected, such as [ADAS3022](/en/products/adas3022.html) with its 500 MΩ input impedance.

Figure 3. RC filter using AD7980 16-bit, 1 MSPS ADC.

#### 1. Filter Settling Time for Multiplexed Sampling Signal Chain

A multiplexed input signal typically consists of large steps when switching between channels. In the worst case, one channel is at negative full scale, while the next channel is at positive full scale (see Figure 4). In this case, the input step size will be the full range of the ADC, when the mux switches channels.

One single filter after the mux can be used for the channels, which makes the design simpler and the cost lower. As discussed above, analog filters invariably introduce settling time. Every time the mux switches between channels, this single filter has to be recharged to the value of the selected channel, thus limiting the throughput rate. For a faster throughput rate, one filter for each channel in front of the mux can be an option, but this entails a higher cost.

Figure 4. Multiplexed input signal chain.

#### 2. Pass Band Flatness and the Transition Band Limitation vs. Noise

Applications encountering high noise levels, especially those with high levels of interference occurring close to the edge of the first Nyquist zone, require filters with aggressive roll off. However, as it is known for practical analog low-pass filters, the amplitude rolls down from low frequency to high frequency and has a transition band. More filter stages, or orders, may help improve flatness on in-band signals and render a narrower transition band. However, the design of these filters is complex because they are too sensitive to gain matching to be practical at a few orders of attenuation magnitude. Additionally, any component, such as a resistor or an amplifier, added in the signal chain will introduce in-band noise.

Figure 5. Ideal Butterworth filter transition band with different orders.

There is a trade-off in analog filter design complexity and performance for some specific applications. For example, in power line relay protection with an [AD7606](/en/products/ad7606.html), the protection channels have lower accuracy requirements for the fundamental 50 Hz/60 Hz input signal and its associated first five harmonics, than the measurement channels. One first-order RC filter could be used for the protection channels, while a second-order RC filter provides better in-band flatness and more aggressive falloff transition for the measurement channels.

#### 3. Phase Delay and Matching Error for Simultaneous Sampling

Filter design is not just about frequency design; users may also need to consider time domain characteristics and phase response of the analog filters. Phase delay may be critical in some real-time applications. Phase alteration becomes even worse if phase varies according to input frequency. The phase variation in a filter is normally measured in terms of group delay. For a nonconstant group delay, a signal spreads out in time, causing a poor impulse response.

For multichannel simultaneous sampling applications, such as phase current measurement in motor control or power line monitoring, the phase delay matching error should also be considered. Make sure the additional phase delay matching errors caused by the filters across multiple channels are negligible, or within the signal chain error budget in the operating temperature range.

#### 4. Component Selection Challenges for Low Distortion and Noise

For low harmonic distortion and low noise applications, users have to select qualified components in the signal chain design. Analog electronics are slightly nonlinear, which creates harmonic distortion. In Walsh's article, he discusses how to select a low distortion amplifier and how to calculate the amplifier noise. While active components such as amplifiers need low THD + N, the distortion and noise of passive components like common resistors and capacitors also needs to be taken into account.

Resistors exhibit nonlinearity from two sources: the voltage coefficient and the power coefficient. Depending on the application, resistors manufactured by specific techniques, such as thin film or metal resistors, could be necessary in a high performance signal chain. The input filtering capacitors may also add significant distortion if not specified correctly. Polystyrene and NP0/C0G ceramic capacitors can be good alternatives to improve THD if the cost budget allows.

Besides amplifier noise, even resistors and capacitors have electronic noise that is generated by the thermal agitation of the charge carriers inside an electrical conductor at equilibrium. Thermal noise in an RC circuit has a simple expression, as higher R contributes to the filtering requirement as well as to more noise. The noise bandwidth of the RC circuit is 1/(4RC).

Two formulas are given to estimate the rms thermal noise of resistors and small capacitors.

*k*B (Boltzmann constant) = 1.38065 × 10–23m2kgs–2K–1

T is temperature in K

f is the brick wall filter approximation bandwidth

Figure 6 shows the THD performance effect of an NP0 cap vs. an X7R cap on an [EVAL-AD7960FMCZ](/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/eval-ad7960.html) evaluation board: (a) shows the spectrum of a 10 kHz single tone sine wave with C76 and C77 being 1 nF 0603 NP0 caps while (b) shows the spectrum using 1 nF 0603 X7R caps.

(a) 0603 1nF NP0 Cap

(b) 0603 1nF X7R Cap

**Figure 6. NP0 vs. X7R caps effects on THD on an EVAL-AD7960FMCZ evaluation board.**

With the previous design concerns in mind, the active analog filters can be designed using ADI's [Analog Filter Wizard](https://www.analog.com/designtools/en/filterwizard/). It will calculate capacitor and resistor values, as well as select amplifiers required for the application.

### Digital Filter Considerations

SAR and Σ-Δ ADCs have been steadily achieving higher sample rates and input bandwidths. Oversampling a signal at twice the Nyquist rate evenly spreads the ADC's quantization noise power into a double frequency band. Then it is easy to design digital filters to band-limit the digitized signal, and then decimate to the desired final sample rate. This technique reduces the in-band quantization error and improves ADC SNR. This technique reduces the pressure on the antialiasing filter by relaxing filter roll-off. Oversampling techniques reduce the demands on the filters, but requires higher sample rate ADCs and faster digital processing.

#### 1. Actual SNR Improvement Utilizing an Oversampling Rate on an ADC

Utilizing oversampling and a decimation filter, the SNR improvement can be derived from the theoretical SNR for an N-bit ADC: SNR = 6.02 × N + 1.76 dB + 10 × log10[OSR], OSR = fs/(2 × BW). Note that, this formula only applies to ideal ADCs in which there is only quantization noise.

Figure 7. Oversampling of a Nyquist converter.

Many other sources introduce noise into ADC conversion codes. For example, there is noise from the signal source and signal chain components, chip thermal noise, shot noise, noise in power supplies, noise in the reference voltage, digital feedthrough noise, and phase noise due to sampling clock jitter. This noise may distribute uniformly in the signal band, and appear as flicker noise. Therefore, the actual achieved SNR improvement in the ADC is commonly lower than that calculated in the formula.

#### 2. Dynamic Improvement with Oversampling on the EVAL-AD7960FMCZ Evaluation Board

In application note [AN-1279](/media/en/technical-documentation/application-notes/AN-1279.pdf), it is shown that the measured dynamic range of an 18-bit AD7960 ADC oversampled by 256× is 123 dB. This application is used for high performance data acquisition signal chains, such as spectroscopy, magnetic resonance imaging (MRI), and gas chromatography, as well as vibration, oil/gas, and seismic systems.

As shown in Figure 8, the measured oversampled dynamic range shows a 1 dB to 2 dB degradation from the theoretical SNR improvement calculation. Because the low frequency noise coming from the signal chain components limits the overall dynamic range performance.

(a) Dynamic Range without OSR

(b) Dynamic Range with OSR = 256

Figure 8. Dynamic range improvement with OSR 256.

#### 3. Taking Advantage of an Integrated Digital Filter in SAR and Σ-Δ ADCs

Usually, digital filters reside in an FPGA, DSP, or processor. To reduce the system design effort, ADI provides some precision ADCs with integrated post digital filters. For example, the AD7606 has a one-order post digital sinc filter for oversampling. It is easily configured by pulling up or down the OS pins. The Σ-Δ ADC AD7175-x not only has a traditional sinc3 filter, but also sinc5 + sinc1 and enhanced 50 Hz and 60 Hz rejection filters. The AD7124-x provides a fast settling mode (sinc4 + sinc1 or sinc3 + sinc1 filter) function.

#### 4. Trade-Off Latency with Multiplexing Sampling ADCs

Digital filters have the disadvantage of latency, which depends on the digital filters' orders and master clock rate. The latency should be limited for real-time applications and loop response time. The output data rate in the data sheet is the rate at which valid conversions are available when continuous conversions are performed on a single channel. When the user switches to another channel, additional time is required for the Σ-Δ modulator and digital filter to settle. The settling time associated with these converters is the time it takes the output data to reflect the input voltage following a channel change. To accurately reflect the analog input following a channel change, the digital filter must be flushed of all data pertaining to the previous analog input.

For previous Σ-Δ ADCs, the channel switching speed is a fraction of the data output rate. Therefore, in switching applications such as multiplexing data acquisition systems, it is important to realize that the rate at which conversions are available is several times less than the conversion rate achieved when continuously sampling a single channel.

Some new ADI Σ-Δ ADCs, such as the AD7175-x, contain optimized digital filters to decrease the settling time when channel switching. The AD7175-x's sinc5 + sinc1 filter is targeted at multiplexed applications and achieves single cycle settling at output data rates of 10 kSPS and lower.

#### 5. Avoid Aliasing by Decimation with Digital filters

As discussed in many articles, the higher the oversampling frequency, the easier the analog filter design becomes. When sampling at a higher rate than you need to satisfy Nyquist, a simpler analog filter could be used to avoid any exposure to aliasing from extremely high frequencies. It is difficult to design an analog filter to attenuate a desired frequency band without distortion, but easy to design an analog filter to reject high frequencies with oversampling. Then it is easy to design digital filters to band-limit the conversion signal, and then decimate to the desired final sample rate without losing desired information.

Before implementing decimation, it is necessary to ensure that this resampling will not introduce new aliasing problems. Make sure the input signal follows Nyquist Theorem referring to the sampling rate after decimation.

The EVAL-AD7606/EVAL-AD7607/EVAL-AD7608EDZ evaluation board can run at 200 kSPS per channel. In the following test, it is configured sampling at 6.25 kSPS with an oversampling rate of 32. Then, a 3.5 kHz –6 dBFS sine wave is applied to the AD7606. Figure 9 shows a –10 dBFS alias image at 2.75 kHz (6.25 kHz – 3.5 kHz). Therefore, if there is no qualified antialias analog filter in front of the ADC, the digital filter could cause alias images by decimation when oversampling is used. An analog antialias filter should be used to remove such noise peaks superimposed on the analog signal.

Figure 9. Alias when the OSR decimation sampling rate < twice the Nyquist frequency.

### Conclusion

The challenges and considerations discussed in this article can help the designer implement practical filters to help achieve the objectives of a precision acquisition system. Analog filters have to interface to the nonideal input structures of SAR or Σ-Δ ADCs without violating system error budgets while digital filter should not cause errors on the processor side. It is not an easy task, and trade offs must be made in system specifications, response time, cost, design effort, and resources.

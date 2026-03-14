---
source: "ADI -- How to Build a 24 GHz FMCW Radar System"
url: "https://www.analog.com/en/resources/technical-articles/how-to-build-a-24-ghz-fmcw-radar-system.html"
format: "HTML"
method: "readability"
extracted: 2026-02-16
chars: 22003
---

# Radar Basics: How to Build a 24 GHz FMCW Radar System

### Abstract

This article serves as an introduction to frequency modulated continuous wave (FMCW) radar generation within the 24 GHz ISM band. This includes the major building blocks required for this type of radar system such as ramp generation, transmit and receive stages, downconversion, and sampling.

### Introduction

There is a wide spectrum of radar types but in the most basic sense they are sensors used for object detection. Various types of radars have different limitations in the objects they can detect and the amount of information they can gather from each object. There is no one radar system able to work best for all applications. For example, some lower complexity radars such as continuous wave (CW) might only detect a single object’s velocity. This generally leads to a relatively straightforward to implement and lower cost system in terms of both hardware and software. But there are other scenarios in which knowing an object’s range, or even its size, is paramount and so a more complex system is required. FMCW radar allows the range and velocity of multiple objects to be detected. FMCW radar offers a good compromise between available object data, complexity, and cost. This technology allows flexibility in terms of the applications it can be designed for and thus it will be the focus of this article.

The ADI [TinyRad](/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/eval-tinyrad.html) radar development platform (block diagram shown in Figure 1) will serve as the main example and talking point for this article. The reasoning behind the TinyRad system design, as well as its implementation, will be used to highlight some of the considerations and compromises that would need to be made during the design process of a radar system.



Figure 1. An EV-TINYRAD24G block diagram. The blocks will be explained in detail within this article.

### What Are You Trying to Detect?

Before deciding on the frequency of operation or the specific radar topology to be used, it is useful to first deduce some parameters of the object(s) that the radar should be able to detect.

* Size and material
* Maximum range
* Maximum velocity
* Proximity to other objects
* The amount of information that is required about the target. Is a clear picture of the target required or just a blip?

The radar cross section (RCS) of an object is a measure of an object’s signature as it appears to a radar. A human has an RCS approximately equal to 1 m².

The operating range of a radar can be estimated by the radar equation given in Equation 1. Outside of the target’s characteristics (RCS given as σ), the main aspects dictating the radar range are the wavelength (λ), the antenna gain (GTx and GRx), and the power at the transmit (PTx) and receive (PTx) stages. The maximum range will be the case when the received signal power is at its lowest possible for the system based on the receive minimum detectable signal (MDS). The radar equation may be expanded to include various other effects and losses such as atmospheric absorption, although only the basic form is shown here.

The maximum range of a radar is also related to the pulse length and thus the analog-to-digital converter (ADC) sampling frequency. This is known as the maximum unambiguous range and is related to the time required for the transmit pulse to be reflected and the meaningful radar data to be deduced.

The maximum velocity an FMCW radar can detect is related to the wavelength and sweep time, as shown in Equation 2.

Taking a modulation period of 280 µs as an example, the maximum target velocity would be approximately 44 km/h.

The resultant baseband signals from these ramps will need to be sampled prior to processing and so the ADC sample rate and the number of samples (N) will also factor into the maximum velocity in practice. While the number of samples may be reduced to allow fast ramps to be sampled, this will degrade the velocity resolution.

The ADC and sampling section will discuss further considerations for sampling the baseband radar signals.

### Frequency Considerations

Higher frequencies of operation do come with several benefits. For example, the smaller wavelength gives better range detection and object classification data, and the shorter wavelength also means the antenna patterns will be smaller, which will lead to a smaller sized system overall. In some cases, the antennas may be built into the IC, but we will see that higher frequency is not always better.

For FMCW radar, the bandwidth of the sweep (that is the ramp start frequency to stop frequency given as bandwidth here) is directly related to the range resolution. The range resolution is given in Equation 4. The range resolution is the minimum distance that two targets in the same bearing need to be separated by to be deduced as two separate targets. The required range resolution is one of the most important considerations when choosing the radar’s frequency of operation as it is not possible to increase this without sweeping a wider frequency range, which is not always viable due to band restrictions.

25 GHz is an ISM band, meaning there are minimal restrictions in the markets the radar can be sold in as a commercial product. There is some variation for each region, but in general the 24 GHz ISM band covers 24 GHz to 24.25 GHz. Using Equation 4, this equates to a range resolution of approximately 60 cm for the 24 GHz band.

The 77 GHz band has a relatively wide bandwidth allocation up to 5 GHz. This gives exceptional range resolution but there are some major limitations that should be noted. The main drawback of the 77 GHz band is it being predominately restricted to automotive applications. There are certain region dependent exceptions such as industrial tank level sensing but for the most part the 77 GHz radar would be limited to automotive only markets. Another drawback is that sweeping a bandwidth of 5 GHz at these frequencies, depending on the ramp rate required, is challenging for a standard analog phase-locked loop (PLL) and voltage controlled oscillator (VCO) topology to generate ramps with acceptable linearity. The result is a complex (and expensive) radar system from the ramp generation perspective alone.

Other notable drawbacks of operating in the 77 GHz band would be the increased demand for careful PCB design, manufacturing, and antenna calibration.

The 60 GHz band, like the 77 GHz band, also has a wide bandwidth allocation and shares many of the advantages while also being an ISM band like the 24 GHz band. With that said, a 60 GHz signal propagating through air will suffer a significant spike in attenuation due to the electromagnetic absorption characteristics of oxygen. Often, 60 GHz radars have an effective range of less than 20 m.

### Angular Resolution

The angular resolution of a radar is a direct function of the receive antenna aperture (D) and the number of elements. To find a target’s position, at least two receive channels are required. If the distance between the receive antennas is known, then the delay in the reflected signal when it arrives at one channel compared with another can be used to triangulate the position of a target in relation to the radar.

Most FMCW radars will show the target in a 2D space only. That is, they will not detect the target’s height. There are some advanced techniques that can be used to estimate height, such as by monopulse radar. This requires that the transmitted signals have additional encoding and the height of a target can be calculated based on this encoded data. This requires a complex ramp profile system and advanced post-processing algorithms. So, this article will focus on the standard FMCW radar topology for plotting targets in the 2D domain.

### Ramp Generation

As discussed in the What Are You Trying to Detect? section, the speed of the target will dictate how fast the ramp needs to be.

The most straightforward method for generating FMCW sweeps is to use a PLL and VCO as a frequency synthesizer. Some models of PLLs have in-built frequency sweepers. These use internal timers and clocks to automatically increment the PLL N counter internally. Increasing the N counter will increase the output frequency creating the ramp profile. The exact profile and timing can be customized to suit the specific application—for example, sawtooth vs. triangle waveform, or adding ramp delay periods.

An alternative method of generating FMCW sweeps is to use external wave generators to impose the waveform on the voltage tuning between the PLL charge pump and the VCO. Another option is to use a PLL in a fixed frequency setup and use a digital direct synthesizer (DDS) as its reference input signal. A DDS allows fast frequency switching and so the reference can be swept to create the ramping waveform from the PLL.

For FMCW radar applications, due to the fast frequency hops that make up FMCW ramp, the PLL lock time is of high importance. For a PLL paired with single band VCO, the largest factor in lock time is the bandwidth of the loop filter. Higher loop bandwidth gives a fast settle time, but also can increase in-band phase noise. If the loop bandwidth is too narrow, the frequency ramp may not be linear—especially in the downramp. There may also be excessive undershoot that can lead to spectral emission/compliance concerns. For fast sweeping FMCW, there is a limit as to how wide the PLL’s loop filter bandwidth can be. A rule of thumb is that it should not exceed 10/PFD frequency. In practice, it can be difficult to achieve loop filter bandwidths above 2 MHz due to the small capacitor sizes required and parasitic effects present at the PCB level disrupting the filter design. If an active loop filter is to be used, another rule of thumb is that the gain bandwidth product (GBP) of the op amp should be at least 10 times larger than the PFD frequency.



Figure 2. A mock diagram of multiple detected radar targets and how the ramp bandwidth and phase noise affect the ability to detect and differentiate between each of the targets.

Analog Devices’ free software [ADIsimPLL](/en/lp/resources/adisimpll.html)™ can be used to perform frequency domain performance analysis and time domain ramp analysis of ADI PLLs that include ramp generators. See the video “[Using ADIsimPLL to Simulate Frequency Ramps on the ADF4158](/en/resources/media-center/videos/1846356091001.html)” for a tutorial.

The [ADF4159](/en/products/adf4159.html) PLL includes ramp generation functionally and is included in the ADIsimPLL software, so this will be taken as our ramp generator for this example. Its max frequency of operation is 13 GHz so a VCO with a divide-by-2 output connected to the PLL input should be used to achieve a ramp covering the 24 GHz ISM band.

### Transmit (Tx) Stage

To propagate the transmitted radar signal efficiently by supplying the FMCW ramp with enough gain and to interface with an antenna, a transmit stage is required. We have previously noted that the radar’s range is a function of the transmitted signal’s strength.

A VCO is also required to lock to the PLL discussed in the previous section. The transmit stage can be built discretely, a VCO with its output split to the PLL feedback and to a PA stage. An integrated option is the [ADF5901](/en/products/adf5901.html) MMIC transmit IC. It has a 24 GHz to 24.25 GHz VCO with an in-built divide-by-2 output that pairs with the choice of ADF4159 PLL. The ADF5901 also includes a power amplifier (PA) at its output that gives up to 8 dBm output power. This is sufficient for ranges up to around 100 m (for RCS = 1 m2). To extend the range further, additional external PA stages may be used.

The ADF5901 has two transmit output channels. For normal operation, only one of these is used. The two transmit channels can be alternated for advanced multiple input multiple output (MIMO) operation (see the Other Features section).

An LO signal is also required for the downconversion of the received radar signal. This LO frequency should be at the exact same frequency as the transmitted signal at each moment. For more details on the downconversion, see the Receive Stage (Rx) and Downconversion section.

### Receive Stage (Rx) and Downconversion

We have previously noted that to triangulate a target’s angular position, more than one receive channel is required. We have also seen that the accuracy in angle offset in which a target can be placed (the angular resolution) of a radar system is directly related to the number of receive channels it has. For the receive stage of our proposed radar, we will consider the ADF5904 receive MMIC. The ADF5904 has four receive channels giving relatively modest angular resolution. One way of increasing the number of channels is using multiple receive ICs. This can be done by ensuring they all receive the same LO signal for accurate downconversion. For two ADF5904 ICs, a passive splitter such as a Wilkinson divider is sufficient given the ADF5901 LO output power that is available and the ADF5904’s LO input sensitivity. For a further increase of receive channels with more than two ADF5904 ICs, some gain in the form of a PA (such as the HMC863ALC4) would be required at the LO output.

While larger numbers of receive channels will result in a higher performance radar, this does come with increased data loads—in turn, demanding more processing power. With many receive channels in an imaging radar, real-time processing could require an expensive FPGA solution with complex firmware routines whereas limiting the number of channels means a comparatively low cost DSP can be used to perform processing and data transmission. Therefore, one ADF5904 with four receive channels will be used for this example since another way to increase the effective receive channels is to utilize MIMO operation given our choice of a two-channel transmit configuration.

The signal power of reflected signals from targets is a small fraction of the transmitted signal power; therefore, an LNA is typically used to gain up the received signals. Another concern of the low reflected signal power is that the noise figure (NF) and the resulting output noise of the receive stage will dictate the minimum detectable signal (MDS) and could limit the maximum range of the system.

With poor NF, there is the possibility that targets may not be detected depending on the signal to noise ratio (SNR) required. A traditional communication system would typically target an SNR of 3 dB. For a radar system, this is not quite required, and typical minimum SNRs would be in the 10 dB to 15 dB region. The proposed SNR will depend on the specific application. For example, if it is important to reduce the possibility of missing targets, a lower minimum SNR would be required. If instead the potential for false targets needs to be minimized, then a higher minimum SNR is a better option. The ADF5904 has a noise figure of 10 dBm that results in an MDS of around –94 dB for a 1 MHz baseband BW and an SNR of 10 dB.

For the FMCW radar downconversion, the received signal must be compared with the transmit signal or in this case, a replication of it being the LO signal. The LO is fed into a mixer and the receive signal is downconverted. A common mixer topology in FMCW radar is direct conversion, also known as a homodyne or zero-IF mixer. The ADF5904 incorporates a direct conversion mixer. The output of the mixer is non-IQ real data. The phase and therefore target velocity are deduced by a series of fast fourier transform (FFT) analyses. (See the article “[24 GHz Demorad Radar Solutions Enable New Contactless Sensors for Emerging Industrial Mass Market](/en/resources/technical-articles/24-ghz-demorad-radar-solutions.html)” for information on the data format used with the TinyRad).

### ADC and Sampling

Before the FMCW data can be processed and the useful target information deduced, the downconverted baseband waveforms must first be filtered and sampled using an analog front end (AFE) and ADC, respectively. Outside of the usual ADC considerations such as the number of channels, dynamic range, SNR, capability for simultaneous sampling of each channel, and robust filtering options, the ADC selection will depend on if the radar will need to utilize fast FMCW ramps to aid in detecting many fast-moving targets or if slow ramps are sufficient for the use case.

Our choice of the ADF5904 receive has a supported demodulation bandwidth of up to 10 MHz, so the proposed radar system thus far could support either low speed or high speed FMCW ramps.

Low speed ramps will have a low baseband bandwidth in the 500 kHz range whereas high speed FMCW ramps would require a high speed signal chain to support the baseband signals of bandwidth 10 MHz and upwards.

The [ADAR7251](/en/products/adar7251.html) was designed to interface to the ADF5904 directly and so it is a good option here for slow FMCW ramps due to its low noise and dynamic range.

For applications where the detection of fast-moving targets is required, the [AD8285](/en/products/ad8285.html) is another viable option. It supports wider input bandwidths of up to 12 MHz and allows faster sample rates while sacrificing some noise performance, gain, filtering options, and resolution when compared with the ADAR7251.

The increased data load from fast FMCW ramps also may require an FPGA to handle the increased data whereas slower speed ramps mean a lower power and cheaper DSP can instead be used to perform processing and data transmission. For our example radar system so far, we have been aiming towards a good balance of performance to cost and we will continue this by selecting the ADAR7251 as our ADC.

### Antenna Design

Antenna design is a complex topic and beyond the scope of this article. For accurate angular positioning, the receive elements should not be separated by greater than 0.5λ. For this design, identical center fed patch antennas will be used for each of the transmit and receive channels. The transmit channels should be separated by greater than 0.5λ to enable MIMO operation. This technique is discussed in the following section, but the distances between each antenna must be calibrated and stored to allow the virtual arrays to operate.

### Other Features

MIMO has been mentioned a few times in this article. It is a technique that can be used to increase the effective number of receive channels of the radar for increased angular resolution.

For a non-MIMO operation, only one transmit channel is used and when paired with the four receive channels the angular resolution is approximately 30° with the antenna arrangement discussed previously.

In MIMO mode for the context of this radar, the transmitted signal is sent through one transmit channel (Tx1) and the following radar chirp (or ramp) is sent to the other transmit channel (Tx2). The separation between the transmit channels causes an offset in the angle of arrival at the receive elements when the transmitted signal has been sent from Tx2 vs. with Tx1. If the separation between each element is known, stored, and calibrated then this offset could be used to create additional virtual antenna elements. This means in MIMO mode, the radar has effectively seven receive elements. Four are real physical elements, four are offset virtual elements as they appear to Tx2, and the center element is an overlap of one each of the real and virtual elements. The angular resolution is improved to below 20° when MIMO operation is used in this example.



Figure 3. The top image shows physical antenna positions and separations and the lower image shows how these will appear virtually with MIMO operation.

### Conclusion

We have introduced and discussed some system-level blocks that are used in the building of an FMCW radar. The frequency of operation was targeted at 24 GHz due to it being an ISM band. Slow speed FMCW ramps were used to take advantage of the lower speed sampling signal chain and lower data rates for ease of real-time data analysis. The ADI 24 GHz chipset has been shown to offer a good level of integration and high degree of performance and allows the radar design to be simplified vs. a completely discrete solution. The TinyRad platform is a premade evaluation platform that incorporates this chipset and includes the necessary software to begin evaluating the radar system immediately, without the lead time required to develop the required hardware from scratch. A detailed specification of the TinyRad performance and operation can be found in its user’s guide on the product page.



Figure 4. An EV-TINYRAD24G credit-card sized board, a complete FMCW radar system. The top image shows the top side showing ADI’s 24 GHz chipset. The lower image shows transmit and receive center-fed patch antennas.

While the TinyRad offers good performance for many applications and is likely the best choice for a beginner radar designer, it may be insufficient for some high demanding scenarios such as those with fast-moving targets or at ranges above 200 m (target size dependent). Potential variations to the TinyRad design that could be made to customize the design for a more specific use case have been proposed. The [EV-RADAR-MMIC](/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/eval-radar-mmic.html) is a connectorized evaluation board that lacks most of the plug and play functionality of the TinyRad but lends itself well to further customization as it can interface with an external ADC, processor, and additional external gain stages on the transmit and receive channels.
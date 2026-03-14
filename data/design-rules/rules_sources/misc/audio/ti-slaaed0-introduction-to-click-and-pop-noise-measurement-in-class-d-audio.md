---
source: "TI SLAAED0 -- Introduction to Click and Pop Noise Measurement in Class-D Audio Amplifiers"
url: "https://www.ti.com/lit/pdf/slaaed0"
format: "PDF 18pp"
method: "ti-html"
extracted: 2026-03-02
chars: 20255
---

Application Note

# TAS27xx Introduction to Click and Pop Noise Measurement in Class-D Audio Amplifiers

# Abstract

This application note outlines an
introduction to click and pop noise in Class-D audio
amplifiers, and methods to measure and optimize click and
pop noise for TAS2780, TAS2781, and TAS2764 devices.

# 1 Introduction

Click and pop noise refers to an undesired
transient audible artifact, which gets played on the speaker, usually during power-up
and shutdown of the speaker driver (in this case, the Class-D audio amplifier). Click
and pop noise can occur even if the audio amplifier receives no input and isn’t playing
any music at the output (idle channel condition).

Pop can occur irrespective of the type of
amplifier driving the speaker. However, it is usually lower in more linear amplifiers
such as Class-A or Class-AB as compared to Class-D. The Class-D amplifier outputs are
pulse width modulated (PWM) based switching to achieve high efficiency at higher output
powers. A settled Class-D amplifier output voltage frequency spectrum comprises of the
gained-up audio input signal frequency (Fin) in audio band (20-20KHz) as well tones
around switching frequency (Fsw), and the multiples.

When the device is in idle channel, the
differential voltage across the speaker (in audio band), after the Class-D output is
settled is just the RMS noise voltage of the amplifier. This can be the *Idle channel
noise* of 32uV A-weighted on TAS2780/81 (Refer Electrical Characteristics in data
sheet).

However, during start of the PWM from
shutdown state, the differential error pulses start to build at Class-D output from zero
error voltage hence resulting in a spectral energy that leaks into audio band. A similar
scenario occurs due to stop of PWM pulses. Click and pop can occur at the output of the
Class-D amplifier irrespective of the modulation scheme due to amplifier output
differential offset (Output offset voltage Vos as per data sheet) and amplifier output
settling related artifacts.

[Figure 1-1](#FIG_ALG_Q1W_JZB) shows a sample start and stop of an LSR modulated Class-D PWM switching waveform.

Figure 1-1 Sample LSR Modulated Class-D PWM
Output Switching Waveforms at the Start and Stop

# 2 Measurement Methodology

Pop is effectively quantified as an
output *peak* voltage that gets played across the speaker before settling of
the amplifier output, during power-up and power-down. Since the audio band energy
(20-20KHz) at Class-D output is only of interest, there are audio band pass filters
used at the Class-D output used for measurement. Further an A-weighting filter,
which is used to mimic the human ear response, is cascaded with these preceding
filters.

Figure 2-1 Pop Measurement

The measured pop is quoted as a voltage across the speaker (either in mV or dBV).

For example, 1mV pop refers to -60dBV
click and pop:

Equation 1.

20
\*
l
o
g
10
(
l
e
-
3
)

=

-
60
d
B
V

The typical click and pop performance
measured on TAS2780, for example, is 0.8mV or -62dBV (Referred to as Kcp in
Electrical Characteristics section 6.5 of data sheet)

[Figure 2-2](#FIG_UWV_BBW_JZB) shows the
measured Class-D output waveform and measured pop due to PWM start and stop.

Figure 2-2 Measured Pop Due to Start and
Stop of Class-D PWM

# 3 Introduction to Noise-gate and Pop in Class-D Amplifiers

Past literature studying the
audibility of click and pop to the human ear clearly show that pop is an perceptible
artifact and hence is critical to minimize the same (Reference: [Click and Pop Measurement
Technique](https://www.ti.com/lit/pdf/slea044)). Since click and pop noise voltage can be played across the
speaker, and hence perceptible to the user. Achieving low pop is critical for best
user audible experience.

In TAS27xx family of amplifiers there
exists a *noise gate feature* (NG) (8.4.2.7 on TAS2780 data sheet), in which
the Class-D amplifier is dynamically shutdown and turned back on based on the audio
input received. For example, if the Noise gate threshold is set to -120dBFs the
Class-D automatically shuts down if the audio input to the device remains lower than
this threshold for >50 ms (NG hysteresis time) duration. The moment an audio
sample greater than the NG threshold is received by the device, the device
automatically exits NG and the Class-D amplifier immediately turns on to play the
corresponding sample faithfully at the Class-D output. This feature allows for
improved amplifier efficiency for audio profiles where there are long durations of
silence. Consequently, since repetitive shutdown of the amplifier happens during
entry and exit from noise gate, it is further important that click and pop noise
remain low.

# 4 Causes of Pop in TAS27xx family of Class-D Amplifiers

The following events on TAS27xx family
of amplifiers can lead to a very low, regulated click and pop at the Class-D output:

* Active to Software shutdown
* Shutdown to Active mode
* Noise gate entry and exit (As per audio input and NG threshold (Note: Increasing
  Noise gate threshold higher than default settings can result in higher click and
  pop)
* Idle channel detect entry and exit

The following events can trigger very
high or uncertain pop:

* Software or hardware reset.
* Fault conditions in the device
  such as clock error, over-current error, over-temperature error, and so on.
  (These conditions can result in very high pop due to abrupt shutdown).
* Abrupt dips and overshoots in the
  supply beyond data sheet limits.
* Incorrect hardware/software
  configuration of the device.

# 5 Click and Pop Using TAS27xx

A method to minimize click and pop
noise is to prevent an abrupt build-up of the differential error voltage across the
speaker. This is done by soft-stepping of the differential Class-D output voltage.
This is similar to the concept of volume ramping the audio signal.

One key technique used by TI to
minimize pop is using the Y-bridge feature in TAS27xx family of devices. In the
Y-bridge mode of operation, the Class-D amplifier power stage switches on VBAT
supply rather than PVDD for lower audio inputs. This is done to reduce switching
losses in the power stage and improve the device efficiency at lower power. This
feature also significantly helps reduce pop. During power-up, for example, the
Class-D always switches out of VBAT supply and switches into PVDD later in the power
sequence. This helps minimize the differential error built up across the speaker.
Similarly, before shutdown the Class-D enters VBAT switching to reduce pop.

TI also uses
several patented soft-stepping techniques to build-up the Class-D output PWM pulses
to make sure smooth build-up of differential voltage across the speaker. [Table 5-1](#GUID-890AF2DF-D015-4DF4-B1FB-5998477992B8) summarizes the click and pop performance in TI’s TAS27xx family of devices.

Table 5-1 Click and Pop Performance in
TAS27xx

| Device | Click and Pop (Typical) | Condition (Measured as per Data Sheet) |
| --- | --- | --- |
| TAS2764 | 1mV | TA = 25 °C, PVDD = 12V, VBAT1S = 3.8V, AVDD = 1.8V IOVDD =1.2V, RL = 4Ω + 16µH fs = 48kHz, Gain = 21dBV, SDZ = 1, EDGE\_RATE[1:0]=00, NG\_EN=0, EN\_LLSR=1, PWR\_MODE1, Measured filter free as in Section 7 (unless otherwise noted). |
| TAS2780 | 0.8mV | TA = 25 °C, PVDD = 18V, VBAT1S = 3.8V, AVDD = 1.8V, IOVDD =1.8V, RL = 4Ω + 15µH, fs = 48kHz, Gain = 21dBV, SDZ = 1, NG\_EN=0, EN\_LLSR=0, PWR\_MODE1(2), measured filter free as in Section 7 (unless otherwise noted). |
| TAS2781 | 0.8mV | TA = 25 °C, PVDD = 18V, VBAT1S = 3.8V, AVDD = 1.8V, IOVDD =1.8V, RL = 4Ω + 15µH, fs = 48kHz, Gain = 21dBV, SDZ = 1, NG\_EN=0, EN\_LLSR=0, PWR\_MODE1(2), measured filter free as in Section 7 (unless otherwise noted). |

# 6 Click and Pop Measurement Technique Using AP v6.0. 2

[Figure 6-1](#FIG_VDX_JBW_JZB) shows a pictorial representation of the hardware connection required for click
and pop measurement. DUT refers to the amplifier driving the speaker.

Figure 6-1 Hardware Configurations
Required for Measurement of Click and Pop

## 6.1 Measurement Setup

*APx555B Series Audio Analyzer* equipment is used for this measurement along
with*APx500 Measurement Software Version 6.0.2*. DUT outputs are connected
to this Analyzer input through a passive filter *AUX-00225/0040* which is a
switching amplifier measurement filter to reduce out-of-band switching signal
components before AP measurements. A pictorial representation of the setup is given
in [Figure 6-1](GUID-39C9B532-9545-4D01-9CFF-FC41B359D70C.html#FIG_VDX_JBW_JZB) for reference.

## 6.2 Filter Settings

AP is configured with the filter
settings as shown in [Figure 6-2](#FIG_DXK_DFV_JZB).

Figure 6-2 AP Filter Settings

High-Pass Filter (Elliptic 20Hz):
20Hz, 5-pole elliptic high-pass filter is chosen. The filter has a passband ripple
of 0.01dB and a sharp roll-off to -60dB.

Low-Pass Filter (AES17 20kHz): This
filter is an 8-pole elliptic filter with a corner frequency at 20kHz, satisfying the
AES17 recommendation for converter measurements and other measurements in the
presence of high out-of-band noise. When this filter is selected, the ADC sample
rate is set to 48kHz.

Note: Elliptic filter is chosen over the Butterworth filter as the
Elliptic filter has a better brick wall response compared to a Butterworth filter
and offers more accurate representation of audio pop. Comparison of Elliptic and
Butterworth Filter responses is given in [Figure 6-3](#FIG_ONK_FGV_JZB) and [Figure 6-4](#FIG_YHL_KXP_S1C) for
reference.

Figure 6-3 100Hz Elliptic Filter
Response

Figure 6-4 100Hz Butterworth Filter
Response

## 6.3 Data Capture Settings

For the click and pop measurement,
continuous capture of *Peak Level* is done over a fixed duration of time (for
example, 30 seconds) through *Measurement Recorder* option in APx555
measurement software. This data is stored in a file and post-processing is done over
the stored data to get A-weighted results.

Figure 6-5 Peak Level Measurement Through
Measurement Recorder

The *Save to File* option in the
*Measurement Recorder* option needs to be enabled as shown in [Figure 6-6](#FIG_JXW_B3G_LZB).

Figure 6-6 Save to File Option to be
Enabled

Click the File Settings button and a
pop-up window appears as shown in [Figure 6-7](#FIG_MSZ_SBW_JZB). In this pop-up window, configure a folder path for the *Measurement
Recorder* to save the data. And select file format as *Extensible
Multi-channel PCM* and Bit depth as 24 bits.

Figure 6-7 Save to File Setting
Options

## 6.4 Auto Range Settings for Pop Measurement

A click and pop event is such a fast
transient event that the auto-range inside the audio measurement system does not
have enough time to select the correct range. For this reason, auto-range needs to
be disabled and the range selected must be high enough that the input signal does
not clip in the audio measurement system and low enough that an adequate resolution
is maintained.

For the APX555, there are eleven range options available in audio precision. These
are the same for both the unbalanced and balanced analog inputs:

* 0 Vrms to 310 mVrms
* 310 Vrms to 620 mVrms
* 620 Vrms to 1.25 mVrms
* 1.25 Vrms to 2.5 mVrms
* 2.5 Vrms to 5 mVrms
* 5 Vrms to 10 mVrms
* 10 Vrms to 20 mVrms
* 20 Vrms to 40 mVrms
* 40 Vrms to 80 mVrms
* 80 Vrms to 160 mVrms
* 160 Vrms to 320 mVrms

[Figure 6-8](#FIG_KWH_G3G_LZB) shows that
*Auto Range* is unchecked and a manual range of 310mVrms is chosen as Input
Range.

Figure 6-8 Auto Range is Disabled and a
Fixed Range of 310mVrms is Chosen

With all the settings mentioned
previously, save the AP project file in a location. This file is used with *APX
Sound Level Meter Utility* tool for the Click and Pop measurement.

## 6.5 ASI or I2S Configurations for Pop Measurement

Figure 6-9 Data and Clock
Configurations

In the AP project file, along with
other settings, configure ASI or I2S settings required for the proper operation of
DUT. A typical configuration used for the family of TAS27xx devices is shown in
[Figure 6-9](#FIG_PQC_L3G_LZB).

## 6.6 APx Sound Level Meter Utility

APx Sound Level Meter Utility (Version
6.0.0) is a tool from Audio Precision which is used along with APx500 series
analyzer to perform click and pop measurement. This utility takes advantage of the
file recording capability of the APx500 software. This method of click and pop
measurement is preferred over any other discrete interval measurement methods
because,in a discrete measurement method, even at a relatively fast measurement rate
of 250 per second, a transient click or pop event can get missed between
acquisitions. But in this method, by making a digital recording at a 48kHz sample
rate, we can be sure that any audible transients can get captured.

APx Sound Level Meter Utility comes-up
with an interface as shown in [Figure 6-10](#FIG_OG2_VBW_JZB). Click the *Load Project* button in the interface and select the AP project
file path which was stored with all required configuration needed for the click and
pop measurement.

Figure 6-10 APx Sound Level Meter Utility
Window

## 6.7 Data Acquisition

Click the Acquire button on the
utility to start recording the file. The recording runs for programmed duration as
per the Project file and then stops. During this time, in parallel, turn ON and OFF
the device under test to manipulate the clicks and pops scenario. The acquisition
happens for the programmed Fixed Time saved in the AP project file (Example: 30
sec). Once the recording gets over, click the Analyze button. In the example given
in [Figure 6-11](GUID-E58BC3A6-61CF-485F-9630-D334B1E5D661.html#FIG_J4B_1CW_JZB), 50 cycles of *Turn On* and *Turn Off* of the device was exercised in
parallel, when the AP was doing the acquisition for a fixed duration of 30 seconds.
[Figure 6-12](GUID-E58BC3A6-61CF-485F-9630-D334B1E5D661.html#FIG_LTL_1CW_JZB) shows the peak level getting captured during this period.

## 6.8 Interpreting Click and Pop Waveforms

This window displays Non A-Weighted
raw data at a reading rate of 250 per second. This is the maximum reading rate
option available in AP. By looking at the data, we can understand that a maximum
peak level of approximately 1.4mV got recorded over the complete acquisition period.
Since this measurement was done by repeatedly powering up and powering down the
device, every alternate pop is due to power up or power down. Post power up the
amplifier output offset voltage is high pass filtered (20Hz in AP) and we observe a
falling settling transient voltage from 200uV to 100uV before shutdown.

Figure 6-11 Measurement Recorder Window –
Capture

Figure 6-12 Measurement Recorder Window –
Zoomed Around Max. Peak Level

## 6.9 Post Processing of AP Waveforms

Once the acquisition is over, click
the Analyze button on the APX Sound Level Meter (SLM) utility tool. This opens up
another window titled Filter and Average Waveforms with three views: the original
data, the data after it has been passed through an optional A weighting filter, and
the data after it has been averaged. If you change the filter, time constant, and
averaging settings in the window, the graphs automatically redraw. SLM utility takes
the raw data *saved as file* by the measurement recorder, processed the data
(Filtering and Averaging), and displayed the data as two different waveforms along
with original waveform in the window as shown in [Figure 6-13](#FIG_YJ1_CCW_JZB).

Figure 6-13 Filter and Average Waveform
Window – SLM Utility Analyze Output

## 6.10 A-Weighted Click and Pop Numbers

For the click and pop measurement,
only the Filtered Waveform section is important. You can discard the Averaging Mode,
Averaging Time, and Averaged Data sections as these are not relevant to the click
and pop measurement. Please make sure to choose *A-weighting* as *Filter*
option in the window. This applies the *A-Weighting* filter on the *Original
Waveform* and the resulted *A-Weighted Waveform* appears in the
*Filtered Waveform* section. In [Figure 6-14](#FIG_BFG_W3G_LZB), zoom in around the Maximum peak level, and analyze both the original and
A-weighted waveform outputs.

The original waveform is displaying a
max peak level of approximately 1.4mV (similar to the capture in Measurement
Recorder Window Output). At the same instance, the A-weighted filtered waveform
displays a max peak level of approximately 1.1mV.

Figure 6-14 Filter and Average Waveform
Window – Zoomed Around Max. Peak Level

## 6.11 Exporting the A-Weighted Numbers

As shown in [Figure 6-15](#FIG_VJZ_Y3G_LZB), you can export the A-weighted results to an excel and do a detailed analysis as
well. To do this, right click on the *Filtered Waveform* data and select
*Export* and choose *Export to Excel*. This opens the *A-Weighted
Filter* output in excel.

Figure 6-15 Exporting A-Weighted Pop
Results From APx

# 7 Noise-Gate Pop and Measurement Technique Using APx

To measure the noise gate (NG) power
up and power down pop of the device, a repetitive audio input stimulus slightly
higher than the noise gate threshold is given to excite the device and exit NG (wake
up). This is followed by a long period of silence greater than the NG hysteresis
timer to allow the device to enter NG and shutdown. By default the NG threshold is
at -120 dBFs in TA27xx amplifier product family.

An input stimulus such as this can be
generated using a low frequency, low amplitude sine wave such as 1Hz with -119dBFs.
This makes sure that the device exits from noise gate at the peak audio sample and
enters into noise gate since the amplitude remains well below noise gate for long
durations (> NG hysteresis of 5ms).

Figure 7-1  Sample Generator Excitation
for Capturing Noise Gate Pop

Using Audacity or other software as
well as excitation.wav waveform file can be generated and imported into AP, and
played in the measurement recorder. If an external audio.wav file is used, the file
has to be fed as input in APx as shown in [Figure 7-2](#FIG_KS2_JKV_JZB).

Figure 7-2 APx Configuration for
Importing External .wav Excitation

All other filter settings, I2S
configuration settings, and recorder sample rate settings remain the same.

# 8 Configuring TAS2764 for Improved Click and Pop Noise Performance

This section details the best device
configurations required to reduce pop noise on TAS2764. In TAS2764, to optimize
device click and pop performance, the recommendation is to force the device into
idle channel mode before shutdown and exit out of the same prior to re-start.

The additional I2C configurations
required for the same are as follows:

* w 70 00 fd
* w 70 0d 0d
* w 70 64 04 #force device into idle channel mode
* w 70 00 00 #page 0
* w 70 02 02 #software shutdown
* w 70 00 fd
* w 70 0d 0d
* w 70 64 00 #device exits from idle channel mode

## 8.1 Explanation

Pop minimization is done through
forcing the device into idle channel mode before power down of the device and
exiting from idle channel mode post power up. This is done to effectively stagger
the shutdown pop in the device. This device optimization is already taken care In
TAS2780 and TAS2781 in internal device power up or power down configurations. [Figure 8-1](#FIG_QQJ_DDW_JZB) shows the
click and pop measured on 1 device in Powermode1 Configuration of the device before
and after applying the script.

Figure 8-1  Hardware Configurations
Required for Measurement of Click and Pop

# 9 Summary

This application note explains the fundamentals of
click and pop in Class-D audio amplifiers. The application note introduces the
measurement techniques as well as designed for configurations required in TAS27xx
for achieving improved click and pop noise performance.

# 10 References

* Texas Instruments, *[TAS2780 Digital Input Mono Class-D Audio Amplifier With Speaker IV
  Sense](https://www.ti.com/lit/pdf/SLOSE75)*, data sheet.
* Texas Instruments, *[TAS2781 24-V Class-D Amplifier with Real Time Integrated Speaker
  Protection and Audio Processing](https://www.ti.com/lit/pdf/SLOSE86)*, data sheet.
* Texas Instruments, *[TAS2764 Digital Input Mono Class-D Audio Amplifier With Speaker IV
  Sense](https://www.ti.com/lit/pdf/SLOS998)*, data sheet.
* Texas Instruments, *[Click and Pop Measurement Technique](https://www.ti.com/lit/pdf/slea044)*, application note.
---
source: "ADI (Trinamic) AN-001 -- Parameterization of spreadCycle"
url: "https://www.analog.com/en/resources/app-notes/an-001.html"
format: "HTML"
method: "readability"
extracted: 2026-02-16
chars: 25026
---

This application note is meant to be a practical guideline for parameterization of the ADI TRINAMIC ICs with
spreadCycle™ chopper. In order to understand where to find the parameters mentioned, and how to set
them, please refer the specific product documentation.

### Optimizing Chopper Settings

Chopper settings can easily be optimized by watching the motor axis behavior and feeling motor
vibration with your finger tips, and by optionally measuring the motor current with an oscilloscope.
The following description shall give a guideline to come to good chopper settings for your
application with a minimum time-effort.



#### Motor Settings



As a first step, you should understand which parameters have a direct or indirect influence on the
chopper settings, and thus should be selected before starting optimization.

Table 1. Parameters which should be considered before optimizing chopper settings.

|  |  |  |
| --- | --- | --- |
| Motor type | Each motor type has unique characteristics like torque curve, inductivity, back-EMF, microstep quality and coil resistance. | Choose a motor fitting your requirements based on the motor torque curve, cost, current, etc. Generally a higher current winding will bring higher velocity limits. |
| Driver supply voltage | Motors cannot operate well below or above their specific voltage limits. | As a guideline, satisfy: RCOIL \* ICOIL << VS < 25 \* RCOIL \* ICOIL |
| Motor coil current | Normally, stepper motors work best at their nominal current, as they provide the highest torque and lowest relative torque ripple. However, factors which might lead to operation at reduced current levels are:   1. Reduction of power dissipation 2. Standby operation | As a guideline operate a stepper at 50% to 100% of nominal current. A short time increase using coolStep™ will provide for extra torque, while the nominal current can be reduced. In standby, current can be reduced down to zero, depending on mechanics and application. |
| Velocity | There are three basic ranges:   1. Low velocity (slow, a few microsteps per second) – here the microstep performance is most important for equidistant steps 2. Medium velocity (motor turning faster) – the optimum sine waveform can be reached, because the back EMF voltage is still below the supply voltage VS 3. High velocity (motor at several rounds per second) – the sinusoidal target waveform cannot be reached any more. The waveform becomes distorted and motor torque drops with increasing velocity. | The motor behavior can be optimized for all of these velocity ranges. Range 1 (slow) and 2 (medium) can be optimized together. Range 3 (fast) might profit from fullstepping and thus can be optimized separately, in case the optimization for range 1 and 2 does not prove sufficient for the application. |
| Chopper frequency | The chopper frequency is determined by many parameters. Basically, it usually should be outside the audible range, i.e. above 16 to 20kHz, but not too high, i.e,. below 50kHz, in order to limit switching losses in the motor and the power driver. | Try to keep chopper frequency low, but above the audible range. For highest velocity operation, a higher frequency may be beneficial. |
| Waveform | For most stepper motors a sinusoidal waveform is a good approach. Specific applications requiring most equidistant microsteps may profit from an adapted microstep waveform. | The waveform can be best optimized when using a high resolution encoder or a laser pointer attached to your motor and moving the motor at very low velocity. |

### Qualitative Approach for a Two Phase Stepper

We will optimize motor settings for the required velocities sequentially; however one or more
iterations might be taken in case a single set of settings is desired.



#### Preparations



Take your motor into operation at nominal conditions. Attach an oscilloscope with current probe to
one of the motor coils, if possible. You might measure the coil voltage to assess the chopper
frequency. In case you have access to the sense resistors, measure the voltage over one or both
sense resistors. This way, you do not need a current probe.

1. Select proper hardware settings like blank time TBL.

*Hint*: A too low TBL will lead to distorted sine waves, but the value should not be unnecessarily
high. 1-2µs (TBL= 1 or 2 at 16MHz clock frequency) is a good starting point.

2. Switch on spreadCycle chopper mode (chm=0)
3. Choose an off-time setting tOFF in the range of 5µs to 20µs
   𝑇𝑂𝐹𝐹 = ⌊𝑡𝑂𝐹𝐹 ∗
   𝑓𝐶𝐿𝐾
   32 −
   12
   32⌋
4. Choose a hysteresis end value of 5 to 12, e.g., 10, and write it to HEND (HSTART=0, HEND=13).
   Remember, that HEND uses an offset of -3, HSTART uses an offset of +1.



#### Low and Medium Velocity Optimization



In the low and medium velocity range, the motor is to work with equidistant steps, lowest possible
vibration, and low chopper noise. Use highest possible microstep resolution for your tests.

Operate your motor at a medium velocity. Try feeling motor vibrations at different velocities with your
fingertips. Try seeing and feeling microstep equidistance at very low velocities.

*Hint*: A long pointer attached to the motor axis will help checking microstep performance at lowest
velocity.

You might want to check the current waveform using an oscilloscope. The oscilloscope should show
a pure sine wave as shown in Figure 1. In case, the sine wave is distorted like shown in Figure 2.2,
the motor velocity is too fast, or the supply voltage is not high enough. A distortion as shown in
Figure 2.3 is a hint for a too low blank time setting. Increase TBL by one. Other distortions are a hint
to a layout problem.



Figure 1. Current waves. CH1 & CH2: Sense resistor voltages, CH3: Current probe on coil A Figure 2.2



Figure 2. Velocity too high – motor current cannot follow.



Figure 3. Distortion caused by too low blank time setting TBL.



#### Optimize Chopper Settings – Behavioral Approach



1. Now, reduce hysteresis to 0 (e.g. HSTART=0; HEND=2). You should perceive increased motor noise
   and less equidistant microsteps. Vary the motor velocity, if you do not perceive any difference in
   motor vibration between hysteresis 0 and the previous hysteresis value. When observing
   microstep equidistance at very low velocity, the motor will make a few shorter steps in intervals
   matching to the microstep resolution – this will look like the motor pausing and continuing
   rotation once at each halfstep position.
   Increase the HEND hysteresis setting, until motor vibration does not reduce further or microstep
   equidistance does not benefit anymore from a further increase. Do one or two additional
   increments if in doubt, to compensate for stray of analog parameters, like supply voltage, etc. If
   you reach the limit of HEND setting (HEND=15), you can increment HSTRT up to HSTRT=3.
2. In case, you end up with a hysteresis setting higher than 15, or the chopper frequency becomes
   audible (high pitch chirping), reduce off-time (TOFF) and go back to step 1.
3. Try increasing off time (TOFF) and find the value where audible chopper noise occurs. Go back by
   some steps again and go back to step 1 with the new setting. This way, the chopper frequency
   becomes reduced, in case it was higher than necessary.



#### Optimize Chopper Settings – Measure with Oscilloscope



* Stop the motor at a position, where one coil current has a medium value, e.g. at a fullstep
  position. Attach the oscilloscope probe and measure sense resistor voltage to GND. Take a single
  shot of one or a few chopper cycles as shown in Figure 2.4 (showing a chopper operating at
  40kHz).


Figure 4. Measure the duration of the fast decay state (2.7μs): CH1: sense resistor voltage, CH3: coil current.

* Check the duration of the fast decay cycle as shown – the duration will vary slightly from cycle to
  cycle. Its (estimated) medium duration should be slightly larger than the blank time tBLANK (see
  table). In case, the duration is too short, increase the HEND hysteresis setting. If you reach the
  limit of HEND setting (HEND=15), you can increment HSTRT up to HSTRT=3.
  In case the duration is much longer than tBLANK, reduce the hysteresis.

Table 2. Blank time setting.

|  |  |  |  |
| --- | --- | --- | --- |
| TBL | Selects the comparator blank time tBLANK. | 0 | 16 tCLK |
| 1 | 24 tCLK |
| 2 | 36 tCLK |
| 3 | 54 tCLK |


* Measure the chopper frequency. A frequency between 20kHz and 50kHz is a reasonable value.
  Decrease TOFF in case the frequency is too low, increment TOFF in case the frequency is too high.
  Go back to step 1, after changing TOFF.



#### Using Hysteresis Decrement



The hysteresis decrementer will stabilize the chopper frequency in low voltage situations and when
the motor back EMF comes near to the supply voltage at increased motor velocity. Therefore, two
additional steps are required:

* Now distribute the hysteresis value you determined to HSTART and HEND value. As a thumb rule,
  we will put 20%-30% of the hysteresis value to hysteresis start setting.

  *Example*: In case you determined a hysteresis value of 10, set HSTART=2; HEND=10. Taking into
  account the offsets of +1 for HSTRT and -3 for HEND, this results in hysteresis start = 3+7 and
  hysteresis end = 7.
* Choose hysteresis decrement speed if your driver allows it. In case you target high chopper
  frequencies (≥40kHz), use 16 clocks (HDEC=0) setting. In case you target lower chopper frequencies
  (25 - 40kHz), you can increase to 32 clocks (HDEC=1), or for lower frequencies a higher setting. If
  hysteresis decrement shall not be used, put most of the value to HEND or use highest HDEC
  setting.



#### Stand Still Optimization



In standstill, chopper noise and position maintenance are the main targets of optimization. In case
the current can be reduced to zero (driver off), chopper noise is zero, but the motor position must be
maintained by mechanical friction. In order to keep the microstep target position, or in case increased
holding torque is required, the motor current cannot be reduced to zero, but typically to 25% to 75%
of operating current.

Put the motor to very slow motion but use the stand still current settings. One or a few microsteps
per second will fit, in order to assess stand still chopper noise at different positions, as it will
randomly occur at some microstep positions.

In case the stand still chopper noise is not an issue or is already good, you can skip this step.

*Hint*: Stand still chopper noise often can only be assessed in a quiet environment, as it should be
barely audible.

1. Try increasing the chopper frequency by reducing TOFF setting to reduce audible noise at noisy
   positions. You might also try reducing the chopper frequency, as mechanics transmits different
   frequencies with different quality.
   Hint: After modifying TOFF, you might need to optimize low and medium velocity chopper
   settings again.
2. Try switching on random off time (rndtf). This will spread the spectrum of noise.
3. In case your driver supports chopSync™, switch on chopSync™ alternatively to rndtf. Use a
   frequency fSYNC near your target chopper frequency. Reduce TOFF by a few decrements to ensure
   that the native chopper frequency is lower than the chopSync™ frequency.
   𝑆𝑌𝑁𝐶 = ⌊
   𝑓𝐶𝐿𝐾
   64 ∗ 𝑓𝑆𝑌𝑁𝐶
   ⌋
   In case switching on chopSync™ leads to half the desired chopper frequency becoming audible,
   reduce TOFF or increase SYNC.

   Additionally, select a velocity threshold VHIGH at low or medium operating velocity, above which
   chopSync™ becomes switched off, as it will lead to worse motor noise at increased velocity.

   *Hint*: After switching on chopSync™, you might need to optimize low and medium velocity
   chopper settings again.
4. Try reducing motor current further, if feasible.
5. Use a set of good microstep positions in standstill by always positioning to these positions. A
   good microstep position will reoccur at a distance of one fullstep. Read out the microstep pointer
   to make sure that you stop at the same position.

   *Attention*: Excessive standstill chopper noise often is a hint to a bad PCB layout.



#### High Velocity Optimization



At high velocity, the motor resonance must be kept low, in order to maintain torque as high as
possible. Microstep waveforms play a reduced role, as the waveform cannot be maintained in this
velocity range anymore (see Figure 2.2), getting worse with each increase in velocity. Fullstepping
sometimes brings a few percent increased motor torque. For high velocity behavior, it is more
important to operate the motor with its application specific load or in its application environment,
but you can do first tests by braking the motor with your fingers, in order to assess its torque before
it stalls.

You can test high velocity behavior by slowly accelerating the motor to the target velocity. In case,
your motor has high resonances or even stalls, before it reaches the target velocity, retry with a faster
acceleration, and try to make sure that you skip the critical velocity in your later application. At
extremely high velocities, the impact of mechanical motor load and mounting conditions is larger, as
the driver cannot control the current waveform anymore (compare Figure 2.7)

1. You might decide to increase chopper frequency for high velocity operation by reducing TOFF
   setting. A setting in the range of two to four often gives the optimum performance for highest
   velocity. A higher chopper frequency reduces the response time of the chopper.
   Hint: After modifying TOFF, you might need to optimize low and medium velocity chopper
   settings again.
2. Try switching the motor to fullstepping, if your driver supports it. Make sure, that the driver coils
   see a fixed current. Therefore it is important to switch to fullstep at or near the fullstep positions
   (TMC26x based drivers) – compare Figure 2.5. Set VHIGHFS (for TMC5XXX drivers).
3. As fullstepping does not require high precision chopper operation, you can try to switch to slow
   decay only chopper – compare Figure 2.6, e.g., by setting VHIGHCHM (for TMC5XXX drivers).
4. Figure out a velocity threshold VHIGH for switching to fullstepping. The threshold can be
   determined using an oscilloscope and finding the velocity, above which the microstep sine wave
   cannot be maintained, as shown in Figure 2.2, or, by assessing motor noise and vibration.



Figure 5. Motor in fullstep operation (CHM=0); CH1 & CH2: Sense resistor voltages, CH3: Current probe coil A.



Figure 6. Motor operation in fullstep with slow decay only (CHM=1).



Figure 7. Motor operation at very high velocity.



#### Low Inductivity Motor Optimization Example



Low inductivity motors allow high velocity operation. On the other hand, chopper ripple may become
excessively high, because the coil current raises and falls quickly due to the low inductivity. This
example guides through the optimization with an example motor using a TMC5130-EVAL. The result
may be used also for all spreadCycle drivers, like TMC2130.

Motor: QSH4218-47-28-040 (0.5Ohm, 0.6mH)

Checking performance using Eval board default settings:

* Standard settings: Velocity=200 000 for all measurements (about 4 RPS).
* RSENSE=0R15, IRUN=23
* TOFF=5, HSTRT=5, HEND=3, TBL=2 (f=27kHz)



Figure 8. Scope shot with original settings: Wave is distorted (Yellow: Current, Blue and Green: voltage at driver outputs).



Figure 9. Scope shot with original settings (zoom) showing current ripple.

*Zoom*: The motor loses about 135mA in each slow decay period. Part of this loss results from breakbefore-make time, which act like a fast decay. Over all current ripple is 300mA. This is much more,
than the hysteresis chopper can do at maximum setting. Therefore the negative on (fast decay) cycle
is at its minimum. The minimum duration is limited by TBL, as the chopper cycle cannot terminate
before end of the blank time.

**Improving Settings**

From the measurement we can see, that the chopper frequency should be increased, and TBL should
be reduced, if possible:

1. TOFF=2 -> reduces peak current ripple from 300mA to 240mA
2. TBL=1 -> reduces peak current ripple from 240mA to 200mA

Now the current wave looks better. Its shape is thinner, because of reduction of the current ripple
from 300mA (Figure 2.8) to 200mA (Figure 2.10). Chopper frequency went up from 26kHz to 60kHz



Figure 10. Reduced TBL=1 and TOFF=2.

Still, the wave shows distortion, and the motor is noisier than it should be. To eliminate distortion,
the chopper hysteresis has to cover the 200mA current ripple:

Increasing HSTRT=12 and HEND=8 improves the wave to a sine wave (attention – with this high
setting of HSTRT and HEND IRUN must be 30 or lower (Figure 2.11).



Figure 11. Increased Hysteresis HSTRT=8, HEND=12.

### Optimizing Chopper Settings for Classic Chopper Operation

The classic chopper mode can be used instead of spread cycle chopper, in case you want to try
operation in this mode. For most motors it will be inferior to spreadCycle™. Similar to the
descriptions on spreadCycle™, TBL, TOFF, TFD and wave offset (OFFSET) can be determined for chm=1
based on motor resonance and microstep quality. The following scope shots are meant to give some
hints on good and bad settings. The scope shots show: CH1 & CH2: Sense resistor voltages, CH3:
Current probe on coil A.



Figure 12. Offset too low (plateau in current zero crossing) – increase OFFSET.



Figure 13. Offset too high (step in current zero crossing) – decrease OFFSET.



Figure 14. Fast decay portion insufficient at increased velocity (increase TFD or reduce TOFF.



#### High Speed Fullstepping with Slow Decay



Classic chopper especially is good for high speed fullstepping operation. This configuration also is
used for dcStep™ operation. The TMC5130 and TMC2130 support a special high speed mode, switching
the driver to fullstepping and slow-decay only mode. Figure 3.4 shows the waveform at both sense
resistors at high speed. The wave shows, that the target current still is reached. When further
increasing velocity, the target current cannot be reached any more. Torque sinks, and the wave looks
similar to operation with spreadCycle at high speed (Figure 2.7).



Figure 15. High Speed Fullstepping with Slow Decay only.

### Qualitative Approach to Optimize Chopper Settings for a Three Phase Stepper

A three phase motor differs from the two phase motor in one main aspect: Its coils have an internal
interconnection. Thus, the chopper scheme differs. However, having taken into operation a two phase
motor with spreadCycle™ chopper will allow you to get a three phase motor parameterized quickly.
We will optimize motor settings for the required velocities sequentially; however one or more
iterations might be taken in case a single set of settings is desired.



#### Preparations



Take you motor into operation at nominal conditions. Attach an oscilloscope with current probe to
one of the motor coils, if possible. You might measure the coil voltage to assess the chopper
frequency. In case you have access to the sense resistor, measure the voltage over the single sense
resistor, too. This way, you do not even need a current probe.

1. Select proper hardware settings like blank time TBL and motor current scale.

    *Hint*: A too low TBL will lead to distorted sine waves, but the value should not be unnecessarily
   high. 1.5-2.5µs (TBL= 2 or 3 at 16MHz clock frequency) is a good starting point.
2. Choose an off-time setting TOFF of two: TOFF = 2. Set the flag nosd in order to skip off time. Most
   motors will not need an additional off time in each chopper cycle.
3. As we will work with Step/Dir input, choose chopper direction UVW (cdir=1). This will always chop
   the coils in the same order as the motor runs, which is optimum. Let the chopper synchronization
   switched off (csync=0), as it is not needed unless you want to turn the motor quickly.
4. Choose a hysteresis end value of 5 to 12, e.g., 10, and write it to HYST.



#### Low and Medium Velocity Optimization



In the low and medium velocity range, the motor is to work with equidistant steps, lowest possible
vibration, and low chopper noise. Use highest possible microstep resolution for your tests.

Operate your motor at a low to medium velocity. Try feeling motor vibrations at different velocities
with your fingertips. Try seeing and feeling microstep equidistance at very low velocities.

*Hint*: A long pointer attached to the motor axis will help checking microstep performance at lowest
velocity.

You might want to check the current waveform using an oscilloscope. The oscilloscope should show
a pure sine wave as shown in Figure 4.1. In case, the sine wave is distorted like shown in Figure 4.2
or Figure 4.3, the motor velocity is too fast, or the supply voltage is not high enough. A completely
distorted waveform at a low velocity is a hint for a too low blank time setting. Increase TBL by one.

For a three phase stepper motor operated with spreadCycle chopper, tuning of the hysteresis setting
is most important – it trades chopper noise against accuracy. At the optimum setting, the motor runs
smoothly. When increasing the hysteresis, chopper noise increases, but the motor does not benefit.

Tuning HYST setting:

1. Increase HYST coming from a low setting like 5. Stop as soon as the motor is not turning
   more smoothly with an additional increment. If checked with an oscilloscope, you will see
   the sine wave becoming more smoothly, but it is very hard to see distortion in the wave.
2. In case chopper noise becomes audible, increase supply voltage if possible, or decrease
   motor current. If there is no good setting, you will need to use a lower inductivity motor.



#### High Velocity Optimization



In the high velocity range (see Figure 4.2 or Figure 4.3), the motor is to work with low resonance.
Best setting is typically with a synchronized chopper. Switching on csync will also not harm at low
velocities, but you will see a little disturbance in current zero crossing when checking with an
oscilloscope.



Figure 16. Three phase motor operating optimally - ch1: sense resistor, ch3: current probe.



Figure 17. Thee phase motor operating slightly above back EMF voltage limit velocity.



Figure 18. Three phase motor operating at high velocity with synchronized chopper (csync=1).

### Chopper Noise Trouble Shooting Guide

Hissing or chirping chopper noise can be annoying. Especially in motor standstill, many applications
are required to be silent. While the latest ADI TRINAMIC drivers support stealthChop for absolutely silent
motor operation, spreadCycle also provides a good performance when compared to traditional
chopper schemes.

In case the optimization process described does not yield the desired result, additional measures can
bring success.

Checklist:

1. **PCB layout.** The PCB layout is critical for optimum motor performance and for low chopper
   noise. As the chopper for both coils of a two phase motor run independently, any coupling
   between them will lead to interdependent modulation. This modulation results in current
   variation, which can cause vibration of the motor as well as audible noise caused by
   magnetostriction within the motor. The most critical point is the tight and symmetrical
   connection between sense resistor ground and driver chip ground, because the sense resistor
   voltage measurement determines the motor current and is related to the common ground.
   Please refer to AN011 - Good Ground Connections.
2. **Choice of driver clock frequency.** As a higher chopper frequency will generally reduce audible
   noise due to both, reduction of current ripple as well as shifting the frequency out of the
   audible range, as a first measure chopper off time and hysteresis can be reduced. An increase
   in driver clock frequency can additionally support this measure, especially when the original
   frequency was low, e.g., 10 MHz or less.
3. **Choice of motor and supply voltage.** A low and audible chopper frequency can result from
   low headroom between nominal motor voltage (Coil resistance multiplied by motor current)
   and supply voltage. Increasing the supply voltage to at least the double nominal motor
   voltage, or choosing a motor with higher current winding will often eliminate chopper noise.
4. **Choice of motor type.** Some motor types are very prone to audible amplification of chopper
   noise, due to certain materials or mounting processes used. Try a different manufacturer.
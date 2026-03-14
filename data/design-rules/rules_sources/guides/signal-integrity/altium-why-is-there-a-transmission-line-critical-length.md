---
source: "Altium -- Why is There a Transmission Line Critical Length?"
url: "https://resources.altium.com/p/why-there-transmission-line-critical-length"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 13116
---
There is a little secret that most literature on PCB design will not tell you: every conductor in your PCB that carries an oscillating analog signal or a digital signal can act like a transmission line. Many prominent companies, including PCB manufacturers, are responsible for perpetuating the myth that transmission line effects only occur when the transmission line exceeds a certain length. In reality, this is not an all-or-nothing scenario; some transmission line effects will become more prominent in different cases, and some will be completely unnoticeable.

One important point in transmission line design is the need for impedance matching, and this has led to the definition of the transmission line critical length. The definition of the critical length of a transmission line depends on who you ask. For analog signals, the critical length is sometimes cited as one-sixth or one-eighth the signal wavelength. One prominent manufacturer who won’t be named here will tell you that the critical length is exactly equal to the quarter wavelength and that the transmission line impedance doesn’t matter at this length. One prominent designer has stated that the critical length is 1/20th the signal wavelength. There seems to be plenty of disagreement on this point, or at minimum the various recommendations are taken out of context.

For digital signals, this is stated in terms of the rise time; some designers will tell you that the critical length is the value corresponding to a propagation delay that is one-tenth the signal rise time. The aforementioned manufacturer states that the critical length corresponds to one-half the signal rise time. I've seen recommendations that include 1/2, 1/3, 1/4, 1/5, 1/6, 1/8, 1/10, 1/12, and 1/20 of the rise time. Clearly, these cannot all be true simultaneously, and it is typical that no context is provided when these values are quoted.

The lack of actionable advice in this area is rather interesting given that this issue is so important for ensuring signal integrity and for preventing (or ensuring) signals from forming standing waves on traces. Let’s look into this idea that the appropriate critical length is for your transmission lines and see you how you can determine when impedance matching is necessary.

## Analyzing Input Impedance vs. Transmission Line Length

To summarize early, I'll tell you what determines a suitable critical length:

* Critical length depends on the allowed impedance deviation between the line and its target impedance.
* Critical length is longer when the impedance deviation is larger.
* If the line impedance is closer to the target impedance, then the critical length will be longer.
* If you use the 1/4 rise time/wavelength limit, then you are just guessing at the critical length.

This means that, in some cases, the 1/4 rise time/wavelength limit will produce massive impedance mismatches, while in other cases it produces extremely small impedance mismatches.

In general, digital and RF designers should not use a critical length rule. It requires excessive calculation to do correctly, and it requires to you calculate the impedance of your mismatched line. You might as well just use the correct impedance to begin with.

So let me offer this piece of advice:

* ***If you intend to use a critical length limit, you must do so by determining an allowed impedance mismatch, do not guess.***
* ***Getting a correct critical length limit requires calculating the impedance of your mismatched transmission line. You'll save time if you just design the line to the target impedance.***
* ***A "critical length" should only be used as an analysis tool for explaining S-parameter measurements or TDR measurements, it should not be used as a design constraint.***

If you are STILL determined to use a critical length rule, follow the steps below.

### How to Determine a Critical Length

The question of the critical transmission line length required for impedance matching is one of determining the input impedance seen by a signal as it attempts to travel on a transmission line. The input impedance is the steady state impedance seen by a signal (i.e., [after transients decay to zero](https://resources.altium.com/p/pole-zero-analysis-and-transient-analysis-high-speed-design)), which is not necessarily equal to the characteristic impedance in every case. As we will see, this depends on a number of factors. The equation below shows the input impedance for a lossy transmission line:

*Input impedance for a lossy transmission line*

The propagation constant is complex, where the imaginary part is the signal wavenumber, and the real part includes all losses along the transmission line. For a lossless transmission line, the propagation constant is imaginary, which converts the tanh(x) function into a tan(x) function. A lossy and lossless transmission line will have some oscillating component in the input impedance. The input impedance of a lossless transmission line is shown below:

*Input impedance for a lossless transmission line*

The mathematically astute designer can see that the input impedance is equal to the load impedance if the transmission line length is zero, regardless of losses in the system. In the case of a sufficiently short transmission line, the characteristic impedance of the transmission line (and the even/odd mode impedances, depending on how neighboring coupled lines are driven) does not play a role in determining signal behavior; you only need to worry about impedance matching the source and load to prevent reflection and ensure [maximum power transfer](https://resources.altium.com/p/damping-and-reflection-transfer-series-termination-resistor).

What about the case where the line is longer? What is the input impedance and how does it vary with the length of the line? Moreover, what is the cutoff that determines the critical length? The graphs below show the real and imaginary parts of the input impedance for different cases involving a transmission line with 50 Ohm characteristic impedance and a resistive 50 Ohm source.

Note that, if the load is inductive or capacitive, we would need to consider the load impedance at different input frequencies in these calculations. Also remember that the characteristic impedance of a transmission line [depends on its geometry](https://resources.altium.com/p/clearing-trace-impedance-calculators-and-formulas). The resistive load is mismatched by various amounts ranging from -30% to +30%. Here I’ve used a [loss tangent of 0.02 and Dk = 4](https://resources.altium.com/p/relative-permittivity-pcb-substrates-high-k-or-low-k-dielectrics).

*Real part of the input impedance*

*Imaginary part of the input impedance*

Initially, we see the typical oscillating behavior, with the oscillation decaying as the length increases. The rate of decay with length depends on the losses; greater losses lead to faster decay in the variation. If the trend in the above graphs is not obvious, you can see it clearly when you plot the graph for longer lengths.

The graph below shows the magnitude of the input impedance up to 2 wavelengths. Here, we can clearly see that the oscillation in the input impedance decays towards the transmission line’s characteristic impedance.

*Magnitude of the input impedance*

## What is The Transmission Line Critical Length?

When the line is short, signals behave as if they are travelling on a transmission line with impedance that is closer to the load impedance (the left side of the graphs above). As the line is made longer, the transmission line behaves as if its impedance is closer to its characteristic impedance. The “transition” region depends on the level of losses in the system and the level of permissible impedance mismatch between the source, load, and transmission line characteristic impedance.

Think of it like this: suppose you match the source to the transmission line’s characteristic impedance, but the load impedance is mismatched. The source will transfer maximum signal power down the transmission line, at which point some of the signal reflects off the load. Interference between the reflected and injected signal causes the transmission line to behave as if its impedance was equal to the input impedance. If the transmission line is short, the source now sees an input impedance that may not equal the characteristic impedance, instead seeing something closer to the load impedance; if the source is not matched to this input impedance value, then there is reflection back into the source and you will not transfer maximum power through the line. If the transmission line is long, the line remains matched to the source, but there is still reflection off the load; we have the same result.

This should illustrate the primary reasons for impedance matching the source, load, and transmission line characteristic impedance to the same value:

* The input impedance (i.e., the actual impedance signals see after transients decay to zero) is just the characteristic impedance when the line and load are matched, regardless of line length. This is shown in the flat gray line above.
* The reflection coefficient is zero. You don’t need to worry about a stair-step increase in the voltage that is seen at the load (for digital signals). For analog signals, you don’t need to worry about [standing waves forming](https://www.nwengineeringllc.com/article/guide-to-signal-integrity-analysis-in-pcb-design.php) on the transmission line.

## How Much Mismatch is Allowed?

One can see that, when there is some mismatch, the level of permissible mismatch depends on the permissible level variation one can tolerate in the input impedance away from the target impedance ([50 Ohms in the examples I've shown](https://resources.altium.com/p/mysterious-50-ohm-impedance-where-it-came-and-why-we-use-it)). In the graph showing the real part of the input impedance, we see that an input impedance deviation of about 10% occurs when the line length is ~1/10th of the wavelength. If your tolerable deviation in the input impedance is 10%, then your critical length is ~1/10th of the wavelength. In this case, you only need to worry about matching the source to the load and the transmission line’s characteristic impedance can effectively be ignored.

Because the decay rate in the input impedance curve is also sensitive to losses in the system, so is the critical length. To get a feel for this, let’s multiply the losses in the system by a factor of 10. In this case, we see the transition to the characteristic impedance is much quicker.

*Magnitude of the input impedance with 10x greater losses*

## What About Digital Signals?

With digital signals, you can break the signal into its Fourier components and analyze each component individually, but this is an intractable exercise. The problem with the frequency content of a digital signal is that its harmonic components extend out to infinite frequency, leaving you with three options for analyzing digital signals:

* Work with the Telegrapher’s Equations in the frequency domain and calculate the impedance mismatch for each frequency component.
* Work with the Telegrapher’s Equations in the time domain by defining a stepped voltage/current source.
* Use a single limiting frequency in the above analysis.

Addressing the first two points above requires its own article; we’ll save this for a future topic. The third point illustrates the reason that the knee frequency is sometimes used as a proxy for analyzing transmission lines. The knee frequency (sometimes called the 3 dB bandwidth frequency) is equal to 0.35 divided by the signal’s rise time, but this frequency is not suitable for actual analysis involving high data rate channels and it should not be used. It is actually intended for understanding the appearance of [Gibbs pre-shoot in oscilloscope measurements](https://resources.altium.com/p/how-gibbs-phenomenon-produces-measurement-artifacts), so again it is not suitable for usage in high-speed design.

Once you determine the input impedance and the critical length that meets your design requirements at your limiting required frequency, you should be able to see how harmonic content at higher frequencies will be reflected. The results are seen very clearly in [S-parameter measurements](https://resources.altium.com/p/expert-analysis-measured-s-parameters).

The powerful PCB design and analysis tools in [Altium](https://www.altium.com/) can help you analyze all aspects of your transmission line, including impedance matching and determining the transmission line critical length. These tools are built on top of a unified rules-driven design engine that interfaces with a number of simulation tools. You’ll also have access to a complete set of manufacturing planning and documentation features in a single platform.

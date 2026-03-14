---
source: "ADI Tutorial 5527 -- Why Your 4.7uF Becomes 0.33uF"
url: "https://www.analog.com/en/resources/technical-articles/temperature-and-voltage-variation-ceramic-capacitor.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 11896
---

# Temperature and Voltage Variation of Ceramic Capacitors, or Why Your 4.7µF Capacitor Becomes a 0.33µF Capacitor

## Abstract

The reality of modern, small form-factor ceramic capacitors is a good reminder to always read the data sheet. This tutorial explains how ceramic capacitor type designations, such as X7R and Y5V, imply nothing about voltage coefficients. Engineers must check the data to know, really know, how a specific capacitor will perform under voltage.

A similar version of this article appeared on [*EDN*](http://www.edn.com/design/analog/4402049/Temperature-and-voltage-variation-of-ceramic-capacitors--or-why-your-4-7--F-capacitor-becomes-a-0-33--F-capacitor), November 26, 2012.

## Introduction: I Was Surprised

A few years ago, after more than 25 years of working with these things, I learned something new about ceramic capacitors. I was working on an LED light-bulb driver and the time constant of an RC circuit in my project simply did not seem to be right.

I immediately assumed that there was an incorrect component value installed on the board, so I measured the two resistors making up a voltage-divider. They were just fine. I desoldered the capacitor from the board and measured it. It, too, was fine. Just to be sure, I got new resistors and capacitor, then measured and installed them. I fired up the circuit, checked that the basic operation was proper, and went to see if my RC time-constant problem was resolved. It was not.

I was testing the circuit in its natural environment: in its housing, which itself was in an enclosure to mimic a "can" for ceiling lighting. The component temperatures in some instances reached well over +100°C. Even in the short time that it took me to get around to retesting the RC behavior, things could get quite hot. My next conclusion, of course, was that the temperature variation of the capacitor was the issue.

I was skeptical about this conclusion as I was using X7R capacitors which, as I had known for many years, only varied ±15% up to +125°C. To be sure and to confirm my memory, I reviewed the data sheet for the capacitor that I was using. That is when my ceramic capacitor reeducation began.

## Background on Some Basic Ceramic Capacitors Types

For those who don't have this stuff memorized (like virtually everyone), Table 1 shows the letters and numbers used for ceramic capacitor types and what each means. This table describes Class II and Class III ceramics. Without getting too deep into details, Class I capacitors include the common COG (NPO) type. These are not as volumetrically efficient as the ones in our table, but they are far more stable with environmental conditions and they do not exhibit piezo effects. The ones in the table below, however, can have widely varying characteristics; they will expand and contract with applied voltage, sometimes causing audible buzzing or ringing, piezo effects.

Table 1. Types of Ceramic Capacitors

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| Z | +10 | 2 | +45 | A | ±1.0 |
| Y | −30 | 4 | +65 | B | ±1.5 |
| X | −55 | 5 | +85 | C | ±2.2 |
| – | – | 6 | +105 | D | ±3.3 |
| – | – | 7 | +125 | E | ±4.7 |
| – | – | 8 | +150 | F | ±7.5 |
| – | – | 9 | +200 | P | ±10 |
| – | – | – | – | R | ±15 |
| – | – | – | – | S | ±22 |
| – | – | – | – | T | +22, −33 |
| – | – | – | – | U | +22, −56 |
| – | – | – | – | V | +22, −82 |

Of the many capacitor types above, the most common in my experience are X5R, X7R, and Y5V. I never use the Y5Vs because of their extremely large capacitance variation over environmental conditions.

When capacitor companies develop products, they choose materials with characteristics that will enable the capacitors to operate within the specified variation (3rd character) over the specified temperature range (1st and 2nd character). The X7R capacitors that I was using should not vary more than ±15% over a temperature range of −55°C to +125°C. OK, so either I had a bad batch of capacitors or something else was happening in my circuit.

## Not All X7Rs Are Created Equal

Since my RC time-constant problem was far greater than would be explained by the specified temperature variation, I had to dig deeper. Looking at the data for capacitance variation versus applied voltage for my capacitor, I was surprised to see how much the capacitance changed with the conditions that I set. I had chosen a 16V capacitor to operate with a 12V bias. The data sheet indicated that my 4.7µF capacitor would typically provide 1.5µF of capacitance under these conditions! Now *this* explains the problem that my RC circuit was having.

The data sheet then showed that if I just increased the size of my capacitor from 0805 to 1206, the typical capacitance under these conditions would be 3.4µF. This called for more investigation.

I found that the Murata and TDK® websites have nifty tools that allow one to plot the variations of capacitors over different environmental conditions. I investigated 4.7µF capacitors of various sizes and voltage ratings. Figure 1 graphs the data that I extracted from the Murata tool for several different 4.7µF ceramic capacitors. I looked at both X5R and X7R types in package sizes from 0603 to 1812 and with voltage ratings from 6.3VDC to 25VDC.

Figure 1. Capacitance variation vs. DC voltage for select 4.7µF capacitors.

Note, first, that as the package size increases, the capacitance variation with applied DC voltage decreases, and substantially.

A second interesting point is that, within a package size and ceramic type, the voltage rating of the capacitors seems often to have no effect. I would have expected that using a 25V-rated capacitor at 12V would have less variation than a 16V-rated capacitor under the same bias. Looking at the traces for X5Rs in the 1206 package, we see that the 6.3V-rated part does indeed perform better than its siblings with higher voltage ratings. If we had looked over a broader range of capacitors, we would have found this behavior to be common. The sample set of capacitors that I was considering do not exhibit this behavior as much as the general population of ceramic capacitors.

A third observation is that, for the same package, the X7Rs always have better voltage sensitivity than X5Rs. I do not know if this holds true universally, but it did seem so in my investigation.

Using the data from this graph, Table 2 shows how much the X7R capacitances decreased with a 12V bias.

Table 2. X7R Capacitors with a 12V Bias

|  |  |  |
| --- | --- | --- |
| 0805 | 1.53 | 32.6 |
| 1206 | 3.43 | 73.0 |
| 1210 | 4.16 | 88.5 |
| 1812 | 4.18 | 88.9 |
| Nominal | 4.7 | 100 |

We see a steady improvement as we progress to larger capacitor sizes, until we reach the 1210 size. Going beyond that size yields no improvement.

In my case, I had chosen the smallest available package for a 4.7µF X7R because size was a concern for my project. In my ignorance I had assumed that any X7R was as effective as any other X7R—clearly, not the case. To get the proper performance for my application, I had to use a larger size package.

## Choosing the Right Capacitor

I really did not want to go to a 1210 package. Fortunately, I had the freedom to increase the values of the resistors involved by about 5x and, thus, decrease the capacitance to 1.0µF. Figure 2 graphs the voltage behavior of several 16V, 1.0µF X7R caps versus their 4.7µF, 16V, X7R cousins.

Figure 2. Performance of 1.0µF vs. 4.7µF capacitors.

The 0603 1.0µF capacitor behaves about the same as the 0805 4.7µF device. Both the 0805 and 1206 1.0µF capacitors perform slightly better than the 1210 4.7µF size. By using the 0805 1.0µF device, I was thus able to keep the capacitor size unchanged while getting a capacitor that only dropped to about 85% of nominal and not to about 30% of nominal under bias.

But there was more to be learned. I was still confused. I had been under the impression that all X7R caps *should* have similar voltage coefficients since the dielectric used was the same, namely X7R. I contacted a colleague and expert on ceramic capacitors.¹ He explained that there are many materials that qualify as "X7R." In fact, any material that allows a device to meet or exceed the X7R temperature characteristics, ±15% over a temperature range of -55°C to +125°C, can be called X7R. He also explained that there are no voltage coefficient specifications for X7R or any other types.

This is a very important point, so I will repeat it. A vendor can call a capacitor X7R (or X5R or any other type) as long as it meets the temperature coefficient specs, regardless of how bad the voltage coefficient is.

As an applications engineer, this fact simply reinforces the old maxim (pun intended) that any experienced apps engineer knows: "Read the data sheet!"

As the capacitor vendors have made smaller and smaller components, they have had to compromise on the materials used. To get the needed volumetric efficiencies in the smaller sizes, they have had to accept worse voltage coefficients. Of course, the more reputable manufacturers do their best to minimize the adverse affects of this trade-off. Consequently, when using ceramic capacitors in small packages, or indeed any components, it is extremely important to read the data sheet. Regrettably, often the commonly available data sheets are abbreviated and will have very little of this kind of information, so you may have to request more detailed information from the manufacturer.

What about those Y5Vs that I summarily rejected? For kicks, let's examine a common Y5V capacitor. I will not identify the vendor of this part, as it is no worse than any other vendor's Y5V. I chose a 4.7µF capacitor rated at 6.3V in an 0603 package and looked at the specs at 5V and +85°C. At 5V the typical capacitance is 92.9% below nominal, or 0.33µF. That's right. Biasing this 6.3V-rated capacitor with 5 volts will result in a capacitance that is 14 times smaller than nominal. At +85°C with 0V bias the capacitance decreases by 68.14%, from 4.7µF to 1.5µF. Now you might expect this to reduce the capacitance under 5V bias from 0.33µF to 0.11µF. Fortunately, these two effects do not combine in this way. In this particular case the change in capacitance with 5V bias is worse at room temperature than at +85°C.
To be clear, with this part under 0V bias we see the capacitance drop from 4.7µF at room temperature to 1.5µF at +85°C, while under 5V bias the capacitance increases with temperature from 0.33µF at room temperature to 0.39µF at +85°C. This should convince you that you really need to check component specifications carefully.

## Conclusion

As a result of this lesson, I no longer just specify an X7R or X5R capacitor to colleagues or customers. Instead, I specify specific parts from specific vendors whose data I have checked. I also warn customers to check data when considering alternative vendors in production to ensure that they do not run into these problems.

The larger lesson here, as you may have surmised, is "read the data sheet," every time, no exceptions. Ask for detailed data when the data sheet does not contain sufficient information. Remember too that the ceramic capacitor type designations, such as X7R, X5R, and Y5V, imply nothing about voltage coefficients. Engineers must check the data to know, really know, how a specific capacitor will perform under voltage.

Finally, keep in mind that, as we continue to drive madly to smaller and smaller sizes, this is becoming more of an issue every day.
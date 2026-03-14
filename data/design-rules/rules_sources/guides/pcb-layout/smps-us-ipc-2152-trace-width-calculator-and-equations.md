---
source: "SMPS.us -- IPC-2152 Trace Width Calculator and Equations"
url: "https://www.smps.us/pcb-calculator.html"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 7112
---

Until recently, the main source for calculation of the printed circuit board (PCB) trace width for temperature rise were plots derived from the experiments conducted more than half a century ago. They are reproduced in Figure 6-4 of IPC-2221B and can be described by the equation

i=K×∆T0.44×Ac0.725

, where i- current in amps, ∆T- temperature rise in

o

C, Ac- conductor cross-sectional area in square mils, K- constant equals to 0.048 for outer layers and 0.024 for inner layers. There are a number of online calculators that implement the above formula. The new standard IPC-2152, which is based on the latest studies is much more involved.

It provides more than 100 different figures and lets you take into account many additional factors, such as thickness of PCB and conductors, distance to a copper plane, etc. Our

[calculator](#calc)

will do all this for you, so you won't have to wander the IPC curves. For those who would like to know the details and use Mathcad or spreadsheet, I'll also provide here some basic explanations and equations.

We will use IPC-2152 Figure 5-2, which represents a typical application. It contains

**i vs. Ac**

charts for the polyimide boards 0.070" thick with 3 ounce copper in still air. They are given for certain discrete values of temperature rise and they all are linear in logarithmic scales. We know that a straight line on log-log graph represents a polynomial. This means that: Ac(i)=K1×i

K2

, where K1 and K2 are some constants. For a selected ∆T one can derive K1 and K2 by estimating the slope and intercept point of an appropriate plot in Fig.5-2. Jack Olson from Caterpillar has calculated these and other coefficients and provided them in his

[spreadsheet](http://frontdoor.biz/PCBportal/HowTo2152.xls)

and a related article. I would like to thank Jack for allowing me to utilize his numbers. Note that both the multiplier K1 and the exponent K2 vary depending on ∆T. I thought it would be convenient to have a unified formula for cross-sectional area as a function of electric current, so we could quickly find it for any arbitrary ∆T. For this I have interpolated K1(∆T) and K2(∆T) between 2 and 100

o

C by using a curve fit function that employs least-squares power curve regression. The result is as follows:

Acsq.mil=(117.555×∆T**-0.913**+1.15)×i0.84×∆T**-0.108**+1.159

where i- rms current in amperes.
Once you determined Ac, you can find the required trace width for a given copper weight:

**width=Ac/thickness**

, where thickness(mil)=oz/1.3. The above equation provides reasonably accurate approximation of the generic Fig.5-2 charts. For example, for i=10A and ∆T=20

o

C the IPC gives Ac=500, while our formula yields 513.1, which is within 3% accuracy. Calculations based on these data should fit most assemblies and here will be referred to as

**universal**

or generic. If you have a multi-layer PCB with a copper plane near your conductor, the actual ∆T will be substantially lower. However, for the boards less than 70 mils thick without a plane the temperatures may be higher. Therefore IPC referring to Fig.5-2 as conservative may be misleading. Anyway, to reflect the conditions of a specific application, one can introduce a

**correction (modifying) factor**

as the ratio between estimated actual and generic ∆T.

Our widget approximates these factors for various cases based on the data in IPC appendix and shows them just for reference, so you can see how much each of them affected the result. If their product is less than 1, you can still use the "universal" numbers for design margin. However, if you don't have enough board space and want to reduce the size of the PCB tracks, you may choose to use more application-specific modified results. Let me explain how our calculator does it with the following example. Suppose you want ∆T=20

o

C and the net correction is 0.5. It means that if you use the "universal" Ac, your actual temperature rise will be 20×0.5=10

o

C. So, we want to revise Ac to get your desired 20

o

C. Since the Ac varies non-linearly with respect to ∆T, we can't just reduce it proportionally. Instead, our script first calculates "virtual temperature", which is your input ∆T divided by the product of all correction factors. This is like a reverse modification of the chart value. In our example it will be 20/0.5=40

o

C. Then the script plugs this number into our generic formula. In our tool this result is referred to as "

**revised**

".

For comparison, we also provided the numbers based on legacy IPC2221. You can see that the old PCB design standard overstated current carrying capacity of external tracks. Therefore it seems that for small boards without planes the designs that relied on the historical charts might have resulted in

**underrated external traces**

. That document also arbitrarily assumed that internal conductors could carry only half of the current of the outer ones. In reality, as mentioned in the new standard, inner layers may actually run cooler because the dielectric has 10 times better thermal conductivity than air. Therefore, because of the wrongful assumption, the legacy recommendations for

*internal*

tracks happened to be conservative. Note that the new rule suggests the same copper size for all board's layers. By the way, it may seem counterintuitive, but thicker conductors have lower current carrying capacity than thinner ones because of the smaller trace width at a given A

C

.

For those who work with metric units, here is a quick conversion reference for copper trace: 1 mm=0.03937", 1 mil^2=0.000645 mm^2, 1 oz/ft^2 copper is 0.033 mm thick minimum.

**Notes**

.

* All the results here are obtained by interpolation of the IPC plots, so there is always some inaccuracy.
* For simplicity, our calculations don't include the effect of the board material (FR4 is worse than polyimide just by 2%).
* The analysis is valid for the assemblies with traces spaced apart by more than 1" (which often may not be practical). If parallel tracks are spaced closer, their temperatures will increase. In this case, you need to use combined current to determine their combined cross-sectional area. The presence of heat dissipating components may also raise the temperature.
* The tests that formed the basis of the new standard were conducted for electric currents up to 30 ampere and ∆T up to 100 degree C.
* The output data here do not include any derating. It is always recommended to add some **safety margin**.

The information and the widget are provided here with

**no liability**

of any kind whatsoever. They reflect only personal opinion of the author and do not constitute a professional or a legal advice. For final decisions consult the appropriate standards and your boss. Also see our general Disclaimer linked below.

IPC-2152 is ©Copyright 2009 IPC, Bannockburn, Illinois, USA.
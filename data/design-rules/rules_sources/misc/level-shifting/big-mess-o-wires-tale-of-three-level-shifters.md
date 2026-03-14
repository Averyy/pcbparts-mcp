---
source: "Big Mess o' Wires -- Tale of Three Level Shifters"
url: "https://www.bigmessowires.com/2023/08/22/a-tale-of-three-bidirectional-level-shifters/"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 10197
---

Level shifters, voltage translators: whatever you call them, these devices are very handy when interfacing 5V and 3.3V logic for devices that aren’t 5V-tolerant. The [74LVC244](https://www.ti.com/lit/ds/symlink/sn74lvc244a.pdf) has long been my go-to solution for unidirectional 5V to 3.3V level shifting, and for 3.3V to 5V I’ll typically do nothing, since the 5V inputs generally work OK without shifting. But sometimes you need *bidirectional* level shifting with automatic direction sensing, and you may also want to step up those 3.3V signals to a full 5V. Enter three solutions from Texas Instruments: [TXB0104](https://www.ti.com/lit/ds/symlink/txb0104.pdf), [TXS0104](https://www.ti.com/lit/ds/symlink/txs0104e.pdf), and [TXS0108](https://www.ti.com/lit/ds/symlink/txs0108e.pdf). These three chips all provide 4 or 8 channels of bidirectional level shifting with auto direction sensing, and at first glance they all seem very similar. But as I recently discovered, under the hood you’ll find significant differences in how they work and the types of applications they’re best suited for.

**TXB0104**

TI describes this chip as a “4-Bit Bidirectional Voltage-Level Translator With Automatic Direction Sensing.”

> This TXB0104 4-bit noninverting translator uses two separate configurable power-supply rails. The A port is designed to track VCCA. VCCA accepts any supply voltage from 1.2 V to 3.6 V. The B port is designed to track VCCB. VCCB accepts any supply voltage from 1.65 V to 5.5 V. This allows for universal low-voltage bidirectional translation between any of the 1.2-V, 1.5-V, 1.8-V, 2.5-V, 3.3-V, and 5-V voltage nodes. VCCA must not exceed VCCB.

Power VCCA with 3.3V, power VCCB with 5V, and then it just works without any further configuration. Signals on pins A1..4 are propagated to pins B1..4 and vice-versa, while performing level shifting. But how? Scroll down to page 16 of the datasheet to find this block diagram of a single level shifter channel:

It’s complicated, but the most important thing here is that when the pins are treated as outputs, they’re actively driven to a high or low voltage with a pair of inverters. The output drive current is supplied by the TXB0104, through these inverters. When the pins are treated as inputs, the input signal is supplied to another inverter. In many ways it’s like the 74LVC245 except the direction is sensed automatically.

Elsewhere in the datasheet, it mentions a maximum data rate of 100 Mbps when VCCA is at least 2.5 volts.

**TXS0104**

Change a single letter in the part name, and you get TXS0104. What’s different? TI describes it as a “4-Bit Bidirectional Voltage-Level Translator for Open-Drain and Push-Pull Applications”. That sounds awfully similar to the TXB.

> This 4-bit non-inverting translator uses two separate configurable power-supply rails. The A port is designed to track VCCA. VCCA accepts any supply voltage from 1.65 V to 3.6 V. VCCA must be less than or equal to VCCB. The B port is designed to track VCCB. VCCB accepts any supply voltage from 2.3 V to 5.5 V. This allows for low-voltage bidirectional translation between any of the 1.8-V, 2.5-V, 3.3-V, and 5-V voltage nodes.

That’s virtually identical to the text in the TXB datasheet. But the block diagram of a single level shifter channel reveals something that’s completely different!

The chip uses a pass transistor to connect the A and B pins. It’s the same basic concept as the classic single-transistor level shifter, commonly built with a BSS138 MOSFET, whose theory of operation is described in section 2.3.1 of this [Philips application note](http://cdn.sparkfun.com/tutorialimages/BD-LogicLevelConverter/an97055.pdf). The drive current for low signals is supplied by the external device that’s driving the pin, and *not* by the TXS0104. For high signals, there’s a 10K pull-up resistor. The TXS0104 improves on the classic design by adding one-shots that can accelerate rising edge times compared to what’s possible with the pull-up alone.

This type of level shifter is best suited to open-drain applications like I2C communication, but can also be used with push-pull input signals that are actively driven high and low. The datasheet mentions a maximum data rate of 2 Mbps for open-drain and 24 Mbps for push-pull.

I won’t be using I2C, but I will be relying on the ability to put signals in a tri-state (floating) condition, and that’s something TXB0104 can’t really do. Yes the TXB has an enable input that can place the whole chip into a tri-state condition, but it requires a separate enable signal from my 3.3V microcontroller, and it doesn’t allow for individual signals to be tri-stated. But the TXS0104 supports this quite well. If a pin on the A side is tri-stated and left to float, the 10K pull-up will lift it to 3.3V, which turns off the pass transistor. Another 10K pull-up on the B side pin lifts it to 5V. This is a weak pull-up, so other devices on the 5V side can actively drive the signal high or low without problems. The TXB0104 can’t do this since it’s always actively driving the pin.

At least this is my analysis based on the datasheets, but I’m happy to be proven wrong here. Perhaps the TXB might also work if the A side is tri-stated and it auto-configures the data direction from B to A. As far as I can see, though, the TXS0104 looks like the best choice for my needs. 24 Mbps (with inputs driven push-pull) should be plenty fast enough, since my application only requires 1 or 2 Mbps at most.

**TXS0108**

Many people would assume the TXS0108 is simply an 8-bit version of the TXS0104, with twice as many channels but everything else the same. The datasheet seems to support this, calling it a “8-Bit Bi-directional, Level-Shifting, Voltage Translator for Open-Drain and Push-Pull Applications”:

> This device is a 8-bit non-inverting level translator which uses two separate configurable power-supply rails. The A port tracks the VCCA pin supply voltage. The VCCA pin accepts any supply voltage between 1.4 V and 3.6 V. The B port tracks the VCCB pin supply voltage. The VCCB pin accepts any supply voltage between 1.65 V and 5.5 V. Two input supply pins allows for low Voltage bidirectional translation between any of the 1.5 V, 1.8 V, 2.5 V, 3.3 V, and 5 V voltage nodes.

But once again, the block diagram of a single level shifter channel reveals something that’s quite different from either the TXB0104 or TXS0104:

It’s conceptually similar to a TXS0104, but with many additions that are designed to support faster signal rates. Instead of a single one-shot to accelerate rising edges, there are separate one-shots to accelerate both rising and falling edges. The pull-up resistors aren’t fixed at 10K ohms anymore, but dynamically change their values depending on whether the signal is rising or falling. There’s also some extra resistance in series with the pass transistor.

The datasheet mentions a maximum data rate of 110 Mbps for push-pull, which is much faster than 24 Mbps on the TXS0104. Faster is better, right? Maybe not. The TXS0108 datasheet also contains a warning that’s not found in the TXS0104 datasheet:

> PCB signal trace-lengths should be kept short enough such that the round trip delay of any reflection is less than the one-shot duration… The one-shot circuits have been designed to stay on for approximately 30 ns… With very heavy capacitive loads, the one-shot can time-out before the signal is driven fully to the positive rail… Both PCB trace length and connectors add to the capacitance of the TXS0108E output. Therefore, TI recommends that this lumped-load capacitance is considered in order to avoid **one-shot retriggering, bus contention, output signal oscillations, or other adverse system-level affects**.

Sparkfun sells a [TXS0108 level shifter breakout board](https://learn.sparkfun.com/tutorials/level-shifter---8-channel-txs0108e-hookup-guide/all), and their hookup guide mentions struggling with this problem:

> Some users may experience oscillations or “ringing” on communication lines (eg. SPI/I2C) that can inhibit communication between devices. Capacitance or inductance on the signal lines can cause the TXS0108E’s edge rate accelerators to detect false rising/falling edges.
>
> When using the TXS0108E, we recommend keeping your wires between devices as short as possible as during testing we found even a 6″ wire like our standard jumper wires can cause this oscillation problem. Also make sure to disable any pull-up resistors on connected devices. When level shifting between I/O devices, this shifter works just fine over longer wires.
>
> The TXS0108E is designed for short distance, high-speed applications so if you need a level shifter for a communication bus over a longer distance, we recommend one of our other level shifters.

This statement confuses me a bit. At first it says even a 6 inch wire is problematic, then it says it works just fine over longer wires, before concluding that you should choose a different solution if you need communication over a long distance. For disk emulation applications I may need to drive signals on a cable that’s several feet long. My take-away is that the TXS0108 is much more fiddly to use successfully than the TXS0104, and is prone to oscillation problems when circuit conditions aren’t ideal – which will probably be the case for me. Since I don’t need 110 Mbps communication, there’s no compelling reason for me to use the TXS0108 except the minor space and cost savings compared to a pair of TXS0104’s. I can run at slower speeds with a TXS0104 and hope to minimize problems with oscillations.

My conclusion? When selecting parts, read the datasheet, the whole datasheet. All three of these chips have nearly identical titles and descriptions on page 1, and it’s only after digging further down that their significant differences become apparent.
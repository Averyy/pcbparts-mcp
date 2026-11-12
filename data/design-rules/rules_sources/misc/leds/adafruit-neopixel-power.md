Source: https://learn.adafruit.com/adafruit-neopixel-uberguide/powering-neopixels
Retrieved: 2026-11-09

# Powering NeoPixels | Adafruit NeoPixel Überguide | Adafruit Learning System

[![Adafruit Logo](https://learn.adafruit.com/logos/adafruit_logo_small.png?-2623312060818385914)](https://learn.adafruit.com)

toggle menu

Search

[0](https://www.adafruit.com/shopping_cart)

# Adafruit NeoPixel Überguide

Everything you always wanted to know about Adafruit NeoPixels but were afraid to ask

![Image for user pburgess](https://secure.gravatar.com/avatar/7d19195b95e1d03ac4c6437aeaed9d15?s=100)

by
[Phillip Burgess](/u/pburgess)

published August 30, 2013, last edited October 06, 2026  
last major update July 21, 2026

posted in [LEDs](/category/leds)

[Save](/guides/350/favorites) 

[Link Note](/guides/350/user_page_associations/new)
[Download](https://cdn-learn.adafruit.com/downloads/pdf/adafruit-neopixel-uberguide.pdf)

1140

Beginner

Product guide

😍
17

🔥
14

💕
7

💖
8

💡
7

🤯
3

🤗
5

👌
6

🙌
4

👍
7

😀
5

😎
8

😲
7

😻
6

✨
5

🥇
4

🌞
9

🌠
7

⚡️
5

🤖
5

👻
7

🍀
5

🍁
11

## Powering NeoPixels

Text emphasized with a red exclamation: 
When connecting NeoPixels to any live power source or microcontroller, ALWAYS CONNECT GROUND (–) BEFORE ANYTHING ELSE. Conversely, disconnect ground last when separating.

Text emphasized with a red exclamation: 
Adding a 300 to 500 Ohm resistor between your microcontroller's data pin and the data input on the first NeoPixel can help prevent voltage spikes that might otherwise damage your first pixel. Please add one between your micro and NeoPixels!

Text emphasized with a blue exclamation: 
Neopixels do not light up on their own. Simply applying power will not make them light up. A microcontroller and some programming are required.

NeoPixels are usually described as “5 Volt devices,” but the reality is a little more nuanced than that.  
  
Some (not all) NeoPixel products can work with slightly higher voltages. This depends on the additional support components around the chip, based on available space, cost and the most likely application. **Refer to the specific product description page for guidance on acceptable voltage limits for each type.** When in doubt, aim for 5 Volts.  
  
**Lower voltages are always acceptable**, with the caveat that the LEDs may be slightly dimmer. There’s a limit below which the LED will fail to light, or will start to show the wrong color.

![leds_cap.jpg](https://cdn-learn.adafruit.com/assets/assets/000/011/763/medium640/leds_cap.jpg?1382390099)

**Before connecting a NeoPixel strip to ANY source of power, a large capacitor (500–1000** **µ****F at 6.3 Volts or higher) across the + and – terminals****provides a small power reservoir for abrupt changes in brightness that the power source might not otherwise handle — a common source of NeoPixel “glitching.”**

For a polarized electrolytic capacitor as seen here, the negative (–) lead is usually indicated by a stripe and/or may be shorter than the + lead.

This is an item we don’t stock, but they can be found from parts distributors like [Digi-Key](https://www.digikey.com).

![leds_LiPo.jpg](https://cdn-learn.adafruit.com/assets/assets/000/010/710/medium640/leds_LiPo.jpg?1377891978)

For many wearable projects we recommend a [lithium-polymer battery](http://www.adafruit.com/products/328). These deliver 3.7 Volts — perfect for directly feeding low-power microcontrollers such as the Adafruit Flora, yet sufficient for a short length of NeoPixels.

![leds_3xAA.jpg](https://cdn-learn.adafruit.com/assets/assets/000/010/711/medium640/leds_3xAA.jpg?1377892169)

Three alkaline cells (such as AA batteries) can be installed in a [battery holder](http://www.adafruit.com/products/771) to provide 4.5 Volts. Though larger and heaver than the fancy lithium-polymer pack, they’re inexpensive and readily available.

![leds_4xAA.jpg](https://cdn-learn.adafruit.com/assets/assets/000/010/712/medium640/leds_4xAA.jpg?1377892326)

Four nickel-metal hydride (NiMH) rechargeable cells can similarly be used in a [4-cell battery holder](http://www.adafruit.com/products/830) to provide 4.8 Volts.  
  
**Make sure you** **only** **use NiMH cells in this configuration.** Four alkaline cells (the disposable type) will output 6V total — that’s too high for some NeoPixels, and definitely too much for the microcontroller!

![leds_4288-05.jpg](https://cdn-learn.adafruit.com/assets/assets/000/104/318/medium640/leds_4288-05.jpg?1630510748)

USB power banks can sometimes be used a couple of ways…

- Powering a microcontroller board through its USB port, tapping power for the NeoPixels from the board’s 5V or VIN pin.
- Dissecting a USB cable to provide 5V directly to the pixels.

Many USB power banks **shut off automatically** when current draw is low (e.g. few or no pixels lit), so this requires experimentation and isn’t ideal for all situations.

![leds_buck-converter.jpg](https://cdn-learn.adafruit.com/assets/assets/000/104/319/medium640/leds_buck-converter.jpg?1630511494)

A [*buck converter*](https://www.adafruit.com/product/1385) can efficiently step a higher DC voltage down to 5V for NeoPixels and microcontrollers … for example if you have a 12V power source, like a car battery.

Different converters have a specific input voltage range and output maximum current, so check specifications carefully.

**Battery-operated LED project planning is discussed in greater detail in** [**Battery Power for LED Pixels and Strips**](http://learn.adafruit.com/battery-power-for-led-pixels-and-strips/overview)**.**

![leds_wallwart.jpg](https://cdn-learn.adafruit.com/assets/assets/000/010/713/medium640/leds_wallwart.jpg?1377892545)

For most non-portable “desktop” projects, a [5V DC switching power supply](http://www.adafruit.com/products/276 "Link: http://www.adafruit.com/products/276") is ideal. This small 2 Amp supply is good for a a meter or so of NeoPixel strip. We’ll explain larger projects in a moment.

![leds_benchsupply.jpg](https://cdn-learn.adafruit.com/assets/assets/000/010/717/medium640/leds_benchsupply.jpg?1377914862)

**Be extremely cautious with bench power supplies.** Some — even reputable, well-regarded brands — can produce a large voltage spike when initially switched on, instantly destroying your NeoPixels!  
  
If you use a bench supply, do not connect NeoPixels directly. Turn on the power supply first, let the voltage stabilize, *then* connect the pixels (GND first).

# Estimating Power Requirements

Each individual NeoPixel draws up to 60 milliamps at maximum brightness white (red + green + blue). In actual use though, it’s rare for all pixels to be turned on that way. When mixing colors and displaying animations, the current draw will be much less. It’s impossible to estimate a single number for all circumstances, but we’ve been using 1/3 this (20 mA per pixel) as a gross rule of thumb with no ill effects. But if you know for a fact that you need every pixel on at maximum brightness, use the full 60 mA figure.  
  
To estimate power supply needs, multiply the number of pixels by 20, then divide the result by 1,000 for the “rule of thumb” power supply rating in Amps. Or use 60 (instead of 20) if you want to guarantee an absolute margin of safety for all situations. For example:  
  
60 NeoPixels × 20 mA ÷ 1,000 = 1.2 Amps minimum  
60 NeoPixels × 60 mA ÷ 1,000 = 3.6 Amps minimum  
  
The choice of “overhead” in your power supply is up to you. Maximum safety and reliability are achieved with a more generously-sized power supply, and this is what we recommend. Most power supplies can briefly push a little extra current for short periods. Many contain a thermal fuse and will simply shut down if overworked. So they may technically *work,* but this is the electronics equivalent of abusing a rental car.

**Keep in mind, 60 mA is a *worst case* estimate! We’ve written a whole separate tutorial on getting things under control: [Sipping Power with NeoPixels](../../../../sipping-power-with-neopixels).**

I estimate I need a 3.6 Amp power supply. I have a 10 Amp supply on-hand. Will this cause my NeoPixels to explode?

As long as the output is 5 Volts DC, you’re golden. The LEDs will only draw as much current (Amperes) as they need. So extra Amps are OK — in fact, it can be a *good* thing. The larger power supply will run cooler because it’s not being pushed to its limit.  
  
Excessive *voltage,* however, will definitely kill your LEDs.  
  
**Extra Amps = good.** **Extra Volts = bad.**

What about batteries and “Amp hours”?

Amp-hours are current over time. A 2,600 mAh (milliamp-hour) battery can be thought of as delivering 2.6 Amps continuously for one hour, or 1.3 Amps for 2 hours, and so forth. In reality, it’s not quite linear like that; most batteries have disproportionally shorter run times with a heavy load. Also, most batteries won’t take kindly to being discharged in an hour — **this can even be dangerous!** Select a battery sufficiently large that it will take at least a couple hours to run down. It’s both safer for you and better for the longevity of the battery.

I need to power LOTS of NeoPixels and don’t have a power supply that large. Can I use several smaller ones?

**Maybe.** There are benefits to using a single supply, and large power supplies are discussed below. “Non-optimal” doesn’t necessarily mean “pessimal” though, and we wouldn’t discourage anyone from using what resources they have.  
  
If you go this route, the key is to have all of the ground pins among the strips connected in common, but the +5V from each power supply should be connected only to one length of NeoPixels — those should *not* all be joined. Every power supply is a little different — not *precisely* 5 Volts — and this keeps some from back-feeding into others.

# Giant Power Supplies

Adafruit offers 5V DC power supplies up to [10 Amps](http://www.adafruit.com/products/658). This is usually sufficient for a couple hundred NeoPixels or more. For *really* large installations, you’ll need to look elsewhere.  
  
One possibility is to repurpose an ATX computer power supply. The nice beefy server types often provide up to 30 Amps. Some minor modifications are needed…Google around for “ATX power supply hack.”  Note that the ATX 5V rail can be very unstable if there's no load on the 12V rail!  
  
Even larger (and scarier, and much more expensive) are laboratory power supplies with ratings into the *hundreds* of Amps. Sometimes this is what’s needed for architectural scale projects and large stage productions. And occasionally we get requests for help…  
  
Please note that **projects of this scale are potentially very dangerous**, and the problems of power distribution are fundamentally different than hobby-scale projects. As much as we enjoy helping our customers in the forums, they are for *product technical support* and not full-on *engineering services.* If you’re developing a project of this scope, hire a professional electrician with experience in high-power, low-voltage systems such as photovoltaics or large RVs and boats. This is no charade.

Power for large-scale NeoPixel installations is discussed further in [this NeoPixel curtain guide](https://learn.adafruit.com/1500-neopixel-led-curtain-with-raspberry-pi-fadecandy/power-topology).

# Distributing Power

The longer a wire is, the more resistance it has. The more resistance, the more voltage drops along its length. If voltage drops too far, the color of NeoPixels can be affected.  
  
Consider a full 4 meter reel of NeoPixels. With 5V applied at one end of the strip, for those pixels closest to this end, power traverses only a few inches of copper. But at the far end of the strip, power traverses *8 meters* of copper — 4 meters out on the +5V line, 4 meters back on the ground line. Those furthest pixels will be tinted brown due to the voltage drop (blue and green LEDs require higher voltage than red).

[![](https://cdn-learn.adafruit.com/assets/assets/000/010/715/medium800/leds_brownout.jpg?1377911754)](/assets/10715) 

**Pro Tip:** NeoPixels don’t care what end they receive power from. Though data moves in only one direction, electricity can go *either way.* You can connect power at the **head**, the **tail**, in the **middle**, or ideally distribute it to **several points**. For best color consistency, aim for 1 meter or less distance from any pixel to a power connection. With larger NeoPixel setups, think of power distribution as **branches of a tree** rather than one continuous line.

[![](https://cdn-learn.adafruit.com/assets/assets/000/010/716/medium800/leds_nobrown.jpg?1377911872)](/assets/10716) 

![leds_stitchy.jpg](https://cdn-learn.adafruit.com/assets/assets/000/010/718/medium640/leds_stitchy.jpg?1377917548)

Resistance is just as much a concern on tiny projects too!  
  
For wearable electronics we like conductive thread…it’s flexible and withstands hand washing. Downside is that it doesn’t carry much current. Here several strands of conductive thread have been grouped to provide better capacity for the + and – conductors down a pair of suspenders.  
  
(From the [Pac Man Pixel Suspenders](http://learn.adafruit.com/pac-man-pixel-suspenders "Link: http://learn.adafruit.com/pac-man-pixel-suspenders") guide.)

# Driving 5V NeoPixels from 3.3V Microcontrollers

Increasingly, microcontrollers are running at 3.3 Volts instead of 5 Volts. That’s great news for efficiency, but can present a communication problem with 5V NeoPixels. The 3.3V signal from the microcontroller may not be “loud” enough to register with the higher-voltage device. The manufacturer recommends a minimum signal voltage of 70% of the NeoPixel voltage.  
  
There are two ways this can be addressed:

1. Lower the voltage to the NeoPixels so it’s closer (or equal) to that of the microcontroller. This is why we recommend LiPo batteries for FLORA projects: 3.7V is enough to run a short length of pixels, and the microcontroller is comfortable at that voltage as well.
2. Use a [logic level shifter](https://www.adafruit.com/product/1787) to step up the signal from the microcontroller to the first pixel.

The “Logic Level Shifting” page explains why some projects can work even without thispart.

For more info on using a level shifter with your NeoPixels, [have a look at this guide.](https://learn.adafruit.com/neopixel-levelshifter)

Page last edited March 08, 2024

[Best Practices](/adafruit-neopixel-uberguide/best-practices) [Logic Level Shifting](/adafruit-neopixel-uberguide/logic-level)

Related Guides

[![

Your browser does not support the video tag. This links to the guide Polka Dot Electro-Swing Dress with NeoPixels.
](https://cdn-learn.adafruit.com/guides/cropped_images/000/004/573/medium640thumb/polkadot_gif.gif?1784757941)
![Woman in front of a brick wall wearing a polka dot dress with red lights that animate and twinkle](https://cdn-learn.adafruit.com/guides/cropped_images/000/004/573/medium640thumb/polkadot_gif.gif?1784757941)](/polka-dot-dress-with-neopixels)

[Polka Dot Electro-Swing Dress with NeoPixels](/polka-dot-dress-with-neopixels)

By
[Erin St Blaine](/u/firepixie)

intermediate

8

[![

Your browser does not support the video tag. This links to the guide Burning Fire Wizard Staff.
](https://cdn-learn.adafruit.com/guides/cropped_images/000/002/944/medium640thumb/lava_staff.gif?1584134352)
![A glowing staff with two illuminated sections, emitting green and white light. The surface appears textured and organic.](https://cdn-learn.adafruit.com/guides/cropped_images/000/002/944/medium640thumb/lava_staff.gif?1584134352)](/burning-fire-wizard-staff)

[Burning Fire Wizard Staff](/burning-fire-wizard-staff)

By
[Erin St Blaine](/u/firepixie)

intermediate

115

[![

Your browser does not support the video tag. This links to the guide Neopixel Jewel 10 Minute Necklace.
](https://cdn-learn.adafruit.com/guides/cropped_images/000/001/645/medium640thumb/10_minute_LED_necklace.gif?1515089957)
![A glowing pendant with a decorative metal frame displays colorful, changing LED lights inside. The LEDs create a dynamic, illuminated pattern.](https://cdn-learn.adafruit.com/guides/cropped_images/000/001/645/medium640thumb/10_minute_LED_necklace.gif?1515089957)](/10-minute-neopixel-necklace)

[Neopixel Jewel 10 Minute Necklace](/10-minute-neopixel-necklace)

By
[Erin St Blaine](/u/firepixie)

beginner

80

[![A DIY magic wand with a glowing red LED tip rests on a cardboard surface. The hilt features a leather-wrapped grip.](https://cdn-learn.adafruit.com/guides/cropped_images/000/001/595/medium640/DSC_1596.JPG?1520544931)](/magic-wand)

[Magic Wand](/magic-wand)

By
[Alex Alves](/u/aalves)

beginner

16

[![

Your browser does not support the video tag. This links to the guide Lego Neon NeoPixel Sign with CircuitPython.
](https://cdn-learn.adafruit.com/guides/cropped_images/000/003/077/medium640thumb/neon-loop-crop.gif?1597071797)
![LED neon-style sign spelling "busy" mounted on a LEGO backboard. The sign is illuminated in green, blue, and white colors.](https://cdn-learn.adafruit.com/guides/cropped_images/000/003/077/medium640thumb/neon-loop-crop.gif?1597071797)](/lego-neon-sign)

[Lego Neon NeoPixel Sign with CircuitPython](/lego-neon-sign)

By
[Ruiz Brothers](/u/pixil3d)

beginner

56

[![A Feather microcontroller board with a WiFi module is connected to a Crickit board, powering a servo motor and a NeoPixel ring. The setup includes various headers and connectors for additional components.](https://cdn-learn.adafruit.com/guides/cropped_images/000/002/095/medium640/keyimage.jpg?1531587036)](/crickit-and-adafruitio)

[Using Crickit and Adafruit IO together](/crickit-and-adafruitio)

By
[Dave Astels](/u/dastels)

intermediate

24

[![A person holds a NeoPixel ring connected to a QT Py running CircuitPython. The setup demonstrates real-time chroma keying with retroreflective fabric.](https://cdn-learn.adafruit.com/guides/cropped_images/000/003/276/medium640/realtimeChromaDemoStill_2k.jpg?1615389142)](/retroreflective-green-screen-light-ring-controller)

[Retroreflective Greenscreen Light Ring QT Py...](/retroreflective-green-screen-light-ring-controller)

By
[John Park](/u/johnpark)

beginner

29

[![Adafruit Spakle Motion connected to two NeoPixel sticks and a NeoPixel strand. The strand and sticks are lit up different colors with different amounts of pixels turned on representing levels of different frequencies in the audio captured by the I2S mic.](https://cdn-learn.adafruit.com/guides/cropped_images/000/004/563/medium640/thumbnail.png?1783018696)](/i2s-microphones-with-circuitpython)

[I2S Microphones with CircuitPython](/i2s-microphones-with-circuitpython)

By
[Tim C](/u/Foamyguy)

beginner

2

[![A silhouette of a person adorned with glowing fiber optic strands emitting blue and green light, creating a dynamic visual effect.](https://cdn-learn.adafruit.com/guides/cropped_images/000/001/785/medium640/fiber_whips.jpg?1505508401)](/fiber-optic-whip)

[Fiber Optic Whip](/fiber-optic-whip)

By
[Erin St Blaine](/u/firepixie)

intermediate

41

[![

Your browser does not support the video tag. This links to the guide Knobby Sequencer.
](https://cdn-learn.adafruit.com/guides/cropped_images/000/004/289/medium640thumb/knob_seq_deom_piano.gif?1752643129)
![A 16-knob step sequencer with a screen displaying a waveform is connected to a control panel with colorful knobs and LED indicators.](https://cdn-learn.adafruit.com/guides/cropped_images/000/004/289/medium640thumb/knob_seq_deom_piano.gif?1752643129)](/knobby-sequencer)

[Knobby Sequencer](/knobby-sequencer)

By
[John Park](/u/johnpark)

intermediate

17

[![A GoPro camera is a yellow case is mounted with a 3D-printed ring light attachment, connected via a pink USB cable. The setup is on a black swivel mount.](https://cdn-learn.adafruit.com/guides/cropped_images/000/001/917/medium640/P1060413.JPG?1520546633)](/neopixel-gopro-lens-light)

[NeoPixel GoPro Lens Light](/neopixel-gopro-lens-light)

By
[Liz Clark](/u/BlitzCityDIY)

intermediate

15

[![A person holds a glowing, futuristic shield with a central circular light and intricate patterns. The Guardian Shield+ Zelda Breath of the Wild is illuminated against a dark background.](https://cdn-learn.adafruit.com/guides/cropped_images/000/001/724/medium640/hero-shield-sword.jpg?1520545425)](/guardian-shield-zelda-breath-of-the-wild)

[Guardian Shield+ Zelda Breath of the Wild](/guardian-shield-zelda-breath-of-the-wild)

By
[Ruiz Brothers](/u/pixil3d)

intermediate

43

[![

Your browser does not support the video tag. This links to the guide LED NeoPixel Corset with Circuit Playground Express and MakeCode.
](https://cdn-learn.adafruit.com/guides/cropped_images/000/002/429/medium640thumb/led_corset.gif?1552583861)
![Two people wearing illuminated corsets with colorful LED strips. The lights create a vibrant, glowing effect in a dim setting.](https://cdn-learn.adafruit.com/guides/cropped_images/000/002/429/medium640thumb/led_corset.gif?1552583861)](/led-corset-with-circuit-playground-and-makecode)

[LED NeoPixel Corset with Circuit Playground Express...](/led-corset-with-circuit-playground-and-makecode)

By
[Erin St Blaine](/u/firepixie)

intermediate

54

[![

Your browser does not support the video tag. This links to the guide Color Spinner Camera Ring Light .
](https://cdn-learn.adafruit.com/guides/cropped_images/000/002/506/medium640thumb/IMG_3721_480.2019-04-22_22_12_56.gif?1556054988)
![A solver and black antique Yashica camera with a solver lens has a ring of changing color NeoPixels around the lens end. Attached to the camera accessory connector is an round black Adafruit Circuit Playground Express. A color wheel next to the Express light sensor is being turned by hand to change the LED ring light color.](https://cdn-learn.adafruit.com/guides/cropped_images/000/002/506/medium640thumb/IMG_3721_480.2019-04-22_22_12_56.gif?1556054988)](/camera-ring-light-with-cpx)

[Color Spinner Camera Ring Light](/camera-ring-light-with-cpx) 

By
[Dano Wall](/u/danowall)

beginner

20

[![

Your browser does not support the video tag. This links to the guide Clockwork Goggles.
](https://cdn-learn.adafruit.com/guides/cropped_images/000/001/798/medium640thumb/goggleCogSolo02_small.gif?1507050416)
![Goggles with two circular LED rings emit a warm orange glow in a dark setting. The LEDs are evenly spaced around each lens.](https://cdn-learn.adafruit.com/guides/cropped_images/000/001/798/medium640thumb/goggleCogSolo02_small.gif?1507050416)](/gemma-m0-clockwork-goggles)

[Clockwork Goggles](/gemma-m0-clockwork-goggles)

By
[John Park](/u/johnpark)

beginner

52

# Search

##### Categories

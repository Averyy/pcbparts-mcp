---
source: "TI SSZT534 -- How to Implement Ship Mode in Li-ion Battery Design"
url: "https://www.ti.com/lit/ta/sszt534/sszt534.pdf"
format: "PDF 5pp"
method: "ti-html"
extracted: 2026-02-16
chars: 6093
---

Technical Article

# Pull the Tab: How to Implement Ship Mode in Your Lithium-ion Battery Design

#

Gautham
Ramachandran

Remember when you were a kid and many
of your battery-operated toys had a little plastic pull tab on the battery ([Figure 1](#R_DOCUMENT-HEADER1_FIG1)) that you pulled off to make the product come to life? This
closes the connection from battery to the active circuit on the product and is one
of the earliest implementations of “ship mode.”

In this blog post, I will address what
ship mode is, and how you can use this feature in your product to deliver the best
user experience. While I will be using TI battery charge management integrated
circuits as examples, you can apply these concepts to any low-power system under
development.

Figure 1 Pull Tab on a Battery-Operated
Product

## What Is Ship Mode, and Why Do You Need It?

Ship mode is the state in which the
product is consuming the lowest battery current. Consumers naturally want to use
battery-operated products immediately after purchasing them. This means that the
battery has to maintain some capacity during transportation from the factory and
during its shelf life, which could be a couple of months or even longer.

Lithium-ion batteries have become a
popular choice for designers because they are rechargeable, support high-power
requirements and are very light. However, unlike non-rechargeable batteries, you
can’t put plastic tabs on products using lithium-ion batteries as you want to
restrict access to these batteries for safety concerns. This means that we need to
find alternative solutions for implementing the ship-mode feature for products both
in its on and off states.

You might be wondering why you should care about ship mode when “shipping” happens only once, but that’s not exactly true. Ship mode is the state in which the product is consuming the lowest quiescent current, while waiting for the user to
press a button to turn the product ON. For instance, TI’s BQ25120A is actively monitoring for either an adapter to be plugged in or a button-press input, all while consuming a typical current of 2 nA.

I often recommend that designers implement ship mode when the product is about to be boxed at the factory, is being used and running low on battery, and is being used and the user wants to power off the product.

The ship mode on the BQ25120A family of chargers is realized using a push-button interface, as shown in [Figure 2](#R_WHAT_IS_SHIP_MODE_AND_WHY_DO_YOU_NEED_IT_FIG1). The
push-button input (/MR) is internally pulled up to the VBAT pin. When the device is in ship mode and the user presses the /MR button, the product comes out of ship mode.

You don’t need a capacitor on this pin, as the signal is internally deglitched, but it is common to see them on some schematics. You could optionally use a transient voltage suppression diode for protection if the switch is exposed to the
user. A low-voltage read on the /MR pin translates to a “button pushed” action. Take care when connecting to a microcontroller (MCU) to drive the /MR pin, as voltage on the /MR pin is pulled to the battery voltage itself. An N-channel
metal-oxide semiconductor is often employedto mimic a “press” action from the MCU in a buttonless system.

Figure 2 Internal Pullup on the /MR
Pin

When a product is about to be boxed at the factory, the EN\_SHIPMODE command is sent over I2C and the device waits to go to ship mode until the VIN(charger) is disconnected, as shown in [Figure 3](#R_WHAT_IS_SHIP_MODE_AND_WHY_DO_YOU_NEED_IT_FIG2).

Figure 3 Illustration of Ship Mode at a Factory Production Line

I have seen many challenges on the production line. Things work great in the lab, but on a line that’s building a few hundred products an hour, it can be a different story. The product is on a jig and the assembler doesn’t have a proper way
to pull off the product without the VINadapter bouncing. The charger will get out of ship mode when VINlooks like it was plugged back in. How do you make sure that the product is in ship mode in this case?

The answer is simple: Set the EN\_SHIPMODE command when the VINis present. Once the product is off the jig that supplied the VIN, raise the /CD pin high to complete the execution of the ship-mode command and put the
device to a ship mode before being boxed, as shown in [Figure 4](#R_DOCUMENT-HEADER1_FIG4). In all these sequences /MR is being pushed to show that the device has indeed
gone into ship mode.

Figure 4 Illustration of Ship Mode at a
Factory with a Bouncy Adapter

When the product is running low on battery, often the best way to power down is to keep some reserve capacity and then go into ship mode. When the user presses the button, the device can read the battery level. If the battery level is too
low, the product can display a warning and return back to ship mode, as shown in [Figure 5](#R_DOCUMENT-HEADER1_FIG5). When using the BQ25120A, for example, you can send
the ship-mode command using a single register write as shown in [Figure 6](#R_DOCUMENT-HEADER1_FIG6).

Figure 5 Wake-Up Routine for your
Product

Figure 6 Ship Mode Entry through I2C Command

Also, to create a power on/off button, you could still use the /MR pin by configuring the MRREC register to go to ship mode and programming the duration of the button of how long it needs to be held low; you’ve just created yourself a
power-off button. To wake back up, press the button again, as illustrated in [Figure 7](#R_DOCUMENT-HEADER1_FIG7).

Figure 7 Power On/Off Button

I hope that this post has given you a good idea on how to use some of the features that are present on a charger and ready to implement ship mode in your next product! Visit our E2E forums for any questions you might have.

## Additional Resources

* Download the [BQ25120A data sheet](https://www.ti.com/lit/ds/symlink/bq25120a.pdf).
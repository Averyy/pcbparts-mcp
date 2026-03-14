---
source: "Hackaday -- All About USB-C: Resistors and Emarkers"
url: "https://hackaday.com/2023/01/04/all-about-usb-c-resistors-and-emarkers/"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 11357
---

If you’ve been following along our USB-C saga, you know that the CC wire in the USB-C cables is used for communications and polarity detection. However, what’s not as widely known is that there are two protocols used in USB-C for communications – an analog one and a digital one. Today, let’s look at the analog signalling used in USB-C – in part, learn more about the fabled 5.1 kΩ resistors and how they work. We’ll also learn about emarkers and the mysterious entity that is VCONN!

USB-C power supply expects to sense a certain value pulldown on the CC line before it provides 5 V on VBUS, and any higher voltages have to be negotiated digitally. The PSU, be it your laptop’s port or a charger, can detect the pulldown (known as `Rd`) because it keeps a pullup (known as `Rp`) on the CC line – it then checks if a voltage divider has formed on CC, and whether the resulting voltage is within acceptable range.

If you plug a device that doesn’t make a pulldown accessible through the CC wire in the cable, your device will never get power from a USB-C port, and would only work with a USB-A to USB-C cable. Even the smarter devices that can talk the digital part of USB-C are expected to have pulldowns, it’s just that those pulldowns are internal to the USB-C communication IC used. A USB-C port that wants to receive power needs to have a pulldown.

This part is well-known by now, but we’ve seen lack-of-resistor failures in cheap devices aplenty, and the colloquial advice is “add 5.1 kΩ resistors”. You might be afraid to think it’s so simple, but you’d be surprised.

## Pullups, Pulldowns, And The Resulting Voltage Divider

There are two kinds of power roles for USB-C ports – supply side and consumer side. The analog side of USB-C lets designers add a simple way to negotiate power requirements when using USB-C at 5 V, without using specific or expensive ICs – using pullups for sources and pulldowns for sinks. The combination of a pullup and a pulldown forms a voltage divider, and the voltage itself represents the charger’s current capability.

Now, in analog signaling mode, the source may adjust the pullup based on the power budget available to it, and that’s quite useful. Imagine a laptop or a charger with multiple USB-C ports. As each port gets loaded, there will be less current to give to other ports, which is in large part defined by how the device is built internally. Take the Framework laptop, for instance, which is equipped with four USB-C ports. Each port can provide 15 W at 5 V / 3 A, but if you want to power four sink-only USB-C devices at once, it will only be able to give 1.5 A on third and fourth port – quite a reasonable limitation from an engineering perspective.

This means that higher-consumption devices, like 1.5 A and 3 A max devices, are expected to monitor the voltage on the CC line to determine whether they might exceed the power budget by adjusting their power demands, or otherwise getting shut down if the newly established current limit is exceeded.

The “Default” power refers to the USB stated current limits we’ve been used to – 500mA max for USB2 devices and 900mA max for USB3 devices. While hardly ever enforced, these are the USB standard-stated limitations, indeed.

What does this mean for you as a user? Nothing, if your devices are low-power enough. Your devices are expected to monitor the voltage on the CC line and adjust their appetite accordingly. Some storebought devices won’t do that, but it’s rare. As a hacker? If you build a device that gets power from a USB-C port and you aim to get full 3 A at 5 V, remember that not all USB-C ports will provide you with that. You can, however, check for 3 A availability by measuring the voltage on the CC line. Or don’t, I’m not your mom, and many a hacker device thrives with zero detection.

What voltages can you expect on the CC line? Well, it’s the kind of voltage you can read with a basic ADC that your microcontroller has, or even a comparator.

As you can see, it’s all under 3.3 V so you won’t need a voltage divider if you’re using a full-swing microcontroller ADC. Oh, and if a USB-C socket is what you have, remember to monitor both CC pins separately, of course.

## Do I Really Have To?

Do you really need to monitor the CC voltage? When you’re just hacking away at something, not really, but it can help if you do when you want to go beyond 0.5 A – 1 A. If you exceed the current demands that the source port can provide, it is supposed to simply stop supplying power to your device – a pretty safe outcome. On the other hand, the USB-C philosophy is to have multiple layers of safeguards, and if you’re building a 15 W device with the simple 5.1 kΩ resistor approach, you might as well make it be a device that can detect its power supply being insufficient. Also, it’s quite easy to do!

Otherwise, you can just expect that your device will want to be paired with a charger that always gives 3 A at 5 V, which the overwhelming majority of chargers out there do. Then, you will never experience problems – always able to work with the full 15 W. If you’re connecting your device to a laptop port, however, be it USB-C or USB-A with a USB-C adapter, you can’t fully expect 3 A to always be there – you actually will want to check.

5.1 kΩ isn’t the only pulldown you will encounter. There’s a different kind of pulldown, which we hackers have met before, and it’s the `Ra` – something that comes into play when we talk about e-marked cables.

## VCONN: Feeding Your Emarker Properly

Emarkers are basically memory chips that can talk USB PD protocol. They’re used in cables that are slightly fancier than normal, i.e. cables with high-speed capabilities like USB3 and Thunderbolt, as well as 5 A cables. They tap into the CC line on the cable, and can be queried by either the source or the sink – though they’re typically queried by the source.

If there’s an emarker inside your USB-C cable, it’s going to need some power, and USB-C has a way to provide power to it – it’s called VCONN. As you know, only one CC pin is used for communication. The opposite CC pin, not connected to a CC line, is used to provide the emarker with power; the other CC pin is VCONN.

Within the USB-C plug, you will know which CC pin is attached to the CC wire, and therefore, you know beforehand which pin will act as VCONN. However, you can insert the plug in two different orientations – and this means that the receptacle has to be able to treat either of two CC pins as either CC communications line or a VCONN pin. This keeps cables relatively dumb and cheap, letting the devices themselves handle the complexity.

As a hacker, you won’t need to worry about VCONN in all likelihood. Most of us will work with USB2 or USB3, no higher than 3 A current, and the emarker check won’t be all that necessary. Going further than that, there are ICs that will take care of a multitude of USB-C aspects for you – including, indeed, supplying VCONN.

The voltage requirements on VCONN are quite lax, as opposed to the 5 V you’re expected to provide to VBUS – the allowed range is 3 V to 5.5 V; often, it’s direct LiIon single-cell battery voltage in smartphone implementations, which means you avoid two conversions and can do quite a bit of power saving. After all, VCONN power isn’t just for emarkers it can be used to power small accessories and headphone adapters with up to 1 W power budget. [This fun presentation from a USB-C hacker](https://www.usb.org/document-library/ctvpds-and-making-your-own-usb-cr-thingamajig) talks about prototyping VCONN-powered devices that cover the full range of what the USB-C spec allows a VCONN-powered device to do.

That said, emarkers are the most widespread thing that wants VCONN, and they’re quite simple. Sometimes a cable will contain two emarkers, sometimes it will contain one – it’s a manufacturing choice. In case of a single-emarker cable, one of the cable ends will contain the emarker, and there’s going to be an extra “bring emarker power to other end” VCONN wire run through the cable from the emarker-equipped plug, connected to the VCONN pin on the other cable plug. So, if you ever see a mention of a VCONN wire, that’s what it means – a diode-isolated wire connected to an unused CC pin on one end of the cable, that simply brings power to an emarker on the other end.

Now, this is fun and all, but what about that `Ra` pulldown thing?

## The Ra-spberry Pi 4 Problem

An emarker signals its presence by applying a pulldown resistor (known as `Ra`) to the VCONN pin; it’s 1 kΩ on average, in the range from 800 Ω to 1200 Ω. If the receptacle is able to provide VCONN, it looks for such resistor on the CC pin not currently used for communications, and feeds VCONN into that pin when the resistor is sensed. This resistor, as a result, is available on the second CC pin inside the cable plug – on both plugs of the cable.

What happens if you short both CC pins together in your device’s receptacle, and then insert an high-capability emarked cable? The 5.1 kΩ resistor gets put in parallel with the 1 kΩ resistor, and you get 840 Ω total pulldown, give or take. This pulldown is what the power supply sees on the CC line, and it’s out of the 5.1 kΩ expectation. Specifically, the voltage divider pulls the voltage too low and the power supply doesn’t provide 5 V on VBUS.

This is what Raspberry Pi 4 did in its first revisions, remember? As a result, you wouldn’t have been able to power the Pi 4 with an emarked cable through a Type-C charger – you’d need a non-emarked cable or perhaps a USB-A to USB-C cable with a USB-A power supply. And, of course, the official Raspberry Pi power supply doesn’t have an emarker in its captive cable. It doesn’t have to have an emarker, either – after all, emarkers are intended for questioning unknown cables, and captive cables are known cables by definition.

The question I’ve seen nobody ask, was – why did they do it? If you check the schematic, you’ll see that the `PD_SENSE` net from the joined CC pins goes to an analog input pin on the PMIC. You might be able to guess by now – they implemented the “voltage monitoring” part of the standard, but didn’t implement the “emarker” part properly. How much voltage monitoring do they actually do, [is questionable,](https://forums.raspberrypi.com/viewtopic.php?p=1506352#p1506352) but the capability’s at least there.

Raspberry Pi resolved the issue in upcoming revisions, and if you have an older revision, you can [patch it yourself.](https://bartlomiej-klocek.medium.com/fix-your-raspberry-pi-4b-usb-c-cable-issue-at-home-45b68f9a8514) We [don’t yet know how they patched it,](https://hackaday.com/2021/06/23/the-compromises-of-raspberry-pi-hardware-documentation/) but we will eventually find out. In the meantime, this is all what you ought should know about resistors, emarkers and the elusive VCONN.

Next up: USB-C power in ports, power roles, and higher voltages!
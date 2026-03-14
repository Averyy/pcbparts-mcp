---
source: "Hackaday -- JST Is Not A Connector"
url: "https://hackaday.com/2017/12/27/jst-is-not-a-connector/"
format: "HTML"
method: "readability"
extracted: 2026-02-16
chars: 4581
---

When reading about cool projects and products, it’s common to see wiring plugs labelled “JST connector.” This looks fine until we start getting hands-on and begin hacking things together. Inevitably we find the JST connector from one part fails to fit in the JST connector of another. This is the moment we learn “JST” is not a connector specification. It is short for [Japan Solderless Terminals Manufacturing Company, Ltd](http://www.jst-mfg.com/). A company whose history [goes back to 1957](http://www.jst-mfg.com/profile/index.php?lang=en_US#corporateHistory) and their website (styled in 1999) lists [hundreds of different types](http://www.jst.com/home8.html).

We can simplify to “JST connector” when chit-chatting about projects. But when it comes to actual hardware specification, that’s not good enough. *Which* JST connector?

Battery pack with JST RCY for discharging and JST XH for balance charging.

The reality is: we live in a world full of ambiguous connector specifications. We also sometimes choose to ignore “No User Serviceable Parts Inside” and merrily explore guts of equipment to which we have no specifications at all. As hackers, we need some skill at deciphering mystery connectors. We’ll start here with a quick survey of the most popular types from JST.

A simple two pin wire-to-wire connector is probably the [RCY](http://www.jst-mfg.com/product/detail_e.php?series=521) series. When a connector interface two or more wires to a circuit board instead, it might be one of the following series. A quick way to narrow down candidates is to look at their pitch: the distance between pins. Then identification becomes a matter of comparing the physical features against datasheets.

3D printer control board with JST XH connection to the stepper motors

We start with the [JST XH](http://www.jst-mfg.com/product/detail_e.php?series=277) series. Its pitch of 2.5 mm is effectively identical to the 0.1″ pitch commonly found on prototyping breadboards. After the XH series, the pin pitch gets narrower, the wires get thinner, and the connectors are more fragile through [PH](http://www.jst-mfg.com/product/detail_e.php?series=199) (2.0 mm), [ZH](http://www.jst-mfg.com/product/detail_e.php?series=287) (1.5 mm), [GH](http://www.jst-mfg.com/product/detail_e.php?series=105) (1.25 mm), and [SH](http://www.jst-mfg.com/product/detail_e.php?series=231) (1.0 mm). The SH series are so small that JST specified optional protrusions to give us something to hold.

If a mystery connector doesn’t match the datasheet for the popular JST connector in that pitch, then unfortunately the search becomes more difficult. When faced with this task of digging deeper keep in mind the possibility that it might not be a JST connector at all. Surplus inventory are frequently mislabeled and some connectors look too much alike. The [Molex PicoBlade](http://www.molex.com/product/picoblade.html) is a 1.25 mm pitch connector frequently confused with JST GH in the same pitch.

This mystery “JST connector” has the 1 mm pitch of the JST SH, but the datasheet says it is too large to be one.

As we gain experience with connectors, we’ll make better guesses based on context. The backyard-friendly hobby aircraft ecosystem (airplane, helicopter, and multi-rotor) uses many connectors designed by JST with Molex as a smaller player. The situation is reversed in PC components where Molex designed most of the connectors in that ecosystem.

Such knowledge will come in handy when it comes time to choose a connector. Usually the connectors used in one-off projects are dictated by those already on components built by others, but sometimes the choice is ours to make. It’s better if we understand the context of the project and choose something that fits existing conventions.

And when you’ve made your choice, be specific in your project documentation. There’s no need to make somebody else (possibly your future self) go through the process of guessing which connector type you used.

This is even more important for component vendors. Even though [internet specifications are generally poor](https://hackaday.com/2017/12/14/truly-terrible-dimensioned-drawings/), that’s no excuse to be lazy. Customers need to know the specific connector to interface with your product.

Help prevent future headaches: be specific about your connectors!
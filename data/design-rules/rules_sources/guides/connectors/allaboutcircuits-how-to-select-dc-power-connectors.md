---
source: "AllAboutCircuits -- How to Select DC Power Connectors"
url: "https://www.allaboutcircuits.com/industry-articles/how-to-select-dc-power-connectors-the-basics/"
format: "HTML"
method: "readability"
extracted: 2026-02-16
chars: 7892
---

The selection of a DC power connector is an often-overlooked aspect of an engineer’s final design. Although a relatively simple and straightforward component, DC power connectors still require a basic understanding to ensure the proper connector is selected.

### The Role of DC Power Connectors

Also known as barrel connectors, [DC power connectors](https://www.cuidevices.com/catalog/interconnect/connectors/dc-power-connectors) will have current and voltage ratings specified by the manufacturer to ensure reliability in power delivery applications. The jack and plug of a standard DC power connector will typically feature two conductors. One conductor is exposed and the second conductor is recessed, which helps prevent an accidental short between the two conductors. Because barrel connectors are almost always used to supply power to an end application, there is virtually no risk of damaging other components by plugging a DC power connector into an incorrect port.

### Common DC Power Connector Nomenclature

In the electronics industry, there are three commonly accepted configurations for DC power connectors: jack, plug, and receptacle. A DC power jack is responsible for receiving power and is usually mounted on the PCB or chassis of an electronic device. DC power receptacles are also intended to receive power but are instead found on the end of a power cord. Lastly, DC power plugs supply power from a power supply by connecting to a suitable DC power jack or receptacle. Figure 1 below shows these common configurations.

##### ***Figure 1.**Typical DC power connector configurations.*

### Gender Definitions of DC Power Connectors

While the definitions of jacks, plugs, and receptacles are well-standardized within the industry, the gender definitions for DC power connectors are less so. Many engineers simply follow the gender conventions of the RF connector industry, which defines a barrel connector’s gender based on the center pin configuration. Therefore, DC power connectors with a center pin are usually defined as male connectors and the mating connector as female. This defining line can sometimes get confused when addressing the difference between male and female jacks and plugs, but Figure 2 provides examples to help clarify.

##### ***Figure 2.** Examples of male and female plugs and jacks.*

### Barrel Connector Dimensions

A few key specifications when deciding on an appropriate barrel connector is the inner pin and outer sleeve diameters. Listed in the tables below are the most common diameters for these specifications.

##### ***Figure 3.**Common inner pin and outer sleeve diameters.*

Although a common clearance has yet to be standardized, the inner sleeve diameter, which interfaces with the inner pin, should be slightly larger than that of the mating pin. When it comes to the outer sleeve and mating connector, the clearance is not critical to the proper function of the connector because the mating connection to the outer sleeve is a cantilevered flat spring.

In addition to the inner pin and outer sleeve diameters, the depth of insertion is another DC power connector specification to note. A designer will often find that the jack insertion depth is less than the plug barrel length. This is because it is important to account for the depth of the chassis wall in certain installations.

If that additional depth is not factored in, the barrel length may be too short to properly mate to the jack in the installation. In other instances where the plug barrel is not required to be fully enclosed when inserted into the jack, a longer barrel length than the insertion depth ratio is acceptable.

### DC Power Connector Conductors

A standard DC power jack or plug has two conductors with the center pin typically for power and the outer sleeve typically for ground. However, reversing this conductor configuration is acceptable. A third conductor that forms a switch with the outer sleeve conductor is also available in certain power jack models. This switch can be used to detect or indicate plug insertion or to select between power sources based on when the plug is or is not inserted.

##### ***Figure 4.** Barrel connector conductor configurations.*

### Mounting Options

As with many components, there are several options for mounting a DC power jack to an end application.

Panel mount DC power jacks offer the convenience of mounting anywhere on the product chassis with the trade-off of needing wires to connect to the electronic circuitry. When it comes to PCB mounted DC power jacks, surface mount (SMT) and through-hole in either horizontal or vertical orientations are most common.

A number of DC power jacks with SMT signal connections will also offer through-hole pins or tabs to further secure the jack on the PCB. These tabs may or may not be electrically connected but will be through-hole soldered to the PCB.

Other forms of stabilization pins are non-conducting and interference fit into holes in the PCB. Mid-mount SMT DC power jacks are another option where the jack sits in an opening routed out of the PCB, creating a more low-profile option for space-constrained applications.

### Audio Connectors Used for Power Delivery

Even with the ability to transfer current and voltage, standard [audio connectors](https://www.cuidevices.com/catalog/interconnect/connectors/audio-connectors) are not recommended for powering an electronic application. This is because not all manufacturers specify an audio connector for the necessary voltage and current capabilities. Secondly, if an audio plug were connected to a power supply, its exposed conductors could easily cause an accidental short between two or more of the conductors. Lastly, if an audio plug were supplying power, it would be easy to plug it into other audio jacks not intended for receiving power with the possibility of damaging internal components.

### USB Connectors Used for Power Delivery

Unlike audio connectors, [USB connectors](https://www.cuidevices.com/catalog/interconnect/connectors/usb-connectors) are widely known for their power delivery and data transfer capabilities. However, their maximum power ratings were more limited until the invention of the USB Type-C standard.

The [USB Type-C connector](https://www.cuidevices.com/usb-type-c) with its four power and four ground contacts has a current rating up to 5 A, maximum 20 V voltage rating, and a power rating up to 100 W. This power delivery capability has made it an attractive solution for power-only applications because of USB Type-C's widespread adoption and simplified design integration. However, in applications where charging or power is the sole function, the high-speed data transfer pins can add unnecessary costs. As a result, [power-only USB Type-C connectors](https://www.cuidevices.com/parametric-search/interconnect/connectors/usb-connectors?q=5RvSP) with no data transfer pins have emerged as a more cost-friendly option for power-only designs.

### Selecting DC Power Connectors

Armed with the right information, the selection of a [DC power connector](https://www.cuidevices.com/catalog/interconnect/connectors/dc-power-connectors) should cause little trouble. Take care to note the inner pin and outer sleeve diameters, as well as the insertion depth, to ensure proper mating connections between jacks and plugs. CUI Devices offers a range of DC power jacks, plugs, and receptacles available with numerous mounting styles and other configurations, while their mating guide on each product page further simplifies the process of finding compatible jacks and plugs.
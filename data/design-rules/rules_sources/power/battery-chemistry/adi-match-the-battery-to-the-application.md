---
source: "ADI -- Match the Battery to the Application"
url: "https://www.analog.com/en/resources/technical-articles/match-the-battery-to-the-application-to-avoid-disappointment.html"
format: "HTML"
method: "readability"
extracted: 2026-02-14
chars: 4932
---

# Match the Battery to the Application to Avoid Disappointment

## Abstract

End-customer satisfaction (or dissatisfaction) with portable devices depends largely on battery performance.

The main performance metric for batteries is, of course, battery life. On the surface, this is a simple spec, but in truth it has many dimensions. These include the system's load profile (how much of the time it spends using full load current, a fraction of it, or just microamps); power-supply efficiency; system power management; battery type; and charging methods.

While these performance characteristics are individually important, how they interact can enhance, or diminish, the end-customer’s experience. Generally, if a customer becomes aware of the battery, that is bad! The best products make the battery \"disappear\" with either very infrequent cell replacement (e.g., TV remote controls) or charging, or with unobtrusive charging (e.g., electric toothbrushes). Situations where customers think about batteries as much as the device's function are best avoided.

## Choosing Battery Chemistry

An often neglected consideration in product design is the interaction between the battery and the system. It is important to match the battery's strengths to the needs of the system. The most common battery types for portable electronic devices, alkaline, nickel metal hydride (NiMH), and lithium-ion (Li+), are not interchangeable—most products have one "best" choice.

#### Nonrecharageable: Alkaline

Alkaline cells are nonrechargeable (notwithstanding claims of late-night TV ads), but excel due to their very low self-discharge rate and low cost of implementation. (No charger or AC power jack is needed.) If power requirements are low, alkaline batteries can be a great choice. However, for these batteries to be used properly, quiescent load, or sleep current, must be reduced with rigorous conviction.

A common design mistake is focusing only on the operating efficiency while ignoring "off" or "sleep" current. Even 10s of µA of wasted current can drain cells so that intermittently used products still require frequent cell replacement. Ironically, this design mistake is more common today than it was years ago, since software switches have replaced mechanical switches that used to completely disconnect the battery.

#### Rechargeables: NiMH and Li+

When operating loads are too great for alkaline batteries or when battery replacement would be too frequent, rechargeable batteries are preferred. This is the norm for portable devices like notebooks, PDAs, and cell phones. The challenge is to make the rechargeable battery as unobtrusive as possible. The best start for this is to pick cells that complement (or, at least, do not interfere with) normal use of the product.

There are two commercially popular rechargeable battery choices, NiMH and Li+.

NiMH, which is lower cost than Li+, can make sense when the product's normal usage pattern is not unhealthy for the cells. This consideration is particularly important in low-cost products that are unlikely to include sophisticated charging, since NiMH cells prefer full charge/discharge cycles. This makes most types of NiMH batteries suitable for products that are frequently used to exhaustion, such as power tools. However, recently a new class of NiMH cell with low self-discharge and negligible memory effect has appeared on the market. These are called "hybrid NiMH" and are represented by such brands as the Sanyo® Eneloop, the Uniross® Hybrio®, and others. This type of NiMH cell holds charge much longer than conventional NiMH cells, typically losing only 15% of their charge in one year. Low self-discharge make hybrid NiMH cells well suited as alkaline "replacements" in applications where cells are removed from the device when depleted, but then charged in an external charger. This is common in digital cameras, but still requires attention from the consumer.

Many portable information products do not conveniently fit the above pattern. PDAs and cell phones are charged regularly but drained sporadically. These products perform best with Li+ batteries. Besides the benefit of their power-to-weight ratio, Li+ batteries provide low self-discharge and also have no difficulty with small and unpredictable charge-discharge cycles. Consumers thus devote less effort to "battery management," and instead simply use the product while rarely thinking about batteries. Li+ cells are especially well suited in products that have "captive" batteries that cannot be replaced by the consumer.

An older version of this article appeared in the November 2003 issue of *Portable Design* magazine.
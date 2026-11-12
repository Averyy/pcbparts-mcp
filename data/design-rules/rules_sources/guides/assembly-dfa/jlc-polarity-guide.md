Source: https://jlcpcb.com/help/article/component-polarity-and-orientation-identification-guide
Retrieved: 2026-11-09

# Component Polarity & Orientation Identification Guide

Get Coupon Here

 [Coupons](https://jlcpcb.com/coupon-center)  

Country / Region

Language

undefined

Currency

USD $

The currency you select is for reference only, payments must be made in US dollars.

Save

Ship to

 

Help Center

[Help Center](/help)

[PCBA After-Sale](/help/catalog/3509-PCBA-After-Sale)

Component Polarity & Orientation Identification Guide

Help Center

![](https://jlcpcb.com/ssr/img/help_search.18c576a.svg)

Get Started

- Register
- Know Before Ordering
- Account Setting

Ordering

- PCB Ordering
- PCB Assembly Ordering
- PCB Stencil Ordering

PCB Manufacturing

- PCB Files Preparation
- PCB Capabilities & Instructions
- PCB Technical Guidelines

PCB Assembly

- PCB Assembly FAQs
- PCBA Price Details
- PCBA Parts Sourcing
- PCBA Capabilities & Instructions
- PCBA Technical Guidelines
- PCBA Files Preparation
- PCBA Lead Time
- PCBA After-Sale

FPC Manufacturing

- FPC Materials & Options
- FPC Design Guidelines

SMT Stencil

- Stencil Ordering
- Stencil Technical Guidelines

PCB Layout

- PCB Layout Ordering
- PCB Layout FAQs

JLCDFM Tool

- DFM Tool Help
- DFM FAQs

JLCONE

- JLCONE FAQs
- JLCONE Download and Installation

Shipping & Delivery

- Shipping Policies
- Shipping Instructions

Payment & Invoice

- Payments

Collab & Activities

- JLCPCB API
- Coupons & Promotions

Policies & Certifications

- Policies
- Certifications

Information

- Notice

Flexible Heater

- Flexible Heater Ordering

# Component Polarity & Orientation Identification Guide

Last updated on Sep 09, 2026

![pcb prototype assembly banner 2](https://rs.jlcpcb.com/static/image/blog/pcb-assembly/pcb-prototype-assembly-banner-2.webp)

## Definition of Polarity

Polarity refers to the correct alignment of a component’s positive/negative terminals or Pin 1 with the corresponding polarity markings or Pin 1 indication on the PCB (Printed Circuit Board). If the orientation of a component does not match the PCB markings, it is considered a reverse-polarity defect.

Throughout the PCBA process, polarity-related errors are critical. Incorrect orientation of polarized components may result in systematic failures, batch-level defects, or complete PCBA malfunction. Therefore, it is essential for engineering and production personnel to fully understand SMT component polarity rules. Polarity verification is also a key step in after-sales component failure analysis, to determine whether incorrect orientation caused PCBA failure or functional damage.

If you are using EasyEDA for PCB design or purchasing components through JLCPCB, polarity and orientation can often be quickly verified using the PCB footprint and schematic symbol libraries available on the JLCPCB / EasyEDA platform.

## Common Polarized SMD Components

### I. Capacitors

#### 1. Tantalum Capacitors (Polarized Components)

On the physical component, the positive terminal is clearly marked. Common identification methods include:

- Color stripe
- “+” symbol
- Chamfered (beveled) edge

When designing PCB pads and silkscreen, clear polarity markings must be included.

![Tantalum capacitor](https://rs.jlcpcb.com/static/image/8703975069014806528-2c2fb5dc4ef14194b71b8ed9e9edb134.webp)

![Tantalum capacitor PCB footprint](https://rs.jlcpcb.com/static/image/8703975169887277056-c62c4233a8d54c4c8a69f9b1a15f3d26.png)

#### 2. Aluminum Electrolytic Capacitors (Polarized Components)

**a) SMD Type**

For surface-mount electrolytic capacitors, the black band on the component body typically indicates the negative terminal.

Corresponding PCB footprint and silkscreen markings should reflect this polarity.

![SMD aluminum electrolytic capacitor](https://rs.jlcpcb.com/static/image/8703975447042555904-7f68acdde83a4aa2bc37a6cdea0f51c3.webp)![SMD aluminum electrolytic capacitor PCB footprint](https://rs.jlcpcb.com/static/image/8703975569906708480-584be35a45404653a38d81ef17335072.png)

**b) Through-Hole Type**

For through-hole electrolytic capacitors, the negative terminal is usually marked with a white stripe or a stripe of a different color than the rest of the body.

The PCB footprint and silkscreen should clearly indicate polarity

![Through-hole aluminum electrolytic capacitor](https://rs.jlcpcb.com/static/image/8703975818922807296-23958bda98894292a182301168a8efbf.png)![](https://rs.jlcpcb.com/static/image/8703975917799194624-15e7d0f5fb8348b8ab16b3f769dc8bc6.png)

### II. Light-Emitting Diodes (LEDs) – Polarized Components

#### 1. SMD LEDs

Polarity can be determined based on top-mount or bottom-mount orientation:

- When viewed from the top, the side with a green marking typically indicates the cathode (negative terminal).
- When viewed from the bottom, the arrow direction or raised arrow shape usually points to the cathode (negative terminal).

![LED (Light-Emitting Diode) – top view](https://rs.jlcpcb.com/static/image/8703976198724747264-8048b0f5177f46c7ab5d37f6a7519771.webp)![LED (Light-Emitting Diode) – bottom view](https://rs.jlcpcb.com/static/image/8703976289603137536-c081672833d742c38a1f24d05f04595c.webp)

![LED PCB footprint with polarity marking](https://rs.jlcpcb.com/static/image/8703976455634796544-69fc2334829a433a8dc048017dfe9cc9.png)

#### 2. Through-Hole LEDs

- Before soldering, for two-lead LEDs, the longer lead is the anode (positive terminal).
- After soldering, polarity can usually be identified by distinct markings on the LED body, such as a white stripe.

![Through-hole diode](https://rs.jlcpcb.com/static/image/8704001989449981952-6e183ae36d354ca3bfbf1acacd4903ec.png)![Through-hole diode PCB footprint](https://rs.jlcpcb.com/static/image/8704002086564761600-4ba6c87f8d644f39a74def9cff7016aa.png)

### III. Diodes – Polarized Components

For SMD diodes, the cathode (negative terminal) is typically indicated by:

- A color band
- A notch or groove

These markings should be visible on both the physical component and the PCB footprint.

![SMD diode](https://rs.jlcpcb.com/static/image/8704002328152748032-9b52cb43b6f84da28b8b5cedc28d1af5.webp)![SMD diode PCB footprint](https://rs.jlcpcb.com/static/image/8704002429311242240-e41b02ed305643f38ddfed23bd8ad30c.png)

### IV. Integrated Circuits (ICs)

*(Classification by Package Type)*

IC polarity and orientation should be determined not only by the package marking, but also by cross-referencing the PCB silkscreen and pad layout.

During PCB design, it is essential to include clear silkscreen markings to enable unambiguous orientation verification.

It is generally recommended to place Pin 1 indicators outside the pad area or in an open board area for easy identification.

![PCB footprint with polarity indicator](https://rs.jlcpcb.com/static/image/8704002777970610176-49bd159e039d43329684bdd2e17e11c0.png)

#### 1. SOIC Packages

Pin 1 identification methods include:

- Color stripe
- Symbol marking
- Dimple or notch
- Chamfered edge

On the PCB footprint, Pin 1 is marked with a distinct and clear symbol near the corresponding pad.

![SOIC package – polarity identification](https://rs.jlcpcb.com/static/image/8704003060834471936-8ca3f53add264e7c8beee6796e15a970.webp)     ![SOIC package](https://rs.jlcpcb.com/static/image/8704003171950379008-018f95105f294e179f76845fc1cc3491.webp)

![SOIC PCB footprint](https://rs.jlcpcb.com/static/image/8704003339407966208-7bcfb3f17e58454792b329390d000f1d.png)

#### 2. QFP / SOP Packages

These are square or rectangular packages with leads on all four sides.

Pin 1 is typically identified by:

- A dimple or notch
- One dot that differs from other dots in size or shape

The PCB footprint includes a distinct Pin 1 indicator near the corresponding pad.

![QFP / SOP package – polarity identification](https://rs.jlcpcb.com/static/image/8704003560300716032-345224621baf4f2da326109fd6a5dfd7.png)

![QFP / SOP component and PCB footprint](https://rs.jlcpcb.com/static/image/8704003682606620672-22f02a1c30054760afa8c7eeef25de5c.webp)

#### 3. QFN Packages

- QFN packages with leads on two sides are typically rectangular.
- QFN packages with leads on all four sides are typically square.

Common Pin 1 indicators include:

- A dot that differs from other dots in size or shape
- A chamfered corner
- Symbol markings (e.g., line, “+” symbol, or dot)

The PCB footprint includes a clear and unique Pin 1 marking.

![QFN package – polarity identification](https://rs.jlcpcb.com/static/image/8704004109641699328-42501cc7b37a4a8299f6154b0e68694e.webp)

![QFN component and PCB footprint](https://rs.jlcpcb.com/static/image/8704004202201464832-a5ef6fbeb5fa4bd091d3945499c435f1.webp)

#### 4. BGA Packages

In classic BGA packages, such as CPUs, the underside of the package is populated with an array of solder balls.

Polarity / Pin 1 identification is typically indicated by:

- Dimple or notch
- Dot or circular marking

The PCB footprint includes distinct Pin 1 indicators.

![BGA component and PCB footprint](https://rs.jlcpcb.com/static/image/8704004478383259648-3917f7466ff3462d927ea4cff2e6bbd8.webp)

### V. Power Modules

Many power modules include polarity or orientation indicators.

For through-hole power modules, common indicators include:

- Dimple or notch
- Dot or circular marking

On the PCB footprint, polarity is typically indicated by a circular marking or a square pad.

![Power module and PCB footprint](https://rs.jlcpcb.com/static/image/8704004669799387136-4c6045e9a712405e9606f1fe52b7b938.webp)

### VI. Terminal Blocks / Connectors

Most terminal blocks do not have electrical polarity, but orientation during assembly is still critical, as it affects the alignment of external interfaces.

For these components, the footprint design typically includes directional indicators to ensure correct orientation during soldering and to avoid reversed connector installation.

![Terminal block and PCB footprint](https://rs.jlcpcb.com/static/image/8704004806176911360-6a22a83ef7464a41b14d73375b3495c6.webp)

**Final Notes:**

When verifying component polarity and orientation, always combine PCB silkscreen markings with physical component markings for confirmation. This dual verification approach helps ensure correct polarity and orientation, minimizing the risk of functional failure or irreversible damage.

    

[Get Coupon >](https://jlcpcb.com/coupon-center) [Live Chat >](/im?platform=H5&language=en)

- [Home](https://jlcpcb.com)
- [Cart](https://cart.jlcpcb.com/shopcart/cart)
- [Files](https://jlcpcb.com/user-center/fileManager)
- [Message](https://jlcpcb.com/user-center/messages)
- [Me](https://jlcpcb.com/user-center/accountSetting)

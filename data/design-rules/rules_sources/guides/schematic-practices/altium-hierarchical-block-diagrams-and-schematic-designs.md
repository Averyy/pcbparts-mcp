---
source: "Altium -- Hierarchical Block Diagrams and Schematic Designs"
url: "https://resources.altium.com/p/how-hierarchical-schematic-design-can-help-your-next-pcb-schematic-layout"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 5843
---
Created: November 16, 2017

**Updated: November 2, 2020**

Do you work for a company that has its structure defined on an organizational chart? If so, then you know how useful a hierarchical structure is. By knowing who reports to whom, and which departments have dotted-line cross-functional reports, you know who to go to for specific questions or tasks. On the other hand, if your company doesn’t have that kind of hierarchical structure, it can lead to a lot of confusion.

The organization of a schematic for a PCB design is similar to the organization of a company. Small schematics can be displayed on one or two sheets, which are easy to work with. However, when the schematic is made up of multiple sheets, it can be difficult to find parts or functionality spread across the different sheets. Just as an organizational chart displays your company’s hierarchical structure, hierarchical schematic designs will organize and display your design’s structure.

A hierarchical schematic layout can be an enormous benefit. Let’s take a look at the different ways that using hierarchy in your schematic can help your design and the advantages of schematic diagrams. First, let’s talk about what a hierarchical schematic is and how it works within the CAD system.

*A typical PCB schematic*

## What are Hierarchical Schematic Designs?

Hierarchical schematic designs, or block designs, are where different schematic designs are represented by block symbols on the top sheet of the main design. Larger designs may also have more than just one top sheet with block symbols. In some cases, a block symbol on the top sheet will represent another sheet with additional block symbols on it.

Each block symbol on the top sheet represents its own schematic design. A processor schematic with a power supply on it is a good example. A block symbol for the power supply is on the top sheet of the processor design, representing the schematic for the power supply. By selecting and opening the block symbol on the top sheet, the power supply schematic is opened and displayed.

## How Are Hierarchical Designs Created and Managed?

There are two ways to create a block of schematic hierarchy in a design:

1. **Create a child design from a new block symbol**. Here you create a block symbol on your top sheet, and then start a new design from the block symbol. The new design is saved as a separate schematic, but its block symbol incorporates the new schematic into the main design.
2. **Pull an existing design into your main design**. Here you pull in a design schematic that already exists and associate it with a block symbol that you create on the top sheet of your main design.

Once the separate schematic designs are incorporated, your schematic editor will manage any data conflicts. Take the processor design again as an example. Although the power supply is a separate schematic, the hierarchical block diagram incorporates it into the processor schematic where its sheets become part of the main design. In addition, all of the net names and reference designators are managed so that there aren’t any conflicts.

*Using hierarchy can help you to better organize your schematic layout*

## How a Hierarchical Schematic Layout Can Help You

A hierarchical schematic enables you to see system-level functions of the design from the top sheet, and then descend down into those functional areas through the individual block symbols. This is an invaluable organizational tool for your schematic that will help engineering, test, and field technicians. Additionally, a hierarchical schematic organization provides the following benefits:

* **Hierarchical Structure reduces the workload for identical blocks of circuitry.** You no longer need to create eight identical channels of circuitry for an eight-channel design. With hierarchy, you can now create one schematic of channel circuitry, and place eight-block symbols that point to the same channel design. The schematic editor will rename nets and references to avoid conflicts.
* **Hierarchical Structure encourages team design**. With the ability to easily add block symbols that point to different schematic designs, multiple engineers can work on separate areas of the design. This enables the concurrent development of the power supply design along with the master processor design. When the design team is ready, the power supply block symbol is added to the main design.
* **Hierarchical Structure enables design reuse**. You can store separate designs, such as the power supply, externally so that they are ready to be added to any new design that requires them. Manage these separate designs in the same way that you would manage a library of different schematic parts.

Using hierarchical schematic design techniques in your schematic layout can better organize your design while decreasing your workload and involving more team members. If you haven’t explored working with hierarchy yet, you owe it to yourself to take a look.

[PCB design software](https://resources.altium.com/p/pcb-design-software-download), like [Altium Designer](https://www.altium.com/altium-designer), has advanced [hierarchical schematic](https://www.altium.com/documentation/altium-designer/multi-sheet-hierarchical-designs) design functionality already built into it. This will help you create a better design in less time.

[Would you like to find out more about how Altium software can help you with your next schematic layout?](https://www.altium.com/contact-us)[Talk to someone today.](https://www.altium.com/contact-us)

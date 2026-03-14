# Design Rules Style Guide

How to write the 41 design rule files in this directory. Every file must follow this guide exactly.

## The Expert Filter

> **Every line in every file must pass the expert filter: would a good LLM already produce this without the doc? If yes — cut it. If no — it belongs here.**

This is the single rule that governs everything else. These files exist to fill the gap between "general EE training data" and "experienced engineer reviewing your board." Target **80% expert-only content, 20% common knowledge** (the 20% is structural glue — section headers, cross-refs, brief context for expert rules).

**Cut:** definitions, theory, how things work, textbook formulas, standard specs, vague best practices

**Keep:** specific part numbers, quantified gotchas from app notes, failure modes from real boards, thresholds that aren't in datasheets, decision rules with concrete numbers

Write like a senior EE reviewing a junior's schematic. Not "here's what a capacitor is" but "you picked the wrong capacitor and here's the specific one that works."

**FAILS the expert filter — common knowledge:**
"Common-mode currents flow in the same direction on all conductors, returning through stray capacitance."

**FAILS the expert filter — true but vague, doesn't change a decision:**
"Ceramic caps lose capacitance under DC bias. Derate: use voltage rating >= 2x operating voltage."

**PASSES the expert filter — specific, non-obvious, changes a decision:**
"A 4.7uF X7R 0805 retains only 1.5uF (32%) at 12V bias. Same cap in 1206: 3.4uF (73%). Check Murata SimSurfing at your operating voltage — the 2x derating rule is often not enough for 0402/0603."

No introductions, no motivation, no marketing language, no hedging. State the rule, the value, the consequence.

## Audience

The reader is Claude — an LLM designing schematics and PCBs. It already knows from training data:
- What every component is and how circuits work (don't explain)
- Standard specs and protocols (don't repeat I2C spec, USB spec, etc.)
- Basic formulas (skin depth, voltage dividers, Ohm's law — don't include)
- General best practices ("minimize loop area," "use decoupling caps" — don't state)

It has access to datasheets via JLCPCB search. It does NOT reliably know:
- Which specific parts to use for a given problem (part numbers, families)
- Quantified gotchas from real app notes (the 187nH -> 13nH loop inductance table, the 6mV TPS3808 hysteresis, the 7.6mm not 8mm SOIC-16 creepage)
- Non-obvious failure modes that experienced engineers learn from dead boards
- Interface-specific component selection (which CMC for USB 2.0 vs USB 3.x)
- The interaction effects that textbooks don't cover (DC bias + aging + temperature on ceramics)
- Concrete thresholds for design decisions ("above 3 Gb/s, simulate; below, rules of thumb suffice")

## File Template

Every file uses these four sections in this order. Do not add new sections. Omit Formulas if the topic has no calculations.

```markdown
# Topic Name

> One-line: when to consult this file.

## Quick Reference

- 3-5 most critical rules, each one line with specific values.
- These alone should be enough for a simple design.

## Design Rules

### Subtopic A

- **Rule in bold.** Specific values, conditions, and rationale in 1-2 sentences.
- **Another rule.** More detail.

> WARNING: Critical pitfall. State what breaks and why.

### Subtopic B

[Continue with more subtopics as needed.
Simple topics may have no subtopic headings — just a flat list of rules.]

## Common Mistakes

- **Mistake description.** What goes wrong -> how to fix it.
[Every entry MUST add information not already in Design Rules.
Do NOT restate a design rule as "not doing X is a mistake."
Good: a non-obvious failure mode, a specific measurement, a real-world scenario.
Bad: "Not using decoupling caps -> noise. Fix: use decoupling caps."]

## Formulas

[Omit this section entirely if the topic has no calculations.]

**Rule of thumb:** [Default values for the common case]
**Formula:** [The actual equation]
**Example:** [One worked calculation]

## Sources

### Related Rules
- `path/to/related-file.md` -- brief description of what's relevant there

### References
1. Source Name -- Document Title: URL
2. Source Name -- Document Title: URL
```

### Section purposes:

| Section | Purpose | Position rationale |
|---------|---------|-------------------|
| Quick Reference | Critical rules for the 80% case | Top — strongest LLM attention |
| Design Rules | Full guidance organized by subtopic | Middle — bulk content |
| Common Mistakes | Anti-patterns and failure modes | Bottom — strong LLM attention |
| Formulas | Calculation recipes | Bottom — reference when needed |
| Sources | Related rule cross-links + reference URLs | Last — bibliography, not read unless needed |

## Length

**No line targets. No tiers. No floors or ceilings.**

The only length rules:
- **Don't pad.** Every line must pass the expert filter (see top of this doc). If it doesn't, cut it.
- **Don't restrict.** If a topic has 300 lines of genuine expert content, use 300 lines. Context budget is not the bottleneck — Claude loads 3-5 files at ~2-4K tokens each, which is 5-10% of a 200K context window. Cutting valuable content to save tokens is a bad trade.
- **Split by topic, not by length.** If a file covers two distinct decision domains, split it into two files. If it covers one domain deeply, keep it as one file regardless of length.

## Units

**Metric first.** Use mm for dimensions, with mil in parentheses where PCB convention is strong.
- "Trace width: 0.25mm (10mil)" — for dimensions
- "4.7K", "100nF", "2.2uH" — for component values
- Use ASCII-safe units: `uF` not `µF`, `kohm` not `kΩ`, `>=` not `≥`
- Use `*` for multiplication in formulas, not `x` (which reads as a variable)
- Use `->` for arrows, not `→` (Unicode)
- Temperature: degrees C

## Rules Format

### Granularity: specific default + conditions

Always give a concrete default value. Then state when to deviate.

**Pattern:** "Default: [value]. Use [alternative] when [condition]."

**Bad:** "Choose an appropriate pull-up resistor for the I2C bus."

**Good:** "I2C pull-ups: 4.7K default (100kHz, <200pF bus). Use 2.2K for 400kHz or >200pF bus."

### Rule format

Most rules use the bold-rule format:

```
- **Rule statement in bold.** Explanation with specific values and rationale in 1-2 sentences.
```

For critical contrasts where the wrong choice breaks hardware, use DO/DON'T pairs:

```
- **DO:** Place decoupling cap within 2mm of VDD pin. Via to ground within 1mm of cap pad.
- **DON'T:** Route cap trace through a via before reaching the pin — via inductance defeats HF bypassing.
```

Lead with what to do. Use DON'T only when the mistake is common and non-obvious. Rules should be predominantly positive, with conditionals for design-dependent decisions and negatives reserved for common failure modes.

### Conditional rules

Use "if/when" for decisions that depend on the design.

```
- **If dropout < 1V and current < 300mA:** LDO (simpler, lower noise).
- **If dropout > 1.5V or current > 500mA:** Buck converter (thermal limit).
```

### Warnings

Use blockquote for critical pitfalls that cause hardware failure:

```
> WARNING: Never connect USB VBUS directly to LDO input without protection.
> A USB hot-plug surge (up to 28V per USB-IF spec) will destroy most 6V-max LDOs.
```

Reserve WARNING for things that break hardware. Not for suboptimal choices.

## Formulas

The expert filter applies here too. Only include formulas that have a non-obvious term, a gotcha, or that Claude would get wrong. Cut: voltage divider, Ohm's law, LED resistor, basic RC time constant, skin depth. Keep: bulk cap sizing with the 1.21 constant, via inductance with the ln(4h/d) term, watchdog window sizing accounting for clock drift.

Include both the shortcut and the real formula. One worked example, no more.

```
**Rule of thumb:** 4.7K for standard mode, 2.2K for fast mode.
**Formula:** R_pull-up = t_rise / (0.8473 * C_bus)
  - t_rise: 1000ns (SM), 300ns (FM), 120ns (FM+)
**Example:** 200pF bus, 400kHz -> 300ns / (0.8473 * 200pF) = 1.77K -> use 1.8K
```

## Cross-References

When a rule touches another file's domain, give a one-line summary with pointer. Don't duplicate full guidance.

```
- Thermal vias: 0.3mm drill, 1mm pitch grid in exposed pad
  (full via design rules -> `guides/pcb-layout.md`).
```

**Exception:** If a value is safety-critical (e.g., "100nF decoupling on every VDD pin"), repeat it even if it's in another file. Don't make Claude load two files to avoid blowing up a chip.

**No cross-file duplication.** If a rule already exists in another file, cross-reference it -- don't copy it. Duplicates drift out of sync, waste tokens, and make updates harder. The only exception is the safety-critical case above.

## Conflicting Sources

When sources disagree on a value, use the most conservative safe value as the default and note the range. Flag the conflict for the user.

```
- **I2C pull-up: 4.7K default.** Range across sources: 2.2K-10K. TI recommends
  4.7K; NXP spec allows up to 10K for standard mode. Use 4.7K unless bus
  capacitance demands lower (calculate with formula below).
```

## Tables

Use tables only for multi-variable decisions where prose would be confusing. Keep to 3-4 columns max.

```markdown
| Dropout | Current | Topology | Why |
|---------|---------|----------|-----|
| < 1V    | < 300mA | LDO      | Simpler, lower noise, fewer components |
| > 1.5V  | Any     | Buck     | LDO would dissipate too much heat |
| < 0V (Vout > Vin) | Any | Boost | Need voltage step-up |
```

Avoid tables for simple lists — bullets are more token-efficient.

## What NOT to Include

- **Definitions and theory.** "Ground is NOT a current return path" — Claude knows this. "Conducted emissions: 150kHz-30MHz" — Claude knows this. "CM currents flow in the same direction on all conductors" — Claude knows this. If it's in a textbook or Wikipedia, don't include it.
- **Basic formulas.** Skin depth, voltage dividers, Ohm's law, LED resistor calculations, basic RC time constants — Claude can derive these. Only include formulas that have a non-obvious term or a gotcha (e.g., bulk cap sizing formula with the 1.21 constant that's easy to get wrong).
- **Standard specs and tables.** IEC voltage levels, USB speed tiers, I2C address ranges — Claude has these from training. Only include a table when YOUR specific values differ from the standard or when the table encodes a decision (e.g., topology selection).
- **Vague best practices.** "Minimize loop area," "use shielded inductors," "place caps close to IC" — these are too generic to change a decision. Instead: "Cap within 2mm. Every additional mm adds ~1nH. A 1.5cm trace shifts a 1.9GHz SRF to 314MHz."
- **Datasheet summaries.** Claude can read the datasheet itself.
- **Tutorial explanations.** No "what is SPI?" or "how does a buck converter work?"
- **History or context.** No "USB Type-C was introduced in 2014..."
- **Multiple worked examples.** One is enough. Two is waste.
- **Inline source citations.** Don't clutter rules with "[Source: TI SLVA450]" attributions. Sources go in the `## Sources` section at the bottom.
- **Padding.** If the topic only has 70 lines of expert content after filtering, the file should be 70 lines.

**The filter in practice — examples from actual files:**

| CUT (LLM already knows) | KEEP (expert knowledge) |
|--------------------------|------------------------|
| "Threshold hysteresis: voltage difference between rising and falling thresholds. Prevents oscillation." | "TPS3808 has 6mV hysteresis on sense pin — reflects to just 27mV on 1.8V input through divider. Battery systems need external hysteresis." |
| "Shielding effectiveness = reflection loss + absorption loss." | "2-mil copper foil at 100MHz: 66dB absorption, 88dB reflection. Apertures determine real-world SE, not material." |
| "X7R: -55C to +125C, +/-15% tolerance." | "X7R at 40% rated voltage loses >20% after 1000 hours. DC bias + aging + temp can stack to 50-85% loss." |
| "SPI signals: MOSI, MISO, SCLK, CS." | "MISO series resistor goes at the slave, not the master — slave is the driver. Placing at master leaves full trace unterminated." |
| "Common-mode choke + Y-caps + X-caps = pi-filter." | "No Y-caps on LISN side of CM choke. Y-caps between choke and cable bypass the choke entirely." |

## What TO Include (ranked by value)

1. **Component recommendations** — the single highest-value content type. Claude hallucinates part numbers and picks wrong parts without guidance. Every subsection involving component selection MUST name specific ICs or families with key specs. Pattern: "For [use case]: [part] ([key spec]). For [alternative]: [other part]." Example: "USB 2.0 CM choke: Murata DLW21SN (0805, 90 ohm CM at 100MHz). USB 3.x: DLW21HN — standard 2.0 CMCs destroy SuperSpeed signal integrity above 5GHz."

2. **Quantified gotchas from app notes** — specific numbers that experienced engineers know from measurement, not from theory. "ADI AN-139: L2 ground plane at 0.13mm reduces hot loop inductance 14x (187nH -> 13nH)." "ST AN5686: 1nH ground inductance adds 30V at IEC Level 4." These are the numbers Claude cannot derive and will get wrong.

3. **Non-obvious failure modes** — real scenarios from dead boards. "SSC on USB clock causes enumeration failure." "Oscilloscope probe adds 10pF, pushing I2C bus over 400pF limit — works with probe, fails without." "WB SOIC-16 creepage is 7.6mm not 8mm due to JEDEC metal tabs."

4. **Decision rules with concrete thresholds** — "Above 3 Gb/s: simulate with IBIS. Below 1 Gb/s: rules of thumb suffice. 1-3 Gb/s: simulate only if connectors or vias in path." Not "consider simulation for high-speed designs."

5. **Interaction effects** — things that compound in ways textbooks don't cover. "DC bias derating + aging + temperature on X7R: 4.7uF nominal -> 1.5uF actual at 12V after 1000 hours." "Ferrite bead + downstream cap = LC resonance in the bead's inductive region = 10-15dB gain at the switching frequency."

6. **Layout rules with specific dimensions** — "Cap within 2mm of VDD pin. Via at pad, not via-then-trace. 4+ vias on TVS ground pad." Only include layout rules that affect schematic decisions or that go beyond "follow the reference design."

## Writing Process

1. **Read the extracted sources first.** All source material is in `raw_sources/{topic}/`. Base rules on what sources actually say, not general knowledge.
2. **Distill, don't summarize.** Each source contributes 1-3 key rules. Identify what each source uniquely teaches — skip content that merely confirms what other sources already cover.
3. **Resolve conflicts across sources.** When two app notes give different values, use the most conservative safe value as default and note the range (see "Conflicting Sources" above).
4. **Apply the expert filter (see top of this doc — mandatory before finalizing).** For each bullet point:
   - **Is this a definition, basic theory, or standard spec?** Cut it. ("Conducted emissions: 150kHz-30MHz" — cut. "CM currents flow in the same direction" — cut.)
   - **Would Claude produce this from training data alone?** If yes — cut it unless it carries a specific number, part, or threshold that Claude would get wrong.
   - **Does it name a specific part, measurement, or failure scenario?** If no — it's probably too generic. Make it specific or cut it.
   - **Does removing this line risk Claude making a wrong design decision?** If no — cut it.
   - **Is it restated elsewhere in the same file?** Merge or cut.
   - **Target: 80% of remaining content should be stuff Claude would get wrong without it.**
5. **Component recommendation check.** Every subsection involving component selection must name specific ICs or families. This is the single most actionable content type — it directly prevents Claude from hallucinating part numbers or picking wrong parts.

## Scope: PCB Layout Content

Four rule files cover PCB layout topics (`pcb-layout.md`, `signal-integrity.md`, `emc.md`, `dfm.md`). For all other files, include layout rules only when they directly affect schematic decisions — e.g., "use exposed-pad footprint variant" influences part selection, "place decoupling cap within 2mm of VDD pin" affects schematic annotation. Don't duplicate general layout guidance that belongs in the dedicated layout files.

## Tone

Write like a senior EE reviewing a junior's schematic. Not teaching — correcting. Not explaining theory — pointing at the specific thing that will fail and naming the specific part that works. Terse, technical, opinionated. Every line should make the reader think "I wouldn't have known that."

# PCB Parts MCP — Branding & Style Guide

## Brand Identity

**Name:** PCB Parts MCP
**Short name:** PCB Parts
**Domain:** pcbparts.dev
**MCP server name:** `pcbparts`
**Tagline:** Electronic component search for AI coding tools

We are an independent tool for hardware engineers, makers, and hobbyists. Not affiliated with JLCPCB, Mouser, DigiKey, or SamacSys — we provide a unified search layer on top of publicly available parts data.

## Design Philosophy

The aesthetic is **"you're looking at a PCB."** Every visual decision should reinforce the feeling that the interface IS a circuit board. This isn't a tech startup landing page with a green color scheme — it's a living, navigable PCB layout.

**Principles:**
- **Authentic, not decorative** — Visual elements reference real PCB features (traces, vias, pads, silkscreen, copper pour) rather than generic tech ornamentation
- **Engineering nerdy** — Lean into the technical. Component designators, zone labels, monospaced text, mounting holes. The audience knows what these things are and will appreciate the detail
- **Dark and dense** — The dark solder mask green background creates depth. Copper accents provide warmth. The overall feel is a board under a magnifying glass
- **Functional first** — Every decorative element serves the theme but never compromises readability or usability

## Color Palette

### Primary Colors

| Token | Hex | Usage |
|---|---|---|
| `--pcb-bg` | `#0B1A12` | Page background — dark solder mask green |
| `--pcb-surface` | `#0F2318` | Elevated surfaces, section backgrounds |
| `--pcb-card` | `#0D1F16` | Card backgrounds |
| `--pcb-trace` | `#1B4D35` | Trace-colored borders, dividers, grid lines |
| `--pcb-trace-dim` | `#153D2A` | Subtle grid lines, secondary traces |
| `--pcb-bright` | `#00875A` | Bright green accent (buttons, links, active states) |

### Copper Accents

| Token | Hex | Usage |
|---|---|---|
| `--copper` | `#CD7F32` | Primary copper — borders, interactive elements, prompts |
| `--copper-bright` | `#E8A94F` | Hover states, highlighted text, prices |
| `--copper-dim` | `rgba(205,127,50,0.15)` | Solder pad dots, subtle copper fills |

### Text Colors

| Token | Hex | Usage |
|---|---|---|
| `--silk` | `#E8E4D9` | Primary text — warm silkscreen white |
| `--silk-dim` | `#8A9A8E` | Secondary text — faded silkscreen |
| `--silk-faint` | `rgba(232,228,217,0.06)` | Ghost text, background labels |

### Terminal / Phosphor

| Token | Hex | Usage |
|---|---|---|
| `--phosphor` | `#33FF33` | Terminal text — classic green phosphor |
| `--phosphor-dim` | `#1a8a1a` | Dim terminal text |

### Terminal Result Colors

| Class | Color | Usage |
|---|---|---|
| `.term-lcsc` | Copper `#CD7F32` | LCSC part codes (C3006824) |
| `.term-mpn` | Silkscreen `#e0e0d0` | Manufacturer part numbers |
| `.term-price` | Copper bright `#E8A94F` | Price values |
| `.term-stock` | Dim green `#1a8a1a` | Stock counts |
| `.term-pkg` | Silk dim `#8A9A8E` | Package type (desktop+ only, hidden on mobile via `display: none`) |

## Typography

| Role | Font | Weight | Style |
|---|---|---|---|
| **Headings** | Space Mono | 700 | Monospaced, technical, nerdy. All headings. |
| **Body text** | IBM Plex Sans | 400, 500, 600 | Industrial, clean, readable. Has IBM engineering heritage. |
| **Code blocks** | JetBrains Mono | 400, 500 | Code snippets, config examples, tool names. |
| **Terminal** | VT323 | 400 | Retro CRT phosphor display. Terminal animation only. |
| **Labels/badges** | Space Mono | 400, 700 | Uppercase, letter-spaced. Nav links, tabs, status badges, zone labels. |

**Never use:** Inter, Roboto, Arial, system fonts, or any generic sans-serif for display purposes.

## PCB Visual Elements

These are the building blocks of the visual language. Each maps to a real PCB feature:

### Traces
- Signal traces: `#1B4D35`, 1.8px stroke, 45° chamfer turns (never 90°)
- Power traces: `#1B4D35`, 4-6px stroke, can be horizontal runs
- Differential pairs: Two parallel traces 8px apart
- Bus routing: 4+ parallel traces with 45° fanout at endpoints
- Opacity: 0.3–0.4 for signal, 0.2 for power

### Vias
- Annular ring: Copper stroke (`#CD7F32`), 1.5px, r=5, opacity 0.2
- Drill hole: Background color fill (`#0B1A12`), r=2
- Via stitching: Smaller (r=3.5), lower opacity (0.1), in rows along edges and power rails

### Component Footprints
- **QFP pads**: Small copper rectangles (8×3px or 3×8px) around IC outline
- **0805/0603 pads**: Pairs of copper rectangles (5×8px), scattered across board
- **Through-hole pads**: Copper circles (r=4) with dark drill holes
- **Decoupling caps**: Small pad pairs placed near IC corners
- Pad fill: `#CD7F32` at opacity 0.1

### Silkscreen Outlines
- Component body outlines in `#E8E4D9` at opacity 0.055
- Pin 1 dot: Small circle inside IC corner
- IC notch: Small arc at top of DIP/SOIC packages
- Include QFP, SOIC, SOT-23, QFN, 0805, DIP, connectors, crystals, electrolytic caps

### Component Designators
- Labels like U1, U2, R1, R2, C1, Q1, J1, Y1 near their footprints
- Component values: 10K, 4K7, 100n
- Space Mono, 5-7px, opacity 0.04
- Also used on bento cards via `data-ref` attribute

### Board Features
- **Mounting holes**: Copper annular ring (r=18 outer stroke, r=10 inner stroke) with dark filled center (`#040a06`, opacity 0.9) for drilled-out look
- **Fiducial markers**: Concentric copper circles (r=6 and r=2) at top/bottom center
- **Board edge**: Copper outline (1.5px, opacity 0.08) around full board
- **Test points**: Exposed copper circles (r=7 ring, r=3 fill) at strategic points
- **Zone labels**: "ZONE: GND" in copper, uppercase Space Mono, opacity 0.15

### Setup Section (Pick-and-Place Machine View)
- Background: `#060E09` — darker than page background
- **Alignment grid**: Major grid (80px, copper 0.07 opacity) + minor grid (16px, copper 0.025)
- **Corner SVGs**: Four separate SVGs (`.pnp-corner-tl`, `-tr`, `-bl`, `-br`) pinned to section corners via CSS `position: absolute`. Each is 240px wide (viewBox 220×180). This avoids `preserveAspectRatio` clipping issues on wide viewports.
- **Mounting holes**: Copper annular rings (r=18 outer, r=10 inner) with dark filled center (`#040a06`, r=9) for drilled-out look. Positioned near corner of each SVG.
- **Scan line**: Horizontal copper gradient line that sweeps top-to-bottom via `pnp-scan` animation (8s ease-in-out)
- **Machine status readouts**: JetBrains Mono 10px text, opacity 0.2-0.3 — `FEEDER: 01  NOZZLE: N2`, `STATUS: READY`, coordinates, rotation, board count, cycle time
- Copper top/bottom borders (1px)

## UI Components

### Navigation (Edge Connector)
- Very dark bar (`rgba(5,13,8,0.97)`) with backdrop blur
- Bottom edge styled as **gold fingers**: `repeating-linear-gradient(90deg)` alternating copper (48px) and gaps (4px) at 3px height — mimics PCB edge connector contact pads
- Links: Space Mono, uppercase, 0.75rem, letter-spaced
- Height: 72px
- Hover: Copper text-shadow glow (no border-bottom — interferes with gold fingers)
- Logo: **PCB** (bold 700) + Parts MCP (dim 400, `--silk-dim`) — same in nav and footer

### Status Badge (LED)
- Round LED indicator with copper pad ring (`box-shadow`)
- Pulsing green glow when online
- Space Mono uppercase text

### Install Command
- Black background with phosphor green text
- Text glow (`text-shadow`) for CRT feel
- Prompt `$` in copper
- Server name in copper-bright
- Flags in grey

### Terminal Animation (CRT)
- VT323 font — retro CRT phosphor look
- Scanline overlay (repeating-linear-gradient, 3px period)
- CRT vignette (radial-gradient darkening edges)
- Green phosphor glow on all text
- Result lines use mixed colors: copper for LCSC codes, silkscreen white for MPNs, copper-bright for prices, dim green for stock
- **CRT power-on flicker**: `crt-on` keyframe animation with brightness flash + opacity flicker on load
- **CRT glitch clear**: `.crt-glitch` class adds `hue-rotate`, `skewX`, and position jitter for 120ms. Triggered at the end of each terminal animation cycle to "clear" the screen
- **Typewriter command**: The `$ claude "..."` command types character-by-character with random jitter (18-28ms per char)
- **Search pause**: 900ms pause after "Searching for PCB components..." appears to simulate thinking
- **Letter spacing**: `0.06em` on tablet+ for wider terminal text (mobile keeps default)
- Terminal header title: "serial monitor" — references real embedded dev tooling

### Code Blocks
- Black background, JetBrains Mono
- Header bar: dark (#111) with dots, title, copy button
- String values highlighted in phosphor green (`.str` class)
- Copy button: Space Mono, uppercase, bordered

### Tabs
- Space Mono uppercase, small
- Active tab: `--pcb-trace` background
- Contained in a dark bordered pill

### Bento Cards
- Background: `--pcb-card`
- Border: `--pcb-trace` (1px), sharp radius (4px, like IC packages)
- Component designator label in top-right (`data-ref` attribute)
- Copper solder pads at all four corners (via `::before` box-shadow trick)
- Hover: copper border glow, pads brighten, slight lift — **transition 0.15s** (fast, no perceived delay)
- Tool name codes: copper-bright on dark background with copper border
- **Emoji icons**: Default `saturate(0.3) sepia(0.6) hue-rotate(50deg) brightness(0.8)` filter for muted green/yellow tint. On card hover, animates to full color with 0.4s transition. No transform on hover (prevents shift)

### Schematic Symbol Dividers
- SVG inline dividers placed between sections
- **Resistor zigzag**: Horizontal copper lines flanking a classic resistor zigzag polyline, labeled "R∞"
- **Capacitor plates**: Two parallel vertical lines (capacitor symbol) connecting horizontal copper lines, labeled "100n"
- Stroke: `var(--copper)`, opacity 0.2–0.25
- Labels: Space Mono, 5px, copper, opacity 0.15
- Fade in via Intersection Observer (0.3s delay after section reveal)

### Copper Shine Sweep (CTA Button)
- `::after` pseudo-element with diagonal white gradient
- Slides from left to right on hover (`transform: translateX`)
- Creates a metallic light-sweep effect on the copper CTA button
- `overflow: hidden` on parent clips the shine element

### Animated Signal Flow
- 5 selected SVG trace paths in the background have `.trace-signal` class
- `stroke-dasharray: 12 280` creates a short moving dot along the path
- Animated with `stroke-dashoffset` over 4.5–7s at varying delays
- Copper-bright stroke, opacity 0.5, `will-change: stroke-dashoffset` (no `drop-shadow` filter for performance)

### Glowing Via Pulses
- 7 via circles with `.via-glow` class at key routing intersections
- `via-flash` animation: opacity-only (0.15 → 0.8 → 0.3) at ~90% of cycle. No `drop-shadow` filter for performance. `will-change: opacity`.
- Default state: dim (opacity 0.15), copper-bright fill
- Flash simulates signal arrival at a junction point
- Staggered durations (4.5–7s) and delays so flashes are asynchronous

### Section Reveal Animation
- All `<section>` elements start with `opacity: 0; transform: translateY(20px)`
- Intersection Observer adds `.revealed` class at 15% threshold
- Smooth 0.6s ease-out transition on opacity and transform
- Hero section is exempt (always visible)

### Chromatic Aberration (Headings)
- Section headings have `data-text` attribute duplicating their text content
- `::before` and `::after` pseudo-elements render red (#ff4444) and cyan (#44ffff) shifted copies
- Triggered on `:hover` with `clip-path: inset()` to show only partial offset
- 0.25s `steps(2)` animation with 2px translate offset
- Subtle, brief — simulates CRT color misalignment

### Footer
- Copper top border (2px)
- Dark background with slight transparency
- Space Mono branding, small legal text

## Spacing & Layout

- Container max-width: 1140px
- Hero CTA / terminal section: max-width 800px (aligned)
- Section padding: 80px vertical
- Card gap: 14px
- Border radius: 4px (cards), 6px (code blocks, terminal), 3px (tabs, buttons)
- Keep radii small and sharp — PCB components don't have soft curves

## Iconography

Currently using emoji for bento card icons. If replacing with custom icons, they should reference:
- Schematic symbols (resistor zigzag, capacitor plates, IC rectangle)
- PCB features (trace paths, via circles, pad shapes)
- Tool metaphors (magnifying glass made of traces, clipboard as BOM)

## Tone of Voice

- Technical and direct, not marketing-fluffy
- Assume the reader knows what a QFP-48 is
- Concise — monospaced fonts reward brevity
- Light engineering humor welcome ("MADE WITH ELECTRONS")

## File Naming

- OG image: `pcbparts-og.png`
- Favicon files: unchanged (already green branded)
- Assets: lowercase, hyphenated (`pcb-trace-pattern.svg`)

## Don'ts

- Don't use glass morphism / frosted glass effects — this is a PCB, not iOS
- Don't use gradient orbs or blobby soft shapes — PCBs are geometric
- Don't use rounded corners larger than 6px — components are sharp
- Don't use blue — the entire palette is green + copper + warm white
- Don't use generic sans-serif fonts for any display text
- Don't add decorative elements that don't map to a real PCB feature

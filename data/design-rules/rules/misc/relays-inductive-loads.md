# Relays and Inductive Loads

> Coil-drive margins, release dynamics and load-specific contact protection.

## Quick Reference

- **A diode across a DC relay coil changes release dynamics.** For normally-open high-inrush loads, TE recommends a reverse-biased rectifier in series with a Zener instead of a plain diode [1, Suggested Methods].
- **A relay's must-operate voltage is a pickup threshold, not its normal coil supply.** Omron defines rated voltage as the normal applied coil voltage [2, Rated Voltage/Must-operate Voltage].
- **G5LE standard contacts are rated 10A at 120VAC or 8A at 30VDC resistive;** its inductive rating is 5A at 120VAC (cos phi=0.4) or 4A at 30VDC. Do not substitute the front-page 10A label for the load rating [3, p.1].
- **For AC inductive contact loads, Omron recommends RC or varistor suppression.** A plain diode is for DC loads only [4, Examples of Surge Suppressors].

## Design Rules

### Coil Driver and Voltage Budget

- **Choose low-side transistor voltage rating for the suppressor's location.** With a suppressor across the coil, the off-state driver voltage is the supply plus the coil clamp; with a suppressor across the transistor, its clamp voltage directly limits driver voltage. Include actual clamping voltage and overshoot in the rating margin; MOSFET selection and gate default -> `misc/mosfet-circuits.md` [1, Figure 1, Effects of Coil Suppression on Relay Dynamics and Life].
- **Budget hot-coil pickup and cold-coil driver current separately.** Omron specifies coil resistance at 23 degrees C; copper heating raises resistance and the required DC operating voltage. Include rail tolerance, wiring drop and the transistor's on-state drop instead of checking only nominal coil watts [2, Coil Resistance/Relationship with Temperature].
- **Check release using the actual off-state leakage and residual coil voltage.** A transistor or protection path that leaves the coil energized invalidates a simple GPIO-low release assumption; compare against the selected relay's must-release specification [2, Must-release Voltage].
- **Distinguish catalog threshold bounds from an individual relay's threshold.** Omron's MY4 example specifies must-operate <=80% and must-release >=10% of rated coil voltage at 23 degrees C. Energize above the catalog's maximum pickup threshold and de-energize below its minimum dropout threshold; use the selected part's bounds and temperature conditions [2, Must-operate Voltage/Must-release Voltage, MY4 example].

### Suppression and Release Time

- **For a coil-connected diode plus Zener, oppose the two diodes so normal coil voltage cannot conduct through them.** TE permits common anodes or common cathodes; the rectifier blocks normal supply and the Zener avalanches on turn-off. Select pulse-energy and clamp ratings for the actual coil [1, Types of Transient Suppression Utilized with Relays, item B/Figure 1].
- **Treat a diode's slow release as a contact-life decision.** TE reports normally-open tack welding with plain diode suppression when switching inductive or high-inrush lamp loads; the lower armature opening speed reduces successful DC interruption [1, Effects of Coil Suppression].
- **Use a bidirectional TVS or diode-plus-Zener for a higher coil clamp, within the driver's rating.** A unidirectional TVS directly across a DC coil in the usual reverse-biased orientation conducts forward on flyback; it does not use its avalanche voltage in that direction [1, Types of Transient Suppression Utilized with Relays, items A-B].
- **Re-measure release with the final suppressor fitted.** G5LE lists 5ms maximum release as an initial characteristic; Omron defines release time at 23 degrees C, excluding bounce, and TE establishes that an external clamp changes dynamics. Do not promise that timing for an added diode [3, p.2; 2, Release Time; 1, Effects of Coil Suppression].

### Contacts and Load Suppression

- **Keep AC and DC switching curves separate.** G5LE's maximum switching voltage is not available simultaneously with maximum switching current; check its maximum switching-capacity graph as well as the rated load [3, pp.1,3].
- **Use actual starting current for lamps, motors and transformers.** Omron identifies these loads as contact-welding risks and describes inrush from several to multiples of ten times normal current; its examples do not establish one universal derating factor [2, Contactability under Load Conditions, p.23].
- **RC suppressors need both opening and closing checks.** Omron's starting guides are C=0.5-1uF per ampere of contact current and R=0.5-1 ohm per volt of contact voltage; these are experimental starting points, not a mains-ready BOM. The resistor limits the capacitor's next closing discharge. Omron's general guide is a 200-300V dielectric strength, and a non-polar AC capacitor on AC [4, CR type].
- **An RC network across contacts passes current into the load while open.** Check the resulting load voltage and release; Omron's AC-use condition requires load impedance much smaller than RC impedance [4, CR type]. With the contacts open the network sits across the supply: Littelfuse says to check that leakage current, the resistor's power dissipation and the capacitor's rating against the peak voltage it sees [5, p.2]. A capacitor that fails short there keeps the load powered.
- **Mains-side copper needs creepage and clearance from the coil side.** Contacts and load traces switching mains must keep the required clearance (through air) and creepage (along the board surface) from coil-drive and low-voltage copper on every layer, including under the relay body [2, Clearance; Creeping Distance]. Size them with `protection/isolation.md`.
- **A MOV protects contacts by clamping the load's turn-off voltage.** Size from the actual load and voltage, and verify release and contact life experimentally; Omron warns that varistor suppression lengthens release of relay/solenoid loads [4, Varistor type].

## Common Mistakes

- **Optimizing only normally-open release speed when the load uses normally-closed contacts.** For primary loads on normally-closed contacts with little or no normally-open load, TE notes that a plain diode's slower armature motion can reduce normally-closed closure bounce; qualify the used contact set [1, Suggested Methods].
- **Choosing a clamp by its nominal voltage alone.** TE's automotive example gives 30-36V for a nominal 33V suppressor versus 45-55V for a nominal 33V MOV at about 130mA coil current; actual clamping voltage, not the label, sets transistor stress [1, Effects of Coil Suppression].
- **Fitting a capacitor-only contact suppressor without checking closing current.** Omron warns that the stored-energy discharge or capacitor charging current on closure can weld contacts; use a qualified suppression network rather than removing the RC network's current-limiting resistor [4, Do not use a surge suppressor in the manners shown below].

## Sources

### Related Rules

- `misc/mosfet-circuits.md` -- Low-side drive, GPIO gate compatibility and basic flyback wiring.
- `protection/isolation.md` -- Isolation boundaries and creepage requirements.
- `misc/motor-control.md` -- Repetitive motor switching.

### References

1. TE Connectivity -- The Application of Relay Coil Suppression with DC Relays (web edition, read 2026-11-09): https://www.te.com/en/products/relays-and-contactors/electromechanical-relays/intersection/relay-coil-suppression-dc-relays.html
2. Omron -- Technical Explanation for General-purpose Relays, CSM_GeneralRelay_TG_E_10_2: https://www.ia.omron.com/data_pdf/guide/36/generalrelay_tg_e_10_2.pdf
3. Omron -- G5LE PCB Power Relay (4-page edition, read 2026-11-09): https://omronfs.omron.com/en_US/ecb/products/pdf/en-g5le.pdf
4. Omron -- FAQ02804, Contact Protection (read 2026-11-09): https://www.ia.omron.com/support/faq/answer/36/faq02804/
5. Littelfuse -- Application Note: Inductive Load Arc Suppression (2016, read 2026-11-10): https://www.littelfuse.com/assetdocs/inductive-load-arc-suppression-application-note?assetguid=67c3a678-da06-4c93-9aa2-d20d951138e2

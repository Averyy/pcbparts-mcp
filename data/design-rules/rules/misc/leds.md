# LEDs and Addressable LEDs

> Indicator current budgets and revision-specific WS2812, SK6812, APA102 and SK9822 interfaces.

## Quick Reference

- **A 5V WS2812B Jan-2016 with VIH=0.7*VDD needs 3.5V HIGH.** A nominal 3.3V GPIO does not meet that requirement; use SN74AHCT125 at the LED supply [2, p.4; 7, Recommended Operating Conditions].
- **WS2812C-2020 V1.2 states 5mA per color channel:** nominal RGB full white is 15mA before control consumption, rather than a universal 60mA per pixel [4, pp.1,3].
- **Reset LOW depends on revision:** WS2812B Jan-2016 >50us; WS2812B-V5 >280us; SK6812RGBW Rev.01 specifies 80us [2, p.5; 3, Data Transfer Time; 5, p.5].
- **Fit the WS2812C-2020's 100nF VDD filter at each pixel.** Bulk capacitance at the power entry does not replace this application-circuit component [4, p.4].

## Design Rules

### Indicator Current and GPIO

- **WP710A10ID's 1.9V Vf is typical, not a lower bound.** Its 2.3V maximum is specified at 10mA, TA=25 degrees C, with a separate +/-0.1V forward-voltage note; do not turn those figures into a guaranteed Vf range at another current or temperature [1, p.2].
- **Size at both electrical corners, including GPIO voltage drop.** For an explicitly assumed LED characterized over the application at Vf=1.8-2.4V, a 3.3V +/-5% rail and 1K +/-1% resistor give 0.728-1.682mA with an ideal switch; include VOL or VOH and temperature in the real budget. This example's Vf range is a design input, not a WP710A10ID guarantee [1, p.2, Vf test conditions].
- **Select brightness from the exact LED's intensity bin and current curve.** WP710A10ID publishes relative intensity versus current as a typical curve; its 30mA absolute maximum at TA=25 degrees C is not the recommended indicator current or a brightness specification [1, pp.1-3].
- **Check source and sink specifications separately.** STM32F405/407 Table 49 specifies 0.4V output drop at 8mA and relaxed 1.3V drop at 20mA, both for 2.7V<VDD<3.6V; the 25mA per-pin absolute maximum is not an operating drive setting. Include aggregate supply/ground current limits and the table's PC13-PC15/PI8 restrictions [10, Tables 12,49].
- **WP710A10ID permits only 5V reverse bias at TA=25 degrees C.** A resistor limits forward current but does not clamp reverse voltage; protect a polarity-reversing application rather than treating the LED as a rectifier [1, p.2].

### Supply and First-Pixel Logic

- **Freeze the manufacturer, suffix and sheet revision in the BOM.** WS2812B-V5 V1.0 and WS2812C-2020 V1.2 print 3.7-5.3V under Absolute Maximum Ratings, with electrical characteristics at 5V/25 degrees C; neither sheet establishes guaranteed operation at 3.3V. SK6812RGBW Rev.01 prints 3.5-5.5V absolute limits but characterizes electrical parameters at 4.5-5.5V [3, Absolute Maximum Ratings/Electrical Characteristics; 4, p.2; 5, p.4].
- **Keep clocked-pixel operating and absolute limits separate too.** APA102C Rev.01 recommends VDD=4.5-5.5V, not its 2.5-7.5V limit-parameter range. SK9822 Rev.01 lists VDD=5.0V typical, 5.3V maximum in Section 8 despite that section's 4.5-5.5V test header; use 5V nominal within the listed 5.3V maximum rather than interpreting its -0.5 to +5.5V absolute rating as an operating range [6, p.6, Recommended working parameters; 11, p.4, Sections 7-8].
- **Do not transfer the old WS2812B input threshold to every revision.** V5 and C-2020 sheets specify VIH(min)=2.7V at 5V/25 degrees C; SK6812RGBW Rev.01 specifies 3.4V at 5V over -20 to +70 degrees C. Compare the MCU's guaranteed VOH, ground offset and actual operating conditions against the purchased pixel's sheet [2, p.4; 3, Electrical Characteristics; 4, p.2; 5, p.4].
- **SN74AHCT125 accepts a guaranteed 2V HIGH with VCC=4.5-5.5V.** Power it from a compliant LED rail and establish OE and data states during startup; a resistor alone does not translate a 3.3V HIGH into 5V logic [7, Recommended Operating Conditions/Electrical Characteristics].
- **Use 300-500 ohm in series immediately before the first NeoPixel DIN as Adafruit's wiring recommendation.** Check the resulting edge waveform with the actual cable; this is a signal-integrity recommendation, not a Worldsemi logic-level guarantee [8, Best Practices].

### Power Distribution and Timing

- **Use the actual channel current for power injection.** C-2020's stated 5mA/channel gives a nominal 100-pixel RGB full-white budget of 1.5A before control consumption; the sheet separately lists quiescent current <0.5mA without an active-control-current maximum or channel-current tolerance. Adafruit's 60mA RGB full-white estimate applies to its conventional NeoPixel budget, not every revision or RGBW part [4, pp.1,3; 9, Estimating Power Requirements].
- **Inject according to voltage drop along both supply and return.** Adafruit recommends distributing power so no pixel is more than about 1m from a power connection; treat that as its strip-wiring guideline and verify the farthest pixel stays within its supply limits under the actual full-white load [9, Distributing Power].
- **Keep RGBW's fourth channel in the data and supply budgets.** The cited SK6812RGBW Rev.01 sheet specifies 32 bits in RGBW order, R7 first through W0; verify the purchased part rather than assuming GRBW. Its DOUT drive-current figures are not LED channel-current ratings [5, pp.4-6, Section 13].
- **APA102C and SK9822 require clocked frames, not a WS2812 reset gap.** APA102C Rev.01's protocol text specifies a 32-zero start frame, three leading one bits in each LED frame and blue-green-red data; SK9822 Rev.01's refresh formula includes 64 framing bits plus 32 bits per pixel. Verify end-frame handling with the selected controller and chain [6, p.5, Communication protocol and timing; 11, p.6, Section 9(5)].
- **APA102C Rev.01 specifies VIH(min)=0.7*VDD over -20 to +80 degrees C.** Shift both clock and data when driving its 5V supply from a 3.3V MCU [6, p.6, Logic level normal working range; 7, Recommended Operating Conditions].

## Common Mistakes

- **Using an old 50us reset with a newer pixel.** C-2020 V1.2 needs >280us LOW and has its own pulse-width windows; a library's generic WS2812 name does not establish compatibility [4, p.3].
- **Driving DIN while pixel power is absent.** Adafruit warns of parasitic powering through data; sequence pixel power before data and establish a shared ground before connecting signals [8, Best Practices].
- **Using an animation average as the supply's full-white rating.** Adafruit's 20mA/pixel animation estimate differs from its 60mA/pixel RGB full-white estimate; select the budget for the maximum allowed command [9, Estimating Power Requirements].

## Sources

### Related Rules

- `misc/level-shifting.md` -- Translator topology and power sequencing.
- `power/decoupling.md` -- Bulk-capacitor selection and supply transients.
- `mcus/stm32.md` -- Device-specific GPIO restrictions.

### References

1. Kingbright -- WP710A10ID, DSAL0505 Rev.V.12A (2023): https://www.kingbrightusa.com/images/catalog/spec/wp710a10id.pdf
2. Worldsemi -- WS2812B Datasheet and Specifications, V1.0 (Jan 2016): https://cdn.sparkfun.com/assets/e/6/1/f/4/WS2812B-LED-datasheet.pdf
3. Worldsemi -- WS2812B-V5, V1.0: https://www.peace-corp.co.jp/data/WS2812B-V5_V1.0_EN.pdf
4. Worldsemi -- WS2812C-2020, V1.2 (2019): https://cdn.sparkfun.com/assets/e/1/0/f/b/WS2812C-2020_V1.2_EN_19112716191654.pdf
5. Opsco -- SK6812RGBW, SPC/SK6812RGBW Rev.01: https://cdn-shop.adafruit.com/product-files/2757/p2757_SK6812RGBW_REV01.pdf
6. APA Electronic -- APA-102C-NEW-260, Rev.01 (2018-10-11): https://www.lcd-module.de/eng/pdf/zubehoer/APA102C.pdf
7. Texas Instruments -- SN74AHCT125, SCLS264R Rev.R (HTML retrieved 2026-11-09): https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf
8. Adafruit -- NeoPixel Uberguide, Best Practices (read 2026-11-09): https://learn.adafruit.com/adafruit-neopixel-uberguide/best-practices
9. Adafruit -- NeoPixel Uberguide, Powering NeoPixels (read 2026-11-09): https://learn.adafruit.com/adafruit-neopixel-uberguide/powering-neopixels
10. STMicroelectronics -- STM32F405xx/STM32F407xx, DS8626 Rev.12: https://www.st.com/resource/en/datasheet/stm32f405rg.pdf
11. Opsco -- SK9822, SPC/SK9822 Rev.01 (2016-03-18): https://www.pololu.com/file/0J1234/sk9822_datasheet.pdf

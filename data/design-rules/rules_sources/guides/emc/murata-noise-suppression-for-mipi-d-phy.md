---
source: "Murata -- Noise Suppression for MIPI D-PHY (2020-05-14)"
url: "https://article.murata.com/en-us/article/noise-suppression-for-mipi-d-phy"
format: "HTML"
method: "fetchaller"
extracted: 2026-11-06
chars: 2018
---

# Noise Suppression for MIPI D-PHY

## 1. What is MIPI D-PHY?
MIPI D-PHY is an interface standard used in the exchange of signals for displays and cameras within a mobile device. In version 2 of D-PHY, communication speeds of up to 4.5 Gbps per lane are possible. Usage: LCD-CPU, Camera-CPU.

## 2. Noise Suppression for MIPI D-PHY
Noise is emitted from the FPC cable by digital signals that pass through MIPI D-PHY lines between the main board and module, and this noise can enter the antenna in the wireless circuit, which can result in reduced reception sensitivity of the antenna.

## 3. Measures
A noise filter is inserted into the interface section of the main board for reducing the outflow of noise to the FPC cable.

## 4. Notes
Conventional interfaces were either differential transmission systems or single-ended systems.
- Differential transmission line -> Common mode choke coil
- Single-ended transmission line -> LC filter, etc.
However, in MIPI, differential signals and single-ended signals are mixed.
-> This requires a noise suppression method that does not affect the waveforms of both high-speed differential and single-ended signals.

## 5. Noise filters for MIPI D-PHY
The following common mode choke coils and noise filters are recommended for MIPI D-PHY version 2.0. These minimize the effect on both differential and single-ended signals for reducing common mode noise.

| Part Number | Size | 700M-900MHz LTE/GSM | 1.5-2.6GHz LTE/GSM | 2.4GHz WiFi/BT | 3.5GHz LTE |
| --- | --- | --- | --- | --- | --- |
| DLM0QSN500HY2 | 0605 | o | o | o | |
| DLM0NSN500HY2 | 0806 | o | o | o | o |

## 6-7. Examples
The DLM0QSN500HY2 was used to successfully reduce noise entering the antenna in the LTE low-band/high-band and WiFi 2.4 GHz wide-area band. Inserting a filter has no negative effect on the signal waveform.

## 8. Conclusion
Because the MIPI D-PHY uses both differential signals and single-ended signals, care must be taken to select a component that does not distort the signal waveforms.

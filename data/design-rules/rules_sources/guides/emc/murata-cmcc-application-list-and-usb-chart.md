---
source: "Murata -- Common Mode Choke Coil / Noise Filter application list (signal line, non-automotive) and USB 2.0/3.0/3.1 selection chart"
url: "https://www.murata.com/-/media/webrenewal/products/emc/emifil/cmcc/pdf/consumer-signal.ashx"
format: "PDF 1p each (charts, read from page renders and PDF coordinates)"
method: "curl + pymupdf"
extracted: 2026-11-06
chars: 2746
---

# Murata common mode choke coil / noise filter charts (signal line, non-automotive)

## Application list and supported products (consumer-signal.ashx)

Columns in order of signal speed. A part spanning several columns is listed under each. Sizes are body dimensions in mm from the chart's rows; Murata labels them 0.45x0.3 (018012 inch / 0403 mm), 0.65x0.5 (025020 / 0605), 0.85x0.65 (03025 / 0806), 1.25x1.0 (0504 / 1210) and 2.0x1.2 (0805 / 2012). (eq) = red in the chart: "for Devices with Equalization functions".

| Interface | Parts |
| --- | --- |
| USB 2.0 (480 Mbps) | DLM0QSN900HY2 (0.65x0.5), DLM0NSN900HY2 (0.85x0.65), DLM11CN900HH2 (1.25x1.0), DLW21HN900SQ2 (2.0x1.2) |
| MIPI D-PHY Ver1.1 (1.5 Gbps) | DLM0QSN500HY2 (0.65x0.5), DLM0NSN900HY2 (0.85x0.65) |
| HDMI 1.4 (1.7 Gbps) | DLM0QSB350HY2, NFG0QHB372HS2 (0.65x0.5), DLM0NSN900HY2 (0.85x0.65), DLM11CN900HH2 (1.25x1.0), DLW21SN900HQ2 (2.0x1.2) |
| MIPI C-PHY Ver1.0 (2.5 Gsym/s) | NFG0NCN162HL3 (0.85x0.65) |
| MIPI D-PHY Ver1.2 (2.5 Gbps) | DLM0QSN500HY2 (0.65x0.5), DLM0NSN500HY2 (0.85x0.65) |
| USB 3.1 gen1 (5 Gbps) | DLM0QSB350HY2, NFG0QHB372HS2 (eq) (0.65x0.5), DLM0NSN500HY2 (eq) (0.85x0.65), DLM11CN500HH2 (eq) (1.25x1.0), DLW21SN900HQ2, DLW21HN900HQ2 (eq) (2.0x1.2) |
| HDMI 2.0 (6 Gbps) | DLM0QSB350HY2, NFG0QHB372HS2 (0.65x0.5), DLM0NSB280HY2 (0.85x0.65), DLM11CB120HH2 (1.25x1.0), DLW21SN900HQ2 (2.0x1.2) |
| DisplayPort 1.4 (8.1 Gbps) | DLM0QSB350HY2, NFG0QHB372HS2 (0.65x0.5), DLM0NSB280HY2 (0.85x0.65), DLW21SN900HQ2 (2.0x1.2) |
| USB 3.1 gen2 (10 Gbps) | DLM0QSB350HY2, NFG0QHB542HS2 (0.65x0.5), DLM0NSB280HY2 (0.85x0.65), DLM11CB120HH2 (1.25x1.0), DLW21SN900HQ2 (2.0x1.2) |
| HDMI 2.1 (12 Gbps) | DLM0QSB120HY2, NFG0QHB542HS2 (0.65x0.5), DLM0NSB120HY2 (0.85x0.65), DLM11CB120HH2 (1.25x1.0) |

## USB 2.0 / 3.0 / 3.1 selection chart (usb.ashx, https://www.murata.com/-/media/webrenewal/products/emc/emifil/cmcc/pdf/usb.ashx)

Parts are placed on an axis of cutoff frequency (1 to 8.5+ GHz). Each interface is a bar that starts at the lowest cutoff Murata accepts and runs right. Bar starts, from the PDF coordinates against the axis labels:

- USB 2.0 (480 Mbps): 1.0 GHz
- USB 3.0 / USB 3.1 Gen1 (5 Gbps), "with equalizing function": 2.5 GHz
- USB 3.1 Gen2 (10 Gbps), "with equalizing function": 5.0 GHz
- USB 3.1 Gen2 (10 Gbps), "Murata's Recommended item": 8.0 GHz

Parts on the chart: NFG0QHB372HS2, NFG0QHB542HS2, DLM0QSN900HY2, DLM0QSB120HY2, DLM0QSB350HY2, DLM0NSN900HY2, DLM0NSN500HY2, DLM0NSM900HY2, DLM0NSB120HY2, DLM0NSB280HY2, DLM11CN201HH2, DLM11CN900HH2, DLM11CN500HH2, DLM11CB120HH2, DLW21HN900SQ2, DLW21HN670SQ2, DLW21HN900HQ2, DLW21HN670HQ2, DLW21SN900HQ2. Each part's own cutoff isn't read here: label and picture sit at different x positions.

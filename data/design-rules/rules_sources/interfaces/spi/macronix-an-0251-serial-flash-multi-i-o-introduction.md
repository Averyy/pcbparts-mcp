---
source: "Macronix AN-0251 -- Serial Flash Multi-I/O Introduction"
url: "https://www.macronix.com/Lists/ApplicationNote/Attachments/1899/AN0251V1%20-%20Macronix%20Serial%20Flash%20Multi%20IO%20Introduction.pdf"
format: "PDF 12pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 9760
---
# Macronix Serial Flash Multi-I/O Introduction

## 1. Introduction

All Macronix serial flash support a serial addressing protocol where 1 byte of instruction opcode is followed by a 3 byte (24 bit) address (note: may be a 4 byte address if the memory space is larger than 128Mb). Historically, to obtain faster data transfer rates and quicker system boot times, parallel flash were used as they had a parallel address bus and a parallel x16 data bus. Unfortunately, the wider busses resulted in flash package pin counts which ranged from 32 to 70 pins along with a similar increase in host interface pins, and an increase in PC board routing, all resulting in a higher BOM cost. To solve this problem, Macronix offers several serial flash families. For example, the MX25xxxx35 series serial flash family (in both 1.8V and 3V densities ranging from 8Mb to 512Mb) in which commands, address, and data can be transmitted synchronously on as many as 4 channels in parallel. The serial interface can be configured in Single x1 I/O Mode (SPI), Dual x2 I/O Mode (DSPI), or Quad x4 I/O Mode (QSPI), with commands issued in either the SPI or QPI format. Not only do serial flash have performance similar to parallel flash when used in the x4 mode, but they are available in industry standard low pin count packages such as 8-SOP, 16-SOP and 8-WSON.

Key advantages of serial NOR flash vs. parallel NOR flash:

- SPI flash has 4 signals (SCLK, CS, SI, SO) versus ~38 signals for Parallel NOR (19 address bus + 16 data bus + 3 control)
- Reduces EMI, system noise and power consumption
- Aggregate bandwidth increases (similar performance)
- PCB area savings resulting in reduced BOM cost

This application note clarifies the differences between serial flash interface configurations and explains how to configure the flash in those modes.

## 2. Serial Flash Interfaces and Read Flow

In SPI (Single I/O) mode, the flash synchronously receives the command, address, and data serially shifted in on one input pin SI (Serial In), and the data is clocked out on SO (Serial Out). The entire sequence takes 48 clock cycles in FastREAD mode.

Single I/O Mode: 4 unidirectional signal lines (CS#, SCLK, MOSI/SI, MISO/SO).

Macronix Serial Flash provides Multi I/O functions by switching pin functions to support both a uni-directional and a bi-directional data bus. In SPI mode, the command is serial (single channel), but the number of channels used for address and data depends on the read command. A Dual I/O SPI mode uses SI and SO pins for data input and output, and a Quad I/O SPI mode (sometimes referred to as QSPI) uses SI, SO, WP#, and NC (or Hold#/Reset#) pins to serve as x4 I/O data input and output. In QPI mode, commands, as well as address and data are sent in x4 mode.

In the x-y-z notation, x specifies the number of channels for the command, y specifies the number of channels for the address, and z is the number of channels for data.

### Macronix Serial Flash Read Modes

1. **FastREAD (cmd = 0Bh): 1-1-1, Single I/O SPI Mode Read** -- cmd on 1 channel, address on 1 channel, data on 1 channel.
2. **DREAD (cmd = 3Bh): 1-1-2, DSPI Mode Dual-Output Read** -- cmd on 1 channel, address on 1 channel, data on 2 channels.
3. **2READ (cmd = BBh): 1-2-2, DSPI Mode Dual-I/O Read** -- cmd on 1 channel, address on 2 channels, data on 2 channels.
4. **QREAD (cmd = 6Bh): 1-1-4, QSPI Mode Quad-Output Read** -- cmd on 1 channel, address on 1 channel, data on 4 channels.
5. **4READ (cmd = EBh): 1-4-4, QSPI Mode Quad-I/O Read** -- cmd on 1 channel, address on 4 channels, data on 4 channels.
6. **4READ (cmd = EBh): 4-4-4, QPI Read** -- cmd on 4 channels, address on 4 channels, data on 4 channels.

Clock cycles to read 1 byte of data:

- Serial x1 I/O (SPI) mode: 48 clocks
- x2 I/O DSPI mode: 28 clocks
- x4 I/O QSPI mode: 22 clocks
- x4 I/O QPI mode: 16 clocks

### Dual I/O (DSPI) Mode

2 unidirectional and 2 bidirectional signal lines.

**DREAD (1-1-2):** Flash receives Commands on SIO0 only. Flash receives Address on SIO0 only. Flash sends Data on SIO[1:0]. Flow: DREAD command -> 3-byte address on SI -> 8 dummy cycles (default) -> Data out interleaved on SIO1, SIO0 -> End by CS# goes high.

**2READ (1-2-2):** Flash receives Commands on SIO0 only. Flash receives Address on SIO[1:0]. Flash sends Data on SIO[1:0]. Flow: 2READ command -> 3-byte address interleaved on SIO1, SIO0 -> 4 dummy cycles (default) -> Data out interleaved on SIO1, SIO0 -> End by CS# goes high.

### Quad I/O (QSPI) Mode

2 unidirectional and 4 bidirectional signal lines.

**QREAD (1-1-4):** Flash receives Commands on SIO0 only. Flash receives Address on SIO0 only. Flash sends Data on SIO[3:0]. 8 dummy cycles (default).

**4READ (1-4-4):** Flash receives Commands on SIO0 only. Flash receives Address on SIO[3:0]. Flash sends Data on SIO[3:0]. 6 dummy cycles (default).

### QPI Mode (4-4-4)

Flash receives Commands on SIO[3:0]. Flash receives Address on SIO[3:0]. Flash sends Data on SIO[3:0].

## 3. Serial Flash Preparation for Quad I/O Operation

Macronix MX25xxxx35 series serial flash is delivered in single I/O mode (x1 bus width). If the serial flash will be used in Quad I/O mode (x4 bus width), the QE (Quad Enable) bit must be set to '1'. The non-volatile QE bit is Bit-6 of the Macronix serial flash Status Register.

**Note:** When QE bit is "1", it performs Quad I/O mode, and WP#, Hold#/Reset# are disabled.

### Sequence to set QE:

1. Send WREN (Write Enable) command (06h). This sets the WEL (Write Enable Latch) bit (Status Register bit 1).
2. Send WRSR (Write Status Register) command (01h) with 40h as the data. This sets the QE bit, but it takes some time for the WRSR operation to complete.
3. Use the RDSR (Read Status Register) command (05h) to poll the Status Register to check when bits 1 and 0 are clear. While the WRSR operation is still in progress, bits 1 and 0 will remain set to 1. Continue polling until bits 1 and 0 clear to zero.

**Note:** The above steps are an overly simplified version. The actual software may need to do a read-modify-write on the Status Register to preserve the state of the other non-volatile bits.

After the QE bit is set, all of the Fast Read (x1) commands are still supported along with the Quad Output (x4) Fast Read command. The Flash I/O pins "SIO2" and "SIO3" will tristate when not driving. The WP# and Reset/Hold# pin functions (if available) are now disabled.

The step to set the QE bit can be avoided if the Macronix MX25Lxx73 series serial flash is used, as the 73 series have the QE bit permanently set to '1'. At this time, the 73 series is only available in 3V and in densities from 8Mb to 128Mb.

For a desktop/notebook/PC Application, Macronix recommends the 73 series part as some chip sets check the SFDP (Serial Flash Discoverable Parameter) table first, and if Quad mode is supported, the chipset will begin talking in Quad mode.

### Macronix Quad I/O Mode Serial Flash (32Mb to 512Mb)

| Voltage | Density | Part Number |
|---|---|---|
| 3V | 32Mb | MX25L3235E, MX25L3273E |
| 3V | 64Mb | MX25L6435E, MX25L6473E |
| 3V | 128Mb | MX25L12835F, MX25L12873F |
| 3V | 256Mb | MX25L25635F |
| 3V | 512Mb | MX66L51235F |
| 1.8V | 32Mb | MX25U3235F |
| 1.8V | 64Mb | MX25U6435F |
| 1.8V | 128Mb | MX25U12835F |
| 1.8V | 256Mb | MX25U25635F |
| 1.8V | 512Mb | MX66U51235F |

## 4. Serial Flash Preparation for QPI Operation

In SPI (1-1-1) and QSPI (1-1-4 or 1-4-4) modes, the commands are always issued on one channel with 8 clocks. In QPI (4-4-4) mode however, commands are issued on 4 channels in 2 clock cycles.

The command EQIO (35h) is issued to enter QPI mode and is sent as a x1 serial stream. Once the serial flash receives this command and enters QPI mode, it expects subsequent commands, addresses, and data on 4 lines. There is no need to set the QE bit.

QPI is disabled with the RSTQIO command (F5h), software reset command, or a power cycle. Enabling QPI mode is different from setting QE=1:

- When QPI is enabled, Fast Read x1 (1-1-1) and Fast Read x4 modes 1-1-4 and 1-4-4 are not supported. Only 4-4-4 mode is supported.
- When QE=1 and QPI is not entered, Fast Read x1 (1-1-1) and Fast Read x4 (1-1-4 and 1-4-4) commands are all still supported.

In both cases (QE=1 or QPI enabled), the "HOLD#/SIO3" pin functions as "SIO3" (HOLD# disabled) and the "WP#/SIO2" functions as "SIO2" (WP# disabled).

## 5. Summary

Macronix serial flash read speeds can nearly double and quadruple when being used in x2 and x4 multi I/O modes.

Macronix offers different serial flash products with Multi-I/O interfaces, and these products are backward compatible to Single I/O serial flash offered by Macronix.

MX25xxxx35 series serial flash is delivered in single I/O mode (x1 bus width) by default. If single I/O mode or dual I/O will be used only, there is no need to set the QE bit. If the serial flash will be used in Quad I/O mode (x4 bus width), the QE bit must be set to '1' or a 73 series serial flash that has QE preset to '1' should be used.

In SPI (1-1-1), DSPI (1-1-2 or 1-2-2) and QSPI (1-1-4 or 1-4-4) modes, commands are always issued on one channel with 8 clocks. In QPI (4-4-4) mode, commands are issued on 4 channels in 2 clock cycles. The command EQIO (35h) is issued to enter QPI mode. If QPI mode has been entered, the QE bit does not need to be set.

## 6. References

| Macronix Doc. | Description |
|---|---|
| AN0209 | Macronix High Density Serial Flash Addressing |

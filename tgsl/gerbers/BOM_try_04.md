# TGSL v3 – Bill of materials

Parts for the TGSL board in `gerbers/try_04`, following the schematic `design/Schematic.pdf` (Rev .3, 2009).
Suggested location in the repo: `tgsl/parts/BOM.md`.

LCSC codes were looked up on 2026-10-22. Stock changes quickly: check each code before ordering.
Where no LCSC code is given, search LCSC by the manufacturer part number (MPN) or use the listed specs as a filter.

## Corrections to the older lists

The schematic (Rev .3) is the reference. The two older lists in the repo disagree with it:

- `design/BOM.pdf` is an older revision: R13/R14 = 5k1 (now 4k7), C14/C17 = 4.7 µF (now 2 × 10 µF each, back to back),
  R6 listed three times, and R1, R2, R52, R55, R56 missing. Do not use it.
- `parts/TGSL_PARTS1.xls`:
  - "R6 22K" is really R2, and its value is **24k** (schematic note "22k -> 24k"). 24k is needed twice (R2, R21).
  - R18 and R22 are counted as fixed 100k resistors and again as pots. Fixed 100k: **9**.
  - 6 sockets for 8-pin ICs are listed, but there are **7** DIP-8 ICs.
  - 330 Ω × 3 is listed; the schematic has 2 (R52, R55).

## Resistors (49)

Metal film, 1/4 W, 1 %. Lead diameter ≤ 0.6 mm (0.8 mm holes).
Series: UNI-ROYAL MFR0W4F…A50 (body 2.2 × 6.5 mm). LCSC sells these in multiples of 50.

| Value | Qty | Refs | MPN | LCSC |
|---|---|---|---|---|
| 330 Ω | 2 | R52, R55 | MFR0W4F3300A50 | search MPN |
| 1k | 5 | R7, R27, R37, R38, R56 | MFR0W4F1001A50 | C57435 |
| 2k2 | 4 | R1, R11, R12, R44 | MFR0W4F2201A50 | search MPN |
| 3k3 | 1 | R19 | MFR0W4F3301A50 | search MPN |
| 4k7 | 6 | R9, R10, R13, R14, R41, R53 | MFR0W4F4701A50 | search MPN |
| 10k | 1 | R20 | MFR0W4F1002A50 | C57436 |
| 15k | 1 | R24 | MFR0W4F1502A50 | search MPN |
| 20k | 2 | R25, R26 | MFR0W4F2002A50 | search MPN |
| 24k | 2 | R2, R21 | MFR0W4F2402A50 | search MPN |
| 27k | 1 | R45 | MFR0W4F2702A50 | search MPN |
| 47k | 4 | R3, R6, R32, R34 | MFR0W4F4702A50 | search MPN |
| 100k | 9 | R8, R17, R23, R28, R30, R40, R42, R49, R50 | MFR0W4F1003A50 | C58597 |
| 200k | 2 | R48, R51 | MFR0W4F2003A50 | search MPN |
| 220k | 3 | R15, R16, R39 | MFR0W4F2203A50 | search MPN |
| 330k | 1 | R43 | MFR0W4F3303A50 | search MPN |
| 470k | 2 | R29, R31 | MFR0W4F4703A50 | search MPN |
| 1M | 3 | R33, R35, R54 | MFR0W4F1004A50 | search MPN |

R18, R22 and R36 are potentiometers (see Other parts).

## Capacitors

All non-electrolytic capacitors have 5 mm lead spacing on the board.
C1, C2 and C6 set the coil frequencies: use film (polyester or polypropylene), not ceramic.

| Value | Qty | Refs | Type | MPN | LCSC |
|---|---|---|---|---|---|
| 10 pF | 1 | C7 | ceramic C0G, P = 5 mm | TDK FG28C0G1H100DNT06 | search MPN |
| 15 pF | 1 | C11 | ceramic C0G, P = 5 mm | TDK FG28C0G1H150JNT06 | search MPN |
| 100 pF | 4 | C9, C10, C19, C22 | ceramic C0G, P = 5 mm | TDK FG28C0G1H101JNT06 | search MPN |
| 15 nF | 1 | C6 (Rx tuning) | polyester film 100 V 5 %, P = 5 mm | KYET PE153J2A0501 | C390169 |
| 22 nF | 7 | C2 (Tx tuning), C13, C16, C20, C23, C24, C25 | polyester film 100 V 5 %, P = 5 mm | KYET PE223J2A0501 | C393117 |
| 100 nF | 11 | C26 and the supply bypass capacitors | ceramic X7R 50 V, P = 5 mm | TDK FG28X7R1H104KNT06 | C342794 |
| 220 nF | 4 | C1 (Tx tuning), C8, C12, C15 | polyester film 100 V 5 %, P = 5 mm | KYET PE224J2A0501 | C393118 |
| 470 nF | 2 | C18, C21 | polyester film 100 V 5 %, P = 5 mm | KNSCHA MPE474J100V82CL0051 | C2803190 |
| 10 µF | 4 | C14, C14b, C17, C17b | electrolytic ≥ 25 V, Ø 5 mm, P = 2–2.5 mm | – | filter by specs |
| 220 µF | 4 | C3, C4, C5, C28 | electrolytic **25–35 V, Ø 10 mm, P = 5 mm** | – | filter by specs |
| 1000 µF | 1 | C27 | electrolytic 25 V, Ø ≤ 16 mm, P = 7.5 mm | – | filter by specs |

Optional for C1: polypropylene KYET PE224J2A0502 (LCSC C478435), same size, lower drift than polyester.

Footprint notes (measured from the try_04 gerbers):
- 220 µF: silkscreen circle Ø 9.9 mm, holes 5.08 mm apart. Smaller 16 V parts (2.5–3.5 mm pitch) also fit with bent leads.
- 1000 µF: silkscreen circle Ø 16 mm, holes 7.6 mm apart, 1.0 mm drill.
- 10 µF: silkscreen circle Ø 5.5 mm, holes 2.54 mm apart.

C19 and C22 are the compensation capacitors of the LM308s. With TL081s (see U104/U105) they have no effect and can be left out.

## Semiconductors

| Part | Qty | Refs | MPN | LCSC | Notes |
|---|---|---|---|---|---|
| 1N4148 | 10 | D3–D12 | onsemi 1N4148TR | C84410 | |
| BC547 | 2 | TR2, TR9 | LGE BC547C | C713614 | BC547B C713613 also fine |
| BD140 | 1 | TR3 | CJ BD140 | C20604 | TO-126, pinout E-C-B; 1.1 mm holes |
| 2N2222A | 2 | TR6, TR8 | ALJ 2N2222A-338 | C22751485 | TO-92; alt. Semtech 2N2222A C118536 |
| 2N2907A | 2 | TR1, TR7 | Semtech 2N2907A | C118537 | TO-92; alt. ALJ 2N2907A-338 C22751484 |
| JFET | 2 | TR4, TR5 | see below | | |
| CD4024BE | 1 | U100 | TI CD4024BE | C225716 | DIP-14 |
| LF353P | 1 | U101 | TI LF353P | C5207 | |
| LM393P | 2 | U102, U106 | TI LM393P | C5209 | |
| LM358P | 2 | U103, U107 | TI LM358P | C5213 | U107 runs from +12 V / −5 V |
| TL081CP | 2 | U104, U105 | TI TL081CP | C38969 | replaces LM308, see below |
| L7808CV | 1 | U108 | ST L7808CV-DG | C3793 | TO-220; IN-GND-OUT as on the silkscreen |

**JFETs (TR4, TR5).** The silkscreen says BF245C, the schematic J107. J107 is obsolete (onsemi J107, LCSC C3753122, out of stock).
A possible substitute is **onsemi J113 (LCSC C274643)**, which LCSC marks "not recommended for new designs".
Its cut-off voltage (−0.5 to −3 V) is lower than the ≈ −5 V gate drive, so it switches fully off.
Its on-resistance (≈ 100 Ω against 8 Ω for J107) is small next to the 20k resistors R25/R26.
Pinout D-S-G, the same as J107. This substitution is a suggestion and has not been tested in a TGSL build.

**U104, U105.** Genuine LM308N is no longer made and relabelled parts are common.
TL081CP is a common replacement in TGSL builds; `parts/TGSL_PARTS1.xls` lists the similar TL071ACP as an alternative.
On this board LM308 pins 1 and 5 have no connection and pin 8 only goes to C19/C22, so the TL081 drops in.

**Pinouts.** TO-92 pin order differs between makers, even for the same part number.
Check each transistor against its own datasheet, not only the silkscreen.
On the first power-up, use a current-limited supply. Expect roughly 25–35 mA at 12 V.

## Other parts (not from LCSC or not checked)

| Part | Qty | Notes |
|---|---|---|
| Potentiometer 100k linear | 2 | R18 (Disc. level), R22 (Ground balance) |
| Potentiometer / trimmer 10k | 1 | R36 (Sens.) |
| IC socket DIP-8 | 7 | |
| IC socket DIP-14 | 1 | |
| Speaker 8 Ω | 1 | SP1 |
| Switch, 3 contacts | 1 | J3, Disc / All metal |
| Power switch | 1 | |
| Battery holder 12 V | 1 | e.g. 8 × AA; the 7808 needs about 10 V at its input |
| Coil connector and shielded cable | 1 | J1 (TX), J2 (RX) |

The board has footprints for one 100k pot and one 10k trimmer (1.3 mm holes, triangle 5.08 × 5.08 mm).
The third control is wired off-board.

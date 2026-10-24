# TGSL v3 – Bill of materials (rev 2)

Parts for the TGSL board in `gerbers/try_04`, following the schematic `design/Schematic.pdf` (Rev .3, 2009).
This file replaces `BOM_try_04.md`. The CSV for LCSC is `tgsl_lcsc_bom_rev2.csv`.

LCSC codes were looked up on 2026-10-22. Stock changes quickly: check each code before ordering.
Where no LCSC code is given, search LCSC by the manufacturer part number (MPN) or use the listed specs as a filter.

## Changes from rev 1 (`BOM_try_04.md`)

Found by checking the full board netlist against the schematic and measuring every footprint on the try_04 gerbers.

1. **R51 is two resistors on the board.** The schematic has one 200k (U107 pin 3 to ground). The board has two
   100K footprints in series in its place. Fit two 100k (R51a, R51b). 100k goes from 9 to **11**. Leaving one
   footprint empty would leave U107 pin 3 pulled to +12 V.
2. **R48:** the schematic says 200k, the silkscreen says 220K. Either works: it only sets the hysteresis of the
   battery comparator (U107b), whose output is not connected to anything. This BOM keeps 200k.
3. **Resistor size.** All resistor footprints are 7.62 mm (0.3") lead spacing with a body outline of about 3.8 × 1.9 mm.
   The rev 1 series (MFR0W4F, body Ø2.2 × 6.5 mm) does not lie flat at 7.62 mm.
   Use the small-body series **UNI-ROYAL MF0S4FF (250 mW, Ø1.9 × 3.3 mm)**. Alternatives: UNI-ROYAL MFR0W8F
   (125 mW, same size) or Vishay MBA 0204 (0.4 W, Ø1.6 × 3.6 mm).
4. **Small ceramic capacitors are 2.54 mm, not 5 mm.** C7 (10 pF), C11 (15 pF), C9, C10, C19, C22 (100 pF)
   have 2.54 mm lead spacing. Use TDK **FG18** (2.5 mm), not FG28 (5 mm).
   Rev 1 said "all non-electrolytic capacitors have 5 mm lead spacing", which is wrong.
5. **100 nF:** the board has 10 positions (C26 + 9 supply bypass), not 11.
6. **Transistor orientation.** The board's TO-92 footprints expect a C-B-E (and, for the JFETs, G-S-D) pin order.
   Many 2N2222A/2N2907A/J107/J113 parts are E-B-C or D-S-G and must be turned 180° relative to the silkscreen.
   See *Fitting the transistors* below.

## Resistors (50 positions)

Metal film, 1 %, small body: Ø ≤ 2.0 mm, length ≤ 3.6 mm, lead diameter ≤ 0.6 mm (0.8 mm holes, 7.62 mm spacing).
Series: UNI-ROYAL MF0S4FF…A50 (250 mW, Ø1.9 × 3.3 mm). Example of an existing code in this series: MF0S4FF6200A50 = LCSC C18724246 (620 Ω).
The MPNs below follow the same pattern; check each one exists and is in stock. LCSC sells these in multiples of 50.

| Value | Qty | Refs | MPN | LCSC |
|---|---|---|---|---|
| 330 Ω | 2 | R52, R55 | MF0S4FF3300A50 | search MPN |
| 1k | 5 | R7, R27, R37, R38, R56 | MF0S4FF1001A50 | search MPN |
| 2k2 | 4 | R1, R11, R12, R44 | MF0S4FF2201A50 | search MPN |
| 3k3 | 1 | R19 | MF0S4FF3301A50 | search MPN |
| 4k7 | 6 | R9, R10, R13, R14, R41, R53 | MF0S4FF4701A50 | search MPN |
| 10k | 1 | R20 | MF0S4FF1002A50 | search MPN |
| 15k | 1 | R24 | MF0S4FF1502A50 | search MPN |
| 20k | 2 | R25, R26 | MF0S4FF2002A50 | search MPN |
| 24k | 2 | R2, R21 | MF0S4FF2402A50 | search MPN |
| 27k | 1 | R45 | MF0S4FF2702A50 | search MPN |
| 47k | 4 | R3, R6, R32, R34 | MF0S4FF4702A50 | search MPN |
| 100k | 11 | R8, R17, R23, R28, R30, R40, R42, R49, R50, R51a, R51b | MF0S4FF1003A50 | search MPN |
| 200k | 1 | R48 (silkscreen says 220K; either works) | MF0S4FF2003A50 | search MPN |
| 220k | 3 | R15, R16, R39 | MF0S4FF2203A50 | search MPN |
| 330k | 1 | R43 | MF0S4FF3303A50 | search MPN |
| 470k | 2 | R29, R31 | MF0S4FF4703A50 | search MPN |
| 1M | 3 | R33, R35, R54 | MF0S4FF1004A50 | search MPN |

R18, R22 and R36 are potentiometers (see Other parts).
R55 (330 Ω, speaker supply) carries up to about 35 mA while the tone is on. With C27 averaging the current it
dissipates well under 250 mW, but do not use a 125 mW part there.

## Capacitors

Lead spacing as measured on the try_04 gerbers.
C1, C2 and C6 set the coil frequencies: use film (polyester or polypropylene), not ceramic.

| Value | Qty | Refs | Spacing | Type | MPN | LCSC |
|---|---|---|---|---|---|---|
| 10 pF | 1 | C7 | 2.54 mm | ceramic C0G | TDK FG18C0G1H100DNT06 | search MPN |
| 15 pF | 1 | C11 | 2.54 mm | ceramic C0G | TDK FG18C0G1H150JNT06 | search MPN |
| 100 pF | 4 | C9, C10, C19, C22 | 2.54 mm | ceramic C0G | TDK FG18C0G1H101JNT06 | search MPN |
| 15 nF | 1 | C6 (Rx tuning) | 5.08 mm | polyester film 100 V 5 % | KYET PE153J2A0501 | C390169 |
| 22 nF | 7 | C2 (Tx tuning), C13, C16, C20, C23, C24, C25 | 5.08 mm | polyester film 100 V 5 % | KYET PE223J2A0501 | C393117 |
| 100 nF | 10 | C26 and 9 supply bypass capacitors | 5.08 mm | ceramic X7R 50 V | TDK FG28X7R1H104KNT06 | C342794 |
| 220 nF | 4 | C1 (Tx tuning), C8, C12, C15 | 5.08 mm | polyester film 100 V 5 % | KYET PE224J2A0501 | C393118 |
| 470 nF | 2 | C18, C21 | 5.08 mm | polyester film 100 V 5 % | KNSCHA MPE474J100V82CL0051 | C2803190 |
| 10 µF | 4 | C14, C14b, C17, C17b | 2.54 mm | electrolytic ≥ 25 V, Ø ≤ 5.5 mm | – | filter by specs |
| 220 µF | 4 | C3, C4, C5, C28 | 5.08 mm | electrolytic 25–35 V, Ø ≤ 10 mm | – | filter by specs |
| 1000 µF | 1 | C27 | 7.6 mm | electrolytic 25 V, Ø ≤ 16 mm | – | filter by specs |

Optional for C1: polypropylene KYET PE224J2A0502 (LCSC C478435), same size, lower drift than polyester.

Footprint notes (measured from the try_04 gerbers):
- **Film capacitor thickness.** Most film positions leave room for a body up to about 3–4 mm thick.
  The tightest is C18 (0.47, next to the 47K of R32): about 3 mm. Check the body thickness in the datasheet
  of the 470 nF part before ordering; if it is thicker, a 63 V part is usually slimmer.
- There is a second footprint in parallel with C6 at the RX input (both marked RXc). It is for trimming the Rx
  resonance and is normally left empty.
- 220 µF: silkscreen circle Ø 9.9 mm. 1000 µF: circle Ø 16 mm, holes 7.6 mm apart, 1.0 mm drill.
  A smaller 1000 µF (Ø 10–13 mm, 5 mm spacing) also fits with the leads bent out.
- 10 µF: silkscreen circle Ø 5.5 mm, holes 2.54 mm apart. C14/C14b and C17/C17b are back to back
  (minus to minus); follow the + marks on the silkscreen.

C19 and C22 are the compensation capacitors of the LM308s. With TL081s (see U104/U105) they have no effect and can be left out.

## Semiconductors

| Part | Qty | Refs | MPN | LCSC | Notes |
|---|---|---|---|---|---|
| 1N4148 | 10 | D3–D12 | onsemi 1N4148TR | C84410 | band as on the silkscreen |
| BC547 | 2 | TR2, TR9 | LGE BC547C | C713614 | BC547B C713613 also fine |
| BD140 | 1 | TR3 | CJ BD140 | C20604 | TO-126, E-C-B; 1.1 mm holes at 2.54 mm (bend the legs slightly) |
| 2N2222A | 2 | TR6, TR8 | ALJ 2N2222A-338 | C22751485 | TO-92; alt. Semtech 2N2222A C118536. Check pin order, see below |
| 2N2907A | 2 | TR1, TR7 | Semtech 2N2907A | C118537 | TO-92; alt. ALJ 2N2907A-338 C22751484. Check pin order, see below |
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
This substitution is a suggestion and has not been tested in a TGSL build.
JFET pin order differs between makers (onsemi J113: D-S-G; Philips J113: G-S-D). See below.

**U104, U105.** Genuine LM308N is no longer made and relabelled parts are common.
TL081CP is a common replacement in TGSL builds; `parts/TGSL_PARTS1.xls` lists the similar TL071ACP as an alternative.
On this board LM308 pins 1 and 5 have no connection and pin 8 only goes to C19/C22 (to ground), so the TL081 drops in.
(Checked on the try_04 netlist.)

## Fitting the transistors

On the silkscreen, each TO-92 outline has one **straight edge** (the flat face of the part) and one side drawn with
cut corners (the round back). Looking at the straight edge from outside the outline, the board expects this order,
left to right:

- bipolar transistors (2N2222, 2N2907, BC547): **C – B – E**
- JFETs (TR4, TR5): **G – S – D**

BC547 is C-B-E, so it goes in as drawn. Most 2N2222A, 2N2907A, J107 and onsemi J113 parts are E-B-C (or D-S-G):
fit those **turned 180°**, flat face towards the cut-corner side of the outline.
Always check the datasheet of the part you actually have, and confirm the base with a multimeter (diode test)
before soldering.

Pads by position, as seen from the component side with the 4024 at the top of the board
(coordinates in mm from the bottom-left corner, as in the gerbers):

| Ref | Part | Straight edge | Pads |
|---|---|---|---|
| TR1 | 2N2907 | bottom | C left (14.6, 74.9), B top (17.2, 77.4), E right (19.7, 74.9) |
| TR6 | 2N2222 | top | E left (23.2, 75.8), B bottom (25.8, 73.3), C right (28.3, 75.8) |
| TR7 | 2N2907 | right | E top (67.3, 90.0), B left (64.7, 87.4), C bottom (67.3, 84.9) |
| TR8 | 2N2222 | left | C top (64.9, 81.9), B right (67.5, 79.3), E bottom (64.9, 76.8) |
| TR2 | BC547 | right | E top (84.4, 90.6), B left (81.9, 88.1), C bottom (84.4, 85.5) |
| TR9 | BC547 | right | E top (90.0, 90.7), B left (87.4, 88.2), C bottom (90.0, 85.6) |
| TR4 | JFET | right | D top (46.2, 60.1), S left (43.7, 57.6), **G bottom** (46.2, 55.1) |
| TR5 | JFET | right | D top (41.8, 32.5), S left (39.2, 30.0), **G bottom** (41.8, 27.4) |
| TR3 | BD140 | – | B left (92.0, 78.4), C middle (94.6, 78.4), E right (97.1, 78.4) |

- **JFETs:** drain and source are interchangeable; what matters is that the gate goes to the bottom pad.
- **BD140:** the "B C E" letters above it are printed upside down. Fit it with the printed face towards those letters
  (metal back towards the 330 Ω resistor below). Seen from the front, BD140 is E-C-B, which then lands E on the right.
- **7808:** metal tab towards the thick line at the top of its outline; IN-GND-OUT as printed below it.

On the first power-up, use a current-limited supply. Expect roughly 25–35 mA at 12 V.
If it draws about 100 mA, a TO-92 is in the wrong way round.

## Other parts (not from LCSC or not checked)

| Part | Qty | Notes |
|---|---|---|
| Potentiometer 100k linear (panel) | 1 | R18 (Disc. level), wired off-board to three octagonal pads (ends: U101 pin 1 and R19; wiper: R20) |
| Potentiometer / trimmer 100k | 1 | R22 (Ground balance), on-board footprint; only the wiper and the grounded end are used |
| Trimmer 10k | 1 | R36 (Sens.), on-board footprint |
| IC socket DIP-8 | 7 | |
| IC socket DIP-14 | 1 | |
| Speaker 8 Ω | 1 | SP1 |
| Switch, 3 contacts | 1 | J3, Disc / All metal |
| Power switch | 1 | |
| Battery holder 12 V | 1 | e.g. 8 × AA; the 7808 needs about 10 V at its input |
| Coil connector and shielded cable | 1 | J1 (TX), J2 (RX) |

The two on-board pot footprints have 1.3 mm holes: the two ends are 5.08 mm apart and the wiper sits 5.08 mm
off that line (horizontal 6–10 mm trimmer layout). Check the pin drawing of the part you buy.

## How this BOM was checked

- The schematic was transcribed by hand (101 parts) and every part on the try_04 silkscreen was read with its
  copper nets (112 parts). Pins per net add up to all 346 holes.
- Matching them, starting from the IC pins: 99 of 101 schematic parts match exactly in value and connections,
  including the polarity of all 10 diodes and 9 electrolytics and the 6 off-board wire groups.
  The other two are R51 (two 100K in series on the board) and R48 (220K on the silkscreen).
  The board adds 9 supply bypass capacitors and the optional second C6 footprint.
- Lead spacings and outline sizes were measured on the gerbers.
- Not checked: every LCSC code one by one (C5207 LF353P and C57435 were confirmed), and the real body
  thickness of the film capacitors.

## Corrections to the older lists

- `design/BOM.pdf` is an older revision: R13/R14 = 5k1 (now 4k7), C14/C17 = 4.7 µF (now 2 × 10 µF each, back to back),
  R6 listed three times, and R1, R2, R52, R55, R56 missing. Do not use it.
- `parts/TGSL_PARTS1.xls`:
  - "R6 22K" is really R2, and its value is **24k** (schematic note "22k -> 24k"). 24k is needed twice (R2, R21).
  - R18 and R22 are counted as fixed 100k resistors and again as pots.
  - 6 sockets for 8-pin ICs are listed, but there are **7** DIP-8 ICs.
  - 330 Ω × 3 is listed; the schematic has 2 (R52, R55).
- `gerbers/BOM_try_04.md` (rev 1): see *Changes from rev 1* above.

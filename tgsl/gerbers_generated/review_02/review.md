# TGSL-Geotech-v3 gerbers, try 02: validation

- **Input (reference):** `tgsl/design/PCB.pdf`, plus `Placement OC.pdf` for silk, links and outline
- **Output (validated):** `tgsl/gerbers/try_02/`
- **Previous review:** `tgsl/gerbers/review_01/` (of `try_01`)
- **Date:** 2026-10-22

## Result

Try 02 fixes every issue raised in review 01. Copper, drills and solder mask are still an exact transfer of PCB.pdf.

It adds one regression: **all 21 decimal points were removed from the silkscreen**. "0.1" now prints as "01", "0.22" as "0 22", and so on. Fix this before ordering. Nothing electrical is affected.

## Status of review 01 issues

| Review 01 issue | Try 02 | Verdict |
|---|---|---|
| Outline was copper bbox + 0.5 mm (106.99 × 95.18 mm), too short | 107.42 × 98.98 mm rectangle: the bounding box of the contour drawn in Placement OC.pdf, widened 0.8 mm on the left | **Fixed.** Right, top and bottom edges match the drawn contour within 0.01 mm. The left edge was widened because copper reaches up to 0.55 mm past the drawn left line (see below). |
| Left 10.16 × 43.14 mm rectangle read as a notch | Kept as copper, not cut out | **Correct.** See "Left rectangle is copper, not a notch". |
| Layers not in a board coordinate system | All layers moved by the same (−0.200, +2.3195) mm. The outline's bottom-left corner is (0, 0). | **Fixed.** Copper, mask, drill, silk and outline are all consistent. |
| Silk clipped at the bottom edge ("-12V", two "0.1" labels, two 220 µF circles) | Restored | **Fixed.** All five items are present. Silk is now at least 1.36 mm inside the outline. |
| Drill sizes larger than the PDF hole marks | Kept at 0.8 / 1.0 / 1.3 mm, with reasons in README.txt | **Accepted.** The PDF marks (0.55 / 0.76 / 0.95 mm) are centring dots for hand drilling, not finished sizes. The chosen sizes are standard for these leads. Smallest annular ring is 0.36 mm. |
| 15 top-copper traces not in PCB.pdf | 13 wire links drawn as 14 segments (one link has two pieces). The zero-length piece is gone. README documents the single-sided option. | **Accepted.** All 14 segment ends sit exactly on pad centres. Each link joins two separate bottom-copper groups (97 groups → 84 nets). Smallest gap from a link to another pad is 1.42 mm. |
| Missing bottom silk and paste | Unchanged | Not needed. The board is all through-hole. |

## New issues

### 1. Decimal points missing from the silkscreen (regression)

Placement OC.pdf draws each decimal point as a zero-length stroke, which prints as a round dot because the PDF uses round line caps. Try 01 kept 19 of the 21 dots; the other 2 were clipped. Try 02 removed every zero-length silk draw, which deleted all 21 decimal points. The bundled `TGSL-Geotech-v3-preview.png` shows it, with labels reading "0 1", "0 022", "0 22" and "0 47".

On a capacitor value, "01" and "0 022" are easy to misread during assembly.

**Fix:** put the zero-length draws back in `F_SilkS` with the 0.15 mm aperture, or flash a 0.15–0.17 mm dot at each point. Remove zero-length draws only from copper. Dot positions, try 02 coordinates in mm:

(32.27, 89.15) (15.34, 71.84) (16.10, 67.44) (29.69, 59.10) (23.09, 44.58) (23.26, 34.25) (42.77, 14.90) (49.88, 9.99) (68.47, 12.23) (76.68, 65.49) (82.90, 65.49) (50.65, 66.55) (60.47, 35.14) (65.21, 51.82) (62.25, 27.60) (76.68, 56.94) (81.55, 33.10) (74.73, 28.02) (94.00, 24.13) (80.03, 1.61) (86.21, 1.44)

Their positions are accurate to about 0.04 mm (the error of the Placement OC.pdf mapping).

### 2. Copper is 0.30 mm from the left board edge (minor)

The 1.98 mm ground track along the left side reaches x = 0.30 mm. The border of the left copper block reaches 0.39 mm. Many fabs set their minimum copper-to-edge gap at about 0.2–0.3 mm, so 0.30 mm may get a DRC warning or a nicked edge. The copper here is ground, so a nick would not change the circuit.

**Optional:** move the left edge out another 0.5 mm (to x = −0.5), or shift everything right by 0.5 mm.

## Decisions for the owner (not defects)

- **Outline shape.** The contour in Placement OC.pdf is slightly skewed: the left edge is 93.90 mm tall, the right edge 98.98 mm. Try 02 uses the bounding rectangle instead. The drawn contour can't be used as-is, because PCB.pdf copper crosses it by up to 0.55 mm at the top-left and left. Compared with the drawn shape, the rectangle adds bare board in two thin triangles, up to 2.54 mm tall, at the top-left and bottom-left corners. Check that the rectangle fits the enclosure.
- **2-layer vs single-sided.** With 2 layers, the links are top-copper traces. A single-sided board needs 13 wire jumpers, and the 14 F_Cu segments are ignored. README.txt covers both options.

## Left rectangle is copper, not a notch

Review 01 (`open_issues_2.md`) reported a 10.16 × 43.14 mm notch in the left edge. Try 02 says it is copper. The evidence supports try 02:

- PCB.pdf has a filled copper area with exactly these corners, (0.78, 27.94)–(10.94, 71.08). Placement OC.pdf draws the same rectangle as an outline.
- That copper is part of the largest copper group on the board, together with the other two copper fills. The group has 47 pads and 205 track segments.
- A plated pad at (10.33, 42.38) lies inside the rectangle and has its own silk outline. Link J3 starts at that pad.
- Four bottom traces run into the rectangle and end there.

A cut-out there would remove a pad and cut ground connections.

## Minor (no action)

- **Silk over pads.** 636 silk strokes touch the top mask openings of 91 pads, by up to 1.44 mm. This is how the source draws it, and it is the same as try 01. Fabs clip silk from pad openings automatically.
- **Copper zero-length draws.** B_Cu still has the 2 harmless zero-length draws noted in review 01.
- **Close top pads.** On the top layer, four pad pairs are only 0.11–0.23 mm apart, for example (24.30, 33.49) and (24.28, 31.41). In each pair, both pads are on the same bottom-copper net, so a bridge would cause no fault. This is the PCB.pdf pad geometry and is unchanged from try 01.
- **Pad and mask sizes, copper-fill self-crossing:** same as review 01.

## What matched

| Layer | Check | Result |
|---|---|---|
| `B_Cu` | Pads | 346 / 346, position error ≤ 0.000013 mm |
| `B_Cu` | Trace segments | 686 / 686, endpoint error ≤ 0.000017 mm, widths exact |
| `B_Cu` | Copper fills | 3 / 3, vertex error ≤ 0.000012 mm |
| `B_Cu` | Pixel overlay vs PCB.pdf at 1200 dpi | No difference wider than 0.085 mm (edge anti-aliasing only) |
| `B_Cu` | Connectivity / clearance | 97 copper groups; smallest gap between different groups 0.54 mm |
| `F_Cu` | Pads | Same 346 as B_Cu |
| `F_Cu` | Links | 14 segments, 0.6 mm wide, all ends on pad centres; 84 nets on the finished board |
| `PTH.drl` | Holes | 346 / 346 on pad centres, error ≤ 0.0006 mm. 0.8 mm × 273, 1.0 mm × 67, 1.3 mm × 6. Smallest hole-to-hole gap 1.16 mm |
| `F_Mask` / `B_Mask` | Openings | 346 / 346, pad + 0.1 mm (the 61 smaller pads get +0.058 mm) |
| `F_SilkS` | vs Placement OC.pdf | Every gerber stroke within 0.045 mm of a PDF stroke. Every PDF silk stroke is covered, except the 21 decimal points. |
| `Edge_Cuts` | Outline | Closed 107.420 × 98.975 mm rectangle. Copper margins: left 0.30, right 1.13, bottom 2.82, top 1.97 mm |
| All | Format | mm, 4.6 format, X2 `FileFunction` set on every layer, copper positive, mask negative. Each file ends with M02, the drill file with M30. |

## Not checked

- The board against the schematic. README.txt says IC power, ground and the main signal paths were checked against Schematic.pdf; this review did not repeat that.
- `TGSL-Geotech-v3-preview.png` was only viewed, not compared.

## Method

1. Fitted PCB.pdf pads to the try 02 B_Cu pads. The PDF unit is 1/600 in, and the board is mirrored in X:
   - x_mm = 160.4639 − u × 0.042333
   - y_mm = u × 0.042333 − 99.5116

   This is the review 01 mapping shifted by (−0.2, +2.3195) mm.
2. Placement OC.pdf is not mirrored: x_mm = u × 0.042333 − 49.2601, y_mm = u × 0.042333 − 99.5116.
3. Matched every pad, trace, fill, mask opening and drill hit to PCB.pdf. Matched silk stroke-by-stroke to Placement OC.pdf in both directions.
4. Rendered PCB.pdf at 1200 dpi with poppler and compared it pixel by pixel with the rasterised B_Cu.
5. Built copper connectivity on both layers, joined through the plated holes, to count nets and measure clearances.
6. Diffed try 02 against try 01 file by file. B_Cu, the masks and the drill file are try 01 moved by (−0.200, +2.3195) mm. F_Cu lost one zero-length segment. F_SilkS lost 28 zero-length draws (the decimal points among them) and gained the restored bottom-edge items.

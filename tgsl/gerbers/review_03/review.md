# TGSL-Geotech-v3 gerbers, try 03: validation before ordering

- **Input (reference):** `tgsl/design/PCB.pdf`. Also used: `Placement OC.pdf` for silk, links and contour, and `Placement.pdf` for an independent orientation check.
- **Output (validated):** `tgsl/gerbers/try_03/`
- **Previous review:** `tgsl/gerbers/review_02/` (of `try_02`)
- **Date:** 2026-10-22
- **Re-run:** `tools/run_all.sh try_03 try_02` (see `tools/README.md`)

## Result

Try 03 fixes both review 02 issues. Copper, hole positions, solder mask, wire links and silkscreen are an exact transfer of the source PDFs. The mirror is correct.

**Fix one thing before ordering: hole sizes.** Five holes are too small for the parts that go in them (issue 1). After that the package is ready. Issue 2 is optional. Everything else is cosmetic or a decision you already made.

## What changed since try 02

Compared file by file, after removing the 0.5 mm shift:

- Copper, masks, drill and silk all moved +0.5 mm in X. Nothing else changed on those layers.
- The outline's left edge stayed at x = 0 and the right edge moved +0.5 mm. The board is now **107.92 × 98.975 mm** (was 107.42).
- F_SilkS gained 23 dots, flashed with a 0.2 mm aperture. Nothing was removed.

## Status of review 02 issues

| Review 02 issue | Try 03 | Verdict |
|---|---|---|
| 21 decimal points missing from silk | 23 dots of 0.2 mm added | **Fixed.** All 21 decimal points in Placement OC.pdf are present, each within 0.005 mm. The 2 extra dots are harmless (see Minor). |
| Copper 0.30 mm from the left edge | Board widened by 0.5 mm, artwork moved right | **Fixed.** Closest copper to the edge is now 0.800 mm (left). Right 1.126, bottom 2.820, top 1.974 mm. |

## Fix before ordering

### 1. Holes too small for the BD140 and the 1000 µF capacitor

The converter set each drill size from the size of PCB.pdf's drill-guide dot. Those dots are centring marks for hand drilling, not hole sizes. For these parts the designer used the smallest dot, so they got 0.8 mm holes. Drill sizes in the file are finished, plated sizes.

| Part | Holes (try 03 mm) | Drill | Pad | Lead | Change to |
|---|---|---|---|---|---|
| BD140 (TO-126), top right, silk "B C E" | (92.02, 78.38) (94.56, 78.38) (97.10, 78.38) | 0.8 | 1.566 | flat, about 0.75 × 0.5 mm (≈ 0.9 mm diagonal) | **1.0 mm** (ring 0.283) or 1.1 mm (ring 0.233) |
| 1000 µF electrolytic, 7.6 mm lead spacing | (91.56, 62.99) (99.16, 62.99) | 0.8 | 1.990 / 1.947 | Caps made for 7.5 mm spacing (16–18 mm diameter) usually have 0.8 mm leads | **1.0 mm** (ring 0.47–0.50) |

As drilled, the BD140 legs won't go in, and neither will a 0.8 mm-lead capacitor. Enlarging these five holes costs nothing: the annular ring stays well above the usual fab minimum of about 0.15 mm. This also makes the drill file match its README, which says transistors and larger capacitors get 1.0 mm.

Checked and fine at 0.8 mm: the four 220 µF capacitors (5 mm spacing, 0.5–0.6 mm leads), the 10 µF capacitors, DIP ICs, resistors, 1N4148 diodes and TO-92 transistors. The TO-92 transistors already have 1.0 mm holes. `drill_sizes.png` shows every hole colour-coded by size.

## Optional

### 2. 7808 regulator holes are snug

The three 7808 (TO-220) holes at (81.06, 13.82), (83.60, 13.82) and (86.14, 13.82) are 1.0 mm, with 1.736 mm pads. TO-220 legs are about 0.8 × 0.5 mm (≈ 0.94 mm diagonal), so they fit, but tightly given fab hole tolerance (about ±0.08 mm). 1.1 mm (ring 0.318) or 1.2 mm (ring 0.268) is more comfortable.

### 3. Four same-net top pad pairs are very close

On F_Cu, four pad pairs are closer than most fabs' standard minimum spacing (about 0.10–0.127 mm):

| Gap | Pads |
|---|---|
| 0.106 mm | (24.78, 31.41) / (24.80, 33.49) |
| 0.113 mm | (17.79, 31.41) / (15.76, 31.75) |
| 0.212 mm | (67.28, 20.96) / (67.32, 23.03) |
| 0.233 mm | (59.68, 20.96) / (59.70, 23.03) |

Each pair is already joined by bottom copper, so a bridge on top can't cause a fault. The solder-mask web between the first two pairs is 0.006 and 0.013 mm, which is too thin to make, so the fab will merge those openings. This is how PCB.pdf draws the pads.

The fab can't tell these pads are on the same net, so it may send an engineering query. Either answer it ("same net, OK to bridge"), or add a short F_Cu trace joining each pair, which removes the gap and the mask sliver.

## Minor (no action needed)

- **2 extra silk dots** at (53.18, 61.21) and (85.14, 49.32). Each sits on the start point of a red circle in Placement OC.pdf: a capacitor outline and a circle near the 10K trimmer. The PDF begins those curves with a repeated point, which the converter read as a dot. A 0.2 mm dot on a 0.15 mm line won't be visible.
- **Self-crossing copper fill.** The top-left fill outline (15 vertices) crosses itself once at (15.05, 89.79). The PDF draws it that way. The two small twisted pieces (0.29 and 0.04 mm²) are fully covered by the fill's own border trace, so the copper is identical whatever fill rule the fab's software uses. Optional cleanup: split the outline at the crossing.
- **2 zero-length copper draws** on B_Cu, at (1.92, 71.54) and (14.79, 87.55). Both sit on existing copper (path-closing leftovers from the PDF).
- **61 pads are 0.042 mm smaller on one axis.** PCB.pdf draws them 1 unit (1/600 in) wider in X than in Y, or the reverse, and the gerber uses one of the two. This is below fab tolerance.
- **Silk line width 0.15 mm**, which is at the minimum most low-cost fabs list. The source pen is 0.168 mm. Text is about 1.3 mm tall, which is fine. A wider line (0.17 mm) would print more reliably, but it's cosmetic.
- **Silk over pads.** Silk touches 91 of the 346 top pad openings (26.8 mm², about 4% of the silk). The fab trims it, so parts of the "BD140" and "7808" labels, which are drawn across their pads, won't print. Same as try 02.
- **opencode review of try 02, "6 square pin-1 pads became round":** this is a false positive. Its script calls a pad "square" when the bounding box is 70×70 units. In PCB.pdf those 6 pads are circles drawn with 4 Bézier curves. PCB.pdf has no square pads. See `tools/opencode/NOTE.md`.

## Decisions for the owner (not defects)

- **Board size and outline.** The outline is a 107.92 × 98.975 mm rectangle. The contour drawn in Placement OC.pdf is a slightly skewed 106.6 × 99.0 mm shape: right edge at x = 107.916, left edge at x = 1.32. It lies fully inside the rectangle, which adds 402 mm² of bare board: a 1.32 mm strip on the left plus two thin triangles. The drawn line can't be the cut line, because PCB.pdf copper goes up to 0.554 mm past it on the left and top-left. Check that 107.9 mm fits your enclosure. Note that many fabs' cheapest price tier is for boards up to 100 × 100 mm. This board is over that even with the drawn contour.
- **2-layer vs single-sided.** Same as before. The 13 wire links are F_Cu traces on a 2-layer board, and README.txt covers etching it single-sided.
- **No mounting holes.** PCB.pdf has none, so none were added.

## Orientation (mirror) check

PCB.pdf is drawn as seen from the solder side, so the gerber mirrors it. A wrong mirror would put every IC pin in the wrong place, and comparing copper to PCB.pdf alone can't catch it. Placement.pdf is the designer's component-side view, with the copper, parts and links drawn together. Its 346 pads match try 03 **without** mirroring, all within 0.017 mm. With mirroring, none match. All 689 copper strokes in Placement.pdf also land on B_Cu within 0.08 mm. **The orientation is correct.**

## What matched

| Layer | Check | Result |
|---|---|---|
| Transform | PCB.pdf → gerber | x = 160.963929 − u·0.0423333, y = u·0.0423333 − 99.511562 (mirrored, 1/600 in). Pad fit error ≤ 0.000013 mm, no scale or shear error. |
| `B_Cu` | Pads | 346 / 346, position error ≤ 0.000013 mm |
| `B_Cu` | Tracks | 686 / 686 plus 27 / 27 fill-border edges. Endpoint error ≤ 0.000017 mm, widths exact (0.7925 / 1.9812 / 2.9718 mm). Only extras: the 2 zero-length draws. PCB.pdf draws one track twice, and it is matched. |
| `B_Cu` | Copper fills | 3 / 3, vertex error ≤ 0.000012 mm. The left 10 × 43 mm block is copper, as in try 02. |
| `B_Cu` | Pixel comparison with PCB.pdf (poppler, 1200 dpi, B_Cu drawn from gerbonara's parse) | No difference thicker than 0.060 mm anywhere (edge smoothing and PCB.pdf's 0.042 mm pad outline). Every drill-guide dot lies inside copper. |
| `B_Cu` + `F_Cu` | Connectivity | 97 bottom-copper islands, all with pads. 84 nets after the links. Smallest bottom gap between different islands 0.542 mm. |
| `F_Cu` | Pads | The same 346 pads |
| `F_Cu` | Wire links | 13 links drawn as 14 traces of 0.6 mm. Every end is on a pad centre; link 7 is in two pieces whose joint lies inside its end pad. Each link joins two different bottom islands. Clearance to other pads ≥ 1.12 mm. All 15 red link strokes in Placement OC.pdf are covered. |
| `PTH.drl` | Holes | 346 / 346 on pad centres, error ≤ 0.0006 mm. 0.8 mm × 273, 1.0 mm × 67, 1.3 mm × 6. Smallest annular ring 0.362 mm. Smallest hole-to-hole wall 1.16 mm. Smallest hole to board edge 2.38 mm. |
| `F_Mask` / `B_Mask` | Openings | 346 / 346, pad + 0.1 mm everywhere. No opening exposes copper of another island. |
| `F_SilkS` | vs Placement OC.pdf | Two-way: every gerber silk item is within 0.045 mm of a PDF stroke, and every PDF stroke is covered within 0.045 mm (large circles are drawn as chords). 19 / 19 filled shapes, vertex error ≤ 0.005 mm. 21 / 21 decimal points. |
| `Edge_Cuts` | Outline | Closed 107.920 × 98.975 mm rectangle, corner at (0, 0) |
| All | Format | gerbonara reads every file with no warnings and detects all layers on its own: top/bottom copper, top/bottom mask, top silk, outline, one drill file. mm, 4.6 format, X2 `FileFunction`/`FilePolarity` on every layer (masks Negative). Gerbers end with M02, the drill file with M30. |

## Cross-check with opencode's scripts

The scripts opencode used for its try 02 review (copied to `tools/opencode/`) were patched to try_03 and run. They agree: pads exact, 713 / 713 segments, 3 / 3 fills, 97 islands, 84 nets. In their raster comparison, the only gerber-only spots are the 346 drill-guide dots.

## Ordering notes

- Upload a zip of the 7 fab files only (`*.gbl *.gtl *.gbs *.gts *.gto *.gm1 *.drl`). Leave out `README.txt` and the preview PNG.
- Settings from README.txt: 2 layers, 1.6 mm FR4, HASL. All holes are plated.

## Not checked

- The board against the schematic. Schematic.pdf has no text layer, so no netlist could be extracted. The links come from the designer's own placement drawings, and both placement PDFs agree with the gerber.
- Fit of the parts' bodies on the board (only hole sizes were checked).

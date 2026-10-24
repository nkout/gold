# TGSL-Geotech-v3 gerbers try_02: validation against PCB.pdf

- **Input (source of truth):** `design/PCB.pdf` (solder-side copper artwork, vector, 1/600-inch units)
- **Secondary sources:** `design/Placement OC.pdf` (outline, wire links, silk), `design/Placement.pdf`
- **Output (validated):** `gerbers/try_02/`
- **Date:** 2026-10-22
- **Review mode:** read-only. No source files modified.

## Verdict

**Faithful transfer. Safe to fabricate.** Two minor, non-blocking notes at the end.

## Method

1. Decoded the vector content stream of PCB.pdf (units 1/600 inch, no raster images, single stream).
2. Parsed all try_02 gerber layers and the Excellon drill file.
3. Fitted the exact affine map PDF → gerber: scale = 25.4/600 mm per unit, X mirrored (PCB.pdf is the solder-side view, gerbers are top view). Residual pad position error < 1 µm.
4. Matched every pad, track segment, copper pour, drill hole, mask opening and wire link one by one.
5. Independent check: rasterised `B_Cu` at 600 dpi and compared pixel by pixel against a poppler render of PCB.pdf in the same frame.
6. Copper islands / net count / minimum clearance / copper-to-edge from a 0.025 mm/px raster.
7. Silkscreen compared against the red layer of Placement OC.pdf rendered at 300 dpi.

## What matched PCB.pdf (all exact)

| Gerber layer | Check | Result |
|---|---|---|
| `B_Cu.gbl` | Pads | 346 / 346, position error < 1 µm, diameters exact |
| `F_Cu.gtl` | Pads | Same 346 pads (plated through-holes) |
| `B_Cu.gbl` | Track segments | All 713 PDF segments found, widths exact: 0.7925 / 1.9812 / 2.9718 mm |
| `B_Cu.gbl` | Copper pours + borders | 3 / 3, vertex-exact |
| `B_Cu.gbl` | Pixel overlay at 600 dpi | PDF-only pixels: 11 (edge anti-alias noise). Gerber-only: exactly 346 clusters — one per pad, the white drill-guide dots of PCB.pdf correctly solidified into copper |
| `PTH.drl` | Hole positions | 346 / 346 on pad centres, error ≤ 0.6 µm |
| `PTH.drl` | Hole sizes | 0.8 mm × 273, 1.0 mm × 67, 1.3 mm × 6; min annular ring 0.362 mm |
| `F_Mask` / `B_Mask` | Openings | 346 / 346 each side, exact positions, pad + 0.1 mm uniform |
| `F_Cu.gtl` | Wire links | 13 links = 14 draws; all match the red wire links of Placement OC.pdf, ends on pad centres |
| `B_Cu.gbl` | Copper islands | 97 islands → 84 nets after links (README claims confirmed) |
| `B_Cu.gbl` | Min clearance | 0.55 mm between separate copper (README says 0.54) |
| `Edge_Cuts` | Copper-to-edge | left 0.283, right 1.14, top 1.87, bottom 2.93 mm — all positive |
| `F_SilkS.gto` | vs Placement OC red layer | 97.2 % match after 0.1 mm registration refinement — faithful copy; the only large "missing" clusters are the wire links themselves (correctly placed on F_Cu, not on silk) |

### Track detail

The single gerber draw with no distinct PDF counterpart at (86.13, 50.29) is a segment that **PCB.pdf itself draws twice** (both directions); the gerber copies both faithfully. Zero-length draws (2) are path-closing artifacts from the PDF, harmless no-ops.

### Drill size note

PCB.pdf has only drill-guide dots (0.55 / 0.75 / 0.95 mm), centring marks for hand drilling, not finished sizes. The 0.8 / 1.0 / 1.3 mm choice for component leads is intentional and documented in the try_02 README — a design decision, not a transfer error.

## Review_01 open issue #1 (the left-edge "notch") — resolved: try_02 is correct

`Placement OC.pdf` (and `Placement.pdf`) draw a 10.16 × 43.14 mm rectangle stepping in from the left board edge. open_issues_2 read it as a cut-out and called try_01's rectangular outline a critical defect. **It is not a cut-out.** Evidence:

- PCB.pdf has a **solid copper fill of exactly that size** (10.16 × 43.14 mm) at exactly that place (mirror-verified against the common print frame).
- **One drilled pad — the end of a wire link — sits inside the zone** at gerber mm (10.33, 42.38). A drilled, soldered pad cannot hang in air.
- 18 track segments connect the zone to the main copper network.
- The placement outline's left edge line runs **continuous** through the marked rectangle; a real notch would replace the edge segment, not coexist with it. The rectangle is an overlay annotation (screen-plate / pour-boundary mark), not an edge modification.

`Edge_Cuts.gm1` as the bounding rectangle 107.420 × 98.975 mm (trapezoid 106.6 × 99.0 drawn, +0.8 mm on the left so the pour border stroke keeps ≥ 0.28 mm inside the edge) is correct and consistent with the README.

## Minor notes (non-blocking)

1. **6 square pin-1 pads became round Ø 2.963 mm flashes.** The circle is inscribed in the original 2.963 mm square: ~21 % less copper at the corners, annular ring still 0.83 mm against the 1.3 mm drill. Cosmetic; fix only if pin-1 square identification matters.
2. **Silkscreen overlaps copper pads on ~60 pads (≈ 23 mm² total).** Most fabs clip silk over pads automatically; harmless for hand soldering.
3. Silk layer registration vs copper differs by ~0.1 mm from the outline-corner math — the converter registered the red layer independently; geometry itself is faithful.

## Not checked

- The board against the schematic (netlist). PCB.pdf was treated as correct; try_02 README claims 15/15 IC power/ground and main signal paths verified separately.

## Reproduction

Analysis scripts (rerunnable for a future try_03): `/tmp/opencode/gerbcheck/` —
`parse_pdf.py`, `parse_poc.py`, `parse_gerber.py`, `extract_pcb.py`, `compare_pads.py`,
`compare_tracks.py`, `raster_diff.py`, `check_space.py`, plus rendered diff images
(`diff_bcu.png`, `diff_parser.png`). Note: /tmp is volatile; copy these into the repo if they should persist.

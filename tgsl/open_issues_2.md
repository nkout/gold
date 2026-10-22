# TGSL-Geotech-v3 gerber review

Source artwork: `tgsl/TGSL - complete details - version 3.0.zip`
Gerber package: `tgsl/TGSL-Geotech-v3-gerbers.zip`
Review date: 2026-10-22
Review mode: read-only. No source files modified.

## Verdict

**Not a fully correct transfer. Do not fabricate as-is.**

The copper artwork, pad/hole positions, silkscreen and solder mask are faithful to the
source PDFs. The board outline is wrong, the drill sizes were enlarged, and the top
copper layer contains 15 traces that do not exist in the source artwork.

## What matches

| Item | Evidence |
|---|---|
| Bottom copper (`B_Cu`) | Rendered gerber vs `PCB.pdf` artwork, mirrored: IoU 0.9009 (direct comparison 0.249). Difference is ~1 px edge/antialias fringe only. Mirroring is correct: `PCB.pdf` is the bottom view, `Placement.pdf` is the top view. |
| Pad positions | 346 flashes on F_Cu and 346 on B_Cu, identical coordinates. |
| Drill positions | 346 drill hits. Every drill center matches a pad center (max error 0.27 µm). Complete hole set: 347 enclosed white regions in the source = 346 holes + 1 pour void. |
| Top silkscreen | `F_SilkS` matches the placement silk. Bounding boxes 97.37 × 91.86 mm (gerber) vs 97.20 × 92.54 mm (source red layer). Same orientation. |
| Solder mask | 346 openings on each side, pad diameter +0.1 mm. F and B mask files are identical except the `FileFunction` attribute. Correct for an all-through-hole board. |
| Gerber format | Millimetres, 4.6 format, X2 `FileFunction` attributes, copper positive, mask negative. Valid. |

## Defects

### 1. `Edge_Cuts` is wrong — critical

- Gerber outline: plain rectangle **106.994 × 95.181 mm**, located at the copper
  bounding box (`106.00 × 94.23 mm`) plus approximately 1 mm.
- Actual board contour in `Placement OC.pdf`: **106.60 × 98.97 mm**, with:
  - a **10.16 × 43.14 mm notch** in the left edge;
  - a trapezoid: right edge 98.97 mm, left edge 93.90 mm (5.08 mm difference).
- The gerber therefore:
  - omits the notch;
  - is **3.8 mm too short**;
  - uses a straight rectangle instead of the trapezoidal outline.
- Root cause: the drill file header states
  `; TGSL Geotech v3 - converted from PCB.pdf`. `PCB.pdf` contains only copper
  artwork, no board outline. The outline exists in `Placement OC.pdf` and was not used.
- The thin 129.9 × 119.9 mm rectangle in the PDFs is the print/page border, not the
  board edge. Even if it were treated as the board edge, 107 × 95.2 mm would still be
  wrong.

**Fix:** redraw `Edge_Cuts` from the thick notched contour in `Placement OC.pdf`.
Reconcile the coordinate origin: the current origin is copper-bbox + 0.5 mm, not the
board origin. Copper, mask, silk and drill coordinates must be shifted together to the
board coordinate system.

### 2. Drill sizes are enlarged relative to the source

- Drill tools: 0.8 mm (273 hits), 1.0 mm (67 hits), 1.3 mm (6 hits).
- Hole diameters drawn in the PDF: approximately **0.55 / 0.75 / 0.9 mm**.
- Drills are **0.25–0.4 mm larger** than the source artwork.
- Positions are correct; sizes are a design decision, not a transfer.

**Fix:** verify drill sizes against component lead diameters. If reproducing the source,
use approximately 0.6 / 0.8 / 1.0 mm, or document why the larger sizes were chosen.

### 3. `F_Cu` contains 15 traces that are not in the source

- `F_Cu` consists of 346 pads plus 15 short 0.6 mm-wide segments.
- Only about 30% of those segment lengths lie on black artwork — the same as a random
  3 mm shift. They are not traced from `PCB.pdf`.
- All segment endpoints are pad centres, and the pad pairs are on **different copper
  islands** in the source artwork.
- They are either undocumented netlist repairs or errors.

**Fix:** remove the 15 segments, or verify each connection against `Schematic.pdf` and
document the intent. Do not ship them as part of a "transfer from the picture".

### 4. Missing bottom silk / paste

Not a defect for this board: all components are through-hole and mounted on the top side,
so `B_SilkS` and paste layers are not required. Add them only if bottom-side parts are
intended.

## Recommended actions before fabrication

1. Replace `Edge_Cuts` with the notched outline from `Placement OC.pdf`.
2. Shift all layers into the board coordinate system and re-check copper-to-edge clearance.
3. Confirm or correct the three drill sizes.
4. Review or remove the 15 `F_Cu` segments against the schematic.
5. Re-run a gerber visual diff against `PCB.pdf` and `Placement.pdf` after the fixes.

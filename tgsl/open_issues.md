# TGSL-Geotech-v3 gerbers: validation against PCB.pdf

- **Input (reference):** `PCB.pdf` from `TGSL - complete details - version 3.0.zip`
- **Output (validated):** `TGSL-Geotech-v3-gerbers.zip`
- **Date:** 2026-10-22

## Result

Bottom copper, drill holes and solder mask are a correct transfer of PCB.pdf.

The output also has three things that PCB.pdf does not define:
- the board outline,
- 15 top-copper traces,
- the silkscreen.

These are the open issues below.

## Open issues

### 1. Board outline is not defined by PCB.pdf

PCB.pdf has no board outline. Its only non-copper item is a thin print frame (129.9 × 119.9 mm). The output correctly leaves that frame out.

`Edge_Cuts.gm1` is a rectangle of 106.99 × 95.18 mm. It equals the copper extents plus a 0.5 mm margin, so the converter chose it rather than taking it from the input.

**To decide:** confirm the real board size and shape.

For reference, the other drawings in the same zip (Placement.pdf, Placement OC.pdf) show a slightly skewed outline. Its right side is 5 mm taller than its left. Corners in gerber coordinates (mm):

| Corner | Placement.pdf outline | Gerber outline |
|---|---|---|
| top-left | (1.0, 94.1) | (0, 95.18) |
| top-right | (107.6, 96.7) | (106.99, 95.18) |
| bottom-right | (107.6, −2.3) | (106.99, 0) |
| bottom-left | (1.0, 0.2) | (0, 0) |

### 2. Top copper has 15 traces that are not in PCB.pdf

`F_Cu.gtl` has 15 traces, 0.6 mm wide. They match the red wire links drawn in Placement OC.pdf:
- Each trace joins the same two pads as its wire link, with ends snapped to the pad centres.
- Each stays at least 1.4 mm from any other pad, and no traces cross, so they create no shorts.
- Two of the links are drawn as two-piece lines. The gerber keeps that shape, including one zero-length piece, which is harmless.

Some form of these connections is required. 13 of them join copper groups that are otherwise separate (97 groups on the bottom layer, 84 nets with the links).

**To decide:** should the links be top-layer traces (this needs a 2-layer board) or wire jumpers, as in the original design?

### 3. Silkscreen is not in PCB.pdf, and is clipped at the bottom edge

`F_SilkS.gto` comes from Placement OC.pdf. It matches that drawing to within 0.05 mm, with line width set to 0.15 mm.

Silk below about y = 0.3 mm was dropped, because the rectangular outline (issue 1) sits higher than the drawn outline at the bottom right. No copper is affected. Lost items (gerber coordinates, mm):

| Item | Location |
|---|---|
| "-12V" label, including the minus sign | x 65.4–69.6, y −0.7 to 0.6 |
| "0.1" label under the 7808 | x 79.0–81.1 |
| "0.1" label under the 7808 | x 85.3–87.3 |
| Bottom of the 220 µF capacitor circle | centre (73.4, 4.6), Ø 10 mm |
| Bottom of the 220 µF capacitor circle | centre (92.9, 4.5), Ø 10 mm |

**Fix once issue 1 is settled:** lower the bottom edge by about 2 mm (or use the drawn outline) and regenerate the silkscreen without clipping.

## Minor differences (no action needed)

- **Pad size:** 61 of the 346 pads are 0.04 mm smaller than in the PDF. The PDF draws them slightly oval (e.g. 41 × 42 units of 1/600 in), and the converter used the horizontal size.
- **Drill sizes:** PCB.pdf has only small hole marks, so the sizes are inferred from the mark size:
  - 13–14 units → 0.8 mm (273 holes)
  - 18 units → 1.0 mm (67 holes)
  - 22–23 units → 1.3 mm (6 holes)

  This puts 1.0 mm on the 7808, transistors and jumper ends, and 1.3 mm on the trimmer pot. Smallest annular ring is 0.36 mm.
- **Copper fill border:** one copper-fill border near (14.5–14.8, 85.2–87.8) mm crosses itself. This is copied from PCB.pdf. The sliver is under 0.3 mm wide and fully covered by the 0.79 mm border line.
- **Zero-length draws:** two zero-length draws sit at the start points of copper-fill borders, from the PDF's path-closing command. They are harmless.
- **Solder mask:** one opening per pad, 0.1 mm larger than the pad (about 0.06 mm larger on the 61 smaller pads).

## What matched PCB.pdf

| Gerber layer | Check | Result |
|---|---|---|
| `B_Cu.gbl` | Pads | 346 / 346, position error ≤ 0.00002 mm |
| `B_Cu.gbl` | Trace segments | 686 / 686, widths exact: 0.7925 / 1.9812 / 2.9718 mm |
| `B_Cu.gbl` | Copper-fill areas and their borders | 3 / 3, vertex error ≤ 0.00002 mm |
| `B_Cu.gbl` | Pixel overlay at 1200 dpi | no differences wider than 0.085 mm (edge anti-aliasing only) |
| `B_Cu.gbl` | Orientation / scale | mirrored correctly (PCB.pdf is the copper-side view, the gerber is the top view); 1:1 scale (IC pins 2.54 mm apart) |
| `F_Cu.gtl` | Pads | same 346 pads as bottom (plated through-holes) |
| `PTH.drl` | Hole positions | 346 / 346 on pad centres, error ≤ 0.0006 mm |
| `F_Mask` / `B_Mask` | Openings | 346 / 346 |

Bottom copper clearance: the smallest gap between separate copper is 0.54 mm, which any PCB maker can handle.

## Not checked

- The board against the schematic (netlist). PCB.pdf was treated as correct.

## Method

1. Decoded the vector drawing commands in PCB.pdf. Units are 1/600 inch; there are no raster images.
2. Parsed the gerber and drill files.
3. Mapped PDF units to gerber mm:
   - x_mm = 160.6639 − u × 0.042333
   - y_mm = u × 0.042333 − 101.8311
4. Matched every pad, trace segment and filled area one by one.
5. As an independent check, rendered PCB.pdf with poppler at 1200 dpi and compared it pixel by pixel against the rasterised `B_Cu` layer.

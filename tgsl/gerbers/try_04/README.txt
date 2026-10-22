TGSL Geotech v3.0 - Gerber package, try 04 (2026-10-22)
Source: "TGSL - complete details - version 3.0.zip" (Geotech forum), files PCB.pdf, Placement.pdf, Placement OC.pdf, Schematic.pdf

Order as: 2 layers, 1.6 mm FR4, HASL, any colour. Upload only the 7 fab files (*.gbl *.gtl *.gbs *.gts *.gto *.gm1 *.drl).

Changes from try 03 (from review_03): hole sizes only. All gerber layers are byte-identical to try 03.
- BD140 (TO-126), 3 holes: 0.8 -> 1.1 mm. Its flat legs (about 0.75 x 0.5 mm) did not fit 0.8 mm.
- 1000 uF capacitor (7.5 mm lead spacing), 2 holes: 0.8 -> 1.0 mm. These capacitors usually have 0.8 mm leads.
- 7808 (TO-220), 3 holes: 1.0 -> 1.1 mm. 1.0 mm fitted but was tight.

Layers
- B_Cu: copper of PCB.pdf, vector-exact (346 pads, 686 track segments, 3 copper fills), mirrored to top view.
- F_Cu: the same 346 pads (plated through-holes) + 13 wire links from Placement OC.pdf drawn as 0.6 mm traces.
  The original single-sided design uses wire jumpers here. Each link joins two copper islands that are separate
  on the bottom layer (97 islands -> 84 nets). If you etch single-sided, ignore F_Cu and fit wire jumpers.
- F_SilkS: Placement OC.pdf (component outlines and values), 0.15 mm lines.
  Decimal points (e.g. "0.1", "0.022") are drawn in Placement OC.pdf as zero-length strokes; they are
  emitted here as 0.2 mm flashes so every fab and viewer prints them.
- F_Mask / B_Mask: one opening per pad, pad + 0.1 mm.
- Edge_Cuts: 107.92 x 98.975 mm rectangle. It encloses the board contour drawn in Placement OC.pdf (106.6 x 99.0 mm drawn, slightly skewed),
  widened on the left so all copper stays at least 0.8 mm inside the edge.
  The 10 x 43 mm rectangle on the left edge of Placement OC.pdf is NOT a cut-out: PCB.pdf has a solid copper fill
  of exactly that size in the same place.
- PTH.drl: hole positions are the pad centres of PCB.pdf. PCB.pdf only has small drill-guide dots (0.55/0.59/0.76/0.93/0.97 mm),
  which are centring marks for hand drilling, not finished hole sizes. Finished (plated) hole sizes:
  0.8 mm (268: resistors, diodes, ICs, small capacitors, the four 220 uF capacitors),
  1.0 mm (66: TO-92 transistors, the 1000 uF capacitor, and the other pads PCB.pdf marks with its larger 0.76 mm dot),
  1.1 mm (6: BD140 and 7808 flat leads),
  1.3 mm (6: 100K pot and 10K trimmer).
  Minimum annular ring 0.23 mm (BD140 pads).
- TGSL-Geotech-v3-preview.png: unchanged from try 03 (it does not show hole sizes).

Checks done: tools/run_all.sh try_04 try_03 (see tools/README.md and review_03/review.md).
Bottom copper identical to PCB.pdf (pads, tracks, fills, 1200 dpi raster check); orientation confirmed against Placement.pdf;
97 copper islands -> 84 nets; min copper clearance 0.54 mm on the bottom layer.
On the top layer four same-net pad pairs are 0.11-0.23 mm apart (joined on the bottom; a bridge is harmless).

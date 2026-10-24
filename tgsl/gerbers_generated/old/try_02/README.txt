TGSL Geotech v3.0 - Gerber package (generated 2026-10-22)
Source: "TGSL - complete details - version 3.0.zip" (Geotech forum), files PCB.pdf, Placement.pdf, Placement OC.pdf, Schematic.pdf

Order as: 2 layers, 1.6 mm FR4, HASL, any colour.

Layers
- B_Cu: copper of PCB.pdf, vector-exact (346 pads, 686 track segments, 3 copper fills), mirrored to top view.
- F_Cu: the same 346 pads (plated through-holes) + 13 wire links from Placement OC.pdf drawn as 0.6 mm traces.
  The original single-sided design uses wire jumpers here. Each link joins two copper islands that are separate
  on the bottom layer (97 islands -> 84 nets). If you etch single-sided, ignore F_Cu and fit wire jumpers.
- F_SilkS: Placement OC.pdf (component outlines and values), 0.15 mm lines.
- F_Mask / B_Mask: one opening per pad, pad + 0.1 mm.
- Edge_Cuts: bounding rectangle of the board contour drawn in Placement OC.pdf (106.6 x 99.0 mm drawn, slightly skewed),
  widened by 0.8 mm on the left so the copper fill stroke stays 0.3 mm inside the edge.
  The 10 x 43 mm rectangle on the left edge of Placement OC.pdf is NOT a cut-out: PCB.pdf has a solid copper fill
  of exactly that size in the same place.
- PTH.drl: hole positions are the pad centres of PCB.pdf. PCB.pdf only has small drill-guide dots (0.55/0.75/0.95 mm),
  which are centring marks for hand drilling, not finished hole sizes. Drill sizes chosen for the component leads:
  0.8 mm (273: resistors, diodes, ICs, small caps), 1.0 mm (67: transistors, 7808, larger caps, link ends),
  1.3 mm (6: large pads, trimmer/pot and wire connections). Minimum annular ring 0.36 mm.

Checks done: bottom copper identical to PCB.pdf (97 copper islands, same partition, independent raster check);
IC power/ground and main signal paths checked against Schematic.pdf (15/15 OK); min copper clearance 0.54 mm.

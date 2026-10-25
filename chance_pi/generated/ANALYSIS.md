# chance_pi PCB Verification Analysis

**Date:** 2026-10-25
**Question:** Is the `chance_pi` generated PCB the same as the original?
**Answer:** **Yes — electrically identical.** All copper tracks, pads, and drills match the
original Sprint-Layout source geometry exactly (within 0.1 µm). Every intentional deviation is
exactly what the generated READMEs claim; zero undocumented deviations were found.

---

## 1. Scope and inputs

| Role | File | Format |
|---|---|---|
| Original main board | `original/Chance layout from DesAlex.lay` | Abacom Sprint-Layout 5 (binary) |
| Original keyboard | `original/keyboard.lay6` | Abacom Sprint-Layout 6 (binary) |
| Generated main board | `generated/ChancePI-DesAlex-fab.zip` | Gerber RS-274X + Excellon (7 files) |
| Generated keyboard | `generated/ChancePI-Keyboard-fab.zip` | Gerber RS-274X + Excellon (7 files) |

Reference material: `original/Chance.mht` (fandy.vov.ru project page), `original/sheme.gif`
(schematic by Andy_F). The DesAlex layout is the "PCB for DIP version" download; firmware v0.8.4
(MCP3201 or ADS7816).

Generated layers per board: `B_Cu`, `F_Cu`, `B_Mask`, `F_Mask`, `F_SilkS`, `Edge_Cuts`, `PTH.drl`.

---

## 2. Method

1. **Parse the originals.** No Python library exists for the Sprint-Layout binary format.
   A parser was ported from KiCad's `pcbnew/pcb_io/sprint_layout/sprint_layout_parser.cpp`
   (the most complete open implementation; format structs also documented in
   `sergey-raevskiy/xlay` → `xlay/lay6.h`).
   Validation: both files parse **byte-exact** — `75392/75392` and `10533/10533` bytes consumed.
2. **Parse the generated Gerbers** with `gerbonara` 1.6.3 (already in `myenv`), extracting
   flashes (pads), line draws (tracks), regions (filled polygons), and Excellon holes.
3. **Fit the coordinate transform** between Sprint-Layout and Gerber space by nearest-neighbour
   matching of pad centres + least-squares refinement (Sprint y axis points down; the converter
   translates without mirroring).
4. **Element-level comparison**: match every pad, every track segment, every drill hole one-to-one
   and report unmatched items and dimension deltas.
5. **Raster XOR** at 20 px/mm: render original geometry and generated geometry to the same pixel
   grid and diff. Red = original-only, green = generated-only, blue = both.
6. **Claim-by-claim check** of both generated READMEs against measured data.

### Original geometry inventory (from the binaries)

| Board | Ver | Pads | Track segments | Polys | Circles | Texts | Bytes |
|---|---|---|---|---|---|---|---|
| DesAlex | 5 | 308 | 648 (297 copper / 351 silk) | 9 | 12 | 0 | 75392/75392 |
| Keyboard | 6 | 38 | 50 (23 copper / 27 silk) | 0 | 0 | 6 (S1–S6) | 10533/10533 |

DesAlex is single-sided as the README states: all 308 pads on layer 3 (bottom copper); silk on
layer 2. Layer counts: `2L3:308, 4L2:7, 4L3:2, 5L2:10, 5L3:2, 6L2:176, 6L3:122`.

### Coordinate transforms

| Board | dx (mm) | dy (mm) | y-flip | Pad position match |
|---|---|---|---|---|
| DesAlex | +2.04999 | +63.01001 | no | 308/308, max error **0.1 µm** |
| Keyboard | 0.00000 | +20.60000 | no | 38/38, max error **0.0 µm** |

---

## 3. Keyboard board — perfect match

| Check | Result |
|---|---|
| B_Cu track segments | **23 / 23 exact** (position **and** width) |
| B_Cu pads | **38 / 38 exact** |
| Raster XOR B_Cu | **IoU = 1.0000** — zero differing pixels |
| F_Cu | 38/38 pads identical to B_Cu, **0 added traces** (README: "F_Cu pads only") ✓ |
| Drills | 38 pads → 37 holes = 1 merge. Every pad has a hole, every hole has a pad |
| Hole sizes | 1.0 mm × 32 (switches + wire pads), 0.9 mm × 3 (diodes), 4.0 mm × 2 (mounting, plated) ✓ |
| Silk | S1–S6 labels and diode symbols come from the original text/graphics objects |

No discrepancies of any kind.

---

## 4. DesAlex main board — match, with only documented deviations

### 4.1 Bottom copper (the circuit layer)

| Check | Result |
|---|---|
| Copper track segments | **297 / 297 exact** (position + width), 0 unmatched either side |
| Pads | **308 / 308** matched at ≤ 0.1 µm |
| Filled polygons | 2 original polys → 2 Gerber regions (G36/G37), 30-point outlines identical |
| Raster XOR B_Cu | **IoU = 0.9931**; both = 1 004 609 px, original-only = 3 788 px, generated-only = 3 186 px |

Residual raster differences are **not geometry differences**:

* 1-px wide blobs on trace boundaries (rasterization rounding of the 20 px/mm grid), e.g. a
  0.00 × 61.35 mm single-pixel column along the left board edge.
* The 2 copper circles are annuli in the source (`in` = 0.95 mm, `out` = 1.05 mm → 0.1 mm ring at
  r = 1.0 mm). The converter polygonizes them into 37-segment circles drawn with a 0.12 mm pen.
  Original ring geometry is preserved to within the polygonization chord error.

### 4.2 Top copper

* Pads: 308/308 identical to bottom (through-hole pads).
* Tracks: **exactly 1**, at (16.510, −22.860) → (16.510, −30.480) in original coordinates,
  width 0.6 mm. Endpoints lie **0 µm** from pad centres.

This is the README's documented VCC→AVCC link (ATmega8 pin 7 → pin 20 + MCP3201 VDD), which are
separate copper nets in the original (intended as a wire link, no silkscreen). README coordinates
match to three decimals. Keyboard F_Cu correctly has 0 added tracks.

### 4.3 Drills

308 original pads → 226 finished holes. **82 merges** — the README's "82 stacked duplicate pads
(0.05–0.18 mm apart) merged into single holes" is exact (78 merges of 2.5 mm-pad pairs + 4 merges
of 3.5 mm-pad pairs). At 0.1 mm position tolerance every pad maps to a hole and every hole is
accounted for; no orphan holes.

Hole size distribution vs README claims:

| README claim | Measured | Status |
|---|---|---|
| 1.0 mm — ATmega8 (28) + general parts | 1.0 mm × 156 | ✓ |
| 0.8 mm — DIP-8 sockets and C5 | 0.8 mm × 26 | ✓ |
| 0.9 mm — small pads | 0.9 mm × 16 | ✓ |
| 1.1 mm — TO-220 (IRF9640) + large pads | 1.1 mm × 18 | ✓ |
| 1.2 mm — wire terminals | 1.2 mm × 4 | ✓ |
| 3.0 mm — mounting (plated) | 3.0 mm × 6 | ✓ |

Hole diameters are deliberately enlarged from the original hand-drilling guides (0.4–0.6 mm) to
finished plated sizes, as documented.

### 4.4 Specific README claims verified numerically

| Claim | Measured | Status |
|---|---|---|
| 82 stacked duplicate pads merged | 308 − 226 = **82** | ✓ exact |
| ATmega8 on 2.5 mm pitch (not 2.54), 0.52 mm over 14 pins | 28 pads, 14 rows, span 32.50 mm; 13 × 2.54 − 32.50 = **0.52 mm** | ✓ exact |
| Minimum copper gap 0.196 mm | **198 µm** (vertex-based distance; method overestimates slightly) | ✓ within 2 µm |
| F_Cu link at (16.51, −22.86)–(16.51, −30.48) | identical to 3 decimals | ✓ exact |
| Board 90.46 × 65.06 mm | Edge_Cuts rectangle exactly 90.46 × 65.06 mm | ✓ exact |
| Single-sided original | all 308 pads on layer 3 | ✓ |

---

## 5. Residual findings — all explained, none are defects

### 5.1 Four apparent "pad diameter mismatches" = stacked duplicate pads

The comparison initially flagged 4 pads where the generated pad diameter differed from the nearest
original pad. Investigation shows the **original itself** contains two pads at the same spot with
different diameters (3.0 mm and 3.5 mm) at each of these 4 locations, and the converter **preserves
both flashes** (Gerber has 2 coincident D03 flashes at each site). The "mismatch" was a
nearest-neighbour pairing artifact. No diameter was changed.

### 5.2 The 74 "extra" B_Cu traces and 2 regions

* 2 Gerber regions = the 2 original 30-point copper polygons, emitted as G36/G37 fills.
* 74 short traces at 0.12 mm = the 2 copper circle annuli polygonized into 37-segment circles.

Both are faithful encodings of original geometry in Gerber primitives; nothing added.

### 5.3 Silkscreen

* Original: 351 segments + 7 polygons + 10 circles + 0 texts.
* Generated: 904 traces + 35 regions.

Breakdown:

* 331 of 351 original segments matched exactly at their drawn widths (0.1 / 0.2 mm).
* The other 20 segments are the five IC body rectangles drawn with **zero** line width in the
  source; the converter strokes them with 0.12 mm so they are manufacturable.
* All 7 original polygons are emitted as edge strokes (5/5 and 24/24 edge midpoints have matching
  Gerber traces), not as fills.
* All 10 original circles are polygonized to 48-segment circles at the correct radius.
* The 35 Gerber regions are stroke-font glyph fills for the **4 added labels**: `ATmega8`,
  `MCP3201`, `OP37`, `7660`, placed inside the corresponding IC outlines. The original contains
  no text objects on the main board (the README states "no designators or values exist in the
  original"), so these labels are the documented addition — visually confirmed by rendering only
  the generated silk that is absent from the original.

---

## 6. Caveat: board outline is not source-derived for DesAlex

Neither original file contains any layer-7 (outline) object — Sprint-Layout stores only a canvas
size, and the canvas is larger than the used area:

| Board | Canvas (size_x × size_y) | Generated Edge_Cuts | Object bbox |
|---|---|---|---|
| DesAlex | 160.00 × 100.00 mm | **90.46 × 65.06 mm** | 86.36 × 67.46 mm |
| Keyboard | 85.00 × 20.60 mm | **85.00 × 20.60 mm** | 80.90 × 13.97 mm |

* Keyboard: Edge_Cuts equals the Sprint-Layout canvas size exactly — consistent.
* DesAlex: Edge_Cuts matches **neither** the canvas nor the geometry bounding box. The README
  documents "Edge_Cuts: rectangle 0.8 mm outside the copper. The original has no outline layer",
  and indeed the copper bounding box is inset 0.8 mm from the Edge_Cuts rectangle.

Edge cuts are therefore a chance_pi construction (as disclosed), not a source-derived outline for
the main board. **Confirm the intended 90.46 × 65.06 mm board size before ordering.**

---

## 7. Tooling notes

* `myenv` (Python 3.12.3) already contained `gerbonara`, `numpy`, `scipy`, `pillow`, `shapely` —
  no additional packages were required.
* Sprint-Layout parser: record walk per KiCad's `sprint_layout_parser` (77-byte object header for
  v5+, Delphi-style strings, connection records after the object list, trailer). Units: v6 =
  1/10000 mm, v5 = 1/100 mm. THT `out`/`in` are **radii** (KiCad doubles them).
* Analysis scripts live outside the repo (`/tmp/opencode/pcb_cmp/`): `parse_sprint.py`,
  `parse_gerbers.py`, `compare.py`, `dig.py`, `dig2.py`, `raster_xor.py`, plus XOR raster PNGs.

---

## 8. Bottom line

| Aspect | Keyboard | DesAlex |
|---|---|---|
| Copper tracks identical | ✓ 23/23 | ✓ 297/297 |
| Pads identical (position) | ✓ 38/38 | ✓ 308/308 |
| Pads identical (size) | ✓ | ✓ (4 stacked pairs preserved) |
| Drills fully accounted | ✓ | ✓ 82 merges, as documented |
| F_Cu additions | none, as documented | 1 track, as documented |
| Silk additions | none | 4 labels, as documented |
| Undocumented deviations | **none** | **none** |

**The generated fabrication files reproduce the original layouts faithfully.** The only
differences from the raw source are the ones the READMEs describe (merged/resized hand-drilling
holes, one VCC–AVCC link on top copper, added board outline, added silk labels). The one item to
double-check before fabrication is the DesAlex board outline, which is a chosen rectangle rather
than something present in the original file.

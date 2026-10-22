# Gerber verification tools

These scripts check a gerber try (`../try_NN`) against the source PDFs in `../../design`. `PCB.pdf` is the reference for copper. `Placement OC.pdf` is the reference for the silkscreen, the wire links and the board contour. `Placement.pdf` is used for an independent orientation check.

You don't need to edit anything for a new try. Each script fits the PDF→gerber transform from the pad centres.

## Run

```sh
uv venv /tmp/tgsl_venv && VIRTUAL_ENV=/tmp/tgsl_venv uv pip install numpy scipy shapely pillow gerbonara
PY=/tmp/tgsl_venv/bin/python tools/run_all.sh try_04 try_03   # second argument (previous try) is optional
```

The scripts also need `pdftoppm` (poppler). Cached PDF streams, the 1200 dpi render (about 140 MB) and copper data go to `$TGSL_WORK` (default `$TMPDIR/tgsl_check`). Images (`diff_bcu.png`, `drillmap.png`) go to `$OUT`. Nothing is written to the repo.

## Scripts

| Script | Checks |
|---|---|
| `diff_tries.py OLD NEW` | Everything that changed between two tries, after removing the overall shift |
| `check_format.py` | gerbonara (an independent reader) parses every file. Shows X2 tags, M02/M30 endings and layer auto-detection as a fab upload would see them |
| `check_copper.py` | Transform fit. Each pad on B_Cu, F_Cu, both masks and the drill file, with sizes. Each PCB.pdf track and fill border is found in B_Cu, and each extra B_Cu draw is explained. Fills vertex by vertex. Self-crossing fill outlines |
| `check_raster.py` | Renders PCB.pdf at 1200 dpi with poppler and compares it pixel by pixel with B_Cu drawn from gerbonara's parse. PASS means no difference is thicker than 0.1 mm |
| `check_orientation.py` | Placement.pdf (component side) must match the gerber pads without mirroring. Placement.pdf's copper copy must agree with B_Cu |
| `check_drc.py` | Copper islands, nets after the links, clearances (with same-net check), copper and holes to edge, annular rings, mask dams, silk over pads |
| `check_silk_links.py` | Silk against Placement OC.pdf in both directions, decimal points, filled silk shapes, text height. Each wire link: pad ends, islands joined, clearance. Outline against the drawn contour |
| `check_parts.py` | Hole sizes for the parts with thick leads (BD140, 7808, electrolytics, pots), plus a drill-size map |

`parsers.py` reads the PDF content stream and the gerber and drill files. `common.py` holds the paths, the transform fit and cached copper geometry.

## Expected results

- try_03: all checks match except the hole sizes. See `../review_03/review.md`.
- try_04 (try_03 with corrected holes): every check passes. `diff_tries` shows only the 8 hole changes. Holes: 0.8 mm × 268, 1.0 mm × 66, 1.1 mm × 6, 1.3 mm × 6. Smallest annular ring 0.233 mm (BD140).

## opencode/

These are copies of the scripts opencode used for its review of try_02. They are hardcoded to `try_02` and its transform. See `opencode/NOTE.md`.

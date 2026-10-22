# TGSL data

Files for the TGSL (Tesoro Golden Sabre Light) metal detector. Everything is unpacked from the original archives. The archives themselves were removed; they are in git history up to commit `65dc427`.

## Layout

| Folder | What it holds | Source archive |
|---|---|---|
| `design/` | Original TGSL v3.0 drawings: `Schematic.pdf`, `PCB.pdf` (solder-side copper), `Placement.pdf`, `Placement OC.pdf`, `BOM.pdf` | `TGSL - complete details - version 3.0.zip` |
| `gerbers/` | `TGSL-Geotech-v3-*` gerbers generated from `design/PCB.pdf` and `design/Placement OC.pdf` | `TGSL-Geotech-v3-gerbers.zip` |
| `reviews/` | Gerber review notes: `open_issues.md`, `open_issues_2.md` | — |
| `parts/` | Parts list: `TGSL_Parts1.doc`, `TGSL_PARTS1.xls` | `TGSL_Parts1.zip` |
| `datasheets/` | 33 component datasheets (1N4148, 2N2222, 2N2907, BC547, BD140, CD4024, J107, LF353, LM308, LM358, LM393, LM7808), several makers each | `TGSL - Datasheets of Components.part1-7.rar` |
| `docs/` | `TGSL_101 _PART1.pdf` and `_PART2.pdf` (introduction to the TGSL), `abstract_2_tones.pdf` (dual-tone add-on card) | `TGSL_101.zip` |
| `docs/coil/` | Coil guides: `TGSLCoil Making.pdf` (27 cm DD coil), `TGSL_case_coil.pdf` (coil enclosures), `TGSL_Concentric-Coil.pdf` | v3.0 zip and TREVO zip |
| `trevo/` | TREVO TGS-001, a Proteus redesign of the TGSL (PCBWay Community, 2019) | `TREVO METAL DISC - CADCAM (2)_PCBWay Community.ZIP` |

### `trevo/`

| Folder | What it holds |
|---|---|
| `gerbers-pcbway/` | CADCAM export from 19:23 on 2019-06-25, the set that was uploaded to PCBWay: RS274X gerbers, Excellon drill (`.DRL`), netlist, read-me |
| `gerbers-x2/` | Earlier CADCAM export from 18:33 on the same day: X2 gerbers, gerber drill file. It was nested as a zip inside the PCBWay zip |
| `proteus/` | Proteus project (`.pdsprj`), autorouter files (`.DO`, `.EDF`, `.log`, `.sts`), DXF and PDF exports, 3D model (`.3DS`) |
| `tgsl-pdfs/` | TGSL PDFs bundled with the TREVO files that differ from `design/`: `TGSL- PCB.pdf` (another PCB artwork) and `Mascara de componentes.pdf` (component overlay) |

## Removed while unpacking

- Exact duplicates in the TREVO zip were kept once only. These were `fabrication  bobine TGSL.pdf` (same as `TGSLCoil Making.pdf`), `Part List.pdf` (same as `BOM.pdf`), `Placement.pdf`, `TGSL-Schematic.pdf` (same as `Schematic.pdf`), two extra copies of `TREVO TGS-001.3DS`, and the loose copies of the nested zip's Proteus files.
- The TREVO zip also held a saved Gmail page about a hotel booking ("Reserva WBNCSC…"). It is personal data that has nothing to do with the project, so it was not extracted.

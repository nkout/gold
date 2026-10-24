# opencode scripts (copied from /tmp/opencode/gerbcheck)

These are the scripts behind `review_02/opencode_review.md`. They are kept for reference and cross-checks. The scripts in `tools/` cover everything they do.

- **Hardcoded paths.** They read `try_02` and use the try_02 transform `A = 160.463926`. To run them on another try, copy them to a scratch folder and change the path and `A` (try_03: `A = 160.963926`). They write their outputs to the current directory, and `raster_diff.py` expects `pcb600-1.png` (`pdftoppm -r 600 -png PCB.pdf pcb600`).
- **False "square pad" result.** `extract_pcb.py` calls a pad "square" when its bounding box is 70×70 units. In PCB.pdf, the 6 largest pads are circles with exactly that bounding box. Each is drawn with 4 Bézier curves. So the opencode note "6 square pin-1 pads became round" is wrong: PCB.pdf has no square pads.
- **Edge distances off by ~0.1 mm.** `check_space.py` maps raster pixels back to millimetres with about 0.1 mm of vertical offset. Its copper-to-edge numbers (top 1.87, bottom 2.93 mm on try_03) differ from the exact values (1.974, 2.820 mm). Its "min gap between islands 22 and 22" also comes from that approximation. The exact minimum is 0.542 mm.
- Run on try_03 (2026-10-22), they agree with `tools/`: 346/346 pads at 0 µm, 713/713 track and fill-border segments, 3/3 fills, 97 islands, 84 nets, and raster differences limited to the 346 drill-guide dots.

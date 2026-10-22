#!/usr/bin/env bash
# Run every check on one try.   Usage: tools/run_all.sh try_03 [previous_try]
# PY selects the interpreter (needs numpy scipy shapely pillow gerbonara); poppler's pdftoppm must be installed.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
TRY="$(cd "$1" && pwd)"
PREV="${2:+$(cd "$2" && pwd)}"
PY="${PY:-python3}"
OUT="${OUT:-${TMPDIR:-/tmp}/tgsl_check/$(basename "$TRY")}"
mkdir -p "$OUT"
cd "$HERE"
if [ -n "$PREV" ]; then echo "##### diff_tries"; "$PY" diff_tries.py "$PREV" "$TRY"; fi
echo "##### check_format";      "$PY" check_format.py "$TRY"
echo "##### check_copper";      "$PY" check_copper.py "$TRY"
echo "##### check_raster";      "$PY" check_raster.py "$TRY" 1200 "$OUT/diff_bcu.png"
echo "##### check_orientation"; "$PY" check_orientation.py "$TRY"
echo "##### check_drc";         "$PY" check_drc.py "$TRY"
echo "##### check_silk_links";  "$PY" check_silk_links.py "$TRY"
echo "##### check_parts";       "$PY" check_parts.py "$TRY" "$OUT/drillmap.png"
echo "images in $OUT"

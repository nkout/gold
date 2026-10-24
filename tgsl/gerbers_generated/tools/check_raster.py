"""Pixel check: poppler render of PCB.pdf vs B_Cu drawn from gerbonara's parse (independent of parsers.py).
Usage: python3 check_raster.py <try_dir> [dpi=1200] [diff.png]"""
import sys, os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from gerbonara import GerberFile, ExcellonFile
from gerbonara.utils import MM
from gerbonara.graphic_primitives import Circle, Line, ArcPoly
from common import *

Image.MAX_IMAGE_PIXELS = None
G = sys.argv[1]; DPI = int(sys.argv[2]) if len(sys.argv) > 2 else 1200
OUT = sys.argv[3] if len(sys.argv) > 3 else None
f = fit(G); TX, TY = f['TX'], f['TY']
os.makedirs(WORK, exist_ok=True)
base = os.path.join(WORK, 'pcb%d' % DPI)
if not os.path.exists(base + '-1.pgm'):
    subprocess.run(['pdftoppm', '-r', str(DPI), '-gray', os.path.join(DESIGN, 'PCB.pdf'), base], check=True)
src = np.array(Image.open(base + '-1.pgm')) < 128
H, W = src.shape
S = 0.12 * DPI / 72          # px per PDF unit
K = S / U2MM                 # px per mm
PH = 842 * DPI / 72          # page height in px (A4 MediaBox 842 pt)
def px(x, y):
    return ((TX - x) / U2MM * S, PH - (y - TY) / U2MM * S)
img = Image.new('1', (W, H), 0); dr = ImageDraw.Draw(img)
def disc(c, r): dr.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=1)
for o in GerberFile.open(layer(G, 'B_Cu.gbl')).objects:
    for p in o.to_primitives(unit=MM):
        if isinstance(p, Circle):
            disc(px(p.x, p.y), p.r * K)
        elif isinstance(p, Line):
            A, B = px(p.x1, p.y1), px(p.x2, p.y2); r = p.width / 2 * K
            dx, dy = B[0] - A[0], B[1] - A[1]; L = math.hypot(dx, dy)
            if L > 0:
                nx, ny = -dy / L * r, dx / L * r
                dr.polygon([(A[0] + nx, A[1] + ny), (B[0] + nx, B[1] + ny), (B[0] - nx, B[1] - ny), (A[0] - nx, A[1] - ny)], fill=1)
            disc(A, r); disc(B, r)
        elif isinstance(p, ArcPoly):
            dr.polygon([px(*q) for q in p.outline], fill=1)
        else:
            raise SystemExit('unhandled primitive %r' % p)
ger = np.array(img, dtype=bool)
# Excluded: PCB.pdf's white drill-guide dots (gerber pads are solid) and the hairline page frame.
ex = Image.new('1', (W, H), 0); de = ImageDraw.Draw(ex)
for o in ExcellonFile.open(layer(G, 'PTH.drl')).objects:
    c = px(o.x, o.y); r = (0.974 / 2 + 0.08) * K
    de.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=1)
ex = np.array(ex, dtype=bool); dots = ex.copy()
frame = [it for it in pdf_items('PCB.pdf') if it['op'] == 'S' and it['width'] == 1.0 and len(it['subpaths'][0]['pts']) == 2]
for it in frame:
    (x1, y1), (x2, y2) = it['subpaths'][0]['pts']
    if x1 == x2:
        c = int(x1 * S); ex[:, c - 6:c + 7] = True
    else:
        r = int(PH - y1 * S); ex[r - 6:r + 7, :] = True
pdf_only = src & ~ger & ~ex; ger_only = ger & ~src & ~ex
mmpp = 25.4 / DPI
print('render %dx%d at %d dpi; PDF dark px %d, gerber dark px %d' % (W, H, DPI, src.sum(), ger.sum()))
for name, m in (('PDF-only', pdf_only), ('gerber-only', ger_only)):
    dt = ndimage.distance_transform_edt(m); lab, n = ndimage.label(m)
    print('%-11s px %7d in %5d blobs; thickest difference %.3f mm' % (name, m.sum(), n, 2 * dt.max() * mmpp))
print('drill-guide dots covered by gerber copper: %.4f' % ger[dots].mean())
print('PASS' if max(2 * ndimage.distance_transform_edt(m).max() * mmpp for m in (pdf_only, ger_only)) < 0.1
      else 'CHECK: a difference thicker than 0.1 mm exists')
if OUT:
    vis = np.full((H, W, 3), 255, np.uint8)
    vis[src & ger] = (170, 170, 170); vis[pdf_only] = (220, 0, 0); vis[ger_only] = (0, 0, 220)
    Image.fromarray(vis).resize((W // 4, H // 4), Image.LANCZOS).save(OUT)

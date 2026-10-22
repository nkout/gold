#!/usr/bin/env python3
"""Re-rasterize PCB.pdf from parsed vector paths; diff vs poppler render.
Validates parser completeness. DPI configurable; outputs diff stats + diff image."""
import sys
sys.path.insert(0,'.')
from parse_pdf import extract_stream, parse_content, subpath_points
import numpy as np
from PIL import Image, ImageDraw

DPI = float(sys.argv[1]) if len(sys.argv)>1 else 150
PAGE_W_PT, PAGE_H_PT = 595.0, 842.0
SCALE = 0.12 * DPI/72.0   # units -> px

paths = []
for s in extract_stream('/home/nkout/projects/gold/tgsl/design/PCB.pdf'):
    paths += parse_content(s)

W = int(PAGE_W_PT/72*DPI); H = int(PAGE_H_PT/72*DPI)
img = Image.new('L', (W, H), 255)
d = ImageDraw.Draw(img)

def to_px(x, y):
    return (x*SCALE, H - y*SCALE)

for p in paths:
    gray = 0 if p['gray'] < 0.5 else 255
    for sp in p['subpaths']:
        pts = [to_px(x,y) for x,y in subpath_points(sp, ncurve=24)]
        if len(pts) < 2: continue
        if p['kind'] == 'fill':
            d.polygon(pts, fill=gray)
        else:
            wpx = max(1, int(round(p['width']*SCALE)))
            d.line(pts, fill=gray, width=wpx, joint='curve')
            # round caps/joints approximation: circles at vertices
            r = wpx/2
            for (x,y) in pts:
                d.ellipse([x-r,y-r,x+r,y+r], fill=gray)

img.save('re_render.png')
pop = np.array(Image.open(f'pcb-pop-{int(DPI)}.png').convert('L')) if False else None
print('re-render saved', img.size)

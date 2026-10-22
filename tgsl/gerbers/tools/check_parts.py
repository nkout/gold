"""Hole sizes of the parts with thick leads, and a drill-size map over the silkscreen.
Usage: python3 check_parts.py <try_dir> [drillmap.png]"""
import sys, math
from PIL import Image, ImageDraw
from common import *

G = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else None
T = pcb_T(G)
# Pad centres in PCB.pdf units (the same for every try). Lead sizes are typical datasheet values.
PARTS = {
    'BD140 (TO-126)':        ([(1509, 4202), (1569, 4202), (1629, 4202)], 'flat leads ~0.75 x 0.5 mm, needs >= 1.0 mm'),
    '7808 (TO-220)':         ([(1887, 2677), (1827, 2677), (1767, 2677)], 'flat leads ~0.8 x 0.5 mm, 1.0 mm is snug, 1.1-1.2 comfortable'),
    '1000uF (7.5 mm pitch)': ([(1639, 3839), (1460, 3839)], 'caps with 7.5 mm pitch usually have 0.8 mm leads, needs >= 1.0 mm'),
    '220uF top':             ([(2059, 4338), (2059, 4457)], '5 mm pitch, 0.5-0.6 mm leads'),
    '220uF mid':             ([(1905, 4093), (1905, 4213)], '5 mm pitch, 0.5-0.6 mm leads'),
    '220uF bottom left':     ([(2063, 2456), (2063, 2576)], '5 mm pitch, 0.5-0.6 mm leads'),
    '220uF bottom right':    ([(1601, 2453), (1601, 2573)], '5 mm pitch, 0.5-0.6 mm leads'),
    'pot 100K':              ([(3558, 2895), (3558, 2775), (3438, 2835)], ''),
    'trimmer 10K':           ([(1748, 3427), (1748, 3547), (1868, 3487)], ''),
}
tools, holes = parse_drill(layer(G, 'PTH.drl'))
pads = parse_gerber(layer(G, 'B_Cu.gbl'))['flashes']
head('Holes of parts with thick leads')
for name, (pts, note) in PARTS.items():
    rows = []
    for u in pts:
        p = T(u)
        h = min(holes, key=lambda q: math.dist(q[0], p)); pd = min(pads, key=lambda q: math.dist(q[0], p))
        rows.append('drill %.1f pad %.3f ring %.3f' % (h[1], pd[1], (pd[1] - h[1]) / 2))
    print('%-22s at (%.2f,%.2f): %s  [%s]' % (name, *T(pts[0]), '; '.join(sorted(set(rows))), note))
if OUT:
    gs = parse_gerber(layer(G, 'F_SilkS.gto')); C = copper(G); b = C['board'].bounds
    K = 16; W, H = int((b[2] - b[0]) * K) + 20, int((b[3] - b[1]) * K) + 40
    im = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(im)
    P = lambda p: (10 + (p[0] - b[0]) * K, H - 10 - (p[1] - b[1]) * K)
    for a, c, w in gs['draws']: d.line([P(a), P(c)], fill=(90, 90, 90), width=2)
    for r in gs['regions']:
        for c in r: d.polygon([P(p) for p in c], fill=(90, 90, 90))
    col = {0.8: (0, 160, 0), 1.0: (0, 80, 255), 1.3: (230, 0, 0)}
    for p, dd in holes:
        q = P(p); r = dd / 2 * K * 1.6
        d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=col.get(dd, (255, 140, 0)))
    d.rectangle([P((b[0], b[3])), P((b[2], b[1]))], outline='black', width=2)
    d.text((14, 6), 'drill: green 0.8 mm, blue 1.0 mm, red 1.3 mm, orange other', fill='black')
    im.save(OUT); print('drill map written to', OUT)

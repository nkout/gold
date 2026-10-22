"""Placement OC.pdf vs F_SilkS (two-way), decimal-point dots, filled silk shapes, text size,
wire links (F_Cu) and the board outline vs the drawn contour.
Usage: python3 check_silk_links.py <try_dir>"""
import sys, math, collections
from shapely.geometry import LineString, Point
from shapely.ops import unary_union, polygonize
from common import *

G = sys.argv[1]
T = oc_T(G)
oc = pdf_items('Placement OC.pdf')
gs = parse_gerber(layer(G, 'F_SilkS.gto')); gt = parse_gerber(layer(G, 'F_Cu.gtl'))
C = copper(G)


class Grid:
    def __init__(s, segs, cell=1.0):
        s.c = cell; s.g = collections.defaultdict(list); s.segs = segs
        for i, (a, b) in enumerate(segs):
            for gx in range(int(min(a[0], b[0]) // cell) - 1, int(max(a[0], b[0]) // cell) + 2):
                for gy in range(int(min(a[1], b[1]) // cell) - 1, int(max(a[1], b[1]) // cell) + 2):
                    s.g[(gx, gy)].append(i)

    def near(s, p):
        return min([segdist(p, *s.segs[i]) for i in s.g.get((int(p[0] // s.c), int(p[1] // s.c)), [])] or [1e9])


def sample(a, b, step=0.05):
    n = max(1, int(math.dist(a, b) / step))
    return [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n + 1)]


head('Silkscreen vs Placement OC.pdf')
ps, tags = [], []
for it in oc:
    if it['op'] == 'S' and it['width'] in (18.72, 1.0):   # links, board contour, hairlines: not silk
        continue
    for sp in it['subpaths']:
        pts = [T(p) for p in sp['pts']]
        if sp['closed']: pts = pts + [pts[0]]
        if len(pts) == 1: pts = pts * 2
        for a, b in zip(pts, pts[1:]):
            ps.append((a, b)); tags.append((it['op'], str(it['color']), round(it['width'] * U2MM, 3)))
gsegs = [(a, b) for a, b, w in gs['draws']] + [(p, p) for p, d in gs['flashes']]
for r in gs['regions']:
    for c in r: gsegs += list(zip(c, c[1:]))
gg, pg = Grid(gsegs), Grid(ps)
g_off = [max(pg.near(p) for p in sample(a, b)) for a, b in gsegs]
p_off = [max(gg.near(p) for p in sample(a, b)) for a, b in ps]
print('gerber silk elements %d: farthest from a PDF stroke %.3f mm (> 0.05 mm: %d)' % (len(gsegs), max(g_off), sum(o > 0.05 for o in g_off)))
print('PDF silk segments %d: farthest from gerber silk %.3f mm (> 0.05 mm: %d)' % (len(ps), max(p_off), sum(o > 0.05 for o in p_off)))
for (a, b), t, o in zip(ps, tags, p_off):
    if o > 0.05: print('   PDF silk not in gerber:', t, tuple(round(v, 2) for v in a + b))
fills = [[T(p) for p in it['subpaths'][0]['pts']] for it in oc if it['op'] == 'f']
w = max(min(max(min(math.dist(p, q) for q in r[0]) for p in f) for r in gs['regions']) for f in fills) if fills else 0
print('filled shapes: PDF %d, gerber regions %d, max vertex err %.4f mm' % (len(fills), len(gs['regions']), w))
print('silk line widths %s, flash sizes %s (PDF pens: %s)' % (sorted(set(x for *_, x in gs['draws'])), sorted(set(d for _, d in gs['flashes'])),
      sorted({round(it['width'] * U2MM, 3) for it in oc if it['op'] == 'S' and it['width'] not in (18.72, 1.0)})))
dots = [(T(sp['pts'][0])) for it in oc if it['op'] == 'S' for sp in it['subpaths']
        if len(sp['pts']) >= 2 and all(p == sp['pts'][0] for p in sp['pts'])]
fl = gs['flashes']
dd = [min(math.dist(f[0], p) for f in fl) if fl else 1e9 for p in dots]
print('decimal points (zero-length strokes) in PDF %d; present as silk flashes: %d (max offset %.3f mm)' % (
    len(dots), sum(d < 0.05 for d in dd), max(dd) if dd else 0))
for f in fl:
    if min((math.dist(f[0], p) for p in dots), default=1e9) > 0.05:
        print('   extra silk dot at (%.3f,%.3f), %.3f mm from the nearest PDF stroke' % (*f[0], pg.near(f[0])))
blobs = unary_union([LineString([T(p) for p in sp['pts']]).buffer(0.12) for it in oc if it['op'] == 'S' and it['color'] == 0
                     and abs(it['width'] - 3.978) < 0.01 for sp in it['subpaths'] if len(sp['pts']) >= 2 and sp['pts'][0] != sp['pts'][-1]])
hs = collections.Counter(round(max(b.bounds[2] - b.bounds[0], b.bounds[3] - b.bounds[1]) - 0.24, 1) for b in blobs.geoms)
print('glyph height histogram (mm, incl. pen):', sorted(hs.items()))

head('Wire links (F_Cu traces)')
pads, pb = C['pads'], C['pb']
red = [[T(p) for p in it['subpaths'][0]['pts']] for it in oc if it['op'] == 'S' and it['width'] == 18.72 and it['color'] != 0]
def pad_at(p):
    j = min(range(len(pads)), key=lambda i: math.dist(p, pads[i][0])); return j, math.dist(p, pads[j][0])
for n, (a, b, w) in enumerate(gt['draws']):
    ja, da = pad_at(a); jb, db = pad_at(b)
    L = LineString([a, b]).buffer(w / 2, 32)
    clr = min(L.distance(Point(pads[i][0]).buffer(pads[i][1] / 2, 64)) for i in range(len(pads)) if i not in (ja, jb))
    seg = LineString([a, b])
    nred = sum(1 for r in red if max(seg.distance(Point(r[0])), seg.distance(Point(r[-1]))) < 0.45)
    inside = 'inside pad' if max(da, db) < pads[ja if da > db else jb][1] / 2 else 'OFF PAD'
    print('L%-2d (%6.2f,%6.2f)-(%6.2f,%6.2f) w %.2f  end-to-pad-centre %.3f/%.3f (%s)  B islands %2d-%2d %s  clearance %.3f mm  red strokes %d' % (
        n + 1, *a, *b, w, da, db, inside, pb[ja], pb[jb], 'joins' if pb[ja] != pb[jb] else 'same', clr, nred))
lonely = [r for r in red if not any(max(LineString([a, b]).distance(Point(r[0])), LineString([a, b]).distance(Point(r[-1]))) < 0.45 for a, b, w in gt['draws'])]
print('red link strokes in PDF %d; without an F_Cu trace: %d' % (len(red), len(lonely)))

head('Board outline vs contour drawn in Placement OC.pdf')
cont = [[T(p) for p in it['subpaths'][0]['pts']] for it in oc if it['op'] == 'S' and it['color'] == 0 and it['width'] == 18.72]
drawn = unary_union(list(polygonize(unary_union([LineString(s) for s in cont]))))
board = C['board']
print('drawn contour bounds (%.3f,%.3f)-(%.3f,%.3f), %.1f x %.1f mm; inside the board outline: %s' % (
    *drawn.bounds, drawn.bounds[2] - drawn.bounds[0], drawn.bounds[3] - drawn.bounds[1], board.buffer(0.01).contains(drawn)))
print('board outline (%.3f,%.3f)-(%.3f,%.3f); bare board added outside the drawn contour %.1f mm2' % (*board.bounds, board.area - drawn.area))
out = unary_union(C['IB']).difference(drawn)
if not out.is_empty:
    depth = max(drawn.exterior.distance(Point(c)) for g in (out.geoms if hasattr(out, 'geoms') else [out]) for c in g.exterior.coords)
    print('copper outside the drawn contour: %.1f mm2, up to %.3f mm past the line -> the drawn line cannot be the cut line' % (out.area, depth))

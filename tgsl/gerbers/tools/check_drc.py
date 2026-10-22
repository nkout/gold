"""Connectivity and design-rule checks on the gerber geometry (shapely, exact).
Usage: python3 check_drc.py <try_dir>"""
import sys, math, itertools, collections
from shapely.geometry import Point, LineString
from shapely.ops import unary_union, nearest_points
from shapely import STRtree
from common import *

G = sys.argv[1]
C = copper(G)
IB, IF, board, holes, pads, pb, pf, net = (C[k] for k in ('IB', 'IF', 'board', 'holes', 'pads', 'pb', 'pf', 'net'))
x0, y0, x1, y1 = board.bounds
head('Board and nets')
print('outline %.3f x %.3f mm, (%.3f,%.3f)-(%.3f,%.3f)' % (x1 - x0, y1 - y0, x0, y0, x1, y1))
print('B_Cu islands %d (islands without pads: %d); F_Cu islands %d' % (len(IB), len(IB) - len(set(pb)), len(IF)))
print('nets after joining through plated holes and F_Cu: %d' % len(set(net)))
joins = [fi for fi in set(pf) if len({pb[i] for i in range(len(pads)) if pf[i] == fi}) > 1]
print('F_Cu islands that join separate B_Cu islands: %d' % len(joins))

head('Clearance between separate copper')
for name, isl in (('B_Cu', IB), ('F_Cu', IF)):
    tree = STRtree(isl); pairs = []
    for i, I in enumerate(isl):
        for j in tree.query(I.buffer(0.6)):
            if j > i:
                d = I.distance(isl[j])
                if d < 0.6: pairs.append((d, i, int(j)))
    pairs.sort()
    d, i, j = pairs[0]; p, q = nearest_points(isl[i], isl[j])
    print('%s minimum %.3f mm at (%.2f,%.2f)-(%.2f,%.2f)' % (name, d, p.x, p.y, q.x, q.y))
    for d, i, j in [x for x in pairs if x[0] < 0.25]:
        pi = [k for k in range(len(pads)) if (pb if name == 'B_Cu' else pf)[k] == i]
        pj = [k for k in range(len(pads)) if (pb if name == 'B_Cu' else pf)[k] == j]
        same = {net[pb[k]] for k in pi} == {net[pb[k]] for k in pj}
        print('   %.3f mm  pads %s / %s  same net: %s' % (d, [tuple(round(v, 2) for v in pads[k][0]) for k in pi],
                                                     [tuple(round(v, 2) for v in pads[k][0]) for k in pj], same))

head('Edges, holes, rings')
for name, isl in (('B_Cu', IB), ('F_Cu', IF)):
    U = unary_union(isl); b = U.bounds
    print('%s copper margins to outline: left %.3f right %.3f bottom %.3f top %.3f mm' % (name, b[0] - x0, x1 - b[2], b[1] - y0, y1 - b[3]))
hd = min((Point(p).distance(board.exterior) - d / 2, p) for p, d in holes)
print('min hole wall to board edge %.3f mm at %s' % hd)
hh = min((math.dist(a[0], b[0]) - a[1] / 2 - b[1] / 2, a[0], b[0]) for a, b in itertools.combinations(holes, 2))
print('min hole-to-hole wall gap %.3f mm between %s and %s' % hh)
def pad_at(p): return min(pads, key=lambda q: math.dist(p, q[0]))
rings = sorted((pad_at(p)[1] / 2 - d / 2 - math.dist(p, pad_at(p)[0]), p, d) for p, d in holes)
print('min annular ring %.3f mm (drill %.1f at %s); holes per size %s' % (rings[0][0], rings[0][2], rings[0][1],
      dict(collections.Counter(d for _, d in holes))))
for name, isl, owner in (('B_Cu', IB, pb), ('F_Cu', IF, pf)):
    w = (1e9,)
    for p, d in holes:
        k = min(range(len(pads)), key=lambda i: math.dist(pads[i][0], p)); hp = Point(p).buffer(d / 2, 64)
        for i, I in enumerate(isl):
            if i != owner[k]:
                dd = I.distance(hp)
                if dd < w[0]: w = (dd, p)
    print('%s min hole wall to copper of another island %.3f mm at %s' % (name, w[0], tuple(round(v, 2) for v in w[1])))

head('Solder mask')
for mname in ('F_Mask.gts', 'B_Mask.gbs'):
    mo = [(p, d / 2) for p, d in parse_gerber(layer(G, mname))['flashes']]
    gaps = sorted((math.dist(a[0], b[0]) - a[1] - b[1], a[0], b[0]) for a, b in itertools.combinations(mo, 2)
                  if math.dist(a[0], b[0]) < a[1] + b[1] + 0.3)
    thin = [g for g in gaps if g[0] < 0.1]
    print('%s: %d openings; dams < 0.1 mm: %d %s' % (mname, len(mo), len(thin), ['%.3f mm at %s' % (g, tuple(round(v, 2) for v in a)) for g, a, b in thin]))
    isl, owner = (IF, pf) if mname.startswith('F') else (IB, pb)
    bad = 0
    for p, r in mo:
        k = min(range(len(pads)), key=lambda i: math.dist(pads[i][0], p)); m = Point(p).buffer(r, 64)
        bad += sum(1 for i, I in enumerate(isl) if i != owner[k] and I.intersects(m))
    print('   openings exposing copper of another island: %d' % bad)

head('Silk over top pad openings (the fab clips this)')
gs = parse_gerber(layer(G, 'F_SilkS.gto'))
silk = unary_union([LineString([a, b]).buffer(w / 2, 16) if a != b else Point(a).buffer(w / 2, 16) for a, b, w in gs['draws']] +
                   [Point(p).buffer(d / 2, 16) for p, d in gs['flashes']])
mask = unary_union([Point(p).buffer(d / 2, 48) for p, d in parse_gerber(layer(G, 'F_Mask.gts'))['flashes']])
n = sum(1 for p, d in parse_gerber(layer(G, 'F_Mask.gts'))['flashes'] if Point(p).buffer(d / 2, 48).intersects(silk))
print('silk %.1f mm2, of which %.2f mm2 over pad openings; openings touched: %d' % (silk.area, silk.intersection(mask).area, n))
sx0, sy0, sx1, sy1 = silk.bounds
print('silk margins to outline: left %.3f right %.3f bottom %.3f top %.3f mm' % (sx0 - x0, x1 - sx1, sy0 - y0, y1 - sy1))

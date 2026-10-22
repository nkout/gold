"""PCB.pdf vs B_Cu / F_Cu / masks / drill: pads, tracks, fills, fill validity.
Usage: python3 check_copper.py <try_dir>"""
import sys, math, collections
from common import *

G = sys.argv[1]
f = fit(G)
head('Transform PCB.pdf -> gerber (mirrored in X, 1/600 in)')
print('x = %.6f - u*%.9f ; y = u*%.9f + %.6f' % (f['TX'], U2MM, U2MM, f['TY']))
print('Placement OC.pdf: x = u*%.9f + %.6f ; y = u*%.9f + %.6f' % (U2MM, f['OC_TX'], U2MM, f['OC_TY']))
print('pads matched %d unique of %d, max position error %.6f mm' % (f['unique'], f['n'], f['maxerr']))
T = pcb_T(G)
items = pdf_items('PCB.pdf')

head('Pads on every layer')
bf, bs, wf = [], [], []
for it in items:
    if len(it['subpaths']) != 1:
        continue
    c = circle_of(it['subpaths'][0])
    if not c:
        continue
    if it['op'] == 'f' and it['color'] == 0: bf.append(c)
    elif it['op'] == 'S' and it['color'] == 0: bs.append(c)
    elif it['op'] == 'f': wf.append(c)
L = {n: parse_gerber(layer(G, n))['flashes'] for n in ('B_Cu.gbl', 'F_Cu.gtl', 'B_Mask.gbs', 'F_Mask.gts')}
tools, holes = parse_drill(layer(G, 'PTH.drl'))
L['PTH.drl'] = holes
print('PDF pads %d (each with outline %d, white drill-guide dot %d); gerber: %s' % (
    len(bf), len(bs), len(wf), ', '.join('%s %d' % (k, len(v)) for k, v in L.items())))
worst = collections.defaultdict(float); rows = collections.Counter(); used = collections.defaultdict(set)
for c in bf:
    sp = None
    p = T(c)
    dot = min(wf, key=lambda w: math.dist(w[:2], c[:2]))
    row = [round(c[2] * U2MM, 4), round(dot[2] * U2MM, 3)]
    for k, fl in L.items():
        j = min(range(len(fl)), key=lambda i: math.dist(fl[i][0], p))
        used[k].add(j)
        worst[k] = max(worst[k], math.dist(fl[j][0], p))
        row.append(fl[j][1])
    rows[tuple(row)] += 1
print('max position error per layer (mm):', {k: round(v, 6) for k, v in worst.items()})
print('unmatched gerber items per layer:', {k: len(L[k]) - len(used[k]) for k in L})
print('count | PDF pad d (max of x/y) | PDF dot d | B_Cu | F_Cu | B_Mask | F_Mask | drill | ring | mask-pad')
for k, v in sorted(rows.items()):
    print('%4d  %s  ring %.3f  mask+%.4f' % (v, k, (k[2] - k[6]) / 2, k[4] - k[2]))
print('note: PDF pads drawn 1 unit (0.042 mm) wider in one axis are emitted at the smaller size.')

head('Tracks, copper fills and fill borders')
segs, fills, borders = [], [], []
for it in items:
    sp = it['subpaths']
    if len(sp) == 1 and circle_of(sp[0]):
        continue
    pts = [T(p) for p in sp[0]['pts']]
    if it['op'] == 'S' and len(pts) == 2 and not sp[0]['closed']:
        if it['width'] != 1.0:  # 1-unit hairlines are the page frame
            segs.append((pts[0], pts[1], it['width'] * U2MM))
    elif it['op'] == 'f':
        fills.append(pts)
    else:
        borders.append((pts, it['width'] * U2MM))
want = list(segs)
for pts, w in borders:
    ring = pts + [pts[0]] if pts[0] != pts[-1] else pts
    want += [(a, b, w) for a, b in zip(ring, ring[1:])]
gb = parse_gerber(layer(G, 'B_Cu.gbl'))
draws = gb['draws']; used = [False] * len(draws); miss = []; maxe = 0; wd = 0
for a, b, w in want:
    best, be = None, 1e9
    for j, (p, q, gw) in enumerate(draws):
        if not used[j]:
            e = seg_err(a, b, p, q)
            if e < be: best, be = j, e
    if be < 0.001 and abs(draws[best][2] - w) < 0.0005:
        used[best] = True; maxe = max(maxe, be); wd = max(wd, abs(draws[best][2] - w))
    else:
        miss.append((a, b, w, be))
print('PDF tracks %d + fill-border edges %d = %d; found in B_Cu %d; max endpoint err %.2e mm; max width diff %.2e mm' % (
    len(segs), len(want) - len(segs), len(want), len(want) - len(miss), maxe, wd))
for m in miss: print('  MISSING from B_Cu:', m)
for j in [j for j in range(len(draws)) if not used[j]]:
    p, q, w = draws[j]
    kind = 'zero-length' if math.dist(p, q) < 1e-6 else ('second copy of a track PCB.pdf draws twice' if any(
        used[i] and seg_err(p, q, a, b) < 1e-6 for i, (a, b, _) in enumerate(draws)) else 'NOT IN PCB.pdf')
    print('  extra B_Cu draw (%.3f,%.3f)-(%.3f,%.3f) w %.4f: %s' % (*p, *q, w, kind))
print('track widths PDF:', dict(collections.Counter(round(w, 4) for *_, w in segs)))
for fpts in fills:
    F = fpts[:-1] if fpts[0] == fpts[-1] else fpts
    best = min((max(min(math.dist(p, q) for q in r[0]) for p in F), len(r[0])) for r in gb['regions'])
    print('PDF fill with %d vertices -> B_Cu region, max vertex err %.2e mm' % (len(F), best[0]))
print('B_Cu regions %d, PDF fills %d' % (len(gb['regions']), len(fills)))

head('Copper fill validity (self-crossing outlines)')
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union, polygonize
from shapely.validation import explain_validity
cover = unary_union([LineString([a, b]).buffer(w / 2, 32) for a, b, w in draws if a != b] +
                    [Point(p).buffer(d / 2, 64) for p, d in gb['flashes']])
for i, r in enumerate(gb['regions']):
    P = Polygon(r[0])
    if P.is_valid:
        print('region %d: %d vertices, valid' % (i, len(r[0])))
        continue
    print('region %d: %d vertices, INVALID: %s' % (i, len(r[0]), explain_validity(P)))
    others = unary_union([cover] + [Polygon(q[0]).buffer(0) for k, q in enumerate(gb['regions']) if k != i])
    for face in sorted(polygonize(unary_union(LineString(r[0]))), key=lambda g: g.area):
        if face.area < 50:
            print('   small face %.4f mm2 at %s; not covered by tracks/pads/other fills: %.6f mm2' % (
                face.area, [round(v, 3) for v in face.bounds], face.difference(others).area))
    print('   -> if every small face is covered, the copper is the same under any fill rule')

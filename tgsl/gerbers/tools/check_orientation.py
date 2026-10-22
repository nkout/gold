"""Mirror check: Placement.pdf (component-side view with copper, parts and links) must match the
gerber pads WITHOUT mirroring. Also checks that Placement.pdf's copper copy agrees with B_Cu.
Usage: python3 check_orientation.py <try_dir>"""
import sys, math, collections
import numpy as np
from common import *

G = sys.argv[1]
P = np.array([(p[0], p[1]) for p in pdf_pads('Placement.pdf')])
Q = np.array([f[0] for f in parse_gerber(layer(G, 'B_Cu.gbl'))['flashes']])
head('Placement.pdf pads vs gerber pads')
best = None
for mirror in (False, True):
    sx = -U2MM if mirror else U2MM
    cp, cq = P.mean(0), Q.mean(0)
    M = np.c_[sx * (P[:, 0] - cp[0]) + cq[0], U2MM * (P[:, 1] - cp[1]) + cq[1]]
    for _ in range(10):
        idx = [int(np.argmin(((Q - m) ** 2).sum(1))) for m in M]
        M = M + (Q[idx] - M).mean(0)
    idx = [int(np.argmin(((Q - m) ** 2).sum(1))) for m in M]
    A = np.c_[P, np.ones(len(P))]
    cx, *_ = np.linalg.lstsq(A, Q[idx, 0], rcond=None); cy, *_ = np.linalg.lstsq(A, Q[idx, 1], rcond=None)
    e = np.hypot(A @ cx - Q[idx, 0], A @ cy - Q[idx, 1])
    print('mirrored=%-5s pads within 0.05 mm: %3d / %d, max err %.3f mm' % (mirror, (e < 0.05).sum(), len(P), e.max()))
    if not mirror: best = (cx, cy, (e < 0.05).sum())
print('ORIENTATION OK (gerber top view = Placement.pdf, i.e. PCB.pdf mirrored)' if best[2] == len(P) == len(Q)
      else 'ORIENTATION PROBLEM')

head('Placement.pdf copper vs B_Cu')
cx, cy, _ = best
T = lambda p: (cx[0] * p[0] + cx[1] * p[1] + cx[2], cy[0] * p[0] + cy[1] * p[1] + cy[2])
items = pdf_items('Placement.pdf')
segs = [(T(it['subpaths'][0]['pts'][0]), T(it['subpaths'][0]['pts'][1]), it['width'] * U2MM) for it in items
        if it['op'] == 'S' and it['color'] == 0 and it['width'] in (18.72, 46.8, 70.2) and len(it['subpaths']) == 1
        and len(it['subpaths'][0]['pts']) == 2]
draws = parse_gerber(layer(G, 'B_Cu.gbl'))['draws']
# Placement.pdf draws the board contour with the same 18.72 pen: drop strokes longer than 50 mm that match nothing.
used = [False] * len(draws); hist = collections.Counter(); bad = []
for a, b, w in segs:
    cand = [(seg_err(a, b, p, q), j) for j, (p, q, gw) in enumerate(draws) if not used[j] and abs(gw - w) < 0.001]
    e, j = min(cand) if cand else (1e9, None)
    if e < 0.12:
        used[j] = True; hist[round(e, 2)] += 1
    else:
        bad.append((a, b, w, e))
contour = [x for x in bad if math.dist(x[0], x[1]) > 50]
print('Placement.pdf copper strokes %d: matched to B_Cu %d (endpoint err histogram %s), board-contour strokes %d, other unmatched %d' % (
    len(segs), sum(hist.values()), sorted(hist.items()), len(contour), len(bad) - len(contour)))
for a, b, w, e in bad:
    if (a, b, w, e) not in contour:
        print('   unmatched (%.3f,%.3f)-(%.3f,%.3f) w %.4f' % (*a, *b, w))
for a, b, w, e in contour:
    print('   drawn contour line (%.3f,%.3f)-(%.3f,%.3f)' % (*a, *b))
print('B_Cu draws with no Placement.pdf stroke: %d (fill borders, drawn there as closed shapes, and zero-length draws)' % used.count(False))

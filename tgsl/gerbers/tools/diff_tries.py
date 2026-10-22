"""Structural diff of two tries, after removing the overall shift between them.
Usage: python3 diff_tries.py <old_try_dir> <new_try_dir>"""
import sys, collections, statistics
from common import *

A, B = sys.argv[1], sys.argv[2]
fa = parse_gerber(layer(A, 'B_Cu.gbl'))['flashes']; fb = parse_gerber(layer(B, 'B_Cu.gbl'))['flashes']
DX = statistics.median(round(q[0][0] - p[0][0], 6) for p, q in zip(sorted(fa), sorted(fb)))
DY = statistics.median(round(q[0][1] - p[0][1], 6) for p, q in zip(sorted(fa), sorted(fb)))
print('overall shift old -> new (median of B_Cu pads): dx %.6f dy %.6f mm' % (DX, DY))
k = lambda p: (round(p[0], 5), round(p[1], 5))
s = lambda p: k((p[0] + DX, p[1] + DY))
for f in ('B_Cu.gbl', 'F_Cu.gtl', 'B_Mask.gbs', 'F_Mask.gts', 'F_SilkS.gto', 'Edge_Cuts.gm1'):
    a = parse_gerber(layer(A, f)); b = parse_gerber(layer(B, f))
    print('\n== %s: old %d flashes %d draws %d regions | new %d flashes %d draws %d regions' % (
        f, len(a['flashes']), len(a['draws']), len(a['regions']), len(b['flashes']), len(b['draws']), len(b['regions'])))
    if sorted(a['aps'].values()) != sorted(b['aps'].values()):
        print('   apertures changed:', sorted(a['aps'].values()), '->', sorted(b['aps'].values()))
    for name, ca, cb in (
            ('flash', collections.Counter((s(p), d) for p, d in a['flashes']), collections.Counter((k(p), d) for p, d in b['flashes'])),
            ('draw', collections.Counter((s(p), s(q), w) for p, q, w in a['draws']), collections.Counter((k(p), k(q), w) for p, q, w in b['draws'])),
            ('region', collections.Counter(tuple(tuple(s(p) for p in c) for c in r) for r in a['regions']),
             collections.Counter(tuple(tuple(k(p) for p in c) for c in r) for r in b['regions']))):
        rem, add = list((ca - cb).elements()), list((cb - ca).elements())
        if rem or add:
            print('   %s: removed %d, added %d' % (name, len(rem), len(add)))
            for x in rem[:8]: print('     -', x if name != 'region' else '%d-vertex region' % len(x[0]))
            for x in add[:30]: print('     +', x if name != 'region' else '%d-vertex region' % len(x[0]))
ta, ha = parse_drill(layer(A, 'PTH.drl')); tb, hb = parse_drill(layer(B, 'PTH.drl'))
ca = collections.Counter(((round(p[0] + DX, 3), round(p[1] + DY, 3)), d) for p, d in ha)
cb = collections.Counter(((round(p[0], 3), round(p[1], 3)), d) for p, d in hb)
print('\n== PTH.drl: old %d holes %s | new %d holes %s; removed %d, added %d' % (
    len(ha), ta, len(hb), tb, sum((ca - cb).values()), sum((cb - ca).values())))
for x in list((ca - cb).elements())[:10]: print('     -', x)
for x in list((cb - ca).elements())[:10]: print('     +', x)

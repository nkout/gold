#!/usr/bin/env python3
"""Track + pour comparison. Transform from compare_pads."""
import sys, json, math
sys.path.insert(0,'.')
import numpy as np
from scipy.spatial import cKDTree
from parse_gerber import Gerber

A, B, s = 160.463926, -99.511558, 0.04233333
def mmx(u): return A - s*u
def mmy(u): return B + s*u

feat = json.load(open('pcb_features.json'))
base='/home/nkout/projects/gold/tgsl/gerbers/try_02/TGSL-Geotech-v3-'
gb = Gerber(base+'B_Cu.gbl')

# PDF tracks -> mm segments
pdf_segs = []
for t in feat['tracks']:
    x1,y1,x2,y2 = t['seg']
    pdf_segs.append((mmx(x1), mmy(y1), mmx(x2), mmy(y2), t['width']*s))
print('pdf segs:', len(pdf_segs), ' gerber draws:', len(gb.draws))

def seg_key(x1,y1,x2,y2):
    return (round(x1,3),round(y1,3),round(x2,3),round(y2,3))

# index gerber draws by endpoints (both directions)
from collections import defaultdict
gmap = defaultdict(list)
for i,(x1,y1,x2,y2,w) in enumerate(gb.draws):
    gmap[seg_key(x1,y1,x2,y2)].append(i)
    gmap[seg_key(x2,y2,x1,y1)].append(i)

matched_g = set()
unmatched_pdf = []
width_bad = []
for (x1,y1,x2,y2,w) in pdf_segs:
    cands = gmap.get(seg_key(x1,y1,x2,y2), [])
    if not cands:
        unmatched_pdf.append((x1,y1,x2,y2,w)); continue
    i = cands[0]; matched_g.add(i)
    gw = gb.draws[i][4]
    if abs(gw-w) > 0.001:
        width_bad.append((x1,y1,x2,y2,w,gw))

print('pdf segs unmatched:', len(unmatched_pdf))
for u in unmatched_pdf[:12]:
    print('   PDF-only:', [f'{v:.3f}' for v in u])
print('gerber draws unmatched:', len(gb.draws)-len(matched_g))
for i in range(len(gb.draws)):
    if i not in matched_g:
        x1,y1,x2,y2,w = gb.draws[i]
        print(f'   GER-only: ({x1:.3f},{y1:.3f})->({x2:.3f},{y2:.3f}) w={w:.4f}  len={math.hypot(x2-x1,y2-y1):.4f}')
print('width mismatches:', len(width_bad))
for u in width_bad[:10]: print('   ', u)

# pours: pdf polygons vs gerber regions
print('\n--- pours ---')
print('pdf pours:', len(feat['pours']), 'gerber regions:', len(gb.regions))
for pi,p in enumerate(feat['pours']):
    for si,spsegs in enumerate(p['subpaths']):
        # polygon vertices (ordered)
        pts = []
        for (x1,y1,x2,y2) in spsegs:
            pts.append((mmx(x1),mmy(y1)))
        print(f'pdf pour {pi} sub {si}: {len(pts)} pts, closed, bbox mm '
              f'x{min(p[0] for p in pts):.2f}-{max(p[0] for p in pts):.2f} y{min(p[1] for p in pts):.2f}-{max(p[1] for p in pts):.2f}')
for ri,r in enumerate(gb.regions):
    print(f'gerber region {ri}: {len(r)} pts bbox x{min(p[0] for p in r):.2f}-{max(p[0] for p in r):.2f} y{min(p[1] for p in r):.2f}-{max(p[1] for p in r):.2f}')

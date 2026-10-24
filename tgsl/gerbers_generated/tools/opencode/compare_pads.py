#!/usr/bin/env python3
"""Core validation: try_02 gerbers vs PCB.pdf features.
Transform: gx = A - s*ux ; gy = B + s*uy (mirror X, solder-side -> top view)."""
import sys, json, math
sys.path.insert(0,'.')
import numpy as np
from scipy.spatial import cKDTree
from parse_gerber import Gerber, Drill

S0 = 25.4/600.0  # mm per PDF unit
feat = json.load(open('pcb_features.json'))
pads_pdf = np.array([[p['cx'], p['cy']] for p in feat['pads']])
base='/home/nkout/projects/gold/tgsl/gerbers/try_02/TGSL-Geotech-v3-'
gb = Gerber(base+'B_Cu.gbl')
flash = np.array([[f[0], f[1]] for f in gb.flashes])

# initial A,B from bbox mirror fit
A = (flash[:,0].max() + S0*pads_pdf[:,0].min() + flash[:,0].min() + S0*pads_pdf[:,0].max())/2
B = (flash[:,1].max() - S0*pads_pdf[:,1].max() + flash[:,1].min() - S0*pads_pdf[:,1].min())/2
s = S0
for it in range(5):
    mapped = np.column_stack([A - s*pads_pdf[:,0], B + s*pads_pdf[:,1]])
    tree = cKDTree(flash)
    dist, idx = tree.query(mapped)
    good = dist < 0.3
    pu = pads_pdf[good]; pf = flash[idx[good]]
    # least squares: gx = A - s*ux ; gy = B + s*uy
    n = len(pu)
    M = np.zeros((2*n, 3)); v = np.zeros(2*n)
    M[:n,0] = 1; M[:n,2] = -pu[:,0]; v[:n] = pf[:,0]
    M[n:,1] = 1; M[n:,2] = pu[:,1];  v[n:] = pf[:,1]
    sol, *_ = np.linalg.lstsq(M, v, rcond=None)
    A, B, s = sol
print(f'transform: A={A:.6f} B={B:.6f} s={s:.8f} (ideal {S0:.8f})')
mapped = np.column_stack([A - s*pads_pdf[:,0], B + s*pads_pdf[:,1]])
tree = cKDTree(flash)
dist, idx = tree.query(mapped)
print(f'pads pdf={len(pads_pdf)} gerber flashes={len(flash)}')
print(f'match dist: max={dist.max()*1000:.1f}um mean={dist.mean()*1000:.2f}um >25um: {(dist>0.025).sum()}')
# any gerber flash unmatched?
used = np.zeros(len(flash), bool); used[idx] = True
print('gerber flashes unmatched:', (~used).sum())

def mm(u): return u*s
# pad size comparison
pad_rec = feat['pads']
size_err = []
for i,(d,k) in enumerate(zip(dist, idx)):
    p = pad_rec[i]
    gw = gb.flashes[k][2]
    pw = mm(p['w']); ph = mm(p['h'])
    size_err.append((i, p['shape'], pw, ph, gw, d))
round_err = [e for e in size_err if e[1]=='round']
sq = [e for e in size_err if e[1]=='square']
de = np.array([abs(e[4]-e[2]) for e in round_err])
print(f'round pads: diam err max={de.max()*1000:.1f}um  >40um: {(de>0.04).sum()}')
print('square pads in gerber as:')
for e in sq: print(f'  pdf {e[2]:.3f}x{e[3]:.3f}mm -> gerber C diam {e[4]:.3f}mm  poserr {e[5]*1000:.1f}um')

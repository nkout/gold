#!/usr/bin/env python3
"""Islands + clearance on B_Cu (raster), copper-to-edge, silk bbox check."""
import sys, json, math
sys.path.insert(0,'.')
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from parse_gerber import Gerber

base='/home/nkout/projects/gold/tgsl/gerbers/try_02/TGSL-Geotech-v3-'
gb = Gerber(base+'B_Cu.gbl')

ppm = 40.0  # px per mm -> 0.025mm/px
xs=[]; ys=[]
for x,y,d in gb.flashes: xs+=[x-d/2,x+d/2]; ys+=[y-d/2,y+d/2]
for x1,y1,x2,y2,w in gb.draws: xs+=[x1,x2]; ys+=[y1,y2]
for r in gb.regions:
    for x,y in r: xs.append(x); ys.append(y)
x0,x1,y0,y1 = min(xs)-1,max(xs)+1,min(ys)-1,max(ys)+1
W=int((x1-x0)*ppm)+4; H=int((y1-y0)*ppm)+4
img = Image.new('L',(W,H),0); d=ImageDraw.Draw(img)
def px(x,y): return ((x-x0)*ppm+2, H-((y-y0)*ppm+2))
for r in gb.regions: d.polygon([px(x,y) for x,y in r], fill=255)
for a,b2,c,e,w in gb.draws:
    wpx=w*ppm
    d.line([px(a,b2),px(c,e)],fill=255,width=int(round(wpx)))
    rx=wpx/2
    for (cx,cy) in [(a,b2),(c,e)]:
        X,Y=px(cx,cy); d.ellipse([X-rx,Y-rx,X+rx,Y+rx],fill=255)
for x,y,di in gb.flashes:
    X,Y=px(x,y); r=di*ppm/2; d.ellipse([X-r,Y-r,X+r,Y+r],fill=255)
mask = np.array(img)>0

# islands (pads+tracks+pours all touching = one island)
lab,n = ndimage.label(mask, structure=np.ones((3,3)))
print('B_Cu islands (incl pads):', n)

# min clearance between DIFFERENT islands: distance transform on background
# label background regions: for each bg px, nearest island id via distance transform with return_indices on island labels
bg = ~mask
dist, inds = ndimage.distance_transform_edt(bg, return_indices=True)
# for each bg px, look at nearest foreground label; find adjacent different-label pairs via dilation boundaries
lab_fg = lab
minsep = {}
H2,W2 = mask.shape
# boundary: bg px whose 8-neighborhood touches >=2 islands within small radius -> use watershed-ish: dilate each island by k and check overlap of labels
# simpler: compute for each bg pixel the nearest label; then find pixels where two different labels meet within 2px
nearest_lab = lab_fg[inds[0], inds[1]]
# smooth: where does nearest_lab change between adjacent pixels -> boundary between catchment zones
chg = np.zeros_like(bg)
chg[:, :-1] |= nearest_lab[:,1:] != nearest_lab[:,:-1]
chg[1:, :] |= nearest_lab[1:,:] != nearest_lab[:-1,:]
yy,xx = np.where(chg)
if len(yy):
    dd = dist[yy,xx]
    i = np.argmin(dd)
    # the two labels at the change
    la = nearest_lab[yy[i],xx[i]]; lb = nearest_lab[yy[i],xx[i]+1] if xx[i]+1<W2 else -1
    print('min gap: %.3f mm between islands %d and %d at (%.2f,%.2f)' % (2*dd[i]/ppm, la, lb, (xx[i]-2)/ppm+x0, (H-(yy[i]-2))/ppm+y0))
    q = np.argsort(dd)[:5]
    print('5 tightest gaps:', ['%.3f' % (2*dist[yy[j],xx[j]]/ppm) for j in q])

# copper to edge: gerber Edge_Cuts rect
ge = Gerber(base+'Edge_Cuts.gm1')
exs=[p for d2 in ge.draws for p in (d2[0],d2[2])]; eys=[p for d2 in ge.draws for p in (d2[1],d2[3])]
ex0,ex1,ey0,ey1 = min(exs),max(exs),min(eys),max(eys)
print('edge rect: %.3f x %.3f mm' % (ex1-ex0, ey1-ey0))
# min dist from copper mask to outside of edge rect (in mm, from copper extents)
cxs=[]; cys=[]
yy,xx = np.where(mask)
gx = (xx-2)/ppm+x0; gy=(H-(yy-2))/ppm+y0
print('copper-to-edge: left %.3f right %.3f top %.3f bottom %.3f mm' % (
    gx.min()-ex0, ex1-gx.max(), ey1-gy.max(), gy.min()-ey0))

# F_Cu islands -> nets with links (B islands merged by F links)
gf = Gerber(base+'F_Cu.gtl')
# union-find over B islands via pad sharing: pads same (x,y) are same island by construction (flashes touch copper)
# simpler: label F_Cu link connectivity via pads: link connects islands of its endpoint pads
flash = np.array([[f[0],f[1]] for f in gb.flashes])
from scipy.spatial import cKDTree
tree = cKDTree(flash)
# island id per pad: pad center px
pad_island = []
for x,y in flash:
    X,Y = int((x-x0)*ppm+2), int(H-((y-y0)*ppm+2))
    pad_island.append(lab[Y,X])
parent = {}
def find(a):
    parent.setdefault(a,a)
    while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
    return a
def union(a,b2):
    ra,rb = find(a),find(b2)
    if ra!=rb: parent[ra]=rb
for d2 in gf.draws:
    _,i1 = tree.query([d2[0],d2[1]]); _,i2 = tree.query([d2[2],d2[3]])
    union(pad_island[i1], pad_island[i2])
nets = len({find(pad_island[i]) for i in range(len(pad_island))})
# islands with no pads (pure pour/track islands not counted by pad method) - count all islands, then nets among pad-islands
print('nets after merging via links (pad-bearing islands):', nets)

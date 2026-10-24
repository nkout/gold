#!/usr/bin/env python3
"""Rasterize B_Cu gerber and compare with poppler render of PCB.pdf (mirrored)."""
import sys
sys.path.insert(0,'.')
import numpy as np
from PIL import Image, ImageDraw
from parse_gerber import Gerber

DPI = 600
S0 = 25.4/600
A, B, s = 160.463926, -99.511558, 0.04233333

gb = Gerber('/home/nkout/projects/gold/tgsl/gerbers/try_02/TGSL-Geotech-v3-B_Cu.gbl')

# gerber bbox
xs=[]; ys=[]
for x,y,d in gb.flashes: xs+=[x-d/2,x+d/2]; ys+=[y-d/2,y+d/2]
for x1,y1,x2,y2,w in gb.draws: xs+=[x1,x2]; ys+=[y1,y2]
for r in gb.regions:
    for x,y in r: xs.append(x); ys.append(y)
x0,x1,y0,y1 = min(xs)-1,min and max(xs)+1,min(ys)-1,max(ys)+1
ppm = DPI/25.4
W = int((x1-x0)*ppm)+4; H=int((y1-y0)*ppm)+4
img = Image.new('L',(W,H),0)
d = ImageDraw.Draw(img)
def px(x,y): return ((x-x0)*ppm+2, H-((y-y0)*ppm+2))
for r in gb.regions:
    d.polygon([px(x,y) for x,y in r], fill=255)
for x1d,y1d,x2d,y2d,w in gb.draws:
    wpx = w*ppm
    d.line([px(x1d,y1d),px(x2d,y2d)], fill=255, width=int(round(wpx)))
    rx=wpx/2
    for (cx,cy) in [(x1d,y1d),(x2d,y2d)]:
        X,Y=px(cx,cy); d.ellipse([X-rx,Y-rx,X+rx,Y+rx], fill=255)
for x,y,di in gb.flashes:
    X,Y=px(x,y); r=di*ppm/2
    d.ellipse([X-r,Y-r,X+r,Y+r], fill=255)
img.save('gerb_bcu.png')

# poppler render of PCB.pdf at same dpi; map: pdf page px -> gerber mm via transform
pop = Image.open(f'pcb600-1.png').convert('L')
pa = np.array(pop)
# pdf px -> units: px / (0.12*dpi/72) ; units -> gerber mm; -> gerber raster px
scale_pdf = 0.12*DPI/72.0
# target canvas same as gerber img
out = np.zeros((H,W), np.uint8)
# vectorized: for each poppler black px, compute gerber px
ys,xs = np.where(pa < 128)
ux = xs/scale_pdf; uy = (pa.shape[0]-ys)/scale_pdf
gx = A - s*ux; gy = B + s*uy
ix = ((gx-x0)*ppm+2).astype(int); iy = (H-((gy-y0)*ppm+2)).astype(int)
ok = (ix>=0)&(ix<W)&(iy>=0)&(iy<H)
out[iy[ok],ix[ok]] = 255
Image.fromarray(out).save('pdf_as_gerber.png')

g = np.array(img)
# dilate-compare: mismatch if difference beyond 1px tolerance
from scipy import ndimage
gd = ndimage.binary_dilation(g>0, iterations=2)
pd = ndimage.binary_dilation(out>0, iterations=2)
g_not_p = (g>0) & ~pd
p_not_g = (out>0) & ~gd
print('gerber px:', (g>0).sum(), 'pdf px:', (out>0).sum())
print('gerber-not-pdf px:', g_not_p.sum(), ' pdf-not-gerber px:', p_not_g.sum())
vis = np.zeros((H,W,3),np.uint8)
vis[(g>0)&(out>0)]=[255,255,255]
vis[g_not_p]=[255,0,0]; vis[p_not_g]=[0,80,255]
Image.fromarray(vis).save('diff_bcu.png')
print('px size: %.4f mm' % (1/ppm))
# report clusters of mismatches
for name,mask in [('GERBER-only',g_not_p),('PDF-only',p_not_g)]:
    lab,n = ndimage.label(mask)
    sizes = ndimage.sum(mask,lab,range(1,n+1))
    big = np.argsort(sizes)[::-1][:8]
    print(name, 'clusters:', n, 'top sizes:', [int(sizes[i]) for i in big if sizes[i]>3])
    for i in big:
        if sizes[i]<=3: continue
        yy,xx = np.where(lab==i+1)
        cx,cy = xx.mean(), yy.mean()
        mmx = (cx-2)/ppm+x0; mmy = (H-(cy-2))/ppm+y0
        print(f'   cluster {int(sizes[i])}px at gerber mm ({mmx:.2f},{mmy:.2f}) bbox_px {xx.min()}-{xx.max()} {yy.min()}-{yy.max()}')

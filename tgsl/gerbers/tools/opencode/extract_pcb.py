#!/usr/bin/env python3
"""Extract normalized features from PCB.pdf: pads, dots, tracks, fills.
Save to pcb_features.json (units = 1/600 inch, raw PDF coords)."""
import sys, json
sys.path.insert(0, '.')
from parse_pdf import extract_stream, parse_content, path_bbox, subpath_points

def flatten_subpath(sp, ncurve=8):
    """Return list of segments as (x1,y1,x2,y2) with curves flattened; note closed flag."""
    segs = []
    pts = []
    start = None
    cur = None
    closed = False
    for seg in sp:
        if seg[0] == 'L':
            x1,y1,x2,y2 = seg[1:]
            if cur is None: start = (x1,y1)
            segs.append((x1,y1,x2,y2)); cur = (x2,y2)
        elif seg[0] == 'C':
            x0,y0,x1,y1,x2,y2,x3,y3 = seg[1:]
            if cur is None: start = (x0,y0)
            px,py = x0,y0
            for k in range(1,ncurve+1):
                t=k/ncurve; mt=1-t
                x = mt**3*x0+3*mt*mt*t*x1+3*mt*t*t*x2+t**3*x3
                y = mt**3*y0+3*mt*mt*t*y1+3*mt*t*t*y2+t**3*y3
                segs.append((px,py,x,y)); px,py = x,y
            cur = (x3,y3)
        elif seg[0] == 'R':
            x,y,w,h = seg[1:]
            start=(x,y)
            segs += [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]
            cur = (x,y); closed = True
        elif seg[0] == 'H':
            if cur and start and cur != start:
                segs.append((cur[0],cur[1],start[0],start[1]))
            closed = True
    return segs, closed

def main():
    paths = []
    for s in extract_stream('/home/nkout/projects/gold/tgsl/design/PCB.pdf'):
        paths += parse_content(s)
    fills = [p for p in paths if p['kind']=='fill']
    strokes = [p for p in paths if p['kind']=='stroke']

    pads, dots, pours = [], [], []
    for p in fills:
        bb = path_bbox(p['subpaths'])
        w,h = bb[2]-bb[0], bb[3]-bb[1]
        cx,cy = (bb[0]+bb[2])/2,(bb[1]+bb[3])/2
        if p['gray'] == 1.0:
            dots.append(dict(cx=cx, cy=cy, w=w, h=h))
        elif max(w,h) > 60 and not (abs(w-70)<1.5 and abs(h-70)<1.5):
            # big polygon/rect pours (not the 70x70 square pads)
            segs_list = []
            for sp in p['subpaths']:
                segs, closed = flatten_subpath(sp)
                segs_list.append(segs)
            pours.append(dict(bbox=bb, subpaths=segs_list))
        else:
            shape = 'square' if (abs(w-h)<0.01 and abs(w-70)<1.5) else 'round'
            pads.append(dict(cx=cx, cy=cy, w=w, h=h, shape=shape))

    # dot containment -> assign dot to pad
    for pad in pads:
        pad['dot'] = None
        for d in dots:
            if abs(d['cx']-pad['cx'])<1 and abs(d['cy']-pad['cy'])<1:
                pad['dot'] = max(d['w'], d['h']); break

    tracks = []
    for p in strokes:
        if p['width'] == 1.0: continue  # frame + pad overpaint
        for sp in p['subpaths']:
            segs, closed = flatten_subpath(sp)
            for s in segs:
                tracks.append(dict(seg=s, width=p['width']))

    json.dump(dict(pads=pads, dots=dots, pours=pours, tracks=tracks),
              open('pcb_features.json','w'))
    print('pads:', len(pads), ' (square:', sum(1 for p in pads if p['shape']=='square'),')',
          ' dots:', len(dots), ' pours:', len(pours), ' track segs:', len(tracks))
    import collections
    print('pads w/o dot:', sum(1 for p in pads if p['dot'] is None))
    print('pour bboxes:', [[round(v,1) for v in p['bbox']] for p in pours])
    print('track width counts:', collections.Counter(t['width'] for t in tracks))
    print('pad size counts:', collections.Counter((round(p['w']),round(p['h'])) for p in pads).most_common())
    print('dot size counts:', collections.Counter(round(p['dot'],1) for p in pads if p['dot']).most_common())

main()

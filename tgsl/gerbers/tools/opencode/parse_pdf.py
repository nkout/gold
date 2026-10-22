#!/usr/bin/env python3
"""Parse vector content of TGSL PDFs (PCB.pdf, Placement OC.pdf).
Units in stream: 1/600 inch (cm scale 0.12 = 72/600). Output geometry in raw units.
"""
import re, zlib, sys, json

def extract_stream(path):
    data = open(path, 'rb').read()
    # collect ALL streams (some pdfs have several)
    out = []
    for m in re.finditer(rb'stream\r?\n', data):
        end = data.find(b'endstream', m.end())
        chunk = data[m.end():end]
        try:
            out.append(zlib.decompress(chunk).decode('latin1'))
        except Exception:
            pass
    return out

def parse_content(text):
    """Return list of painted paths: dict(kind='stroke'|'fill', width, gray, subpaths)
    subpath = list of segments; seg = ('L', x1,y1,x2,y2) | ('C', x1..y4) | ('R', x,y,w,h)
    Points stored absolute."""
    toks = text.split()
    i = 0
    paths = []
    cur = []          # current subpath list
    sp = None         # current subpath segments
    cp = None         # current point
    width = 1.0
    g_fill = 0.0; g_stroke = 0.0
    n = len(toks)
    def isnum(t):
        try: float(t); return True
        except ValueError: return False
    stack = []
    while i < n:
        t = toks[i]
        if isnum(t):
            stack.append(float(t)); i += 1; continue
        op = t
        if op == 'w':
            width = stack.pop()
        elif op == 'g':
            g_fill = stack.pop()
        elif op == 'G':
            g_stroke = stack.pop()
        elif op == 'm':
            y = stack.pop(); x = stack.pop()
            if sp is not None:
                cur.append(sp)
            sp = []; cp = (x, y)
        elif op == 'l':
            y = stack.pop(); x = stack.pop()
            sp.append(('L', cp[0], cp[1], x, y)); cp = (x, y)
        elif op == 'c':
            y3=stack.pop(); x3=stack.pop(); y2=stack.pop(); x2=stack.pop(); y1=stack.pop(); x1=stack.pop()
            sp.append(('C', cp[0], cp[1], x1, y1, x2, y2, x3, y3)); cp = (x3, y3)
        elif op == 'h':
            # closepath: mark closed
            if sp is not None:
                sp.append(('H',))
        elif op == 're':
            h=stack.pop(); w=stack.pop(); y=stack.pop(); x=stack.pop()
            if sp is not None:
                cur.append(sp)
            sp = [('R', x, y, w, h)]; cp = (x, y)
        elif op in ('S', 's'):
            if sp is not None: cur.append(sp)
            paths.append(dict(kind='stroke', width=width, gray=g_stroke, subpaths=cur))
            cur = []; sp = None; cp = None
        elif op in ('f', 'f*', 'F'):
            if sp is not None: cur.append(sp)
            paths.append(dict(kind='fill', width=width, gray=g_fill, subpaths=cur, rule=op))
            cur = []; sp = None; cp = None
        # else ignore (q,Q,cm,J,j, etc. — we already know the cm)
        stack = []
        i += 1
    return paths

def subpath_points(sp, ncurve=16):
    """Flatten subpath to points (for bbox)."""
    pts = []
    for seg in sp:
        if seg[0] == 'L':
            pts.append((seg[1], seg[2])); pts.append((seg[3], seg[4]))
        elif seg[0] == 'C':
            x0,y0,x1,y1,x2,y2,x3,y3 = seg[1:]
            for k in range(ncurve+1):
                t = k/ncurve
                mt = 1-t
                x = mt**3*x0 + 3*mt*mt*t*x1 + 3*mt*t*t*x2 + t**3*x3
                y = mt**3*y0 + 3*mt*mt*t*y1 + 3*mt*t*t*y2 + t**3*y3
                pts.append((x, y))
        elif seg[0] == 'R':
            x,y,w,h = seg[1:]
            pts += [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
    return pts

def path_bbox(subpaths):
    pts = []
    for sp in subpaths:
        pts += subpath_points(sp)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)

if __name__ == '__main__':
    path = sys.argv[1]
    streams = extract_stream(path)
    print(f'streams: {len(streams)}', file=sys.stderr)
    paths = []
    for s in streams:
        paths += parse_content(s)
    print(f'painted paths: {len(paths)}', file=sys.stderr)
    fills = [p for p in paths if p['kind']=='fill']
    strokes = [p for p in paths if p['kind']=='stroke']
    print(f'fills: {len(fills)} strokes: {len(strokes)}', file=sys.stderr)
    # summarize fills by bbox size
    import collections
    info = []
    for p in fills:
        bb = path_bbox(p['subpaths'])
        info.append((bb[2]-bb[0], bb[3]-bb[1], p['gray'], len(p['subpaths'])))
    sizes = collections.Counter((round(w), round(h)) for w,h,g,ns in info)
    print('fill bbox size histogram (w,h):', sizes.most_common(20), file=sys.stderr)
    sw = collections.Counter(round(p['width'],2) for p in strokes)
    print('stroke widths:', sw.most_common(), file=sys.stderr)

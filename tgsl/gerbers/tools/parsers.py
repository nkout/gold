"""Parsers for the PCB.pdf content stream and the gerber/drill files."""
import re, math

U2MM = 25.4 / 600.0  # PDF user unit (after 0.12 cm) = 1/600 inch


def bez(p0, p1, p2, p3, n=16):
    pts = []
    for i in range(1, n + 1):
        t = i / n
        a = (1 - t) ** 3; b = 3 * (1 - t) ** 2 * t; c = 3 * (1 - t) * t * t; d = t ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


def parse_pdf_stream(path):
    """Returns list of drawing items in raw stream units (1/600 in)."""
    toks = open(path, 'rb').read().decode('latin-1').split()
    stack = []
    items = []
    lw = 1.0; sc = 0.0; fc = 0.0
    path_ = []      # list of subpaths; each subpath dict(pts=[], curves=int, closed=bool)
    cur = None
    def flush(op):
        nonlocal path_, cur
        items.append(dict(op=op, width=lw, color=(sc if op == 'S' else fc),
                          subpaths=path_))
        path_ = []; cur = None
    for t in toks:
        if re.fullmatch(r'-?[0-9.]+', t):
            stack.append(float(t)); continue
        a = stack; stack = []
        if t == 'm':
            cur = dict(pts=[(a[0], a[1])], curves=0, closed=False, ctrl=[]); path_.append(cur)
        elif t == 'l':
            cur['pts'].append((a[0], a[1]))
        elif t == 'c':
            p0 = cur['pts'][-1]
            cur['ctrl'].append((p0, (a[0], a[1]), (a[2], a[3]), (a[4], a[5])))
            cur['pts'].extend(bez(p0, (a[0], a[1]), (a[2], a[3]), (a[4], a[5])))
            cur['curves'] += 1
        elif t == 'y':
            p0 = cur['pts'][-1]
            cur['ctrl'].append((p0, (a[0], a[1]), (a[2], a[3]), (a[2], a[3])))
            cur['pts'].extend(bez(p0, (a[0], a[1]), (a[2], a[3]), (a[2], a[3])))
            cur['curves'] += 1
        elif t == 'v':
            p0 = cur['pts'][-1]
            cur['ctrl'].append((p0, p0, (a[0], a[1]), (a[2], a[3])))
            cur['pts'].extend(bez(p0, p0, (a[0], a[1]), (a[2], a[3])))
            cur['curves'] += 1
        elif t == 'h':
            cur['closed'] = True
        elif t == 're':
            x, y, w, h = a
            cur = dict(pts=[(x, y), (x + w, y), (x + w, y + h), (x, y + h)], curves=0,
                       closed=True, ctrl=[], rect=(x, y, w, h))
            path_.append(cur)
        elif t in ('S', 's'):
            flush('S')
        elif t in ('f', 'f*', 'F'):
            flush('f')
        elif t == 'n':
            path_ = []; cur = None
        elif t == 'w':
            lw = a[0]
        elif t == 'g':
            fc = a[0]
        elif t == 'G':
            sc = a[0]
        elif t == 'rg':
            fc = tuple(a)
        elif t == 'RG':
            sc = tuple(a)
        elif t in ('q', 'Q', 'J', 'j', 'cm', 'd', 'M', 'i'):
            pass
        else:
            raise ValueError('unhandled op ' + t)
    return items


def circle_of(sp):
    """If subpath is a 4-bezier circle, return (cx, cy, diameter)."""
    if sp['curves'] != 4 or len(sp['ctrl']) != 4:
        return None
    ends = [c[0] for c in sp['ctrl']]
    xs = [p[0] for p in ends]; ys = [p[1] for p in ends]
    cx = (max(xs) + min(xs)) / 2; cy = (max(ys) + min(ys)) / 2
    d = max(max(xs) - min(xs), max(ys) - min(ys))
    return (cx, cy, d)


def parse_gerber(path):
    txt = open(path).read()
    aps = {}
    for m in re.finditer(r'%ADD(\d+)C,([0-9.]+)\*%', txt):
        aps[int(m.group(1))] = float(m.group(2))
    body = re.sub(r'%[^%]*%', '', txt)
    cmds = [c.strip() for c in body.split('*') if c.strip()]
    x = y = 0.0; ap = None
    flashes = []; draws = []; regions = []
    in_region = False; region = None
    for c in cmds:
        if c in ('G01', 'M02'):
            continue
        if c == 'G36':
            in_region = True; region = []; continue
        if c == 'G37':
            in_region = False; regions.append(region); region = None; continue
        m = re.fullmatch(r'D(\d+)', c)
        if m and int(m.group(1)) >= 10:
            ap = int(m.group(1)); continue
        m = re.fullmatch(r'(?:G0?1)?(?:X(-?\d+))?(?:Y(-?\d+))?D0?([123])', c)
        if not m:
            raise ValueError('unhandled gerber cmd %r in %s' % (c, path))
        nx = int(m.group(1)) / 1e6 if m.group(1) else x
        ny = int(m.group(2)) / 1e6 if m.group(2) else y
        d = int(m.group(3))
        if in_region:
            if d == 2:
                region.append([(nx, ny)])
            elif d == 1:
                region[-1].append((nx, ny))
            else:
                raise ValueError('flash in region')
        else:
            if d == 1:
                draws.append(((x, y), (nx, ny), aps[ap]))
            elif d == 3:
                flashes.append(((nx, ny), aps[ap]))
        x, y = nx, ny
    return dict(aps=aps, flashes=flashes, draws=draws, regions=regions)


def parse_drill(path):
    tools = {}; holes = []; tool = None
    for line in open(path):
        line = line.strip()
        m = re.fullmatch(r'T(\d+)C([0-9.]+)', line)
        if m:
            tools[int(m.group(1))] = float(m.group(2)); continue
        m = re.fullmatch(r'T(\d+)', line)
        if m:
            tool = int(m.group(1)); continue
        m = re.fullmatch(r'X(-?[0-9.]+)Y(-?[0-9.]+)', line)
        if m:
            holes.append(((float(m.group(1)), float(m.group(2))), tools[tool]))
    return tools, holes

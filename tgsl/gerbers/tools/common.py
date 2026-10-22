"""Shared helpers for the TGSL gerber checks.

Source PDFs are read from ../../design (override with TGSL_DESIGN).
Extracted PDF streams, renders and cached copper islands go to TGSL_WORK
(default: $TMPDIR/tgsl_check), never into the repo.
"""
import os, re, zlib, math, pickle, hashlib, functools
import numpy as np
from parsers import parse_pdf_stream, parse_gerber, parse_drill, circle_of, U2MM

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.environ.get('TGSL_DESIGN', os.path.normpath(os.path.join(HERE, '..', '..', 'design')))
WORK = os.environ.get('TGSL_WORK', os.path.join(os.environ.get('TMPDIR', '/tmp'), 'tgsl_check'))
PREFIX = 'TGSL-Geotech-v3-'
# Placement OC.pdf is not mirrored. Its x offset is always the PCB.pdf offset minus this constant
# (checked on try_02 and try_03): x_mm = u*U2MM + (PCB_TX - OC_DX), y_mm = u*U2MM + PCB_TY.
OC_DX = 209.724


def layer(try_dir, name):
    return os.path.join(try_dir, PREFIX + name)


@functools.lru_cache(None)
def pdf_items(pdf_name):
    """Parsed drawing items of a design PDF (raw units, 1/600 in)."""
    os.makedirs(WORK, exist_ok=True)
    out = os.path.join(WORK, pdf_name.replace(' ', '_') + '.content.txt')
    if not os.path.exists(out):
        data = open(os.path.join(DESIGN, pdf_name), 'rb').read()
        best = b''
        for m in re.finditer(rb'stream\r?\n', data):
            end = data.find(b'endstream', m.end())
            try:
                dec = zlib.decompress(data[m.end():end])
            except Exception:
                continue
            if len(dec) > len(best):
                best = dec
        open(out, 'wb').write(best)
    return parse_pdf_stream(out)


def pdf_pads(pdf_name):
    """(cx, cy, d) of every black filled 4-curve circle (copper pads)."""
    return [circle_of(it['subpaths'][0]) for it in pdf_items(pdf_name)
            if it['op'] == 'f' and it['color'] == 0 and len(it['subpaths']) == 1 and circle_of(it['subpaths'][0])]


@functools.lru_cache(None)
def fit(try_dir):
    """Fit PCB.pdf -> gerber: x = TX - u*U2MM (mirrored), y = u*U2MM + TY, using pad centres."""
    P = np.array([(p[0], p[1]) for p in pdf_pads('PCB.pdf')])
    Q = np.array([f[0] for f in parse_gerber(layer(try_dir, 'B_Cu.gbl'))['flashes']])
    TX = Q[:, 0].mean() + P[:, 0].mean() * U2MM
    TY = Q[:, 1].mean() - P[:, 1].mean() * U2MM
    for _ in range(3):
        M = np.c_[TX - P[:, 0] * U2MM, P[:, 1] * U2MM + TY]
        idx = [int(np.argmin(((Q - m) ** 2).sum(1))) for m in M]
        TX = (Q[idx, 0] + P[:, 0] * U2MM).mean()
        TY = (Q[idx, 1] - P[:, 1] * U2MM).mean()
    M = np.c_[TX - P[:, 0] * U2MM, P[:, 1] * U2MM + TY]
    err = np.sqrt(((Q[idx] - M) ** 2).sum(1))
    return dict(TX=float(TX), TY=float(TY), OC_TX=float(TX - OC_DX), OC_TY=float(TY),
                maxerr=float(err.max()), unique=len(set(idx)), n=len(P))


def pcb_T(try_dir):
    f = fit(try_dir)
    return lambda p: (f['TX'] - p[0] * U2MM, p[1] * U2MM + f['TY'])


def oc_T(try_dir):
    f = fit(try_dir)
    return lambda p: (p[0] * U2MM + f['OC_TX'], p[1] * U2MM + f['OC_TY'])


def copper(try_dir):
    """Shapely copper islands of both layers, board rectangle, pads, pad->island maps and nets.
    Cached in WORK, keyed by the gerber file contents."""
    h = hashlib.sha1()
    for n in ('B_Cu.gbl', 'F_Cu.gtl', 'PTH.drl', 'Edge_Cuts.gm1'):
        h.update(open(layer(try_dir, n), 'rb').read())
    cache = os.path.join(WORK, 'copper_%s.pkl' % h.hexdigest()[:16])
    if os.path.exists(cache):
        return pickle.load(open(cache, 'rb'))
    from shapely.geometry import Point, LineString, Polygon, box
    from shapely.ops import unary_union
    from gerbonara import GerberFile, ExcellonFile
    from gerbonara.utils import MM
    from gerbonara.graphic_primitives import Circle, Line, ArcPoly

    def geoms(path):
        out = []
        for o in GerberFile.open(path).objects:
            for p in o.to_primitives(unit=MM):
                if isinstance(p, Circle):
                    g = Point(p.x, p.y).buffer(p.r, 64)
                elif isinstance(p, Line):
                    a, b = (p.x1, p.y1), (p.x2, p.y2)
                    g = LineString([a, b]).buffer(p.width / 2, 64) if a != b else Point(a).buffer(p.width / 2, 64)
                elif isinstance(p, ArcPoly):
                    g = Polygon(p.outline).buffer(0)
                else:
                    raise SystemExit('unhandled primitive %r' % p)
                out.append((type(o).__name__, g, p))
        return out

    def islands(gs):
        U = unary_union([g for _, g, _ in gs])
        return list(U.geoms) if U.geom_type == 'MultiPolygon' else [U]

    B = geoms(layer(try_dir, 'B_Cu.gbl')); F = geoms(layer(try_dir, 'F_Cu.gtl'))
    E = [p for _, _, p in geoms(layer(try_dir, 'Edge_Cuts.gm1'))]
    xs = [v for p in E for v in (p.x1, p.x2)]; ys = [v for p in E for v in (p.y1, p.y2)]
    board = box(min(xs), min(ys), max(xs), max(ys))
    holes = [((o.x, o.y), o.tool.diameter) for o in ExcellonFile.open(layer(try_dir, 'PTH.drl')).objects]
    IB, IF = islands(B), islands(F)
    pads = [((p.x, p.y), p.r * 2) for k, g, p in B if k == 'Flash']

    def owner(isl, pt):
        for i, I in enumerate(isl):
            if I.buffer(1e-6).contains(Point(pt)):
                return i
    pb = [owner(IB, p) for p, _ in pads]; pf = [owner(IF, p) for p, _ in pads]
    par = list(range(len(IB)))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for fi in set(pf):
        bs = sorted({pb[i] for i in range(len(pads)) if pf[i] == fi})
        for b in bs[1:]:
            par[find(b)] = find(bs[0])
    net = [find(i) for i in range(len(IB))]
    res = dict(IB=IB, IF=IF, board=board, holes=holes, pads=pads, pb=pb, pf=pf, net=net)
    os.makedirs(WORK, exist_ok=True)
    pickle.dump(res, open(cache, 'wb'))
    return res


def segdist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def seg_err(a, b, p, q):
    """Endpoint error between segment a-b and p-q, either direction."""
    d = math.dist
    return min(max(d(a, p), d(b, q)), max(d(a, q), d(b, p)))


def head(title):
    print('\n=== %s ===' % title)

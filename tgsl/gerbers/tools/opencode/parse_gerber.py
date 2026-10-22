#!/usr/bin/env python3
"""Parse RS-274X gerber (subset: FS, MO, AD circle apertures, D01/D02/D03, G36/G37 regions)
and Excellon drill files. Geometry in mm (floats)."""
import re

class Gerber:
    def __init__(self, path):
        self.flashes = []   # (x,y,aperture_diam)
        self.draws = []     # (x1,y1,x2,y2,width)
        self.regions = []   # list of polygon (list of (x,y)) contours; first = outline, rest = holes
        self.apertures = {} # dnum -> diam (circle only)
        self.parse(path)

    def parse(self, path):
        text = open(path).read()
        # strip block comments G04...*
        text = re.sub(r'G04[^*]*\*', '', text)
        # format
        m = re.search(r'%FSLAX(\d)(\d)Y(\d)(\d)\*%', text)
        xi, xd, yi, yd = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
        def conv(xs, ys):
            v = int(xs) / 10**xd, int(ys) / 10**yd
            return v
        for am in re.finditer(r'%ADD(\d+)C,([\d.]+)\*%', text):
            self.apertures[int(am.group(1))] = float(am.group(2))
        cur_ap = None
        x = y = 0.0
        in_region = False
        region = None
        # tokenize coordinates
        for tm in re.finditer(r'(X(-?\d+)Y(-?\d+)D0?([123])|D(\d+)\*|G36\*|G37\*|G0?1\*|G0?2\*|G0?3\*|M02\*|D0?([123])\*)', text):
            tok = tm.group(0)
            if tok.startswith('X'):
                nx, ny = conv(tm.group(2), tm.group(3))
                d = tm.group(4)
                if in_region:
                    if d == '2':
                        if region is not None and len(region) > 1:
                            self.regions.append(region)
                        region = [(nx, ny)]
                    else:
                        if region is None: region = []
                        region.append((nx, ny))
                else:
                    if d == '1':
                        if cur_ap is None: raise ValueError('draw with no aperture')
                        self.draws.append((x, y, nx, ny, self.apertures[cur_ap]))
                    elif d == '3':
                        self.flashes.append((nx, ny, self.apertures[cur_ap]))
                x, y = nx, ny
            elif tok == 'G36*':
                in_region = True; region = None
            elif tok == 'G37*':
                if region is not None and len(region) > 1:
                    self.regions.append(region)
                in_region = False; region = None
            elif tok.startswith('D') and tok.endswith('*') and len(tok) > 2 and tok[1:-1].isdigit() and int(tok[1:-1]) >= 10:
                cur_ap = int(tok[1:-1])

class Drill:
    def __init__(self, path):
        self.tools = {}   # Tn -> diam mm
        self.hits = []    # (x,y, tool_diam)
        self.parse(path)
    def parse(self, path):
        cur = None
        for line in open(path):
            line = line.strip()
            m = re.match(r'T(\d+)C([\d.]+)', line)
            if m:
                self.tools[f'T{m.group(1)}'] = float(m.group(2)); continue
            m = re.match(r'T(\d+)$', line)
            if m:
                cur = self.tools[f'T{m.group(1)}']; continue
            m = re.match(r'X(-?[\d.]+)Y(-?[\d.]+)', line)
            if m and cur is not None:
                self.hits.append((float(m.group(1)), float(m.group(2)), cur))

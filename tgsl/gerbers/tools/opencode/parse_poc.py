#!/usr/bin/env python3
"""Parse Placement OC.pdf: board outline (black thick), red silk, red wire links."""
import sys, json
sys.path.insert(0,'.')
from parse_pdf import extract_stream

def parse_colored(text):
    toks = text.split()
    i=0; paths=[]; cur=[]; sp=None; cp=None
    width=1.0; stroke_col=(0,0,0); fill_col=(0,0,0)
    stack=[]
    def isnum(t):
        try: float(t); return True
        except ValueError: return False
    while i < len(toks):
        t = toks[i]
        if isnum(t): stack.append(float(t)); i+=1; continue
        if t=='w': width=stack.pop()
        elif t=='G': stroke_col=(stack.pop(),)*3
        elif t=='g': fill_col=(stack.pop(),)*3
        elif t=='RG': b=stack.pop(); g=stack.pop(); r=stack.pop(); stroke_col=(r,g,b)
        elif t=='rg': b=stack.pop(); g=stack.pop(); r=stack.pop(); fill_col=(r,g,b)
        elif t=='m':
            y=stack.pop(); x=stack.pop()
            if sp is not None: cur.append(sp)
            sp=[]; cp=(x,y)
        elif t=='l':
            y=stack.pop(); x=stack.pop()
            sp.append((cp[0],cp[1],x,y)); cp=(x,y)
        elif t=='c':
            y3=stack.pop();x3=stack.pop();y2=stack.pop();x2=stack.pop();y1=stack.pop();x1=stack.pop()
            sp.append(('C',cp[0],cp[1],x1,y1,x2,y2,x3,y3)); cp=(x3,y3)
        elif t=='h':
            if sp is not None: sp.append(('H',))
        elif t=='re':
            h=stack.pop();w=stack.pop();y=stack.pop();x=stack.pop()
            if sp is not None: cur.append(sp)
            sp=[(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y),('H',)]; cp=(x,y)
        elif t in ('S','s'):
            if sp is not None: cur.append(sp)
            paths.append(dict(kind='stroke',width=width,col=stroke_col,subpaths=cur))
            cur=[];sp=None;cp=None
        elif t in ('f','f*','F'):
            if sp is not None: cur.append(sp)
            paths.append(dict(kind='fill',width=width,col=fill_col,subpaths=cur))
            cur=[];sp=None;cp=None
        stack=[]; i+=1
    return paths

paths = []
for s in extract_stream('/home/nkout/projects/gold/tgsl/design/Placement OC.pdf'):
    paths += parse_colored(s)

black_strokes = [p for p in paths if p['kind']=='stroke' and p['col']==(0,0,0)]
red_strokes = [p for p in paths if p['kind']=='stroke' and p['col']==(1.0,0,0)]
red_fills = [p for p in paths if p['kind']=='fill' and p['col']==(1.0,0,0)]
print('black strokes:', len(black_strokes), 'red strokes:', len(red_strokes), 'red fills:', len(red_fills))
import collections
print('black widths:', collections.Counter(p['width'] for p in black_strokes))
print('red widths:', collections.Counter(p['width'] for p in red_strokes))

# board outline = black w=18.72 strokes
outline = [p for p in black_strokes if p['width']==18.72]
print('\noutline strokes:', len(outline))
for p in outline:
    for sp in p['subpaths']:
        pts=[]
        for seg in sp:
            if seg[0]=='C': pts.append(('CURVE',))
            elif seg[0]=='H': pass
            else: pts.append((seg[0],seg[1]))
        print('  subpath pts:', len(pts), pts[:30])

json_paths = []
for p in paths:
    json_paths.append(dict(kind=p['kind'],width=p['width'],col=list(p['col']),subpaths=p['subpaths']))
json.dump(json_paths, open('poc_paths.json','w'))
print('saved poc_paths.json')

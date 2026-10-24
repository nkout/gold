"""File-format checks with gerbonara (an independent reader): parse, layer detection, X2 tags, endings.
Usage: python3 check_format.py <try_dir>"""
import sys, glob, os, re, collections, warnings
from gerbonara import GerberFile, ExcellonFile, LayerStack
from gerbonara.utils import MM
from common import head

G = sys.argv[1]
head('Gerber files')
with warnings.catch_warnings(record=True) as wl:
    warnings.simplefilter('always')
    for f in sorted(glob.glob(os.path.join(G, '*.g*'))):
        txt = open(f).read()
        g = GerberFile.open(f)
        c = dict(collections.Counter(type(o).__name__ for o in g.objects))
        x2 = re.findall(r'%TF\.(FileFunction|FilePolarity),([^*]*)\*%', txt)
        fmt = re.search(r'%FS([^*]*)\*%', txt).group(1); unit = re.search(r'%MO([^*]*)\*%', txt).group(1)
        print('%-32s %s  FS %s MO %s  %s  ends M02: %s' % (os.path.basename(f), c, fmt, unit, dict(x2), txt.rstrip().endswith('M02*')))
    e = ExcellonFile.open(os.path.join(G, 'TGSL-Geotech-v3-PTH.drl'))
    c = collections.Counter((round(o.tool.diameter, 3)) for o in e.objects)
    txt = open(os.path.join(G, 'TGSL-Geotech-v3-PTH.drl')).read()
    print('%-32s holes %s, header %s, ends M30: %s' % ('TGSL-Geotech-v3-PTH.drl', dict(c), [l for l in txt.splitlines()[:4]], txt.rstrip().endswith('M30')))
wl = [w for w in wl if not issubclass(w.category, ResourceWarning)]
print('gerbonara parse warnings: %d %s' % (len(wl), [str(w.message) for w in wl[:5]]))
head('Layer auto-detection (what a fab upload would see)')
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    st = LayerStack.open(G)
for k, v in st.graphic_layers.items():
    print('  %-22s %s' % (' '.join(k), v.original_path.name))
print('  %-22s %s' % ('drill', [l.original_path.name for l in st.drill_layers]))
other = [os.path.basename(f) for f in glob.glob(os.path.join(G, '*')) if not re.search(r'\.(g[a-z0-9]+|drl)$', f)]
print('non-fab files in the folder (leave out of the upload zip):', other)

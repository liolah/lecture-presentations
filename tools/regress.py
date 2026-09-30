"""Regression check for engine / refactor changes: compare two builds of the same deck slide by slide.

Usage:  python tools/regress.py OLD.pptx NEW.pptx
Ignores what PowerPoint randomises per build (shape/slide creationId GUIDs, relationship ids).
Rule: any change to tools/ must leave every active family's deck output identical.
"""
import sys, zipfile, re
from lxml import etree
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def slides(path):
    z = zipfile.ZipFile(path)
    pres = etree.fromstring(z.read('ppt/presentation.xml'))
    rid = {r.get('Id'): r.get('Target') for r in etree.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
    out = []
    for s in pres.findall('.//p:sldId', NS):
        x = z.read('ppt/' + rid[s.get('{%s}id' % NS['r'])]).decode('utf-8')
        x = re.sub(r'<(a16|p14):creationId[^>]*/>', '', x)   # random per-build ids (shape + slide)
        x = re.sub(r'r:(embed|id)="rId\d+"', '', x)
        out.append(x)
    return out
a, b = slides(sys.argv[1]), slides(sys.argv[2])
assert len(a) == len(b), (len(a), len(b))
bad = [i + 1 for i, (x, y) in enumerate(zip(a, b)) if x != y]
print(f'{len(a)} slides compared; differing (non-GUID): {bad or "none"}')
if bad:
    x, y = a[bad[0] - 1], b[bad[0] - 1]
    i = next(k for k in range(min(len(x), len(y))) if x[k] != y[k])
    print('first diff in slide', bad[0], 'at', i, ':\n A:', x[i - 120:i + 120], '\n B:', y[i - 120:i + 120])

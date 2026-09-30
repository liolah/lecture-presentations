"""Design lint: check a deck against ITS FAMILY's tokens without rendering (cheap; run before visual review).

Usage:  python tools/lint.py DECK.pptx [--family NAME] [--slides 3-8] [--quiet]
The family comes from the deck's `deck_family` property, else --family (see tools/family.py).
Checks: off-token / retired fonts & colors, text contrast on bg, tiny text, off-canvas shapes,
        LaTeX/paste residue, empty text boxes. Exit code 1 if any ERROR.
"""
import argparse, json, os, re, sys, zipfile
from lxml import etree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import family
T = None  # loaded per deck in main()
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
E = 12700  # EMU per point


def lum(h):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def palette():
    c = T['color']
    s = {v.upper() for k, v in c.items() if isinstance(v, str)} | {v.upper() for v in c['link']}
    s |= {'FFFFFF', '000000'}
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('deck'); ap.add_argument('--slides'); ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--family')
    a = ap.parse_args()
    global T
    fam = family.resolve(a.family, deck=a.deck)
    T = family.tokens(fam)
    print(f'-- family: {fam}')
    z = zipfile.ZipFile(a.deck)
    pres = etree.fromstring(z.read('ppt/presentation.xml'))
    rid = {r.get('Id'): r.get('Target') for r in etree.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
    parts = ['ppt/' + rid[s.get('{%s}id' % NS['r'])] for s in pres.findall('.//p:sldId', NS)]
    sz = pres.find('p:sldSz', NS); W, H = int(sz.get('cx')) / E, int(sz.get('cy')) / E
    sel = None
    if a.slides:
        sel = set()
        for p in a.slides.split(','):
            x, _, y = p.partition('-'); sel.update(range(int(x), int(y or x) + 1))
    allowed = set(T['allowed_fonts']); retired_f = set(T['retired']['fonts'])
    retired_c = {c.upper() for c in T['retired']['colors']}; pal = palette()
    bg = T['color']['bg']; muted = T['color']['muted'].upper()
    errors = warns = 0
    for n, part in enumerate(parts, 1):
        if sel and n not in sel: continue
        x = etree.fromstring(z.read(part))
        issues = []
        for sp in x.iter('{%s}sp' % NS['p'], '{%s}cxnSp' % NS['p'], '{%s}pic' % NS['p']):
            nv = sp.find('.//p:cNvPr', NS); name = nv.get('name') if nv is not None else '?'
            if name.startswith('chrome'): continue
            off = sp.find('p:spPr/a:xfrm/a:off', NS); ext = sp.find('p:spPr/a:xfrm/a:ext', NS)
            in_group = sp.getparent().tag.endswith('grpSp') and sp.getparent().getparent().tag.endswith('grpSp')
            if off is not None and ext is not None and not in_group:
                x0, y0 = int(off.get('x')) / E, int(off.get('y')) / E
                x1, y1 = x0 + int(ext.get('cx')) / E, y0 + int(ext.get('cy')) / E
                if x0 < -2 or y0 < -2 or x1 > W + 2 or y1 > H + 2:
                    issues.append(('ERROR', f'off-canvas "{name}" ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f})'))
            fill = sp.find('p:spPr/a:solidFill/a:srgbClr', NS)
            has_fill = fill is not None
            if has_fill and fill.get('val').upper() in retired_c:
                issues.append(('WARN', f'retired fill {fill.get("val")} "{name}"'))
            txt = ''.join(t.text or '' for t in sp.findall('.//a:t', NS))
            if sp.tag.endswith('}sp') and sp.find('.//p:ph', NS) is None and sp.find('p:txBody', NS) is not None \
                    and not txt.strip() and not has_fill and sp.find('p:spPr/a:ln/a:solidFill', NS) is None:
                issues.append(('WARN', f'empty text box "{name}"'))
            if re.search(r'\$\\|\\(oplus|frac|overline|bar)\b', txt):
                issues.append(('ERROR', f'LaTeX residue "{name}": {txt[:50]!r}'))
            for r in sp.iter('{%s}r' % NS['a']):
                rp = r.find('a:rPr', NS); t = (r.findtext('a:t', namespaces=NS) or '')
                if not t.strip() or rp is None: continue
                lat = rp.find('a:latin', NS)
                if lat is not None:
                    fn = lat.get('typeface')
                    if fn in retired_f:
                        issues.append(('ERROR', f'retired font {fn} "{name}": {t[:30]!r}'))
                    elif not fn.startswith('+') and fn not in allowed:
                        issues.append(('WARN', f'off-token font {fn} "{name}"'))
                s = rp.get('sz')
                if s and int(s) < 1400:
                    issues.append(('WARN', f'tiny text {int(s)/100:g}pt "{name}": {t[:30]!r}'))
                c = rp.find('a:solidFill/a:srgbClr', NS)
                if c is not None:
                    v = c.get('val').upper()
                    if v in retired_c:
                        issues.append(('ERROR', f'retired color {v} "{name}": {t[:30]!r}'))
                    elif v not in pal:
                        issues.append(('WARN', f'off-token color {v} "{name}": {t[:30]!r}'))
                    need = 3.0 if (s and int(s) >= 3600) else 4.5  # large text (>=18pt at 10in scale)
                    if not has_fill and v not in (muted, 'FFFFFF') and contrast(v, bg) < need:  # white = text on a dark fill below
                        issues.append(('ERROR', f'low contrast {v} ({contrast(v, bg):.1f}:1) "{name}": {t[:30]!r}'))
        # collapse duplicates
        seen = {}
        for lvl, msg in issues:
            key = (lvl, re.sub(r': .*$', '', msg))
            seen[key] = seen.get(key, 0) + 1
        for (lvl, msg), k in seen.items():
            if lvl == 'ERROR': errors += 1
            else: warns += 1
            if not a.quiet or lvl == 'ERROR':
                print(f's{n:03d} {lvl:5s} {msg}' + (f'  (x{k})' if k > 1 else ''))
    print(f'-- {errors} error(s), {warns} warning(s) in {len(parts)} slides')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()

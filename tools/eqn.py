"""Native PowerPoint equations (OMML) from LaTeX.

Pipeline: LaTeX --latex2mathml--> MathML --Office MML2OMML.XSL--> OMML --(Word run props -> DrawingML run props)-->
a14:m inside the text box. The result is a real PowerPoint equation: editable, crisp in the PDF, searchable.

Build-time use (COM or pptcom builds): create the equation as an ordinary text box whose text is the LaTeX source and
whose name contains the token `eq` (deckkit-style names, e.g. 'eq @2'). After the deck is saved and closed, run
    python tools/eqn.py DECK.pptx            (or call inject(path))
and every such box is converted in place. Font size and colour come from the box's first run, so the box is styled
like any other text. PowerPoint re-saves equations normally afterwards (states.py duplicates them fine).
"""
import copy, os, re, sys, zipfile, shutil, tempfile
from lxml import etree

XSL = r'C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL'
NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a14': 'http://schemas.microsoft.com/office/drawing/2010/main',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
}
A, M, W, A14, MC, P = (NS[k] for k in ('a', 'm', 'w', 'a14', 'mc', 'p'))
_xslt = None


def _transform():
    global _xslt
    if _xslt is None:
        _xslt = etree.XSLT(etree.parse(XSL))
    return _xslt


_SUB_BRACED = re.compile(r'_\{(?!\\)([A-Za-z][A-Za-z0-9,\s]*)\}')
_SUB_SINGLE = re.compile(r'_([A-Za-z])')


def upright_subscripts(latex):
    """Letter subscripts are labels (V_GS, i_D, k_n), not variables: set them upright.
    Uses \\text, because latex2mathml drops \\mathrm on single letters (V_G, units like V stay italic)."""
    latex = _SUB_BRACED.sub(lambda m: r'_{\text{%s}}' % m.group(1), latex)
    latex = _SUB_SINGLE.sub(lambda m: r'_{\text{%s}}' % m.group(1), latex)
    return re.sub(r'\\mathrm\{', r'\\text{', latex)


MML = 'http://www.w3.org/1998/Math/MathML'
_TOKENS = ('mi', 'mn', 'mo', 'mtext')
_END = '\ue0ff'           # private-use sentinels carry \textcolor spans through MML2OMML, which drops colours


def _mark_colours(mml):
    """\\textcolor{#RRGGBB}{..} -> mstyle@mathcolor. Wrap the text of every token inside it in sentinels
    (U+E000+i ... U+E0FF) and return the colour list; pptx_math() turns the marked text into coloured runs."""
    colours = []
    for ms in mml.iter('{%s}mstyle' % MML):
        c = ms.get('mathcolor')
        if not c:
            continue
        i = len(colours); colours.append(c.lstrip('#').upper())
        for tok in ms.iter(*('{%s}%s' % (MML, t) for t in _TOKENS)):
            if tok.text:
                if tok.tag.endswith('mi') and len(tok.text) == 1 and tok.get('mathvariant') is None:
                    tok.set('mathvariant', 'italic')     # keep single letters italic once the text gets longer
                tok.text = chr(0xE000 + i) + tok.text + _END
    return colours


def to_omml(latex, roman_subs=True, with_colours=False):
    """LaTeX -> <m:oMath> element (Word-flavoured run properties still inside)."""
    from latex2mathml.converter import convert
    if roman_subs:
        latex = upright_subscripts(latex)
    latex = re.sub(r'\\mathrm\{', r'\\text{', latex)   # units etc.: latex2mathml drops \mathrm on single letters
    mml = etree.fromstring(convert(latex).encode('utf-8'))
    colours = _mark_colours(mml)
    out = _transform()(mml).getroot()
    om = out if out.tag == '{%s}oMath' % M else out.find('.//m:oMath', NS)
    return (om, colours) if with_colours else om


def _split_coloured_runs(om, colours):
    """Split runs at the sentinels; coloured segments get their own run with the span's colour."""
    cur = None
    for r in list(om.iter('{%s}r' % M)):
        t = r.find('m:t', NS)
        if t is None or not t.text:
            continue
        segs, buf = [], ''
        for ch in t.text:
            o = ord(ch)
            if 0xE000 <= o < 0xE0FF or ch == _END:
                if buf:
                    segs.append((buf, cur)); buf = ''
                cur = None if ch == _END else o - 0xE000
            else:
                buf += ch
        if buf:
            segs.append((buf, cur))
        if not segs:
            r.getparent().remove(r); continue
        if len(segs) == 1 and segs[0][1] is None and t.text == segs[0][0]:
            continue
        parent, idx = r.getparent(), r.getparent().index(r)
        parent.remove(r)
        for k, (txt, ci) in enumerate(segs):
            nr = copy.deepcopy(r)
            nr.find('m:t', NS).text = txt
            if ci is not None:
                ap = nr.find('a:rPr', NS)
                sf = ap.find('a:solidFill', NS)
                if sf is None:
                    sf = etree.Element('{%s}solidFill' % A); ap.insert(0, sf)
                for c in list(sf):
                    sf.remove(c)
                etree.SubElement(sf, '{%s}srgbClr' % A, val=colours[ci])
                ap.set('b', '1')
            parent.insert(idx + k, nr)


def _arpr(size, color, font, bold=False):
    r = etree.Element('{%s}rPr' % A, lang='en-US', sz=str(int(round(size * 100))), b='1' if bold else '0')
    if color:
        sf = etree.SubElement(r, '{%s}solidFill' % A)
        etree.SubElement(sf, '{%s}srgbClr' % A, val=color)
    etree.SubElement(r, '{%s}latin' % A, typeface=font)
    etree.SubElement(r, '{%s}cs' % A, typeface=font)
    return r


def pptx_math(latex, size, color, font='Cambria Math', align='left', roman_subs=True):
    """-> <a14:m><m:oMathPara>...</m:oMathPara></a14:m> ready to drop into an <a:p>."""
    om, colours = to_omml(latex, roman_subs=roman_subs, with_colours=True)
    for rpr in om.iter('{%s}rPr' % W):         # Word run props -> DrawingML run props
        parent = rpr.getparent()
        parent.replace(rpr, _arpr(size, color, font))
    for r in om.iter('{%s}r' % M):              # runs without any props still need size/colour
        if r.find('a:rPr', NS) is None:
            r.insert(0 if r.find('m:rPr', NS) is None else 1, _arpr(size, color, font))
    for cp in om.iter('{%s}ctrlPr' % M):
        if cp.find('a:rPr', NS) is None:
            cp.append(_arpr(size, color, font))
    if colours:
        _split_coloured_runs(om, colours)
    m14 = etree.Element('{%s}m' % A14, nsmap={'a14': A14})
    para = etree.SubElement(m14, '{%s}oMathPara' % M, nsmap={'m': M})
    ppr = etree.SubElement(para, '{%s}oMathParaPr' % M)
    etree.SubElement(ppr, '{%s}jc' % M, {'{%s}val' % M: align})
    para.append(om)
    return m14


def _convert_sp(sp, roman_subs=True):
    body = sp.find('p:txBody', NS)
    paras = body.findall('a:p', NS)
    latex = '\n'.join(''.join(t.text or '' for t in p.iter('{%s}t' % A)) for p in paras).strip()
    r0 = body.find('.//a:r/a:rPr', NS)
    size = int(r0.get('sz', '2800')) / 100 if r0 is not None else 28
    col = r0.find('a:solidFill/a:srgbClr', NS) if r0 is not None else None
    color = col.get('val') if col is not None else None
    algn = paras[0].find('a:pPr', NS).get('algn', 'l') if paras[0].find('a:pPr', NS) is not None else 'l'
    align = {'l': 'left', 'ctr': 'center', 'r': 'right'}.get(algn, 'left')
    ppr = copy.deepcopy(paras[0].find('a:pPr', NS))
    for p in paras:
        body.remove(p)
    p = etree.SubElement(body, '{%s}p' % A)
    if ppr is not None:
        p.append(ppr)
    p.append(pptx_math(latex, size, color, align=align, roman_subs=roman_subs))
    # wrap the shape in mc:AlternateContent (what PowerPoint itself writes for equations)
    parent = sp.getparent(); idx = parent.index(sp)
    ac = etree.Element('{%s}AlternateContent' % MC, nsmap={'mc': MC})
    ch = etree.SubElement(ac, '{%s}Choice' % MC, Requires='a14', nsmap={'a14': A14})
    fb = etree.SubElement(ac, '{%s}Fallback' % MC)
    fallback = copy.deepcopy(sp)
    for x in fallback.find('p:txBody', NS).findall('a:p', NS):
        fallback.find('p:txBody', NS).remove(x)
    fp = etree.SubElement(fallback.find('p:txBody', NS), '{%s}p' % A)
    etree.SubElement(etree.SubElement(fp, '{%s}r' % A), '{%s}t' % A).text = latex
    parent.remove(sp)
    ch.append(sp); fb.append(fallback)
    parent.insert(idx, ac)
    return latex


def inject(path, roman_subs=True):
    """Convert every text box whose name has the token 'eq' into a native equation. Returns the count.
    roman_subs=False keeps letter subscripts italic (Sedra/Smith style: v_GS with italic GS)."""
    tmp = path + '.eqtmp'
    n = 0
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if re.fullmatch(r'ppt/slides/slide\d+\.xml', item.filename):
                x = etree.fromstring(data)
                for sp in list(x.iter('{%s}sp' % P)):
                    nv = sp.find('p:nvSpPr/p:cNvPr', NS)
                    if nv is None or 'eq' not in nv.get('name', '').split():
                        continue
                    if sp.getparent().tag == '{%s}Choice' % MC:
                        continue                       # already converted
                    _convert_sp(sp, roman_subs); n += 1
                if n:
                    root_ns = x.nsmap
                    data = etree.tostring(x, xml_declaration=True, encoding='UTF-8', standalone=True)
            zout.writestr(item, data)
    shutil.move(tmp, path)
    return n


if __name__ == '__main__':
    for f in sys.argv[1:]:
        print(f, inject(os.path.abspath(f)), 'equation(s)')

"""Deck toolkit (engine): PowerPoint COM helpers (or their python-pptx stand-in, tools/pptcom.py) that apply the ACTIVE FAMILY's design tokens
(families/<family>/design/tokens.json, resolved via tools/family.py).

Import from a family build script:  import family; family.use('<family>'); from deckkit import *
All coordinates are points on the 1440x810 canvas. Colors accept token names
('navy', 'answer', 'link0'..'link3', 'aux', 'action', 'text2', 'muted', ...) or 'RRGGBB'.

Rich text mini-markup (used by text()):
    [[link0:unsigned]]   color a span         [[answer+b:1011]]  color + bold
    **bold**             bold span (navy)      \n                 paragraph break
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import family as _family
FAMILY = _family.resolve()                      # set by the family build script (family.use) or DECK_FAMILY
T = _family.tokens(FAMILY)
C, F, S, G = T['color'], T['font'], T['size'], T['grid']

# COM constants
TRUE, FALSE = -1, 0
AL = {'l': 1, 'c': 2, 'r': 3}
AN = {'t': 1, 'm': 3, 'b': 4}
RECT, ROUND, OVAL = 1, 5, 9


def hexcol(c):
    if c.startswith('link'):
        return C['link'][int(c[4:])]
    if c in C:
        return C[c]
    if c in T['roles']:
        return C[T['roles'][c]]
    assert re.fullmatch(r'[0-9A-Fa-f]{6}', c), c
    return c.upper()


def rgb(c):
    h = hexcol(c)
    return int(h[0:2], 16) + int(h[2:4], 16) * 256 + int(h[4:6], 16) * 65536


def _has_com():
    try:
        import win32com.client  # noqa
        return True
    except ImportError:
        return False


# 'com': PowerPoint itself (Windows). 'pptx': tools/pptcom.py on python-pptx (Linux, claude.ai), same output design.
BACKEND = os.environ.get('DECKKIT_BACKEND') or ('com' if _has_com() else 'pptx')


def app():
    if BACKEND == 'pptx':
        import pptcom
        return pptcom.Application()
    import win32com.client
    return win32com.client.Dispatch('PowerPoint.Application')


def mono_w(size, n=1):
    """Advance width of n Consolas characters at `size` pt."""
    return size * T['mono_advance_em'] * n


# ---------------------------------------------------------------- text
_SPAN = re.compile(r'\[\[(\w+?)(\+b)?:(.*?)\]\]|\*\*(.*?)\*\*', re.S)


def parse_markup(s, base_color):
    """-> (plain_text, [(start0, length, color, bold)])"""
    out, spans, pos = [], [], 0
    for m in _SPAN.finditer(s):
        out.append(s[pos:m.start()])
        cur = sum(len(x) for x in out)
        if m.group(4) is not None:
            txt, col, bold = m.group(4), base_color, True
        else:
            txt, col, bold = m.group(3), m.group(1), bool(m.group(2))
        out.append(txt)
        spans.append((cur, len(txt), col, bold))
        pos = m.end()
    out.append(s[pos:])
    return ''.join(out), spans


_SUBS = re.compile(r'_\{(.*?)\}')


def split_subscripts(plain, spans):
    """'J_{A}' -> 'JA' with A subscripted: strips the _{ } markers, remaps the colour spans and returns
    (plain, spans, [(start0, length)] subscript ranges). Text without '_{' is returned unchanged."""
    if '_{' not in plain:
        return plain, spans, []
    new, mp, subs, pos = [], [], [], 0
    for m in _SUBS.finditer(plain):
        for k in range(pos, m.start()):
            mp.append(len(new)); new.append(plain[k])
        mp += [len(new)] * (m.start(1) - m.start())      # the '_{' marker
        subs.append((len(new), len(m.group(1))))
        for k in range(m.start(1), m.end(1)):
            mp.append(len(new)); new.append(plain[k])
        mp.append(len(new))                               # the '}'
        pos = m.end()
    for k in range(pos, len(plain)):
        mp.append(len(new)); new.append(plain[k])
    mp.append(len(new))
    spans = [(mp[st], mp[st + ln] - mp[st], c, b) for st, ln, c, b in spans]
    return ''.join(new), spans, subs


def style_range(tr, font=None, size=None, color=None, bold=None, italic=None):
    f = tr.Font
    if font: f.Name = font
    if size: f.Size = size
    if color: f.Color.RGB = rgb(color)
    if bold is not None: f.Bold = TRUE if bold else FALSE
    if italic is not None: f.Italic = TRUE if italic else FALSE


def text(sl, x, y, w, h, s, size=None, font=None, color='navy', align='l', anchor='t',
         name=None, bold=False, italic=False, spacing=1.0, after=0, autofit=False, wrap=True, raw=False):
    """raw=True: no mini-markup (used for LaTeX equation sources, where _{..} and ** are LaTeX)."""
    size = size or S['body']
    font = font or F['body']
    shp = sl.Shapes.AddTextbox(1, x, y, w, h)
    tf = shp.TextFrame
    tf.MarginLeft = tf.MarginRight = tf.MarginTop = tf.MarginBottom = 0
    tf.AutoSize = 1 if autofit else 0      # before WordWrap: a non-wrapping auto-size box collapses to 0 width
    tf.WordWrap = TRUE if wrap else FALSE
    tf.VerticalAnchor = AN[anchor]
    if raw:
        plain, spans, subs = s.replace('\n', '\r'), [], []
    else:
        plain, spans = parse_markup(s.replace('\n', '\r'), color)
        plain, spans, subs = split_subscripts(plain, spans)
    tr = tf.TextRange
    tr.Text = plain
    style_range(tr, font, size, color, bold, italic)
    pf = tr.ParagraphFormat
    pf.Alignment = AL[align]
    pf.SpaceWithin = spacing
    pf.SpaceAfter = after
    pf.SpaceBefore = 0
    for st, ln, col, b in spans:
        style_range(tr.Characters(st + 1, ln), color=col, bold=b if b else None)
    italic_base = T.get('text', {}).get('italic_symbols', False)   # v_{GS}: italic v, like the equations
    for st, ln in subs:
        tr.Characters(st + 1, ln).Font.Subscript = TRUE
        if italic_base and st > 0 and plain[st - 1].isalpha() and (st < 2 or not plain[st - 2].isalpha()):
            tr.Characters(st, 1).Font.Italic = TRUE
    if not autofit:
        shp.Left, shp.Top, shp.Width, shp.Height = x, y, w, h   # re-assert geometry (alignment edges)
    else:
        shp.Left, shp.Top, shp.Width = x, y, w                  # height follows the text
    if name: shp.Name = name
    return shp


def mono(sl, x, y, s, size=None, color='navy', align='l', name=None, w=None, bold=False):
    """Single-line monospace text. For align='r', x is the RIGHT edge. Width is exact."""
    size = size or S['working']
    plain, _ = parse_markup(s, color)
    width = w or mono_w(size, max(len(plain), 1)) + 2
    left = x - width if align == 'r' else (x - width / 2 if align == 'c' else x)
    return text(sl, left, y, width, size * 1.2, s, size=size, font=F['mono'], color=color,
                align=align, name=name, bold=bold, wrap=False, anchor='m')


def note(sl, x, y_row, row_size, s, size=None, w=420, color='annotation', name=None, font=None):
    """Annotation vertically centred on a mono row that starts at y_row (row box height = row_size*1.2)."""
    return text(sl, x, y_row, w, row_size * 1.2, s, size=size or S['annotation'], color=color,
                anchor='m', name=name, font=font, wrap=False)


def frac(sl, x, yc, num, den, size=34, font=None, color='navy', name=None, gap=4):
    """Stacked fraction; x = left edge, yc = bar y. Returns right edge. Width estimated (0.52em/char)."""
    font = font or F['math']
    est = lambda s: len(parse_markup(s, color)[0]) * size * 0.52
    w = max(est(num), est(den)) + 12
    a = text(sl, x, yc - size * 1.25 - gap, w, size * 1.25, num, size=size, font=font, color=color,
             align='c', anchor='b', wrap=False)
    b = line(sl, x, yc, x + w, yc, color=color, w=1.75)
    c = text(sl, x, yc + gap, w, size * 1.25, den, size=size, font=font, color=color, align='c',
             anchor='t', wrap=False)
    if name:
        for s_ in (a, b, c): s_.Name = name
    return x + w, [a, b, c]


# ---------------------------------------------------------------- shapes
def box(sl, x, y, w, h, fill='surface', line=None, lw=1.0, kind=RECT, radius=None,
        name=None, transparency=0.0):
    shp = sl.Shapes.AddShape(kind, x, y, w, h)
    shp.Shadow.Visible = FALSE
    if fill:
        shp.Fill.Visible = TRUE
        shp.Fill.Solid()
        shp.Fill.ForeColor.RGB = rgb(fill)
        shp.Fill.Transparency = transparency
    else:
        shp.Fill.Visible = FALSE
    if line:
        shp.Line.Visible = TRUE
        shp.Line.ForeColor.RGB = rgb(line)
        shp.Line.Weight = lw
    else:
        shp.Line.Visible = FALSE
    if kind == ROUND and radius is not None:
        shp.Adjustments.SetItem(1, radius)
    if shp.HasTextFrame:
        shp.TextFrame.TextRange.Text = ''
    if name: shp.Name = name
    return shp


def line(sl, x1, y1, x2, y2, color='navy', w=None, arrow=False, dash=None, name=None):
    ln = sl.Shapes.AddLine(x1, y1, x2, y2)
    ln.Line.ForeColor.RGB = rgb(color)
    ln.Line.Weight = w or T['shape']['line_w']
    if arrow:
        ln.Line.EndArrowheadStyle = 2
        ln.Line.EndArrowheadLength = 2
        ln.Line.EndArrowheadWidth = 2
    if dash:
        ln.Line.DashStyle = dash  # 3 = msoLineRoundDot
    if name: ln.Name = name
    return ln


def poly(sl, pts, color='navy', w=3.0, name=None):
    fb = sl.Shapes.BuildFreeform(0, pts[0][0], pts[0][1])
    for x, y in pts[1:]:
        fb.AddNodes(0, 0, x, y)
    shp = fb.ConvertToShape()
    shp.Fill.Visible = FALSE
    shp.Line.ForeColor.RGB = rgb(color)
    shp.Line.Weight = w
    shp.Shadow.Visible = FALSE
    if name: shp.Name = name
    return shp


CHIP = {  # kind -> (fill, line, text colour, prefix)
    'answer': ('answer_tint', 'answer', 'answer', ''),   # the final answer
    'ok':     ('ok_tint', 'ok', 'ok', '✓  '),            # positive outcome (e.g. no overflow)
    'bad':    ('bad', 'bad', 'FFFFFF', '✗  '),           # negative outcome (e.g. overflow): solid, unmistakable
    'info':   ('info_tint', 'info', 'navy', ''),         # neutral outcome worth noting (e.g. borrow out)
}


def chip(sl, x, y, s, size=None, font=None, name=None, pad=(18, 8), align='l', kind='answer'):
    """Outcome chip (answer / ok / bad / info), rounded. Returns (bg, txt)."""
    size = size or S['working']
    font = font or F['mono']
    fill, ln, tc, pre = CHIP[kind]
    s = pre + s
    plain, _ = parse_markup(s, tc)
    if font == F['mono']:
        tw = mono_w(size, len(plain))
    else:
        tw = size * 0.56 * len(plain)
    w, h = tw + 2 * pad[0], size * 1.2 + 2 * pad[1]
    left = x - w if align == 'r' else x
    bg = box(sl, left, y, w, h, fill=fill, line=ln, lw=1.5, kind=ROUND, radius=0.25,
             name=(name + ' bg') if name else None)
    t = text(sl, left + pad[0], y + pad[1], tw + 4, size * 1.2, s, size=size, font=font,
             color=tc, name=name, wrap=False, bold=kind in ('ok', 'bad'))
    return bg, t


def explain(sl, x, y, w, items, size=None, gap=10, color='navy', title=None):
    """Explanation panel: left-aligned bullets stacked top-down; each item = (state_tag_or_'', markup).
    Bullets appear with their state, so the explanation builds up with the reveal. Returns bottom y."""
    size = size or S['explain']
    if title:
        text(sl, x, y, w, size * 1.3, title, size=size - 4, font=F['heading'], color='text2', name='explain title')
        y += size * 1.3 + 4
    for st, s in items:
        shp = text(sl, x, y, w, size * 1.4, s, size=size, color=color, spacing=1.0, autofit=True, name='explain')
        pf = shp.TextFrame.TextRange.ParagraphFormat
        pf.Bullet.Visible = TRUE
        pf.Bullet.Character = 8226
        pf.Bullet.Font.Color.RGB = rgb('text2')
        shp.TextFrame.Ruler.Levels(1).FirstMargin = 0
        shp.TextFrame.Ruler.Levels(1).LeftMargin = size * 0.9
        if st:
            tag(shp, st)
        y = shp.Top + shp.Height + gap
    return y


def send_back(sl, pred):
    """Send every shape matching pred(shape) to the back, keeping their relative order."""
    objs = [s for s in sl.Shapes if pred(s)]
    for s in reversed(objs):
        s.ZOrder(1)  # msoSendToBack


def tag(shapes, t):
    """Append a state tag (e.g. '@3', '@2-4', '@dim5') to one shape or a list of shapes."""
    if not isinstance(shapes, (list, tuple)):
        shapes = [shapes]
    for s in shapes:
        if s is None: continue
        s.Name = (s.Name + ' ' + t).strip()
    return shapes


# ---------------------------------------------------------------- slide scaffolding
def content_slide(pres, layout, badge, title, name=None):
    sl = pres.Slides.AddSlide(pres.Slides.Count + 1, layout)
    for ph in sl.Shapes.Placeholders:
        t = ph.PlaceholderFormat.Type
        if t == 1:  # title
            ph.TextFrame.TextRange.Text = title
        elif t in (2, 7):  # body -> badge
            if badge:
                ph.TextFrame.TextRange.Text = badge
    # delete empty badge placeholder when no badge
    if not badge:
        for i in range(sl.Shapes.Placeholders.Count, 0, -1):
            ph = sl.Shapes.Placeholders(i)
            if ph.PlaceholderFormat.Type in (2, 7):
                ph.Delete()
    if name: sl.Name = name
    return sl


def question_strip(sl, s, y=None, size=None, h=None, w=None):
    y = G['content_top'] - 32 if y is None else y
    size = size or S['question']
    return text(sl, G['margin_x'], y, w or (T['canvas']['w'] - 2 * G['margin_x']), h or size * 1.5, s,
                size=size, name='question strip')

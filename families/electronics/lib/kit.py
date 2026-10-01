"""Electronics lecture kit: slide components for the APPROVED style X ('angular': parallelogram tags, sharp cards,
corner geometry; tokens in design/tokens.json). The 'rounded' branches (style Y) are retired and kept only so the
round-2 drafts can be rebuilt.

    import family; family.use('electronics'); import kit; kit.setup(footer='ELEC1 · Lecture 3 · MOSFETs')

Worked examples (user preference): givens() lists colour-coded givens; gc('g1', latex) colours a given inside an
equation; solution() lays out elaborate steps (title, comment, equations, conclusion).
"""
import os, re
from deckkit import *                       # noqa

ANG = T['style']['shape'] == 'angular'
W, H = T['canvas']['w'], T['canvas']['h']
MX = G['margin_x']
PARA = 2
LABEL = F.get('label', F['body'])
CTX = {'footer': ''}


def setup(footer):
    CTX['footer'] = footer


# ------------------------------------------------------------------ primitives
def shape_text(shp, s, size, color, font, bold=True, align='c'):
    tf = shp.TextFrame
    tf.MarginLeft = tf.MarginRight = tf.MarginTop = tf.MarginBottom = 0
    tf.WordWrap = FALSE; tf.VerticalAnchor = 3
    tr = tf.TextRange; tr.Text = s
    style_range(tr, font, size, color, bold=bold)
    tr.ParagraphFormat.Alignment = AL[align]


def rounded(sl, x, y, w, h, r, **kw):
    s = box(sl, x, y, w, h, kind=ROUND, **kw)
    s.Adjustments.SetItem(1, min(0.5, r / min(w, h)))
    return s


def para(sl, x, y, w, h, fill, slant=0.35, name='geo'):
    s = box(sl, x, y, w, h, fill=fill, kind=PARA, name=name)
    s.Adjustments.SetItem(1, slant)
    return s


def label_tag(sl, x, y, s, name='tag', fill=None):
    """Label: X = filled parallelogram, white caps; Y = outlined pill, accent text. Returns (shape, width)."""
    size = S['eyebrow']
    if ANG:
        s = s.upper()
        w = len(s) * size * 0.66 + 40
        shp = para(sl, x, y, w, 26, fill or 'accent', slant=0.4, name=name)
        shape_text(shp, s, size, 'FFFFFF', LABEL)
        return shp, w
    w = len(s) * size * 0.58 + 36
    shp = rounded(sl, x, y, w, 30, 15, fill='surface', line=fill or 'accent', lw=1.25, name=name)
    shape_text(shp, s, size, fill or 'accent', LABEL)
    return shp, w


def card(sl, x, y, w, h, fill='surface', line_='hairline', name='card'):
    if ANG:
        c = box(sl, x, y, w, h, fill=fill, line=line_, lw=1.25, name=name)
        box(sl, x, y - 1, 56, 5, fill='accent', name=name)
        return c
    return rounded(sl, x, y, w, h, 18, fill=fill, line=line_, lw=1.5, name=name)


def panel(sl, x, y, w, h, name='panel'):
    """Tinted block for definitions, outcomes, key results."""
    return card(sl, x, y, w, h, fill='accent_tint', line_=None, name=name) if ANG else \
        rounded(sl, x, y, w, h, 24, fill='accent_tint', name=name)


def badge(sl, x, y, n, d=32, st=None):
    b = box(sl, x, y, d, d, fill='accent', kind=1 if ANG else OVAL, name='badge')
    shape_text(b, str(n), 17, 'FFFFFF', LABEL)
    if st:
        tag(b, st)
    return b


def result(sl, x, y, s, size=24, name='result'):
    n = len(re.sub(r'_\{(.*?)\}', r'\1', s))
    w = n * size * 0.6 + 56
    h = size * 1.9
    bg = para(sl, x, y, w, h, 'answer', slant=0.3, name=name) if ANG else \
        rounded(sl, x, y, w, h, h / 2, fill='answer', name=name)
    text(sl, x, y, w, h, s, size=size, font=LABEL, color='FFFFFF', bold=True, align='c', anchor='m', name=name)
    return w


def bullet(shp, char=None):
    pf = shp.TextFrame.TextRange.ParagraphFormat
    pf.Bullet.Visible = TRUE; pf.Bullet.Character = char or (9632 if ANG else 8226)
    pf.Bullet.Font.Color.RGB = rgb('accent')
    shp.TextFrame.Ruler.Levels(1).FirstMargin = 0; shp.TextFrame.Ruler.Levels(1).LeftMargin = 26


def eq(sl, x, y, latex, size=None, color='navy', w=820, h=None, st=None, align='l'):
    size = size or S['eq']
    h = h or size * (2.3 if ('\\frac' in latex or '\\left' in latex) else 1.5)
    return text(sl, x, y, w, h, latex, size=size, font=F['math'], color=color, align=align, anchor='m', wrap=False,
                name='eq' + (' ' + st if st else ''), raw=True)


def eq_h(latex, size=None):
    size = size or S['eq']
    return size * (2.3 if ('\\frac' in latex or '\\left' in latex) else 1.5)


def figure(sl, path, credit, x, y, w, h, align='c', name='figure'):
    """Cleaned reference figure inside a card (fitted), credit inside the card. Returns the card box."""
    from PIL import Image
    iw, ih = Image.open(path).size
    pad, cap = 20, (18 if credit else 0)
    k = min((w - 2 * pad) / iw, (h - 2 * pad - cap) / ih)
    fw, fh = iw * k, ih * k
    cw, ch = fw + 2 * pad, fh + 2 * pad + cap
    cx = x + (w - cw) / 2 if align == 'c' else x
    cy = y
    card(sl, cx, cy, cw, ch, name=name + ' card')
    p = sl.Shapes.AddPicture(path, 0, -1, cx + pad, cy + pad, fw, fh); p.Name = name
    if credit:
        text(sl, cx + pad, cy + ch - cap - 10, cw - 2 * pad, cap, 'Figure: ' + credit, size=S['caption'],
             color='text2', align='r', name='credit')
    return cx, cy, cw, ch


def points(sl, x, y, w, items, size=None, gap=22, color='navy'):
    """Bulleted points, each optionally state-tagged: items = [(state or '', markup)]. Returns bottom y."""
    size = size or S['body']
    for st, s in items:
        shp = text(sl, x, y, w, size * 1.3, s, size=size, color=color, autofit=True, spacing=1.05,
                   name='point' + (' ' + st if st else ''))
        bullet(shp)
        y = shp.Top + shp.Height + gap
    return y


def steps(sl, x, y, w, items, label_size=21, eq_size=26):
    """Worked steps: items = [(state, label_markup, latex or None, extra_text or None)]. Badges numbered.
    Returns bottom y."""
    for i, (st, lab, latex, extra) in enumerate(items, 1):
        badge(sl, x, y + 1, i, st=st)
        lt = text(sl, x + 48, y, w - 48, label_size * 1.4, lab, size=label_size, color='text2', autofit=True,
                  name='lab ' + st)
        yy = lt.Top + lt.Height + 4
        if latex:
            eq(sl, x + 48, yy, latex, size=eq_size, w=w - 48, st=st)
            yy += eq_h(latex, eq_size)
        if extra:
            et = text(sl, x + 48, yy, w - 48, label_size * 1.4, extra, size=label_size, color='navy', autofit=True,
                      name='lab ' + st)
            yy = et.Top + et.Height
        y = yy + 16
    return y


# ------------------------------------------------------------------ worked examples
def gc(key, latex):
    """Colour a given inside an equation: gc('g1', '10') -> \\textcolor{#1F6FA8}{10}."""
    return r'\textcolor{#%s}{%s}' % (C[key], latex)


def givens(sl, x, y, w, items, title='Given', size=20, gap=8):
    """Colour-coded givens: items = [(colour_key, markup)]. Each line starts with a colour square. Returns bottom y."""
    label_tag(sl, x, y, title, name='given')
    y += 40
    for key, s in items:
        box(sl, x, y + size * 0.35, size * 0.55, size * 0.55, fill=key, name='given')
        t = text(sl, x + size, y, w - size, size * 1.4, f'[[{key}+b:{s}]]', size=size, autofit=True, name='given')
        y = t.Top + t.Height + gap
    return y


def solution(sl, x, y, w, steps, title_size=20, note_size=17, eq_size=24, gap=14):
    """Elaborate worked steps. steps = [dict(st, title, note=None, eq=[latex...], then=None)].
    title: what the step does (bold); note: why (comment, grey); eq: one or more equations; then: conclusion line.
    Returns bottom y."""
    for i, s in enumerate(steps, 1):
        st = s.get('st', '')
        badge(sl, x, y + 1, s.get('n', i), st=st or None)
        t = text(sl, x + 46, y, w - 46, title_size * 1.4, f"**{s['title']}**", size=title_size, autofit=True,
                 name='step ' + st)
        yy = t.Top + t.Height + 2
        if s.get('note'):
            n = text(sl, x + 46, yy, w - 46, note_size * 1.4, s['note'], size=note_size, color='text2', autofit=True,
                     italic=True, name='note ' + st)
            yy = n.Top + n.Height + 2
        for latex in s.get('eq', []):
            eq(sl, x + 46, yy, latex, size=eq_size, w=w - 46, st=st)
            yy += eq_h(latex, eq_size)
        if s.get('then'):
            c = text(sl, x + 46, yy, w - 46, title_size * 1.4, s['then'], size=title_size - 1, color='navy',
                     autofit=True, name='then ' + st)
            yy = c.Top + c.Height
        y = yy + gap
    return y


# ------------------------------------------------------------------ scaffolding
def new_pres():
    pp = app()
    pres = pp.Presentations.Add(0)
    pres.PageSetup.SlideWidth, pres.PageSetup.SlideHeight = W, H
    bg = pres.SlideMaster.Background.Fill
    bg.Solid(); bg.ForeColor.RGB = rgb('bg')
    lay = [pres.SlideMaster.CustomLayouts(i) for i in range(1, pres.SlideMaster.CustomLayouts.Count + 1)]
    return pres, next(l for l in lay if l.Name == 'Title Only')


def slide(pres, lay, title, section=None, name='', title_box=None, title_size=None, footer=True):
    sl = pres.Slides.AddSlide(pres.Slides.Count + 1, lay)
    sl.Name = f'{name or title[:30]} s{pres.Slides.Count}'      # unique (PowerPoint requires it)
    t = sl.Shapes.Title
    x, y, w, h = title_box or (MX, G['title_y'], W - 2 * MX, G['title_h'])
    t.Left, t.Top, t.Width, t.Height = x, y, w, h
    tf = t.TextFrame
    tf.MarginLeft = tf.MarginRight = tf.MarginTop = tf.MarginBottom = 0
    tf.AutoSize = 0; tf.WordWrap = TRUE; tf.VerticalAnchor = 4
    plain, _, subs = split_subscripts(title, [])        # titles accept v_{DS}-style subscripts
    tr = tf.TextRange; tr.Text = plain
    style_range(tr, F['heading'], title_size or S['title'], 'navy', bold=not ANG)
    for st, ln in subs:
        tr.Characters(st + 1, ln).Font.Subscript = TRUE
        if ANG and st > 0:      # all-caps display face would turn g_m into G_M: set symbols in the body face
            sym = tr.Characters(st, ln + 1).Font
            sym.Name = F['body']; sym.Italic = TRUE
    tr.ParagraphFormat.Alignment = 1
    tr.ParagraphFormat.SpaceWithin = 0.9
    t.Name = 'title'
    if section:
        label_tag(sl, x, y - 40, section, name='section tag')
    if footer:
        if ANG:
            para(sl, MX, H - 34, 34, 10, 'accent', slant=0.5, name='chrome footer')
            fx = MX + 46
        else:
            box(sl, MX, H - 35, 10, 10, fill='accent', kind=OVAL, name='chrome footer')
            fx = MX + 20
        text(sl, fx, H - 41, 700, 22, CTX['footer'], size=13, font=F['body'], color='text2', name='chrome footer')
    return sl


def corner_geometry(sl):
    g, c, n = ('accent', 'answer', 'geo')
    para(sl, -50, 0, 300, 56, g); para(sl, 232, 0, 70, 56, g); para(sl, 300, 0, 560, 14, n)
    para(sl, 1250, 0, 250, 56, c)
    para(sl, -50, H - 56, 200, 56, c); para(sl, 150, H - 14, 560, 14, n)
    para(sl, 1180, H - 56, 320, 56, g); para(sl, 1110, H - 56, 64, 56, g)


def node_motif(sl, x, y, scale=1.0):
    pts = [(0, 0), (120, 0), (120, 90), (240, 90), (240, 20), (330, 20)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        line(sl, x + ax * scale, y + ay * scale, x + bx * scale, y + by * scale, color='geo', w=3, name='motif')
    for px, py in (pts[0], pts[2], pts[5]):
        box(sl, x + px * scale - 9, y + py * scale - 9, 18, 18, fill='surface', line='answer', lw=3, kind=OVAL,
            name='motif')
    box(sl, x + 240 * scale - 7, y + 90 * scale - 7, 14, 14, fill='accent', kind=OVAL, name='motif')


# ------------------------------------------------------------------ structural slides
def title_slide(pres, lay, M, lecture_no, title, subtitle, fig=None):
    """fig = (path, credit) shown in a card on the right."""
    if ANG:
        sl = slide(pres, lay, title, name='title #nochrome', title_box=(MX + 8, 250, 760, 130),
                   title_size=S['cover'], footer=False)
        corner_geometry(sl)
        label_tag(sl, MX + 8, 200, f'{M.CODE}  ·  {M.NAME}')
        text(sl, MX + 8, 388, 700, 80, subtitle, size=28, color='text2', name='subtitle', spacing=1.0)
        text(sl, MX + 8, 480, 400, 40, f'LECTURE {lecture_no}', size=34, font=F['heading'], color='answer',
             name='lecture')
        text(sl, MX + 8, 600, 700, 30, M.AUTHOR, size=22, font=F['body'], bold=True, color='navy', name='author')
        text(sl, MX + 8, 632, 760, 26, f'{M.DEPARTMENT}  ·  {M.YEAR}', size=15, color='text2', name='meta')
        if fig:
            figure(sl, fig[0], fig[1], 800, 240, 580, 300)
    else:
        sl = slide(pres, lay, title, name='title #nochrome', title_box=(MX + 40, 250, 700, 110),
                   title_size=S['cover'], footer=False)
        rounded(sl, MX, 90, 720, 620, 36, fill='surface', line='hairline', lw=1.5, name='frame').ZOrder(1)
        _, w1 = label_tag(sl, MX + 40, 140, M.CODE)
        label_tag(sl, MX + 40 + w1 + 12, 140, f'Lecture {lecture_no}')
        text(sl, MX + 40, 205, 640, 30, M.NAME, size=20, font=F['heading'], color='accent', bold=True, name='course')
        text(sl, MX + 40, 370, 640, 80, subtitle, size=28, color='text2', name='subtitle', spacing=1.0)
        text(sl, MX + 40, 590, 640, 30, M.AUTHOR, size=22, font=F['heading'], bold=True, color='navy', name='author')
        text(sl, MX + 40, 624, 660, 26, f'{M.DEPARTMENT}  ·  {M.YEAR}', size=15, color='text2', name='meta')
        node_motif(sl, 860, 120, 1.3)
        if fig:
            figure(sl, fig[0], fig[1], 830, 330, 540, 300)
    return sl


def map_slide(pres, lay, lecture_no, sections, outcomes):
    sl = slide(pres, lay, 'Lecture map', section=f'Lecture {lecture_no}', name='map')
    y = 180
    pitch = min(98 if ANG else 92, 470 // max(1, len(sections)))
    for i, (t, sub) in enumerate(sections, 1):
        if ANG:
            b = box(sl, MX, y, 46, 46, fill='accent', name='map n')
            shape_text(b, str(i), 30, 'FFFFFF', F['heading'], bold=False)
            text(sl, MX + 66, y - 2, 640, 32, t, size=25, font=F['body'], bold=True, color='navy', name='map t')
            if sub:
                text(sl, MX + 66, y + 28, 640, 26, sub, size=18, color='text2', name='map s')
        else:
            rounded(sl, MX, y, 720, 70, 35, fill='surface', line='hairline', lw=1.5, name='map pill')
            text(sl, MX + 28, y, 60, 70, f'{i:02d}', size=24, font=F['heading'], bold=True, color='accent',
                 anchor='m', name='map n')
            text(sl, MX + 92, y + 8, 540, 30, t, size=23, font=F['heading'], bold=True, color='navy', name='map t')
            if sub:
                text(sl, MX + 92, y + 38, 540, 24, sub, size=17, color='text2', name='map s')
            c = box(sl, MX + 720 - 58, y + 15, 40, 40, fill='surface', line='accent', lw=1.5, kind=OVAL, name='arrow')
            shape_text(c, '→', 18, 'accent', F['body'])
        y += pitch
    px, pw = 880, W - MX - 880
    panel(sl, px, 180, pw, 470, name='outcomes')
    label_tag(sl, px + 30, 206, 'By the end you can')
    y = 260
    for o in outcomes:
        s = text(sl, px + 30, y, pw - 60, 30, o, size=22, color='navy', name='outcome', autofit=True)
        bullet(s)
        y = s.Top + s.Height + 22
    return sl


def section_slide(pres, lay, n, title, items, sections):
    if ANG:
        sl = slide(pres, lay, title, name='section #nochrome', title_box=(MX + 8, 330, 820, 110),
                   title_size=S['section'] if len(title) <= 22 else int(S['section'] * 0.7), footer=False)
        corner_geometry(sl)
        text(sl, MX + 4, 140, 400, 200, f'{n:02d}', size=200, font=F['display'], color='accent', anchor='b',
             name='numeral')
        y = 460
        for it in items:
            s = text(sl, MX + 8, y, 700, 34, it, size=23, color='text2', name='item'); bullet(s)
            y += 42
        mx = 960
        for i, (t, _) in enumerate(sections, 1):
            on = i == n
            b = box(sl, mx, 190 + (i - 1) * 64, 34, 34, fill='accent' if on else 'surface',
                    line=None if on else 'hairline', lw=1.25, name='map')
            shape_text(b, str(i), 22, 'FFFFFF' if on else 'muted', F['heading'], bold=False)
            text(sl, mx + 50, 190 + (i - 1) * 64, 380, 34, t, size=19, font=F['body'], bold=on,
                 color='navy' if on else 'muted', anchor='m', name='map')
    else:
        sl = slide(pres, lay, title, name='section #nochrome', title_box=(MX + 300, 230, 560, 180),
                   title_size=S['section'], footer=False)
        rounded(sl, MX, 110, 880, 590, 40, fill='surface', line='hairline', lw=1.5, name='frame').ZOrder(1)
        c = box(sl, MX + 50, 230, 210, 210, fill='accent', kind=OVAL, name='numeral')
        shape_text(c, str(n), 120, 'FFFFFF', F['display'])
        y = 470
        for it in items:
            s = text(sl, MX + 300, y, 540, 34, it, size=22, color='text2', name='item'); bullet(s)
            y += 42
        node_motif(sl, 1010, 130, 1.0)
        for i, (t, _) in enumerate(sections, 1):
            on = i == n
            yy = 300 + (i - 1) * 62
            rounded(sl, 1000, yy, 368, 48, 24, fill='accent' if on else 'surface', line=None if on else 'hairline',
                    lw=1.25, name='map')
            text(sl, 1022, yy, 340, 48, f'{i}   {t}', size=17, font=F['heading'] if on else F['body'], bold=on,
                 color='FFFFFF' if on else 'muted', anchor='m', name='map')
    return sl


def table(sl, x, y, widths, header, rows, row_h=96, cell_size=21):
    """Header band + rows; a cell is markup text, or ('eq', latex). Returns bottom y."""
    total = sum(widths)
    if ANG:
        box(sl, x, y, total, 44, fill='accent', name='th')
    else:
        rounded(sl, x, y, total, 44, 22, fill='accent', name='th')
    cx = x + 24
    for wd, h in zip(widths, header):
        text(sl, cx, y, wd - 24, 44, h.upper() if ANG else h, size=15, font=LABEL, bold=True, color='FFFFFF',
             anchor='m', name='th')
        cx += wd
    y += 54
    for row in rows:
        cx = x + 24
        for j, (wd, cell) in enumerate(zip(widths, row)):
            if isinstance(cell, tuple) and cell[0] == 'eq':
                eq(sl, cx, y + (row_h - 16) / 2 - 36, cell[1], size=24, w=wd - 24, h=72)
            elif j == 0:
                text(sl, cx, y, wd - 24, row_h - 16, cell, size=30 if ANG else 24, font=F['heading'], bold=not ANG,
                     color='navy', anchor='m', name='td')
            else:
                text(sl, cx, y, wd - 24, row_h - 16, cell, size=cell_size, color='navy', anchor='m', name='td')
            cx += wd
        y += row_h
        line(sl, x, y - 8, x + total, y - 8, color='hairline', w=1.0, name='rule')
    return y


def closing_slide(pres, lay, next_lecture, credit_name, credit_role, sources):
    sl = slide(pres, lay, 'Thank you', name='closing #nochrome',
               title_box=(MX + 8, 230, 800, 120) if ANG else (MX + 40, 230, 760, 100),
               title_size=S['cover'] if ANG else S['section'], footer=False)
    if ANG:
        corner_geometry(sl)
    else:
        rounded(sl, MX, 110, 880, 590, 40, fill='surface', line='hairline', lw=1.5, name='frame').ZOrder(1)
        node_motif(sl, 1010, 130, 1.0)
    bx = MX + 8 if ANG else MX + 40
    label_tag(sl, bx, 380, 'Next lecture')
    text(sl, bx, 420, 700, 40, next_lecture, size=28, font=F['heading'], bold=not ANG, color='navy', name='next')
    text(sl, bx, 520, 760, 60, f'With thanks to **{credit_name}**, {credit_role}.', size=20, color='text2',
         name='thanks')
    text(sl, bx, 590, 760, 60, 'Figures: ' + '; '.join(sources) + '.', size=15, color='text2', name='sources')
    return sl

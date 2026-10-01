"""Round 2 design sample: two new lecture identities from the reference templates, same 7 L3 slides. EXPLORATORY.

X 'Schematic' (angular: green/orange template)   Y 'Rounded' (pills and outlined cards: cream template)
Usage:  python build.py            (both)      python build.py X
Output: .build/electronics/round2/<V>/
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.exists(os.path.join(ROOT, 'tools', 'family.py')):
    ROOT = os.path.dirname(ROOT)
LEC = os.path.join(ROOT, 'modules', 'Electronics 1 - 25CPES102', 'Lecture 3 - MOSFETs', 'source')
R1 = os.path.join(os.path.dirname(HERE), 'round1')

if len(sys.argv) == 1:
    for v in 'XY':
        subprocess.run([sys.executable, __file__, v], check=True)
    sys.exit(0)

V = sys.argv[1]
os.environ['DECK_TOKENS'] = os.path.join(HERE, V, 'tokens.json')
sys.path[:0] = [os.path.join(ROOT, 'tools'), R1, LEC]
import family
family.use('electronics')
from deckkit import *                       # noqa
import eqn, states
import circuit, check, figures as FIG

ANG = T['style']['shape'] == 'angular'
W, H = T['canvas']['w'], T['canvas']['h']
MX = G['margin_x']
OUT = family.scratch('electronics', 'round2', V)
PARA = 2
LABEL = F['label']


def _module():
    import importlib.util
    spec = importlib.util.spec_from_file_location('mod', os.path.join(os.path.dirname(os.path.dirname(LEC)), 'module.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


M = _module()


# ------------------------------------------------------------------ components
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


def label_tag(sl, x, y, s, name='tag'):
    """Section / block label: X = filled parallelogram, white caps; Y = outlined pill, accent text."""
    size = S['eyebrow']
    if ANG:
        s = s.upper()
        w = len(s) * size * 0.66 + 40
        shp = para(sl, x, y, w, 26, 'accent', slant=0.4, name=name)
        shape_text(shp, s, size, 'FFFFFF', LABEL)
        return shp, w
    w = len(s) * size * 0.58 + 36
    shp = rounded(sl, x, y, w, 30, 15, fill='surface', line='accent', lw=1.25, name=name)
    shape_text(shp, s, size, 'accent', LABEL)
    return shp, w


def card(sl, x, y, w, h, fill='surface', line_='hairline', name='card'):
    if ANG:
        c = box(sl, x, y, w, h, fill=fill, line=line_, lw=1.25, name=name)
        box(sl, x, y - 1, 56, 5, fill='accent', name=name)            # tab: the angular identity's corner mark
        return c
    return rounded(sl, x, y, w, h, 18, fill=fill, line=line_, lw=1.5, name=name)


def badge(sl, x, y, n, d=32, st=None):
    b = box(sl, x, y, d, d, fill='accent', kind=1 if ANG else OVAL, name='badge')
    shape_text(b, str(n), 17, 'FFFFFF', LABEL)
    if st:
        tag(b, st)
    return b


def result(sl, x, y, s, size=26, name='result'):
    """The final answer: X = copper parallelogram, Y = coral pill; white bold text."""
    import re
    n = len(re.sub(r'_\{(.*?)\}', r'\1', s))
    w = n * size * 0.6 + 56
    h = size * 1.9
    bg = para(sl, x, y, w, h, 'answer', slant=0.3, name=name) if ANG else \
        rounded(sl, x, y, w, h, h / 2, fill='answer', name=name)
    t = text(sl, x, y, w, h, s, size=size, font=LABEL, color='FFFFFF', bold=True, align='c', anchor='m', name=name)
    return bg, t, w


def bullet(shp, char=8226):
    pf = shp.TextFrame.TextRange.ParagraphFormat
    pf.Bullet.Visible = TRUE; pf.Bullet.Character = char
    pf.Bullet.Font.Color.RGB = rgb('accent')
    shp.TextFrame.Ruler.Levels(1).FirstMargin = 0; shp.TextFrame.Ruler.Levels(1).LeftMargin = 26


def eq(sl, x, y, latex, size=None, color='navy', w=820, h=None, st=None, align='l'):
    size = size or S['eq']
    h = h or size * (2.3 if '\\frac' in latex else 1.5)
    return text(sl, x, y, w, h, latex, size=size, font=F['math'], color=color, align=align, anchor='m', wrap=False,
                name='eq' + (' ' + st if st else ''), raw=True)


def figure(sl, key, x, y, w, h):
    """Cleaned reference figure inside a card, fitted and centred, credit inside the card."""
    from PIL import Image
    iw, ih = Image.open(FIG.path(key)).size
    pad, cap = 20, 18
    k = min((w - 2 * pad) / iw, (h - 2 * pad - cap) / ih)
    fw, fh = iw * k, ih * k
    cw, ch = fw + 2 * pad, fh + 2 * pad + cap
    cx, cy = x + (w - cw) / 2, y
    card(sl, cx, cy, cw, ch, name='figure card')
    p = sl.Shapes.AddPicture(FIG.path(key), 0, -1, cx + pad, cy + pad, fw, fh); p.Name = 'figure'
    text(sl, cx + pad, cy + ch - cap - 10, cw - 2 * pad, cap, 'Figure: ' + FIG.credit(key), size=S['caption'],
         color='text2', align='r', name='credit')
    return cx, cy, cw, ch


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
    sl.Name = name or title[:30]
    t = sl.Shapes.Title
    x, y, w, h = title_box or (MX, G['title_y'], W - 2 * MX, G['title_h'])
    t.Left, t.Top, t.Width, t.Height = x, y, w, h
    tf = t.TextFrame
    tf.MarginLeft = tf.MarginRight = tf.MarginTop = tf.MarginBottom = 0
    tf.AutoSize = 0; tf.WordWrap = TRUE; tf.VerticalAnchor = 4
    tr = tf.TextRange; tr.Text = title
    style_range(tr, F['heading'], title_size or S['title'], 'navy', bold=not ANG)
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
        text(sl, fx, H - 41, 600, 22, 'ELEC1  ·  Lecture 3  ·  MOSFETs', size=13, font=F['body'], color='text2',
             name='chrome footer')
    return sl


def corner_geometry(sl, light=False):
    """Structural slides only (X): parallelogram clusters in the corners, from the green/orange template."""
    g, c, n = ('accent', 'answer', 'geo')
    para(sl, -50, 0, 300, 56, g); para(sl, 232, 0, 70, 56, g); para(sl, 300, 0, 560, 14, n)
    para(sl, 1250, 0, 250, 56, c)
    para(sl, -50, H - 56, 200, 56, c); para(sl, 150, H - 14, 560, 14, n)
    para(sl, 1180, H - 56, 320, 56, g); para(sl, 1110, H - 56, 64, 56, g)


def node_motif(sl, x, y, scale=1.0):
    """Structural slides only (Y): a few circuit nodes and traces, decorative."""
    pts = [(0, 0), (120, 0), (120, 90), (240, 90), (240, 20), (330, 20)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        line(sl, x + ax * scale, y + ay * scale, x + bx * scale, y + by * scale, color='geo', w=3, name='motif')
    for px, py in (pts[0], pts[2], pts[5]):
        box(sl, x + px * scale - 9, y + py * scale - 9, 18, 18, fill='surface', line='answer', lw=3, kind=OVAL,
            name='motif')
    box(sl, x + 240 * scale - 7, y + 90 * scale - 7, 14, 14, fill='accent', kind=OVAL, name='motif')


# ------------------------------------------------------------------ slides
MAP = [('Structure and operation', 'how a channel forms; the threshold voltage'),
       ('I–V characteristics', 'cutoff, triode and saturation'),
       ('MOSFETs in DC circuits', 'finding the operating point'),
       ('The MOSFET as an amplifier', 'transconductance, small-signal model'),
       ('The MOSFET as a switch', '')]
OUTCOMES = ['Explain how v_{GS} creates a channel and how v_{DS} pinches it off',
            'Pick the right region and use its i_{D} equation',
            'Find the DC operating point of a MOSFET circuit']


def s_title(pres, lay):
    if ANG:
        sl = slide(pres, lay, 'MOSFETs', name='title #nochrome', title_box=(MX + 8, 250, 760, 130),
                   title_size=S['cover'], footer=False)
        corner_geometry(sl)
        label_tag(sl, MX + 8, 200, f'{M.CODE}  ·  {M.NAME}')
        text(sl, MX + 8, 388, 700, 80, 'Metal-oxide-semiconductor\nfield-effect transistors', size=28,
             color='text2', name='subtitle', spacing=1.0)
        text(sl, MX + 8, 480, 400, 40, 'LECTURE 3', size=34, font=F['heading'], color='answer', name='lecture')
        text(sl, MX + 8, 600, 700, 30, M.AUTHOR, size=22, font=F['body'], bold=True, color='navy', name='author')
        text(sl, MX + 8, 632, 760, 26, f'{M.DEPARTMENT}  ·  {M.YEAR}', size=15, color='text2', name='meta')
        figure(sl, 'structure', 800, 240, 580, 300)
    else:
        sl = slide(pres, lay, 'MOSFETs', name='title #nochrome', title_box=(MX + 40, 250, 700, 110),
                   title_size=S['cover'], footer=False)
        rounded(sl, MX, 90, 720, 620, 36, fill='surface', line='hairline', lw=1.5, name='frame').ZOrder(1)
        label_tag(sl, MX + 40, 140, M.CODE)
        label_tag(sl, MX + 40 + len(M.CODE) * 14 * 0.58 + 50, 140, 'Lecture 3')
        text(sl, MX + 40, 205, 640, 30, M.NAME, size=20, font=F['heading'], color='accent', bold=True, name='course')
        text(sl, MX + 40, 370, 640, 80, 'Metal-oxide-semiconductor\nfield-effect transistors', size=28,
             color='text2', name='subtitle', spacing=1.0)
        text(sl, MX + 40, 590, 640, 30, M.AUTHOR, size=22, font=F['heading'], bold=True, color='navy', name='author')
        text(sl, MX + 40, 624, 660, 26, f'{M.DEPARTMENT}  ·  {M.YEAR}', size=15, color='text2', name='meta')
        node_motif(sl, 860, 120, 1.3)
        figure(sl, 'structure', 830, 330, 540, 300)
    return sl


def s_map(pres, lay):
    sl = slide(pres, lay, 'Lecture map', section='Lecture 3', name='map')
    y = 180
    for i, (t, sub) in enumerate(MAP, 1):
        if ANG:
            b = box(sl, MX, y, 46, 46, fill='accent', name='map n')
            shape_text(b, str(i), 30, 'FFFFFF', F['heading'], bold=False)
            text(sl, MX + 66, y - 2, 640, 32, t, size=25, font=F['body'], bold=True, color='navy', name='map t')
            if sub:
                text(sl, MX + 66, y + 28, 640, 26, sub, size=18, color='text2', name='map s')
            y += 98
        else:
            rounded(sl, MX, y, 720, 70, 35, fill='surface', line='hairline', lw=1.5, name='map pill')
            text(sl, MX + 28, y, 60, 70, f'{i:02d}', size=24, font=F['heading'], bold=True, color='accent',
                 anchor='m', name='map n')
            text(sl, MX + 92, y + 8, 540, 30, t, size=23, font=F['heading'], bold=True, color='navy', name='map t')
            if sub:
                text(sl, MX + 92, y + 38, 540, 24, sub, size=17, color='text2', name='map s')
            c = box(sl, MX + 720 - 58, y + 15, 40, 40, fill='surface', line='accent', lw=1.5, kind=OVAL, name='arrow')
            shape_text(c, '→', 18, 'accent', F['body'])
            y += 92
    px, pw = 880, W - MX - 880
    if ANG:
        card(sl, px, 180, pw, 450, fill='accent_tint', line_=None, name='outcomes')
    else:
        rounded(sl, px, 180, pw, 450, 28, fill='accent_tint', name='outcomes')
    label_tag(sl, px + 30, 206, 'By the end you can')
    y = 260
    for o in OUTCOMES:
        s = text(sl, px + 30, y, pw - 60, 110, o, size=23, color='navy', name='outcome')
        bullet(s, 9632 if ANG else 8226)
        y += 118
    return sl


def s_section(pres, lay, n, title, items):
    if ANG:
        sl = slide(pres, lay, title, name='section #nochrome', title_box=(MX + 8, 330, 820, 110),
                   title_size=S['section'], footer=False)
        corner_geometry(sl)
        text(sl, MX + 4, 140, 400, 200, f'{n:02d}', size=200, font=F['display'], color='accent', anchor='b',
             name='numeral')
        y = 460
        for it in items:
            s = text(sl, MX + 8, y, 640, 34, it, size=23, color='text2', name='item'); bullet(s, 9632)
            y += 42
        mx = 960
        for i, (t, _) in enumerate(MAP, 1):
            on = i == n
            b = box(sl, mx, 190 + (i - 1) * 64, 34, 34, fill='accent' if on else 'surface',
                    line=None if on else 'hairline', lw=1.25, name='map')
            shape_text(b, str(i), 22, 'FFFFFF' if on else 'muted', F['heading'], bold=False)
            text(sl, mx + 50, 190 + (i - 1) * 64, 380, 34, t, size=19, font=F['body'], bold=on,
                 color='navy' if on else 'muted', anchor='m', name='map')
    else:
        sl = slide(pres, lay, title, name='section #nochrome', title_box=(MX + 300, 250, 560, 160),
                   title_size=S['section'], footer=False)
        rounded(sl, MX, 110, 880, 590, 40, fill='surface', line='hairline', lw=1.5, name='frame').ZOrder(1)
        c = box(sl, MX + 50, 230, 210, 210, fill='accent', kind=OVAL, name='numeral')
        shape_text(c, str(n), 120, 'FFFFFF', F['display'])
        y = 470
        for it in items:
            s = text(sl, MX + 300, y, 520, 34, it, size=22, color='text2', name='item'); bullet(s)
            y += 42
        node_motif(sl, 1010, 130, 1.0)
        for i, (t, _) in enumerate(MAP, 1):
            on = i == n
            yy = 300 + (i - 1) * 62
            rounded(sl, 1000, yy, 368, 48, 24, fill='accent' if on else 'surface', line=None if on else 'hairline',
                    lw=1.25, name='map')
            text(sl, 1022, yy, 340, 48, f'{i}   {t}', size=17, font=F['heading'] if on else F['body'], bold=on,
                 color='FFFFFF' if on else 'muted', anchor='m', name='map')
    return sl


def s_channel(pres, lay):
    sl = slide(pres, lay, 'Creating a channel: the threshold voltage', section='1 · Structure and operation',
               name='channel')
    figure(sl, 'channel', 700, 175, 668, 545)
    x, w, y = MX, 580, 190
    for st, s in (('@1', 'A positive v_{GS} pushes holes away from the region under the gate and draws electrons '
                         'in from the n⁺ source and drain.'),
                  ('@2', 'Once enough electrons gather, they form an n-type **inversion layer**: the channel that '
                         'links source to drain.')):
        text(sl, x, y, w, 130, s, size=S['body'], name='para ' + st, spacing=1.05)
        y += 150
    blk = card(sl, x, y, w, 170, fill='accent_tint', line_=None, name='def @3') if ANG else \
        rounded(sl, x, y, w, 170, 24, fill='accent_tint', name='def @3')
    tg, _ = label_tag(sl, x + 26, y + 22, 'Definition', name='def @3')
    text(sl, x + 26, y + 66, w - 52, 100, '**Threshold voltage V_{t}**: the value of v_{GS} at which the channel '
         'just forms.', size=S['body'], name='def @3')
    return sl


def s_regions(pres, lay):
    sl = slide(pres, lay, 'Triode and saturation: one curve, two equations', section='2 · I–V characteristics',
               name='regions')
    figure(sl, 'triode_curve', MX, 175, 690, 480)
    x, w = 810, W - MX - 810
    y = 185
    for st, name, cond, latex in (
            ('@2', 'Triode', 'v_{DS} < v_{GS} − V_{t}',
             r"i_D = k_n^{\prime}\frac{W}{L}\left[(v_{GS}-V_t)\,v_{DS}-\frac{1}{2}v_{DS}^2\right]"),
            ('@3', 'Saturation', 'v_{DS} ≥ v_{GS} − V_{t}',
             r"i_D = \frac{1}{2}\,k_n^{\prime}\frac{W}{L}\,(v_{GS}-V_t)^2")):
        tg, tw = label_tag(sl, x, y, name, name='lab ' + st)
        text(sl, x + tw + 16, y - 2, w - tw - 16, 32, cond, size=22, color='navy', name='lab ' + st, anchor='m')
        eq(sl, x, y + 46, latex, size=26, w=w, st=st)
        y += 190
    s = text(sl, x, y, w, 70, 'Both require v_{GS} > V_{t}: without a channel, i_{D} = 0 (cutoff).', size=21,
             color='text2', name='note @4')
    return sl


def s_example(pres, lay):
    r = check.ex_dc_drain_voltage(); f = check.fmt
    sl = slide(pres, lay, 'Example: find the drain voltage', section='3 · MOSFETs in DC circuits', name='example')
    text(sl, MX, 140, W - 2 * MX, 34, 'Given V_{t} = 1 V and k′_{n}(W/L) = 1 mA/V². The gate draws no current.',
         size=23, color='text2', name='question')
    card(sl, MX, 196, 520, 540, name='circuit card')
    nodes = circuit.dc_example(sl, MX + 150, 236, color='navy', size=19)
    for (px, py), s, st, col in ((nodes['G'], f"V_{{G}} = {f(r['VG'])} V", '@2', 'accent'),
                                 (nodes['S'], f"V_{{S}} = {f(r['VS'])} V", '@6', 'accent'),
                                 (nodes['D'], f"V_{{D}} = {f(r['VD'])} V", '@6', 'answer')):
        text(sl, px + 16, py - 34, 160, 30, s, size=19, font=LABEL, color=col, bold=True, name='node ' + st)
    x, w = 640, W - MX - 640
    y = 200
    steps = [
        ('@2', 'Gate voltage: the divider is unloaded',
         rf"V_G = V_{{DD}}\,\frac{{R_{{G2}}}}{{R_{{G1}}+R_{{G2}}}} = {f(r['VG'])}\ \mathrm{{V}}"),
        ('@3', 'Assume saturation, with V_{GS} = V_{G} − I_{D}R_{S}   (I in mA, R in kΩ)',
         r"I_D = \frac{1}{2}(1)\,(5-6I_D-1)^2"),
        ('@4', 'Solve the quadratic',
         rf"18I_D^2-25I_D+8=0\ \Rightarrow\ I_D={f(r['roots_mA'][1])}\ \text{{or}}\ {f(r['roots_mA'][0])}\ \mathrm{{mA}}"),
    ]
    for i, (st, lab, latex) in enumerate(steps, 1):
        badge(sl, x, y + 1, i, st=st)
        text(sl, x + 48, y, w - 48, 34, lab, size=21, color='text2', name='lab ' + st)
        eq(sl, x + 48, y + 36, latex, size=26, w=w - 48, st=st)
        y += 36 + (72 if '\\frac' in latex else 50) + 18
    badge(sl, x, y + 1, 4, st='@5')
    text(sl, x + 48, y, w - 48, 70,
         f"I_{{D}} = {f(r['roots_mA'][1])} mA would give V_{{GS}} = {f(r['rejected_VGS'])} V < V_{{t}} "
         f"(no channel): reject.  So I_{{D}} = {f(r['ID'] * 1e3)} mA and V_{{GS}} = {f(r['VGS'])} V.",
         size=21, color='navy', name='lab @5')
    y += 86
    badge(sl, x, y + 1, 5, st='@6')
    eq(sl, x + 48, y - 6, rf"V_D = V_{{DD}} - I_DR_D = 10 - {f(r['ID'] * 1e3)}(6) = {f(r['VD'])}\ \mathrm{{V}}",
       size=26, w=w - 48, st='@6')
    y += 54
    bg, t, rw = result(sl, x + 48, y, f"V_{{D}} = {f(r['VD'])} V", size=24, name='answer @6')
    text(sl, x + 48 + rw + 24, y + 2, w - rw - 80, 60,
         f"✓ V_{{DS}} = {f(r['VDS'])} V ≥ V_{{GS}} − V_{{t}} = {f(r['VOV'])} V: saturation holds.",
         size=19, color='ok', name='check @6')
    return sl


def s_summary(pres, lay):
    sl = slide(pres, lay, 'Summary: three regions of operation', section='Lecture 3 · summary', name='summary')
    c1, c2, c3 = MX + 24, MX + 270, MX + 700
    y0, rh = 180, 96
    if ANG:
        box(sl, MX, y0, W - 2 * MX, 44, fill='accent', name='th')
    else:
        rounded(sl, MX, y0, W - 2 * MX, 44, 22, fill='accent', name='th')
    for cx, h in ((c1, 'Region'), (c2, 'Condition'), (c3, 'Drain current')):
        text(sl, cx, y0, 300, 44, h.upper() if ANG else h, size=15, font=LABEL, bold=True, color='FFFFFF',
             anchor='m', name='th')
    rows = [('Cutoff', 'v_{GS} ≤ V_{t}', r"i_D = 0"),
            ('Triode', 'v_{GS} > V_{t},  v_{DS} < v_{GS} − V_{t}',
             r"i_D = k_n^{\prime}\frac{W}{L}\left[(v_{GS}-V_t)\,v_{DS}-\frac{1}{2}v_{DS}^2\right]"),
            ('Saturation', 'v_{GS} > V_{t},  v_{DS} ≥ v_{GS} − V_{t}',
             r"i_D = \frac{1}{2}\,k_n^{\prime}\frac{W}{L}\,(v_{GS}-V_t)^2")]
    y = y0 + 54
    for reg, cond, latex in rows:
        text(sl, c1, y, 240, rh - 16, reg, size=30 if ANG else 24, font=F['heading'], bold=not ANG, color='navy',
             anchor='m', name='td')
        text(sl, c2, y, 420, rh - 16, cond, size=21, color='navy', anchor='m', name='td')
        eq(sl, c3, y + (rh - 16) / 2 - 36, latex, size=24, w=W - MX - c3, h=72)
        y += rh
        line(sl, MX, y - 8, W - MX, y - 8, color='hairline', w=1.0, name='rule')
    y += 24
    for s in ('In a DC problem: **assume** a region, **solve**, then **check** the assumption.',
              'Current saturates because the channel is pinched off at the drain end.'):
        shp = text(sl, MX, y, W - 2 * MX, 40, s, size=23, color='navy', name='takeaway'); bullet(shp, 9632 if ANG else 8226)
        y += 50
    return sl


def main():
    pres, lay = new_pres()
    src = os.path.join(OUT, f'round2-{V}-source.pptx')
    try:
        s_title(pres, lay)
        s_map(pres, lay)
        s_section(pres, lay, 2, 'I–V characteristics', ['Increasing v_{DS}: pinch-off', 'Triode and saturation',
                                                         'The i_{D}–v_{DS} family of curves'])
        s_channel(pres, lay)
        s_regions(pres, lay)
        s_example(pres, lay)
        s_summary(pres, lay)
        pres.SaveAs(src)
    finally:
        pres.Close()
    print('equations:', eqn.inject(src, roman_subs=False))
    for mode in ('teaching', 'solution'):
        for p in states.build(src, OUT, mode):
            print(p)


main()

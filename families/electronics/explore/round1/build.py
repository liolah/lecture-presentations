"""Round 1 design sample: the same 7 real L3 slides in each direction (A, B, C). EXPLORATORY.

Usage:  python build.py            (all variants)     python build.py A    (one variant)
Output: .build/electronics/round1/<V>/  (source, teaching, solution pptx/pdf) + renders under .build/renders/.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.exists(os.path.join(ROOT, 'tools', 'family.py')):
    ROOT = os.path.dirname(ROOT)
LEC = os.path.join(ROOT, 'modules', 'Electronics 1 - 25CPES102', 'Lecture 3 - MOSFETs', 'source')

if len(sys.argv) == 1:                      # driver: one process per variant (deckkit reads tokens at import)
    for v in 'ABC':
        subprocess.run([sys.executable, __file__, v], check=True)
    sys.exit(0)

V = sys.argv[1]
os.environ['DECK_TOKENS'] = os.path.join(HERE, V, 'tokens.json')
sys.path[:0] = [os.path.join(ROOT, 'tools'), HERE, LEC]
import family
family.use('electronics')
from deckkit import *                       # noqa
import deckkit, eqn, states
import circuit, check, figures as FIG

ST = T['style']
W, H = T['canvas']['w'], T['canvas']['h']
MX = G['margin_x']
OUT = family.scratch('electronics', 'round1', V)
FOOT = 'ELEC1 · Lecture 3 · MOSFETs'


# ------------------------------------------------------------------ scaffolding
def new_pres():
    pp = app()
    pres = pp.Presentations.Add(0)
    pres.PageSetup.SlideWidth, pres.PageSetup.SlideHeight = W, H
    bg = pres.SlideMaster.Background.Fill
    bg.Solid(); bg.ForeColor.RGB = rgb('bg')
    lay = [pres.SlideMaster.CustomLayouts(i) for i in range(1, pres.SlideMaster.CustomLayouts.Count + 1)]
    return pres, next(l for l in lay if l.Name == 'Title Only')


def eyebrow_text(s):
    return s.upper() if ST['eyebrow_case'] == 'upper' else s


def slide(pres, lay, title, eyebrow=None, name='', title_box=None, title_size=None, title_color='navy',
          title_font=None, footer=True):
    sl = pres.Slides.AddSlide(pres.Slides.Count + 1, lay)
    sl.Name = name or title[:30]
    t = sl.Shapes.Title
    x, y, w, h = title_box or (MX, G['title_y'], W - 2 * MX, G['title_h'])
    t.Left, t.Top, t.Width, t.Height = x, y, w, h
    tf = t.TextFrame
    tf.MarginLeft = tf.MarginRight = tf.MarginTop = tf.MarginBottom = 0
    tf.AutoSize = 0; tf.WordWrap = TRUE; tf.VerticalAnchor = 4
    tr = tf.TextRange; tr.Text = title
    style_range(tr, title_font or F['heading'], title_size or S['title'], title_color, bold=False)
    tr.ParagraphFormat.Alignment = 1
    t.Name = 'title'
    if eyebrow:
        text(sl, x, y - 30, w, 24, eyebrow_text(eyebrow), size=S['eyebrow'], font=F['eyebrow'],
             color='accent', name='eyebrow')
    if ST['title_rule'] and footer:
        line(sl, MX, y + h + 14, W - MX, y + h + 14, color='hairline', w=1.0, name='rule')
    if footer and ST['footer']:
        text(sl, MX, G['footer_y'], 600, 22, FOOT, size=S['caption'],
             font=F['mono'] if F['eyebrow'] == 'Consolas' else F['body'], color='text2', name='chrome footer')
    return sl


def figure(sl, key, x, y, w, h, credit=True, align='c'):
    """Place a cleaned reference figure, fitted inside (x, y, w, h), in the direction's frame style."""
    from PIL import Image
    p = FIG.path(key)
    iw, ih = Image.open(p).size
    pad = 0 if ST['figure'] == 'bare' else 18
    cap = 22 if credit else 0
    aw, ah = w - 2 * pad, h - 2 * pad - cap
    k = min(aw / iw, ah / ih)
    fw, fh = iw * k, ih * k
    bw, bh = fw + 2 * pad, fh + 2 * pad
    bx = x + (w - bw) / 2 if align == 'c' else x
    by = y
    shapes = []
    if ST['figure'] == 'plate':
        shapes.append(box(sl, bx, by, bw, bh, fill='surface', line='hairline', lw=1.0, name='figure frame'))
    elif ST['figure'] == 'card':
        shapes.append(box(sl, bx, by, bw, bh, fill='surface', line='hairline', lw=0.75, kind=ROUND, radius=0.03,
                          name='figure frame'))
    pic = sl.Shapes.AddPicture(p, 0, -1, bx + pad, by + pad, fw, fh)
    pic.Name = 'figure'
    shapes.append(pic)
    if credit:
        shapes.append(text(sl, bx, by + bh + 6, bw, 20, 'Figure: ' + FIG.credit(key), size=S['caption'],
                           color='text2', align='r', name='credit'))
    return shapes, (bx, by, bw, bh)


def eq(sl, x, y, latex, size=None, color='navy', w=820, h=None, tag_=None, align='l'):
    size = size or S['eq']
    h = h or size * (2.3 if '\\frac' in latex else 1.5)
    s = text(sl, x, y, w, h, latex, size=size, font=F['math'], color=color, align=align, anchor='m', wrap=False,
             name='eq' + (' ' + tag_ if tag_ else ''), raw=True)
    return s


def step_badge(sl, x, y, n, tag_=None):
    d = 30
    b = box(sl, x, y, d, d, fill='accent', kind=OVAL, name='badge')
    t = text(sl, x, y, d, d, str(n), size=16, font=F['heading'], color='FFFFFF', align='c', anchor='m', name='badge')
    if tag_:
        tag([b, t], tag_)
    return b, t


# ------------------------------------------------------------------ slides
def s_title(pres, lay):
    import importlib.util
    spec = importlib.util.spec_from_file_location('mod', os.path.join(os.path.dirname(os.path.dirname(LEC)),
                                                                       'module.py'))
    M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    if V == 'C':   # left navy band (structural slide: decoration allowed)
        sl = slide(pres, lay, 'MOSFETs', name='title #nochrome', title_box=(MX, 250, 640, 90),
                   title_size=S['cover'] + 16, footer=False)
        box(sl, 0, 0, W, 10, fill='accent', name='band')
    else:
        sl = slide(pres, lay, 'MOSFETs', name='title #nochrome', title_box=(MX, 250, 640, 90),
                   title_size=S['cover'] + 16, footer=False)
    text(sl, MX, 190, 700, 28, f'{M.CODE} · {M.NAME}', size=18,
         font=F['eyebrow'], color='accent', name='code')
    text(sl, MX, 350, 640, 80, 'Metal-oxide-semiconductor\nfield-effect transistors', size=28, color='text2',
         name='subtitle', spacing=1.05)
    if V == 'B':
        box(sl, MX, 450, 90, 4, fill='accent', name='rule')
    else:
        line(sl, MX, 452, MX + 90, 452, color='accent', w=3, name='rule')
    text(sl, MX, 470, 640, 30, 'Lecture 3', size=24, font=F['heading'], color='navy', name='lecture')
    text(sl, MX, 640, 700, 30, M.AUTHOR, size=22, font=F['heading'], color='navy', name='author')
    text(sl, MX, 672, 700, 26, f'{M.DEPARTMENT} · {M.YEAR}', size=16, color='text2', name='meta')
    figure(sl, 'structure', 760, 250, 620, 320)
    return sl


MAP = [('Structure and operation', 'how a channel forms; the threshold voltage'),
       ('I–V characteristics', 'cutoff, triode and saturation'),
       ('MOSFETs in DC circuits', 'finding the operating point'),
       ('The MOSFET as an amplifier', 'transconductance, small-signal model'),
       ('The MOSFET as a switch', '')]
OUTCOMES = ['Explain how v_{GS} creates a channel and how v_{DS} pinches it off',
            'Pick the right region and use its i_{D} equation',
            'Find the DC operating point of a MOSFET circuit']


def s_map(pres, lay, current=None):
    sl = slide(pres, lay, 'Lecture map', eyebrow='Lecture 3 · MOSFETs', name='map')
    y = 180
    for i, (t, sub) in enumerate(MAP, 1):
        on = current is None or current == i
        col = 'navy' if on else 'muted'
        num = f'{i:02d}' if V == 'B' else str(i)
        text(sl, MX, y - 2, 60, 44, num, size=32, font=F['mono'] if V == 'B' else F['heading'],
             color='accent' if on else 'muted', name='map n')
        text(sl, MX + 70, y, 640, 36, t, size=28, font=F['heading'] if V != 'B' else F['body'], color=col,
             name='map t', bold=(V == 'B'))
        if sub:
            text(sl, MX + 70, y + 38, 640, 28, sub, size=20, color='text2' if on else 'muted', name='map s')
        y += 100
    # outcomes panel
    px, pw = 860, W - MX - 860
    if V == 'A':
        box(sl, px, 170, pw, 470, fill='accent_tint', name='panel')
    elif V == 'C':
        box(sl, px, 170, pw, 470, fill='surface', line='hairline', lw=0.75, kind=ROUND, radius=0.03, name='panel')
    else:
        line(sl, px, 170, px, 640, color='hairline', w=1.0, name='panel')
    ix = px + 32
    text(sl, ix, 196, pw - 64, 26, eyebrow_text('By the end you can'), size=S['eyebrow'], font=F['eyebrow'],
         color='accent', name='outcomes h')
    y = 240
    for o in OUTCOMES:
        s = text(sl, ix, y, pw - 64, 110, o, size=24, color='navy', name='outcome', spacing=1.0)
        pf = s.TextFrame.TextRange.ParagraphFormat
        pf.Bullet.Visible = TRUE; pf.Bullet.Character = 8212 if V == 'B' else 8226
        pf.Bullet.Font.Color.RGB = rgb('accent')
        s.TextFrame.Ruler.Levels(1).FirstMargin = 0; s.TextFrame.Ruler.Levels(1).LeftMargin = 24
        y += 125
    return sl


def s_section(pres, lay, n, title, items):
    if V == 'C':
        sl = slide(pres, lay, title, name='section #nochrome', title_box=(560, 300, 800, 90),
                   title_size=S['section'], footer=False)
        box(sl, 0, 0, 440, H, fill='accent', name='band')
        text(sl, 0, 250, 440, 240, str(n), size=200, font=F['display'], color='FFFFFF', align='c', anchor='m',
             name='numeral')
        tx = 560
    else:
        sl = slide(pres, lay, title, name='section #nochrome', title_box=(MX, 420, 1100, 90),
                   title_size=S['section'], footer=False)
        num = f'{n:02d}' if V == 'B' else str(n)
        text(sl, MX - 6, 170, 600, 240, num, size=190, font=F['mono'] if V == 'B' else F['display'],
             color='accent', anchor='b', name='numeral')
        if V == 'B':
            line(sl, MX, 530, W - MX, 530, color='hairline', w=1.0, name='rule')
        tx = MX
    y = 540 if V != 'C' else 420
    for it in items:
        text(sl, tx, y, 640, 34, it, size=24, color='text2', name='item')
        y += 40
    # where we are: the lecture map, current section highlighted
    mx = 960
    yy = 200 if V != 'C' else 560
    if V == 'C':
        mx = 560
    else:
        line(sl, mx - 28, 200, mx - 28, 200 + 5 * 52 - 12, color='hairline', w=1.0, name='map rule')
    if V != 'C':
        for i, (t, _) in enumerate(MAP, 1):
            on = i == n
            text(sl, mx, yy, 420, 34, f'{i}  {t}', size=20, font=F['heading'] if on else F['body'],
                 color='navy' if on else 'muted', name='map')
            yy += 52
    return sl


def s_channel(pres, lay):
    sl = slide(pres, lay, 'Creating a channel: the threshold voltage', eyebrow='1 · Structure and operation',
               name='channel')
    figure(sl, 'channel', 700, 160, 668, 560)
    x, w, y = MX, 580, 190
    pts = [('@1', 'A positive v_{GS} pushes holes away from the region under the gate and draws electrons '
                   'in from the n⁺ source and drain.'),
           ('@2', 'Once enough electrons gather, they form an n-type **inversion layer**: the channel that '
                  'links source to drain.')]
    for st, s in pts:
        shp = text(sl, x, y, w, 130, s, size=S['body'], name='para ' + st, spacing=1.05)
        y += 150
    # definition block
    if V == 'B':
        d0 = line(sl, x, y + 4, x, y + 136, color='accent', w=3, name='def @3')
        lab = text(sl, x + 22, y, w - 22, 24, 'DEFINITION', size=15, font=F['mono'], color='accent', name='def @3')
        body = text(sl, x + 22, y + 30, w - 22, 110, '**Threshold voltage V_{t}**: the value of v_{GS} at which '
                    'the channel just forms.', size=S['body'], name='def @3')
    else:
        d0 = box(sl, x, y, w, 150, fill='accent_tint' if V == 'A' else 'surface',
                 line=None if V == 'A' else 'hairline', lw=0.75, name='def @3')
        if V == 'C':
            box(sl, x, y, 6, 150, fill='accent', name='def @3')
        body = text(sl, x + 26, y + 20, w - 50, 110, '**Threshold voltage V_{t}**: the value of v_{GS} at which '
                    'the channel just forms.', size=S['body'], name='def @3')
    return sl


def s_regions(pres, lay):
    sl = slide(pres, lay, 'Triode and saturation: one curve, two equations', eyebrow='2 · I–V characteristics',
               name='regions')
    figure(sl, 'triode_curve', MX, 165, 680, 470, align='l')
    x, w = 800, W - MX - 800
    y = 190
    for st, name, cond, latex in (
            ('@2', 'Triode', 'v_{DS} < v_{GS} − V_{t}',
             r"i_D = k_n^{\prime}\frac{W}{L}\left[(v_{GS}-V_t)\,v_{DS}-\frac{1}{2}v_{DS}^2\right]"),
            ('@3', 'Saturation', 'v_{DS} ≥ v_{GS} − V_{t}',
             r"i_D = \frac{1}{2}\,k_n^{\prime}\frac{W}{L}\,(v_{GS}-V_t)^2")):
        text(sl, x, y, w, 34, f'**{name}**   ' + cond, size=24, color='navy', name='lab ' + st)
        eq(sl, x, y + 44, latex, size=26, w=w, tag_=st)
        if V != 'B':
            line(sl, x, y + 150, x + w, y + 150, color='hairline', w=1.0, name='sep ' + st)
        y += 180
    text(sl, x, y, w, 70, 'Both require v_{GS} > V_{t}: without a channel, i_{D} = 0 (cutoff).', size=22,
         color='text2', name='note @4')
    return sl


def s_example(pres, lay):
    r = check.ex_dc_drain_voltage()
    f = check.fmt
    sl = slide(pres, lay, 'Example: find the drain voltage', eyebrow='3 · MOSFETs in DC circuits', name='example')
    text(sl, MX, 132, W - 2 * MX, 34, 'Given V_{t} = 1 V and k′_{n}(W/L) = 1 mA/V². Assume the gate draws no current.',
         size=24, color='text2', name='question')
    nodes = circuit.dc_example(sl, MX + 120, 215, color='navy', size=20)
    # node labels revealed with the steps
    gx, gy = nodes['G']
    for (px, py), s, st, col in ((nodes['G'], f"V_{{G}} = {f(r['VG'])} V", '@2', 'accent'),
                                 (nodes['S'], f"V_{{S}} = {f(r['VS'])} V", '@6', 'accent'),
                                 (nodes['D'], f"V_{{D}} = {f(r['VD'])} V", '@6', 'answer')):
        text(sl, px + 16, py - 34, 160, 30, s, size=20, color=col, bold=True, name='node ' + st)
    # steps
    x, w = 640, W - MX - 640
    y = 196
    steps = [
        ('@2', 'Gate voltage: the divider is unloaded',
         rf"V_G = V_{{DD}}\,\frac{{R_{{G2}}}}{{R_{{G1}}+R_{{G2}}}} = {f(r['VG'])}\ \mathrm{{V}}"),
        ('@3', 'Assume saturation, with V_{GS} = V_{G} − I_{D}R_{S}  (I in mA, R in kΩ)',
         r"I_D = \frac{1}{2}(1)\,(5-6I_D-1)^2"),
        ('@4', 'Solve the quadratic',
         rf"18I_D^2-25I_D+8=0\ \Rightarrow\ I_D={f(r['roots_mA'][1])}\ \text{{or}}\ {f(r['roots_mA'][0])}\ \mathrm{{mA}}"),
    ]
    for i, (st, lab, latex) in enumerate(steps, 1):
        step_badge(sl, x, y + 2, i, st)
        text(sl, x + 44, y, w - 44, 34, lab, size=22, color='text2', name='lab ' + st)
        e = eq(sl, x + 44, y + 38, latex, size=26, w=w - 44, tag_=st)
        y += 38 + (72 if '\\frac' in latex else 50) + 18
    step_badge(sl, x, y + 2, 4, '@5')
    text(sl, x + 44, y, w - 44, 70,
         f"I_{{D}} = {f(r['roots_mA'][1])} mA would give V_{{GS}} = {f(r['rejected_VGS'])} V < V_{{t}} "
         f"(no channel): reject it.  So I_{{D}} = {f(r['ID'] * 1e3)} mA, V_{{GS}} = {f(r['VGS'])} V.",
         size=22, color='navy', name='lab @5')
    y += 88
    step_badge(sl, x, y + 2, 5, '@6')
    eq(sl, x + 44, y - 4, rf"V_D = V_{{DD}} - I_DR_D = 10 - {f(r['ID'] * 1e3)}(6) = {f(r['VD'])}\ \mathrm{{V}}",
       size=26, w=w - 44, tag_='@6')
    y += 56
    chip(sl, x + 44, y, f"V_{{D}} = {f(r['VD'])} V", size=24, font=F['body'], name='answer @6', kind='answer')
    text(sl, x + 250, y + 2, w - 250, 60,
         f"✓ Check: V_{{DS}} = {f(r['VDS'])} V ≥ V_{{GS}} − V_{{t}} = {f(r['VOV'])} V, so saturation holds.",
         size=20, color='ok', name='check @6')
    return sl


def s_summary(pres, lay):
    sl = slide(pres, lay, 'Summary: three regions of operation', eyebrow='Lecture 3 · summary', name='summary')
    cols = [(MX, 230, 'Region'), (MX + 250, 420, 'Condition'), (MX + 690, W - 2 * MX - 690, 'Drain current')]
    y0, rh = 180, 96
    for cx, cw, h in cols:
        text(sl, cx, y0, cw, 26, eyebrow_text(h) if V != 'B' else h.upper(), size=S['eyebrow'],
             font=F['eyebrow'], color='text2', name='th')
    line(sl, MX, y0 + 36, W - MX, y0 + 36, color='navy' if V == 'B' else 'hairline', w=1.25, name='rule')
    rows = [('Cutoff', 'v_{GS} ≤ V_{t}', r"i_D = 0"),
            ('Triode', 'v_{GS} > V_{t},  v_{DS} < v_{GS} − V_{t}',
             r"i_D = k_n^{\prime}\frac{W}{L}\left[(v_{GS}-V_t)\,v_{DS}-\frac{1}{2}v_{DS}^2\right]"),
            ('Saturation', 'v_{GS} > V_{t},  v_{DS} ≥ v_{GS} − V_{t}', r"i_D = \frac{1}{2}\,k_n^{\prime}\frac{W}{L}\,(v_{GS}-V_t)^2")]
    y = y0 + 50
    for i, (reg, cond, latex) in enumerate(rows):
        if V == 'A' and i % 2 == 1:
            box(sl, MX - 12, y - 8, W - 2 * MX + 24, rh, fill='surface', name='band')
        text(sl, MX, y, 240, rh - 16, reg, size=26, font=F['heading'], color='navy', anchor='m', name='td')
        text(sl, MX + 250, y, 420, rh - 16, cond, size=22, color='navy', anchor='m', name='td')
        eq(sl, MX + 690, y + (rh - 16) / 2 - 36, latex, size=24, w=W - 2 * MX - 690, h=72)
        y += rh
        line(sl, MX, y - 8, W - MX, y - 8, color='hairline', w=0.75, name='rule')
    y += 20
    for s in ('In a DC problem: **assume** a region, **solve**, then **check** the assumption.',
              'Current saturates because the channel is pinched off at the drain end.'):
        shp = text(sl, MX, y, W - 2 * MX, 40, s, size=24, color='navy', name='takeaway')
        pf = shp.TextFrame.TextRange.ParagraphFormat
        pf.Bullet.Visible = TRUE; pf.Bullet.Character = 8226; pf.Bullet.Font.Color.RGB = rgb('accent')
        shp.TextFrame.Ruler.Levels(1).FirstMargin = 0; shp.TextFrame.Ruler.Levels(1).LeftMargin = 24
        y += 52
    return sl


# ------------------------------------------------------------------ build
def main():
    pres, lay = new_pres()
    src = os.path.join(OUT, f'round1-{V}-source.pptx')
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
    print('equations:', eqn.inject(src))
    for mode in ('teaching', 'solution'):
        for p in states.build(src, OUT, mode):
            print(p)


main()

"""Expand tagged final-state slides into instructional states and build deliverables.

Usage:
    python tools/states.py SOURCE.pptx [--family NAME] [--out DIR] [--modes teaching,solution] [--no-pdf]

The deck's family (its `deck_family` property, or --family) decides which tokens the chrome uses;
output defaults to .build/<family>/ (scratch; deliverables are copied into modules/ by the deck's build script).

Tags live in shape names (see families/<family>/design/principles.md):
    @k        visible from state k          @a-b      visible in states a..b
    @dimK     muted from state K            @dimA-B   muted in states A..B
    @final    solution build + last teaching state only
    @teach    teaching build only
Slide names containing '#nochrome' get no progress dots / page number (cover, section, closing).

teaching  -> every tagged slide becomes N slides (state 1..N); bottom-left dots show progress k/N.
solution  -> every tagged slide shows only its final state, minus transient aids
             (shapes shown only in a finite range @a-b, and finite dims @dimA-B).
"""
import argparse, math, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import family


def _engine(src=None):
    """Load deckkit for the deck's family; refuse to mix families."""
    own = family.from_deck(src) if src else None
    env = os.environ.get('DECK_FAMILY')
    if own and env and own != env:
        raise SystemExit(f'{os.path.basename(src)} belongs to family "{own}" but "{env}" is active.')
    os.environ['DECK_FAMILY'] = family.resolve(env or own)
    global app, rgb, text, box, T, C, F, S, OVAL, TRUE, FALSE
    from deckkit import app, rgb, text, box, T, C, F, S, OVAL, TRUE, FALSE

INF = 10 ** 6
_TAG = re.compile(r'@(dim)?(\d+)(?:-(\d+))?$|@(final|teach|q)$')


def tags_of(name):
    t = {'show': [], 'dim': [], 'flags': set()}
    for tok in name.split():
        m = _TAG.match(tok)
        if not m:
            continue
        if m.group(4):
            t['flags'].add(m.group(4))
            continue
        a = int(m.group(2)); b = int(m.group(3)) if m.group(3) else INF
        t['dim' if m.group(1) else 'show'].append((a, b))
    return t


def n_states(sl):
    n = 1
    for shp in sl.Shapes:
        t = tags_of(shp.Name)
        for a, b in t['show'] + t['dim']:
            n = max(n, a, b if b < INF else a)
    return n


def visible(t, s, n, mode):
    if 'teach' in t['flags'] and mode == 'solution':
        return False
    if 'final' in t['flags']:
        return mode == 'solution' or s == n
    if t['show']:
        if mode == 'solution' and all(b < INF for a, b in t['show']):
            return False  # transient focus aid (tint, step callout): not part of the complete solution
        return any(a <= s <= b for a, b in t['show'])
    return True


def dimmed(t, s, mode):
    ranges = t['dim'] if mode == 'teaching' else [(a, b) for a, b in t['dim'] if b >= INF]
    return any(a <= s <= b for a, b in ranges)


def dim_shape(shp):
    muted = rgb('muted')
    try:
        if shp.Type == 6:  # group
            for i in range(1, shp.GroupItems.Count + 1):
                dim_shape(shp.GroupItems(i))
            return
    except Exception:
        pass
    if shp.HasTextFrame and shp.TextFrame.HasText:
        shp.TextFrame.TextRange.Font.Color.RGB = muted
    try:
        if shp.Line.Visible:
            shp.Line.ForeColor.RGB = muted
        if shp.Fill.Visible and shp.Fill.Transparency > 0.3:
            shp.Fill.ForeColor.RGB = muted
    except Exception:
        pass


def apply_state(sl, s, n, mode):
    doomed = []
    for i in range(1, sl.Shapes.Count + 1):
        shp = sl.Shapes(i)
        t = tags_of(shp.Name)
        if not visible(t, s, n, mode):
            doomed.append(i)
        elif dimmed(t, s, mode):
            dim_shape(shp)
    for i in reversed(doomed):
        sl.Shapes(i).Delete()


def dot_color(i):
    """Gradient across the 5 progress dots, left -> right: tokens progress.gradient = [from, to]
    (default navy -> chrome_cyan)."""
    a, b = (C[k] for k in T['progress'].get('gradient', ['navy', 'chrome_cyan']))
    f = i / 4
    return ''.join('%02X' % round(int(a[k:k + 2], 16) * (1 - f) + int(b[k:k + 2], 16) * f) for k in (0, 2, 4))


def progress(sl, k, n):
    p = T['progress']
    filled = p['dots'] if n <= 1 else max(1, math.ceil(p['dots'] * k / n))
    for i in range(p['dots']):
        col = dot_color(i) if i < filled else C['hairline']
        box(sl, p['x'] + i * p['pitch'], p['y'], p['d'], p['d'], fill=col, kind=OVAL, name='chrome progress')
    if n > 1:
        text(sl, p['x'] + p['dots'] * p['pitch'] + 6, p['y'] - 4, 80, 20, f'{k}/{n}', size=14,
             color='text2', name='chrome progress label')


def page_number(sl, k):
    w = T['canvas']['w']
    text(sl, w - 72 - 60, T['progress']['y'] - 4, 60, 22, str(k), size=S['page_no'], color='text2',
         align='r', name='chrome page')


def build(src, out_dir, mode, pdf=True):
    _engine(src)
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(src))[0]
    dst = os.path.abspath(os.path.join(out_dir, f'{stem}-{mode}.pptx'))
    shutil.copyfile(src, dst)
    pp = app()
    pres = pp.Presentations.Open(dst, FALSE, FALSE, FALSE)
    try:
        for i in range(pres.Slides.Count, 0, -1):
            sl = pres.Slides(i)
            n = n_states(sl)
            chrome = '#nochrome' not in sl.Name
            if mode == 'teaching' and n > 1:
                copies = [sl]
                for _ in range(n - 1):
                    copies.append(copies[-1].Duplicate().Item(1))
                for k, c in enumerate(copies, 1):
                    apply_state(c, k, n, mode)
                    if chrome: progress(c, k, n)
            else:
                apply_state(sl, n, n, mode)
                if chrome: progress(sl, n, n)
        for i in range(1, pres.Slides.Count + 1):
            if '#nochrome' not in pres.Slides(i).Name:
                page_number(pres.Slides(i), i)
        pres.Save()
        out = [dst]
        if pdf:
            p = dst[:-5] + '.pdf'
            pres.SaveAs(p, 32)
            out.append(p)
        return out
    finally:
        pres.Close()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--family')
    ap.add_argument('--out')
    ap.add_argument('--modes', default='teaching,solution')
    ap.add_argument('--no-pdf', action='store_true')
    a = ap.parse_args()
    fam = family.resolve(a.family, deck=a.src)
    os.environ['DECK_FAMILY'] = fam
    a.out = a.out or family.scratch(fam)
    for m in a.modes.split(','):
        for f in build(os.path.abspath(a.src), a.out, m, pdf=not a.no_pdf):
            print(f)

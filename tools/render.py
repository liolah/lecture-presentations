"""Render slides to PNG via PowerPoint COM (read-only open), or LibreOffice + pdftoppm without PowerPoint,
+ optional contact sheet.

Usage:
    python tools/render.py DECK.pptx [--slides 1-5,9] [--width 1280] [--out .build/renders] [--sheet] [--force]

Per-slide XML hashes are cached in <out>/<deck>/index.json; unchanged slides are not re-exported
(token/time saver: only review what changed). Prints the paths of the PNGs that were (re)rendered.
"""
import argparse, glob, hashlib, json, os, re, sys, zipfile
from lxml import etree

NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def slide_hashes(path):
    z = zipfile.ZipFile(path)
    pres = etree.fromstring(z.read('ppt/presentation.xml'))
    rid = {r.get('Id'): r.get('Target') for r in etree.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
    out = []
    for s in pres.findall('.//p:sldId', NS):
        part = 'ppt/' + rid[s.get('{%s}id' % NS['r'])]
        h = hashlib.md5(z.read(part))
        rel = part.replace('slides/', 'slides/_rels/') + '.rels'
        if rel in z.namelist():
            h.update(z.read(rel))
        out.append(h.hexdigest()[:12])
    return out


def parse_sel(sel, n):
    if not sel:
        return list(range(1, n + 1))
    s = set()
    for part in sel.split(','):
        a, _, b = part.partition('-')
        s.update(range(int(a), int(b or a) + 1))
    return sorted(i for i in s if 1 <= i <= n)


def contact_sheet(pngs, out, cols=4, tw=400):
    from PIL import Image, ImageDraw
    ims = [Image.open(p) for p in pngs]
    th = int(tw * ims[0].height / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * (tw + 8) + 8, rows * (th + 26) + 8), (90, 90, 90))
    d = ImageDraw.Draw(sheet)
    for i, (p, im) in enumerate(zip(pngs, ims)):
        x = 8 + (i % cols) * (tw + 8); y = 8 + (i // cols) * (th + 26)
        sheet.paste(im.resize((tw, th)), (x, y + 18))
        d.text((x, y + 3), os.path.basename(p), fill=(255, 255, 255))
    sheet.save(out, quality=85)
    return out


def _backend():
    if os.environ.get('DECKKIT_BACKEND'):
        return os.environ['DECKKIT_BACKEND']
    try:
        import win32com.client  # noqa
        return 'com'
    except ImportError:
        return 'pptx'


def _render_pdf(deck, d, todo, width):
    """No PowerPoint: PPTX -> PDF (LibreOffice) -> PNG per slide (pdftoppm, else PyMuPDF)."""
    import shutil, subprocess, tempfile
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import pptcom
    tmp = tempfile.mkdtemp()
    pdf = pptcom.to_pdf(deck, os.path.join(tmp, 'deck.pdf'))
    if shutil.which('pdftoppm'):
        for i in todo:
            subprocess.run(['pdftoppm', '-png', '-singlefile', '-f', str(i), '-l', str(i), '-scale-to-x', str(width),
                            '-scale-to-y', '-1', pdf, os.path.join(d, 's%03d' % i)], check=True)
    else:
        import fitz
        doc = fitz.open(pdf)
        for i in todo:
            pg = doc[i - 1]
            pg.get_pixmap(matrix=fitz.Matrix(width / pg.rect.width, width / pg.rect.width)).save(
                os.path.join(d, 's%03d.png' % i))
    shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('deck')
    ap.add_argument('--slides')
    ap.add_argument('--width', type=int, default=1280)
    ap.add_argument('--out', default=os.path.join(ROOT, '.build', 'renders'))
    ap.add_argument('--sheet', action='store_true')
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    deck = os.path.abspath(a.deck)
    name = re.sub(r'[^A-Za-z0-9_.-]', '_', os.path.splitext(os.path.basename(deck))[0])
    d = os.path.abspath(os.path.join(a.out, name))  # COM Export needs an absolute path
    os.makedirs(d, exist_ok=True)
    idx_path = os.path.join(d, 'index.json')
    idx = json.load(open(idx_path)) if os.path.exists(idx_path) else {}
    hashes = slide_hashes(deck)
    want = parse_sel(a.slides, len(hashes))
    todo = [i for i in want if a.force or idx.get(str(i)) != hashes[i - 1]
            or not os.path.exists(os.path.join(d, 's%03d.png' % i))]
    if todo and _backend() == 'pptx':
        _render_pdf(deck, d, todo, a.width)
        for i in todo:
            idx[str(i)] = hashes[i - 1]
        json.dump({k: v for k, v in idx.items() if int(k) <= len(hashes)}, open(idx_path, 'w'), indent=0)
    elif todo:
        import win32com.client
        pp = win32com.client.Dispatch('PowerPoint.Application')
        p = pp.Presentations.Open(deck, True, False, False)
        try:
            h = int(a.width * p.PageSetup.SlideHeight / p.PageSetup.SlideWidth)
            for i in todo:
                p.Slides(i).Export(os.path.join(d, 's%03d.png' % i), 'PNG', a.width, h)
                idx[str(i)] = hashes[i - 1]
        finally:
            p.Close()
        # drop stale entries beyond deck length
        idx = {k: v for k, v in idx.items() if int(k) <= len(hashes)}
        json.dump(idx, open(idx_path, 'w'), indent=0)
    for i in todo:
        print(os.path.join(d, 's%03d.png' % i))
    if a.sheet:
        pngs = [os.path.join(d, 's%03d.png' % i) for i in want]
        print(contact_sheet(pngs, os.path.join(d, 'sheet.jpg')))
    if not todo:
        print('(no changed slides)', file=sys.stderr)


if __name__ == '__main__':
    main()

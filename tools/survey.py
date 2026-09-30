"""Survey reference inputs once, cheaply: a cached text digest (+ a contact sheet for decks).

Usage:
    python tools/survey.py FILE [FILE ...] [--force] [--no-sheet]

For each input (pptx / pdf / docx; old .ppt / .doc / .odp / .odt are converted with LibreOffice first) writes
.build/digest/<stem>/digest.md, page images of PDFs (pages/pNN.png), the pictures embedded in decks and Word files
(media/), and for decks also sheet.jpg (via render.py, low-res). Inputs are keyed by content hash in .build/digest/index.json, so an unchanged
file is never re-processed (prints the cached path instead). PDF pages with almost no text layer are
flagged "SCANNED: read visually" (handwritten answer keys, figure pages).

Token rule: read digest.md first; open the original only for what the digest flags (figures, scans).
Curated, verified content (answer transcriptions, the teacher's REV1.0 comments) goes into the deck's
own source/digest.md, which is versioned with the deck.
"""
import argparse, hashlib, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.build', 'digest')


def sha(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def pptx_digest(path):
    from pptx import Presentation
    p = Presentation(path)
    out = []

    def walk(shapes, ind=''):
        for sh in shapes:
            if sh.shape_type == 6:  # group
                walk(sh.shapes, ind + '  ')
                continue
            if getattr(sh, 'has_table', False) and sh.has_table:
                rows = [' | '.join(c.text.strip() for c in r.cells) for r in sh.table.rows]
                out.append(f'{ind}- TABLE {sh.name}:\n' + '\n'.join(f'{ind}    {r}' for r in rows))
            elif sh.has_text_frame and sh.text_frame.text.strip():
                t = sh.text_frame.text.strip().replace('\n', ' / ')
                out.append(f'{ind}- {t}')
            elif sh.shape_type == 13:
                out.append(f'{ind}- [picture {sh.name} {round(sh.width / 12700)}x{round(sh.height / 12700)}pt]')
            elif sh.shape_type in (7, 16):  # OLE / embedded (e.g. equations)
                out.append(f'{ind}- [embedded object {sh.name}]')
    for i, s in enumerate(p.slides, 1):
        out.append(f'\n## slide {i}')
        walk(s.shapes)
        if s.has_notes_slide and s.notes_slide.notes_text_frame.text.strip():
            out.append('- NOTES: ' + s.notes_slide.notes_text_frame.text.strip().replace('\n', ' / '))
    return '\n'.join(out)


def _pdf_reader(path):
    for mod in ('PyPDF2', 'pypdf'):
        try:
            return __import__(mod, fromlist=['PdfReader']).PdfReader(path)
        except ImportError:
            continue
    return None


def pdf_digest(path):
    r = _pdf_reader(path)
    if r is None:                                   # neither PyPDF2 nor pypdf: pdfplumber
        import pdfplumber
        out = []
        with pdfplumber.open(path) as pdf:
            for i, pg in enumerate(pdf.pages, 1):
                t = (pg.extract_text() or '').strip()
                flag = ' SCANNED: read visually' if len(t) < 60 else (' (+figures: check visually)' if pg.images else '')
                out.append(f'\n## page {i}{flag}\n{t}')
        return '\n'.join(out)
    out = []
    for i, pg in enumerate(r.pages, 1):
        try:
            t = (pg.extract_text() or '').strip()
        except Exception:
            t = ''
        try:  # only a count is needed; some embedded images fail to decode
            xo = pg['/Resources'].get('/XObject', {}) if '/Resources' in pg else {}
            imgs = len(xo.get_object()) if hasattr(xo, 'get_object') else len(xo)
        except Exception:
            imgs = 1
        flag = ' SCANNED: read visually' if len(t) < 60 else (' (+figures: check visually)' if imgs else '')
        out.append(f'\n## page {i}{flag}\n{t}')
    return '\n'.join(out)


def docx_digest(path):
    import docx
    d = docx.Document(path)
    out = [p.text for p in d.paragraphs if p.text.strip()]
    for k, tb in enumerate(d.tables, 1):
        out.append(f'\nTABLE {k}:')
        out += [' | '.join(c.text.strip() for c in r.cells) for r in tb.rows]
    n_img = len([r for r in d.part.rels.values() if 'image' in r.reltype])
    if n_img:
        out.append(f'\n[{n_img} embedded images: check visually]')
    return '\n'.join(out)


def pdf_pages(path, d, dpi=100):
    """Page images for visual reading (scans, handwriting, figures): pages/p01.png ... (pdftoppm, else PyMuPDF)."""
    import shutil
    pd = os.path.join(d, 'pages')
    os.makedirs(pd, exist_ok=True)
    if shutil.which('pdftoppm'):
        subprocess.run(['pdftoppm', '-png', '-r', str(dpi), path, os.path.join(pd, 'p')], check=False,
                       capture_output=True)
        for f in os.listdir(pd):                    # p-1.png / p-01.png -> p01.png
            m = re.match(r'p-0*(\d+)\.png$', f)
            if m:
                os.replace(os.path.join(pd, f), os.path.join(pd, 'p%02d.png' % int(m.group(1))))
    else:
        try:
            import fitz
        except ImportError:
            return None
        for i, pg in enumerate(fitz.open(path), 1):
            pg.get_pixmap(dpi=dpi).save(os.path.join(pd, 'p%02d.png' % i))
    return pd


def media(path, d):
    """Pictures embedded in a .docx / .pptx (figures, scanned answers) -> media/."""
    import zipfile
    md, n = os.path.join(d, 'media'), 0
    with zipfile.ZipFile(path) as z:
        for f in z.namelist():
            if re.search(r'/media/[^/]+\.(png|jpe?g|gif|bmp|tiff?|emf|wmf)$', f, re.I):
                os.makedirs(md, exist_ok=True)
                with open(os.path.join(md, os.path.basename(f)), 'wb') as o:
                    o.write(z.read(f))
                n += 1
    return md if n else None


LEGACY = {'.ppt': 'pptx', '.pps': 'pptx', '.odp': 'pptx', '.doc': 'docx', '.odt': 'docx', '.rtf': 'docx'}


def convert_legacy(path, d):
    """.ppt / .doc / .odp / .odt / .rtf -> .pptx / .docx with LibreOffice (headless)."""
    import shutil
    exe = shutil.which('soffice') or shutil.which('libreoffice')
    if not exe:
        raise SystemExit(f'{os.path.basename(path)}: converting this format needs LibreOffice (soffice)')
    os.makedirs(d, exist_ok=True)
    target = LEGACY[os.path.splitext(path)[1].lower()]
    subprocess.run([exe, '--headless', '--convert-to', target, '--outdir', d, path], check=True, capture_output=True)
    return os.path.join(d, os.path.splitext(os.path.basename(path))[0] + '.' + target)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--no-sheet', action='store_true')
    ap.add_argument('--no-pages', action='store_true', help='skip the PDF page images')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    idx_p = os.path.join(OUT, 'index.json')
    idx = json.load(open(idx_p)) if os.path.exists(idx_p) else {}
    for f in a.files:
        f = os.path.abspath(f)
        # parent folder in the name: "Sheet 1.pdf" exists in several modules
        stem = re.sub(r'[^A-Za-z0-9_.-]+', '_', os.path.basename(os.path.dirname(f))[:24] + '__' +
                      os.path.splitext(os.path.basename(f))[0])
        if not f.lower().endswith('.pdf'):          # "Sheet 1.pdf" and "Sheet 1.docx" side by side
            stem += '_' + os.path.splitext(f)[1][1:].lower()
        d = os.path.join(OUT, stem)
        h = sha(f)
        md = os.path.join(d, 'digest.md')
        if not a.force and idx.get(f) == h and os.path.exists(md):
            print('cached', md)
            continue
        os.makedirs(d, exist_ok=True)
        ext = os.path.splitext(f)[1].lower()
        src = convert_legacy(f, d) if ext in LEGACY else f
        ext = os.path.splitext(src)[1].lower()
        body = {'.pptx': pptx_digest, '.pdf': pdf_digest, '.docx': docx_digest}[ext](src)
        extra = []
        if ext == '.pdf' and not a.no_pages:
            pd = pdf_pages(src, d)
            if pd:
                extra.append(f'page images: {pd}{os.sep}pNN.png (view the flagged pages)')
        if ext in ('.pptx', '.docx'):
            mdir = media(src, d)
            if mdir:
                extra.append(f'embedded pictures: {mdir}')
        try:
            rel = os.path.relpath(f, ROOT)
        except ValueError:                          # another drive (Windows)
            rel = f
        with open(md, 'w', encoding='utf-8') as o:
            o.write(f'# {os.path.basename(f)}\nsource: {rel}\nhash: {h}\n' + ''.join(e + '\n' for e in extra) +
                    f'{body}\n')
        if ext == '.pptx' and not a.no_sheet:
            subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'render.py'), src, '--sheet', '--width', '960',
                            '--out', d], check=False, capture_output=True)
        idx[f] = h
        json.dump(idx, open(idx_p, 'w'), indent=0)
        print('wrote', md)


if __name__ == '__main__':
    main()

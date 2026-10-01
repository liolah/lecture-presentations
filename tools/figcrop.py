"""Clean a reference figure out of an original slide.

Renders ONLY the chosen shapes of one slide (everything else hidden) at high resolution, crops to their union,
trims near-white margins and saves a PNG. Overlaid label boxes (the originals paste white text boxes over web
images) are flattened into the figure, so the result is one clean picture that can be framed and credited.

Usage:
    python tools/figcrop.py DECK.pptx SLIDE SHAPE_ID[,SHAPE_ID...] OUT.png [--scale 3] [--pad 6]
Shape ids come from tools/shapes.py. The original deck is never modified (a scratch copy is rendered).
Programmatic use: crop(deck, slide, ids, out, scale=3).
"""
import argparse, os, shutil, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import family


def _trim(im, thresh=246, pad=6):
    from PIL import ImageChops, Image
    g = im.convert('L').point(lambda v: 255 if v >= thresh else 0)
    bbox = ImageChops.invert(g).getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def crop(deck, slide, ids, out, scale=3.0, pad=6, trim=True):
    import win32com.client
    from PIL import Image
    tmpd = family.scratch('figcrop')
    tmp = os.path.join(tmpd, 'src.pptx')
    shutil.copyfile(os.path.abspath(deck), tmp)
    pp = win32com.client.Dispatch('PowerPoint.Application')
    pres = pp.Presentations.Open(tmp, False, False, False)
    try:
        sl = pres.Slides(slide)
        W, H = pres.PageSetup.SlideWidth, pres.PageSetup.SlideHeight
        box = None
        for i in range(1, sl.Shapes.Count + 1):
            sh = sl.Shapes(i)
            if sh.Id in ids:
                b = (sh.Left, sh.Top, sh.Left + sh.Width, sh.Top + sh.Height)
                box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
            else:
                sh.Visible = 0
        if box is None:
            raise SystemExit(f'no shapes {ids} on slide {slide}')
        sl.FollowMasterBackground = 0
        sl.Background.Fill.Solid()
        sl.Background.Fill.ForeColor.RGB = 0xFFFFFF
        sl.DisplayMasterShapes = 0
        png = os.path.join(tmpd, 'full.png')
        wpx = int(W * scale)
        sl.Export(png, 'PNG', wpx, int(H * scale))
    finally:
        pres.Close()
    im = Image.open(png).convert('RGB')
    k = im.width / W
    x0, y0, x1, y1 = (max(0, int(box[0] * k)), max(0, int(box[1] * k)),
                      min(im.width, int(box[2] * k) + 1), min(im.height, int(box[3] * k) + 1))
    im = im.crop((x0, y0, x1, y1))
    if trim:
        im = _trim(im, pad=pad)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    im.save(out)
    return out, im.size


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('deck'); ap.add_argument('slide', type=int); ap.add_argument('ids'); ap.add_argument('out')
    ap.add_argument('--scale', type=float, default=3.0); ap.add_argument('--pad', type=int, default=6)
    a = ap.parse_args()
    print(*crop(a.deck, a.slide, {int(x) for x in a.ids.split(',')}, a.out, a.scale, a.pad))

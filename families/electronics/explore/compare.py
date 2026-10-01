"""Side-by-side comparison of exploration variants: rows = variants, columns = chosen slides.

Usage: python compare.py ROUND SLIDES VARIANTS OUT     e.g.  python compare.py round1 1,4,5,6 A,B,C out.jpg
Reads renders from .build/renders/<round>-<V>-source-solution/sNNN.png (made by tools/render.py).
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(ROOT, 'tools', 'family.py')):
    ROOT = os.path.dirname(ROOT)


def main(rnd, slides, variants, out, tw=760):
    slides = [int(s) for s in slides.split(',')]
    variants = variants.split(',')
    lab = 70
    th = int(tw * 9 / 16)
    sheet = Image.new('RGB', (lab + len(slides) * (tw + 12) + 12, len(variants) * (th + 12) + 12), (70, 70, 74))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype('segoeuib.ttf', 44)
    except OSError:
        font = ImageFont.load_default()
    for r, v in enumerate(variants):
        y = 12 + r * (th + 12)
        d.text((20, y + th // 2 - 26), v, fill=(255, 255, 255), font=font)
        for c, s in enumerate(slides):
            p = os.path.join(ROOT, '.build', 'renders', f'{rnd}-{v}-source-solution', 's%03d.png' % s)
            im = Image.open(p).convert('RGB').resize((tw, th), Image.LANCZOS)
            sheet.paste(im, (lab + 12 + c * (tw + 12), y))
    sheet.save(out, quality=90)
    print(out)


if __name__ == '__main__':
    main(*sys.argv[1:5])

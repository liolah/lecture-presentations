"""One-command visual review of a tagged source deck (scratch only).

    python tools/review.py SRC.pptx [--teaching 12,40-44] [--width 1280]

1. lint (errors + warning count),
2. solution build (no PDF) into .build/<family>/ and a contact sheet of it,
3. optionally teaching-build slides by number (e.g. mid-animation states) rendered at full width.
Prints the paths to look at. Unchanged slides are not re-rendered (render.py hash cache).
"""
import argparse, os, subprocess, sys
TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import family


def run(*args, check=True):
    r = subprocess.run([sys.executable, *args], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode and check:
        print(r.stdout[-2000:], r.stderr[-2000:])
        raise SystemExit(r.returncode)
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--teaching')
    ap.add_argument('--width', default='1280')
    a = ap.parse_args()
    src = os.path.abspath(a.src)
    fam = family.resolve(deck=src)
    os.environ['DECK_FAMILY'] = fam
    out = family.scratch(fam)
    lint = run(os.path.join(TOOLS, 'lint.py'), src, check=False).strip().splitlines()  # report, keep going
    print('\n'.join([l for l in lint if 'ERROR' in l] + lint[-1:]))
    modes = 'solution,teaching' if a.teaching else 'solution'
    run(os.path.join(TOOLS, 'states.py'), src, '--modes', modes, '--no-pdf', '--out', out)
    stem = os.path.splitext(os.path.basename(src))[0]
    sol = os.path.join(out, f'{stem}-solution.pptx')
    print(run(os.path.join(TOOLS, 'render.py'), sol, '--sheet', '--width', a.width).strip().splitlines()[-1])
    if a.teaching:
        tea = os.path.join(out, f'{stem}-teaching.pptx')
        print(run(os.path.join(TOOLS, 'render.py'), tea, '--slides', a.teaching, '--width', a.width).strip())


if __name__ == '__main__':
    main()
